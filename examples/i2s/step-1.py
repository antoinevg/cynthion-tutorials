import sys

from amaranth            import *
from amaranth.build      import Attrs, Pins, Platform, Resource, Subsignal
from amaranth.lib.memory import Memory
from amaranth.lib        import wiring
from amaranth.lib.wiring import In, Out
from amaranth.utils      import bits_for

from luna                            import top_level_cli
from luna.gateware.platform          import NullPin
from luna.gateware.architecture.car  import LunaECP5DomainGenerator

from tutorials.gateware.platform.cynthion         import I2S_RESOURCES
from tutorials.gateware.architecture.cynthion_i2s import I2SDomainGenerator

from tutorials.gateware.util  import Blinky, Leds


# - module: Top ---------------------------------------------------------------

class Top(Elaboratable):
    def __init__(self):
        pass

    def elaborate(self, platform):
        platform.add_resources(I2S_RESOURCES)

        m = Module()

        # create clocks & resets
        m.submodules.car = LunaECP5DomainGenerator()
        m.submodules.car_i2s = car_i2s = I2SDomainGenerator()

        # resources
        i2s   = platform.request("i2s", 1)
        leds  = Cat(platform.request_optional("led", i, default=NullPin()).o for i in range(0, 8))
        pmod0 = platform.request("user_pmod", 0)
        m.d.comb += pmod0.oe.eq(1)

        # blinky
        m.submodules.leds   = leds   = Leds(leds)
        m.submodules.blinky = blinky = Blinky()
        wiring.connect(m, blinky.output, leds.input)

        # generate i2s sclk, lrck
        clkdiv = Signal(12)
        m.d.i2s += clkdiv.eq(clkdiv + 1)
        sclk = Signal()
        lrck = Signal()
        m.d.comb += [
            sclk.eq(~clkdiv[2]),
            lrck.eq(~clkdiv[8]),
        ]

        # i2s pass-through
        m.d.comb += [
            # d/a
            i2s.da_mclk.o.eq(ClockSignal("i2s")),
            i2s.da_lrck.o.eq(lrck),
            i2s.da_sclk.o.eq(sclk),
            i2s.da_sdi.o.eq(i2s.ad_sdo.i),

            # a/d
            i2s.ad_mclk.o.eq(ClockSignal("i2s")),
            i2s.ad_lrck.o.eq(lrck),
            i2s.ad_sclk.o.eq(sclk),
        ]

        # debug
        debug = Cat([pmod0.o[i] for i in range(0, 8)])
        m.d.comb += [
            debug[0].eq(i2s.da_mclk.o),
            debug[1].eq(i2s.da_lrck.o),
            debug[2].eq(i2s.da_sclk.o),
            debug[3].eq(i2s.da_sdi.o),
            debug[4].eq(i2s.ad_sdo.i),
        ]

        return m



# - main ----------------------------------------------------------------------

if __name__ == "__main__":
    top_level_cli(Top)
