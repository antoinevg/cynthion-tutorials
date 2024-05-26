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

from tutorials.gateware.interface  import I2sTransmitter, I2sReceiver
from tutorials.gateware.util       import Blinky, Leds, NCO


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

        # generate i2s sclk, lrck
        clkdiv = Signal(9)
        m.d.i2s_mclk += clkdiv.eq(clkdiv + 1)
        sclk = Signal()
        lrck = Signal()
        m.d.comb += [
            sclk.eq(~clkdiv[2]),
            lrck.eq(~clkdiv[8]),
        ]

        # wire up i2s interface & codec
        i2s_tx = I2sTransmitter()
        i2s_rx = I2sReceiver()
        m.submodules += [i2s_tx, i2s_rx]
        m.d.comb += [
            # i2s interface clock signals
            i2s_tx.i2s.mclk.eq(ClockSignal("i2s_mclk")),
            i2s_tx.i2s.lrck.eq(lrck),
            i2s_tx.i2s.sclk.eq(sclk),
            i2s_rx.i2s.mclk.eq(ClockSignal("i2s_mclk")),
            i2s_rx.i2s.lrck.eq(lrck),
            i2s_rx.i2s.sclk.eq(sclk),

            # codec clock signals
            i2s.da_mclk.o.eq(ClockSignal("i2s_mclk")),
            i2s.da_lrck.o.eq(lrck),
            i2s.da_sclk.o.eq(sclk),
            i2s.ad_mclk.o.eq(ClockSignal("i2s_mclk")),
            i2s.ad_lrck.o.eq(lrck),
            i2s.ad_sclk.o.eq(sclk),

            # codec data signals
            i2s.da_sdi.o.eq(i2s_tx.i2s.sdi),
            i2s_rx.i2s.sdo.eq(i2s.ad_sdo.i),
        ]

        # wire i2s receiver up to i2s transmitter
        m.d.comb += [
            i2s_tx.left    .eq(i2s_rx.left),
            i2s_tx.right   .eq(i2s_rx.right),
        ]

        # debug
        debug = Cat([pmod0.o[i] for i in range(0, 8)])
        m.d.comb += [
            # clocks
            debug[0].eq(i2s.da_mclk.o),
            debug[1].eq(i2s.da_lrck.o),
            debug[2].eq(i2s.da_sclk.o),

            # transmitter
            debug[3].eq(i2s.da_sdi.o),
            debug[4].eq(i2s_tx.next),

            # receiver
            debug[5].eq(i2s.ad_sdo.i),
            debug[6].eq(i2s_rx.next),
        ]

        return m


# - main ----------------------------------------------------------------------

if __name__ == "__main__":
    top_level_cli(Top)
