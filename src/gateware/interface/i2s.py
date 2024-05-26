from amaranth            import *
from amaranth.lib        import wiring
from amaranth.lib.wiring import In, Out


# Notes:
#
#   - lrck: low is left, high is right
#   - lrck transitions one clock period _before_ completion of a data
#     word (or data word starts 1 period _after_ transition)
#

class I2sSignature(wiring.Signature):
    def __init__(self):
        super().__init__({
            "mclk": In(1),
            "lrck": In(1),
            "sclk": In(1),
            "sdi":  Out(1), # tx
            "sdo":  In(1),  # rx
        })

    def __eq__(self, other):
        return self.members == other.members

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

class I2sTransmitter(wiring.Component):
    i2s:   In(I2sSignature())
    left:  In(24)
    right: In(24)

    next: In(1)

    def elaborate(self, platform):
        m = Module()

        # generate i2s_sclk_tx domain from i2s sample clock
        m.domains.i2s_sclk_tx = ClockDomain()
        m.d.comb += [
            ClockSignal(domain="i2s_sclk_tx").eq(~self.i2s.sclk), # negate for polarity: falling edge
        ]

        # edge detector for lrck
        m.submodules.lr_edge = lr_edge = EdgeDetector(self.i2s.lrck)

        # shift register for current sample
        shift_register = Signal(32)
        m.d.comb += shift_register.eq(Mux(self.i2s.lrck, self.right, self.left))

        # clock sample shift register into sdi
        bit_counter = Signal(5) # 32 bits
        with m.If(lr_edge.rose | lr_edge.fell):
            m.d.i2s_sclk_tx += bit_counter.eq(0)
        with m.Else():
            m.d.i2s_sclk_tx += bit_counter.eq(bit_counter + 1)
        next_bit = shift_register.bit_select(bit_counter, width=1)

        # i2s only starts clocking data in 1 sclk cycle after lrck has changed state
        delay = Signal(24)
        m.d.i2s_sclk_tx += delay.eq(next_bit)
        m.d.comb += self.i2s.sdi.eq(delay)

        # signal next sample
        with m.If(~self.i2s.lrck & (bit_counter == 31)):
            m.d.comb += self.next.eq(1)

        return m


class I2sReceiver(wiring.Component):
    i2s:   In(I2sSignature())
    left:  Out(24)
    right: Out(24)

    next: In(1)

    def elaborate(self, platform):
        m = Module()

        # generate i2s_sclk_rx domain from i2s sample clock
        m.domains.i2s_sclk_rx = sclk_rx = ClockDomain()
        m.d.comb += [
            ClockSignal(domain="i2s_sclk_rx").eq(~self.i2s.sclk), # negate for polarity: falling edge
        ]

        # edge detector for lrck
        m.submodules.lr_edge = lr_edge = EdgeDetector(self.i2s.lrck)

        # current sample
        sample = Signal(32)

        # clock sdo into sample register
        bit_counter = Signal(5) # 32 bits
        with m.If(lr_edge.rose | lr_edge.fell):
            m.d.i2s_sclk_rx += bit_counter.eq(0)
        with m.Else():
            m.d.i2s_sclk_rx += bit_counter.eq(bit_counter + 1)
        m.d.i2s_sclk_rx += sample.bit_select(bit_counter, width=1).eq(self.i2s.sdo)

        # load sample into output register
        with m.If((bit_counter == 31) & self.i2s.lrck):
            m.d.i2s_sclk_rx += self.right.eq(sample)
        with m.Elif(bit_counter == 31):
            m.d.i2s_sclk_rx += self.left.eq(sample)

        # signal next sample
        with m.If(~self.i2s.lrck & (bit_counter == 31)):
            m.d.comb += self.next.eq(1)

        return m
