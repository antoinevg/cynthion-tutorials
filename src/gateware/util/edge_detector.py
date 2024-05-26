from amaranth        import *

class EdgeDetector(Elaboratable):
    def __init__(self, clock, domain="sync"):
        self.clock = clock
        self._domain = domain
        self.rose = Signal()
        self.fell = Signal()

    def elaborate(self, platform):
        m = Module()
        past = Signal()
        m.d.sync += past.eq(self.clock)
        m.d.comb += self.rose.eq(~past & self.clock)
        m.d.comb += self.fell.eq(past & ~self.clock)
        return DomainRenamer({"sync": self._domain})(m)
