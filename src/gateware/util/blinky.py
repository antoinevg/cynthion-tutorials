from amaranth            import *
from amaranth.lib        import wiring
from amaranth.lib.wiring import In, Out


# - module: Blinky ------------------------------------------------------------

class SimpleSignature(wiring.Signature):
    def __init__(self, data_shape):
        super().__init__({
            "data": Out(data_shape),
        })

    def __eq__(self, other):
        return self.members == other.members

class Blinky(wiring.Component):
    output: Out(SimpleSignature(6))

    def elaborate(self, platform):
        m = Module()
        counter = Signal(32)
        m.d.sync += [
            counter.eq(counter + 1)
        ]
        m.d.comb += self.output.data.eq(counter[32 - 6:])
        return m

class Leds(wiring.Component):
    input: In(SimpleSignature(6))

    def __init__(self, pads):
        super().__init__()
        self.pads = pads

    def elaborate(self, platform):
        m = Module()
        m.d.comb += self.pads.eq(self.input.data)
        return m
