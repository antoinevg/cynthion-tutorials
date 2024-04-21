import logging, sys

from amaranth import *
from amaranth.build     import Attrs, Pins, PinsN, Platform, Resource, Subsignal

from amaranth.lib.fifo    import AsyncFIFO
from amaranth.lib.memory  import Memory

from luna.gateware.platform import NullPin
from luna.gateware.stream   import StreamInterface

from tutorials.gateware.bridge    import StreamBridge
from tutorials.gateware.interface import RxRgmii


# - module: Mac ---------------------------------------------------------------

class Mac(Elaboratable):
    def __init__(self, rx_rgmii, buffer_len=2048):
        self.rx_rgmii = rx_rgmii

        self.rx_buffer = Memory(shape=unsigned(8), depth=buffer_len, init=[])
        self.rx_read   = self.rx_buffer.read_port()
        self.rx_write  = self.rx_buffer.write_port(domain="eth_rx")

        # outputs
        self.rx_valid  = Signal()
        self.rx_offset = Signal(self.rx_write.addr.width)
        self.rx_len    = Signal(self.rx_write.addr.width)

    def elaborate(self, platform):
        m = Module()
        m.submodules += self.rx_buffer

        rx_control = self.rx_rgmii.rx_control_out
        rx_data    = self.rx_rgmii.rx_data_out

        # write incoming packets to rx_buffer
        addr = Signal(self.rx_write.addr.width)
        debug_data = Signal(8)
        with m.FSM(domain="eth_rx") as fsm:
            m.d.comb += [
                self.rx_write.addr.eq(addr),
                self.rx_write.data.eq(rx_data),
                #self.rx_write.data.eq(debug_data), # debug
                self.rx_write.en.eq(rx_control == 0b11)
            ]

            with m.State("IDLE"):
                m.d.eth_rx += self.rx_valid.eq(0)
                m.d.eth_rx += self.rx_len.eq(0)
                with m.If(rx_control == 0b11): # TODO both ?
                    m.d.eth_rx += self.rx_offset.eq(addr)
                    m.next = "RX_FRAME"

            with m.State("RX_FRAME"):
                m.d.eth_rx += debug_data.eq(debug_data + 1) # debug
                m.d.eth_rx += addr.eq(addr + 1)
                m.d.eth_rx += self.rx_len.eq(self.rx_len + 1)
                with m.If(rx_control != 0b11): # TODO both ?
                    m.next = "EOF"

            with m.State("EOF"):
                m.d.eth_rx += self.rx_valid.eq(1)
                m.next = "IDLE"


        return m

# - module: Top ---------------------------------------------------------------

class Top(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        # detect platform and add additional platform resources
        from cynthion.gateware.platform         import CynthionPlatformRev1D2
        from tutorials.gateware.platform.ecpix5 import ECPIX585Rev03Platform
        if type(platform) is CynthionPlatformRev1D2:
            from tutorials.gateware.platform.cynthion import RGMII_RESOURCES
            platform.add_resources(RGMII_RESOURCES)
            debug0 = Signal(8)
            debug1 = Signal(8)
        elif type(platform) is ECPIX585Rev03Platform:
            from tutorials.gateware.platform.ecpix5 import RGMII_RESOURCES
            platform.add_resources(RGMII_RESOURCES)
            user_io0  = platform.request("user_io", 0)
            user_io1  = platform.request("user_io", 1)
            m.d.comb += [
                user_io0.oe.eq(1),
                user_io1.oe.eq(1),
            ]
            debug0 = Cat([user_io0.o[i] for i in range(0, 8)])
            debug1 = Cat([user_io1.o[i] for i in range(0, 8)])
        else:
            logging.error(f"unsupported platform: {platform}")
            sys.exit(0)

        # resources
        leds = Cat(platform.request_optional("led", i, default=NullPin()).o for i in range(0, 8))
        rgmii    = platform.request("eth_rgmii", 0)

        # generate domain clocks/resets
        m.submodules.car = platform.clock_domain_generator()

        # add eth_rx domain from rgmii.rx_clk: 125 MHz (external)
        m.domains.eth_rx = ClockDomain("eth_rx")
        m.d.comb += ClockSignal("eth_rx").eq(rgmii.rx_clk.i)

        # create MAC
        rx_delay=2e-9 # Numato RTL8211E
        #rx_delay=0   # ecpix5 KSZ9031RNXCC-TR
        rx_rgmii = RxRgmii(rgmii.rx_ctrl.i, rgmii.rx_data.i, rx_delay=rx_delay)
        mac      = Mac(rx_rgmii)
        m.submodules += [rx_rgmii, mac]

        # create USB interface
        m.submodules.usb_bridge = usb_bridge = StreamBridge()

        # wire up ethernet MAC & StreamDevice
        stream = StreamInterface(payload_width=8)
        m.d.comb += usb_bridge.stream_ep.stream.stream_eq(stream)

        # stream packets over usb
        delim      = Signal(8)
        rx_addr    = Signal.like(mac.rx_offset) # cdc
        rx_len     = Signal.like(mac.rx_len)    # cdc
        bytes_sent = Signal.like(rx_len)
        fsm_state  = Signal(4)

        # synchronize mac rx_offset, rx_len signals with usb domain
        mac_rx_offset = Signal.like(mac.rx_offset)
        mac_rx_len    = Signal.like(mac.rx_len)
        mac_rx_valid  = Signal()
        mac_rx_ack    = Signal()
        m.submodules.mac_rx_fifo = mac_rx_fifo = AsyncFIFO(
            #width=mac.rx_offset.width + mac.rx_len.width,
            width=11 + mac.rx_len.width,
            depth=4,
            r_domain = "usb",
            w_domain = "eth_rx",
        )
        m.d.comb += [
            # mac side
            mac_rx_fifo.w_data.eq(Cat(mac.rx_offset, mac.rx_len)),
            mac_rx_fifo.w_en.eq(mac.rx_valid),
            # usb side
            Cat(mac_rx_offset, mac_rx_len).eq(mac_rx_fifo.r_data),
            mac_rx_valid.eq(mac_rx_fifo.r_rdy),
            mac_rx_fifo.r_en.eq(mac_rx_ack),
        ]

        with m.FSM(domain="usb") as fsm:
            with m.State("IDLE"):
                m.d.comb += fsm_state.eq(0b0001)
                m.d.comb += stream.valid.eq(0)
                m.d.usb += mac_rx_ack.eq(0)

                # when we have received a packet...
                with m.If(mac_rx_valid): # cdc
                    m.d.usb += [
                        delim.eq(0),
                        bytes_sent.eq(0),
                        rx_addr.eq(mac_rx_offset), # cdc
                        rx_len.eq(mac_rx_len),     # cdc
                        #rx_len.eq(14),
                    ]
                    m.next = "HEADER_LSB"

            with m.State("HEADER_LSB"):
                # write first byte of rx_len
                m.d.comb += fsm_state.eq(0b0010)
                m.d.comb += stream.payload.eq(rx_len[0:8]) # LSB
                m.d.comb += stream.valid.eq(1)
                with m.If(stream.ready):
                    m.next = "HEADER_MSB"

            with m.State("HEADER_MSB"):
                # write second byte of rx_len
                m.d.comb += stream.payload.eq(rx_len[8:16]) # MSB
                m.d.comb += stream.valid.eq(1)
                with m.If(stream.ready):
                    m.next = "PACKET"

            with m.State("PACKET"):
                m.d.comb += fsm_state.eq(0b0100)

                # send bytes from the packet memory over the stream interface
                m.d.comb += [
                    stream.valid.eq(1),
                    mac.rx_read.addr.eq(rx_addr),         # cdc
                    stream.payload.eq(mac.rx_read.data),  # cdc
                ]

                # incrementing the memory address whenever the stream is ready to receive data
                with m.If(stream.ready):
                    m.d.usb += rx_addr.eq(rx_addr + 1)
                    m.d.usb += bytes_sent.eq(bytes_sent + 1)

                # until we have sent the whole packet
                with m.If(bytes_sent >= rx_len - 1):
                    m.d.usb += mac_rx_ack.eq(1)
                    m.next = "DELIMITER"

            with m.State("DELIMITER"):
                m.d.comb += fsm_state.eq(0b1000)
                m.d.usb += mac_rx_ack.eq(0)
                m.d.comb += [
                    stream.valid.eq(1),
                    stream.payload.eq(33),
                ]
                # send some delimiter bytes
                with m.If(stream.ready):
                    m.d.usb += delim.eq(delim + 1)
                with m.If(delim >= 7):
                    m.next = "IDLE"


        # debug signals
        m.d.comb += [
            #debug0[0].eq(rgmii.rx_clk),
            #debug0[1].eq(rx_rgmii.rx_control_out[0]),
            #debug0[2].eq(rx_rgmii.rx_data_out[0]),
            #debug0[3].eq(mac.rx_valid),

            #debug0[3].eq(stream.ready),
            #debug0[4:8].eq(fsm_state),
        ]

        # obblinky
        blinky = Signal(28)
        m.d.sync += blinky.eq(blinky + 1)
        m.d.comb += Cat(leds).eq(blinky[-3:])

        return m



# - build ---------------------------------------------------------------------

if __name__ == "__main__":
    from luna import top_level_cli

    top_level_cli(Top)
