import sys

from amaranth        import *
from amaranth.utils  import bits_for
from amaranth.build  import Attrs, Pins, Platform, Resource, Subsignal

from luna                            import top_level_cli
from luna.gateware.platform          import NullPin
from luna.gateware.architecture.car  import LunaECP5DomainGenerator

from tutorials.gateware.interface    import WS2812

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

        # ws2812
        ws2812 = WS2812(sys_clock_freq=120e6, bus_length=len(self.pattern), pattern=self.pattern)
        m.submodules += ws2812
        m.d.comb += ws2812.start_in.eq(1)
        m.d.comb += pmod0.o[0].eq(ws2812.nzr_out)

        # debug
        m.d.comb += pmod1.o[0].eq(ws2812.clock_out)
        m.d.comb += pmod1.o[1].eq(ws2812.nzr_out)
        m.d.comb += pmod1.o[2].eq(ws2812.done_out)

        return m

if __name__ == "__main__":
    top_level_cli(Top)
