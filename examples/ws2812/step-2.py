import sys

from amaranth        import *
from amaranth.utils  import bits_for
from amaranth.build  import Attrs, Pins, Platform, Resource, Subsignal

from luna                            import top_level_cli
from luna.gateware.platform          import NullPin
from luna.gateware.architecture.car  import LunaECP5DomainGenerator

from tutorials.gateware.bridge     import WishboneBridge
from tutorials.gateware.interface  import WS2812

# - module: Top ---------------------------------------------------------------

class Top(Elaboratable):
    def __init__(self):
        self.pattern = []

        # test
        data = [
            0x110000,
            0x001100,
            0x000011,

            0x111111,
            0x111111,

            0x000011,
            0x001100,
            0x110000,
        ]
        for i in range(0, 8):
            self.pattern += data

        self.pattern = generate_grb_spectrum(64)
        #self.pattern = [0x000001 for i in range(0, 64)]

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
        debug = Cat([pmod1.o[i] for i in range(0, 8)])

        # usb bridge
        usb_bridge = WishboneBridge()
        m.submodules += usb_bridge

        # ws2812
        print(f"Initializing ws2812 with {len(self.pattern)} leds")
        ws2812 = DomainRenamer("usb")(WS2812(sys_clock_freq=60e6, bus_length=len(self.pattern), pattern=self.pattern))
        m.submodules += ws2812
        m.d.comb += ws2812.start_in.eq(1)
        m.d.comb += pmod0.o[0].eq(ws2812.nzr_out)

        # TODO connect our usb bridge device's vendor request handler to the wishbone decoder
        # connect(m, usb_bridge.vendor_request_handler.bus, decoder.bus)

        # wire usb_bridge stream OUT up to ws2812
        stream = usb_bridge.stream_out.stream
        byte_counter = Signal(2)
        addr = Signal(6)
        data = Signal(24)

        m.d.comb += [
            ws2812.addr_in.eq(addr),
            ws2812.data_in.eq(data),
        ]
        m.d.comb += stream.ready.eq(1)

        with m.If(stream.valid & stream.ready):
            m.d.usb += [
                data.word_select(byte_counter, 8).eq(stream.payload),
                byte_counter.eq(byte_counter + 1),
            ]
            with m.If(byte_counter == 2):
                m.d.usb += [
                    ws2812.write_enable_in.eq(1),
                    addr.eq(addr + 1),
                    byte_counter.eq(0),
                ]

        # connect debug signals
        m.d.comb += [
            debug[2].eq(stream.valid),
            debug[3].eq(stream.ready),
            debug[4].eq(ClockSignal("usb"))
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
