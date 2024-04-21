from amaranth        import *
from amaranth.utils  import bits_for
from amaranth.build  import Platform

from luna                            import top_level_cli
from luna.gateware.platform          import NullPin
from luna.gateware.architecture.car  import LunaECP5DomainGenerator


# - module: ClockDivider ------------------------------------------------------

class ClockDivider(Elaboratable):
    def __init__(self, *, domain, div):

        self._domain = domain
        self.div = div

        print(f"DIV: {self.div}")
        print(f"  => bits_for:         {bits_for(int(self.div))}")
        print(f"  => Const().shape():  {Const(self.div).shape()}")
        print(f"  => len(Const()):     {len(Const(self.div))}")
        print(f"  => Const(range()):   {Const(0, range(self.div)).shape()}")
        print(f"  => Signal(range()):  {Signal(range(self.div)).shape()}")

        self.clock_out = Signal()

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        counter = Signal(range(self.div + 1))

        with m.If(counter < (self.div - 1)):
            m.d.sync += counter.eq(counter + 1)
        with m.Else():
            m.d.sync += counter.eq(0)

        with m.If(counter < int(self.div / 2)):
            m.d.sync += self.clock_out.eq(1)
        with m.Else():
            m.d.sync += self.clock_out.eq(0)

        m = DomainRenamer({"sync": self._domain})(m)
        return m


# - module: ClockDivider2 ------------------------------------------------------

class ClockDivider2(Elaboratable):
    def __init__(self, *, domain, div):

        self._domain = domain
        self.div = div

        self.clock_out = Signal()

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        counter = Signal(range(self.div + 1))


        m = DomainRenamer({"sync": self._domain})(m)
        return m
