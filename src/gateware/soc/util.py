class ClockStretch(wiring.Component):
    def __init__(self, cycles):
        super().__init__({
            "input":  In(unsigned(1)),
            "output": Out(unsigned(1)),
        })

        self.cycles = cycles

    def elaborate(self, platform):
        m = Module()

        counter = Signal(16)

        with m.FSM():
            with m.State("IDLE"):
                m.d.sync += counter.eq(0)
                with m.If(self.input == 1):
                    m.next = "STRETCH"
            with m.State("STRETCH"):
                m.d.comb += self.output.eq(1)
                m.d.sync += counter.eq(counter + 1)
                with m.If(counter == self.cycles):
                    m.next = "IDLE"

        return m
