from amaranth            import *
from amaranth.lib        import wiring
from amaranth.lib.wiring import In, Out

class I2sSignature(wiring.Signature):
    def __init__(self):
        super().__init__({
            "mclk": In(1),
            "lrck": In(1),
            "sclk": In(1),
            #"sdi":  In(1),
            "sdo":  Out(1),
        })

    def __eq__(self, other):
        return self.members == other.members


class I2sTransmitter(wiring.Component):
    i2s:   In(I2sSignature())
    left:  In(24)
    right: In(24)

    next: In(1)

    def elaborate(self, platform):
        m = Module()

        # generate sclk domain from i2s sample clock
        m.domains.sclk = sclk = ClockDomain()
        m.d.comb += [
            ClockSignal(domain="sclk").eq(~self.i2s.sclk), # negate for polarity: falling edge
        ]

        # shift register for current sample
        shift_register = Signal(24)
        m.d.comb += shift_register.eq(Mux(self.i2s.lrck, self.left, self.right))

        # clock sample shift register into output
        bit_counter = Signal(5) # 32 bits
        with m.If(bit_counter == 31):
            m.d.sclk += bit_counter.eq(0)
        with m.Else():
            m.d.sclk += bit_counter.eq(bit_counter + 1)
        next_bit = shift_register.bit_select(bit_counter, width=1)

        # i2s only starts clocking data in 1 sclk cycle after lrck has changed state
        delay = Signal(24)
        m.d.sclk += delay.eq(next_bit)
        m.d.comb += self.i2s.sdo.eq(delay)

        # signal next sample
        with m.If(~self.i2s.lrck & (bit_counter == 31)):
            m.d.comb += self.next.eq(1)

        return m
