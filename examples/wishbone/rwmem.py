import sys

from amaranth            import *
from amaranth.lib.memory import Memory
from amaranth.utils      import bits_for
from amaranth.build      import Attrs, Pins, Platform, Resource, Subsignal

from luna                            import top_level_cli
from luna.gateware.platform          import NullPin
from luna.gateware.architecture.car  import LunaECP5DomainGenerator

from tutorials.gateware.bridge      import WishboneBridge
from tutorials.gateware.interface   import WS2812

# - module: Top ---------------------------------------------------------------

class Top(Elaboratable):
    def __init__(self):
        self.data = [i for i in range(0, 512)]

    def elaborate(self, platform):
        m = Module()

        # domain clocks/resets
        clocking = LunaECP5DomainGenerator()
        m.submodules += clocking

        # resources
        leds  = Cat(platform.request_optional("led", i, default=NullPin()).o for i in range(0, 8))
        pmod0 = platform.request("user_pmod", 0)
        pmod1 = platform.request("user_pmod", 1)
        m.d.comb += pmod0.oe.eq(1)
        m.d.comb += pmod1.oe.eq(1)

        # debug
        debug = Cat([pmod0.o[i] for i in range(0, 8)])

        # usb bridge
        usb_bridge = WishboneBridge()
        m.submodules += usb_bridge

        # memory
        mem = Memory(shape=8, depth=512, init=self.data)
        m.submodules += mem
        read_port  = mem.read_port(domain="usb")
        write_port = mem.write_port(domain="usb")

        # - stream OUT --------------------------------------------------------

        # wire usb_bridge stream OUT up to memory
        stream_out = usb_bridge.stream_out.stream
        write_addr = Signal(9) # 0..512
        rx_count   = Signal(8)

        m.d.comb += [
            write_port.addr.eq(write_addr),
            write_port.en.eq(stream_out.valid),
            write_port.data.eq(stream_out.payload),
        ]

        with m.FSM(domain="usb") as fsm:
            m.d.comb += stream_out.ready.eq(fsm.ongoing("RECEIVING"))

            with m.State("IDLE"):
                with m.If(stream_out.first):
                    with m.If(stream_out.valid):
                        m.d.usb += usb_bridge.stream_in.discard.eq(1) # TODO fixes buffered data in IN stream
                        m.next = "RECEIVING"

            with m.State("RECEIVING"):
                m.d.usb += usb_bridge.stream_in.discard.eq(0) # TODO fixes buffered data in IN stream
                m.d.usb += [
                    write_addr.eq(write_addr + 1),
                    rx_count.eq(rx_count + 1),
                ]
                with m.If(stream_out.last):
                    m.d.usb += [
                        write_addr.eq(0),
                        rx_count.eq(0),
                    ]
                    m.next = "IDLE"


        # - stream IN ---------------------------------------------------------

        # wire usb_bridge stream IN up to memory
        stream_in = usb_bridge.stream_in.stream
        read_addr = Signal(9) # 0..512
        tx_count = Signal(9)  # 0..512

        m.d.comb += [
            read_port.addr.eq(read_addr),
            read_port.en.eq(stream_in.ready),
            stream_in.payload.eq(read_port.data),
            stream_in.last.eq(read_addr[6]), # stop sending after 64 bytes
        ]

        with m.FSM(domain="usb") as fsm:
            m.d.comb += stream_in.valid.eq(fsm.ongoing("SENDING"))

            with m.State("IDLE"):
                with m.If(stream_in.ready):
                    m.d.comb += stream_in.first.eq(1)
                    m.d.usb += [
                        read_addr.eq(read_addr + 1),
                        tx_count.eq(tx_count + 1),
                    ]
                    m.next = "SENDING"

            with m.State("SENDING"):
                m.d.comb += stream_in.first.eq(0)
                m.d.usb += [
                    read_addr.eq(read_addr + 1),
                    tx_count.eq(tx_count + 1),
                ]
                with m.If(read_addr[6]): # stop sending after 64 bytes
                    m.d.usb += [
                        read_addr.eq(0),
                        tx_count.eq(0),
                    ]
                    m.next = "IDLE"



        # connect debug signals
        m.d.comb += [
            #debug[0].eq(ClockSignal("usb")),
            #debug[1].eq(stream_out.valid),
            #debug[2].eq(stream_out.ready),
            #debug[3].eq(stream_out.first),
            #debug[4].eq(stream_out.last),

            #debug[1].eq(stream_in.ready),
            #debug[2].eq(stream_in.valid),
            #debug[3].eq(stream_in.first),
            #debug[4].eq(stream_in.last),

            #debug[0:7].eq(read_addr),
            #debug[7].eq(stream_in.ready),
        ]


        return m


# - helpers --------------------------------------------------------------------

def generate_grb_spectrum(num_divisions):
    step_size = 256 // num_divisions

    rgb_spectrum = []
    for i in range(num_divisions):
        red = i * step_size
        green = (i + num_divisions // 3) % num_divisions * step_size
        blue = (i + 2 * num_divisions // 3) % num_divisions * step_size

        red = int(red * 0.01)
        green = int(green * 0.01)
        blue = int(blue * 0.01)

        rgb_value = (green << 16) | (red << 8) | blue
        rgb_spectrum.append(rgb_value)

    return rgb_spectrum


# - main ----------------------------------------------------------------------

if __name__ == "__main__":
    top_level_cli(Top)
