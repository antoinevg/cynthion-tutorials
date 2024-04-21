from amaranth        import *
from amaranth.utils  import bits_for
from amaranth.build  import Platform


# - module: WS2812 ------------------------------------------------------------

class WS2812(Elaboratable):
    def __init__(self, *, sys_clock_freq, bus_length, pattern):
        # parameters
        self.bus_length  = bus_length
        self.clock_ticks = int(sys_clock_freq // 800e3)
        self.low_ticks   = int(0.32 * self.clock_ticks)
        self.high_ticks  = int(0.64 * self.clock_ticks)
        self.reset_ticks = int(self.clock_ticks * 40) # TODO
        print(f"clock ticks: {self.clock_ticks}")

        self.framebuffer = Memory(width=24, depth=bus_length, init=pattern)

        # I / O
        self.data_in         = Signal(24)
        self.addr_in         = Signal(range(bus_length))
        self.write_enable_in = Signal()

        self.nzr_out = Signal()

        self.start_in  = Signal()
        self.done_out  = Signal()

        # debug
        self.clock_out = Signal()


    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.submodules.fb_read_port  = fb_read_port  = self.framebuffer.read_port(domain="usb")
        m.submodules.fb_write_port = fb_write_port = self.framebuffer.write_port(domain="usb")

        grb = Signal(3 * 8)

        led_counter = Signal(bits_for(self.bus_length) + 1)
        bit_counter = Signal(5)
        current_bit = Signal()

        n = int(self.clock_ticks)
        print(f"total_clock_ticks: {n}")
        print(f"  => bits_for:         {bits_for(int(n))}")
        print(f"  => Const().shape():  {Const(n).shape()}")
        print(f"  => len(Const()):     {len(Const(n))}")
        print(f"  => Signal(range()):  {Signal(range(n)).shape()}")

        #cycle_counter_width  = bits_for(int(self.clock_ticks)) + 1
        cycle_counter_width  = bits_for(int(self.reset_ticks)) + 1
        cycle_counter        = Signal(cycle_counter_width)
        current_ticks        = Signal.like(cycle_counter)

        print(f"cycle counter: {cycle_counter_width}")

        # debug
        m.d.comb += self.clock_out.eq(cycle_counter[7])

        m.d.comb += [
            self.nzr_out.eq(1),
            current_bit.eq(grb[23]),
            current_ticks.eq(Mux(current_bit, self.high_ticks, self.low_ticks)),
            fb_write_port.addr.eq(self.addr_in),
            fb_write_port.data.eq(self.data_in),
            fb_write_port.en.eq(self.write_enable_in),
            fb_read_port.addr.eq(led_counter),
        ]

        with m.FSM():
            with m.State("IDLE"):
                with m.If(self.start_in):
                    m.d.sync += led_counter.eq(0)
                    m.next = "RESET"

            with m.State("RESET"):
                m.d.comb += self.nzr_out.eq(0)
                m.d.sync += cycle_counter.eq(cycle_counter + 1)

                with m.If(cycle_counter >= Const(self.reset_ticks)):
                    m.d.sync += cycle_counter.eq(0)

                    with m.If(led_counter == 0):
                        m.d.sync += [
                            grb.eq(fb_read_port.data),
                            led_counter.eq(led_counter + 1),
                        ]
                        m.next = "TRANSMIT"

                    with m.Else():
                        m.d.comb += self.done_out.eq(1)
                        m.d.sync += led_counter.eq(0)
                        m.next = "IDLE"

            with m.State("TRANSMIT"):
                m.d.sync += cycle_counter.eq(cycle_counter + 1)

                with m.If(cycle_counter < current_ticks):
                    m.d.comb += self.nzr_out.eq(1)
                with m.Else():
                    m.d.comb += self.nzr_out.eq(0)

                with m.If(cycle_counter >= Const(self.clock_ticks)):
                    m.d.sync += cycle_counter.eq(0)

                    last_bit = 23
                    with m.If(bit_counter < last_bit):
                        m.d.sync += [
                            grb.eq(grb << 1),
                            bit_counter.eq(bit_counter + 1),
                        ]
                    with m.Else():
                        m.d.sync += [
                            bit_counter.eq(0),
                            led_counter.eq(led_counter + 1),
                        ]

                        # transmit each LED's data
                        with m.If(led_counter < self.bus_length):
                            m.d.sync += grb.eq(fb_read_port.data),

                        # if all LEDS' data has been transmitted, send another reset
                        with m.Else():
                            m.next = "RESET"

        return m
