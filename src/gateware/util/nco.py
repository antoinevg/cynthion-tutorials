from amaranth import *
from amaranth.sim import *

import math

# - lut generation ------------------------------------------------------------

TAU = math.pi * 2.

def fsin(x, fs, phi=0):
    T = 1.0 / float(fs)
    w = TAU
    return math.cos(w * x * T + phi)

def sinusoid_lut(bit_depth, memory_size, twos_complement=False):
    fs = memory_size
    scale = math.pow(2, bit_depth) - 1

    ys = [fsin(x, fs) for x in range(int(fs))]

    # scale signal to integer range
    ys = [y * (scale/2) for y in ys]

    # optional: convert to unsigned
    #ys = [y + (scale/2) for y in ys]

    # signal gain
    #gain = 0.794328 # -2dB
    #ys = [y * gain for y in ys]

    # convert to integer
    ys = [int(y) for y in ys]

    # 2s complement - I think amaranth is natively 2's complement so this may not be needed
    if twos_complement:
        print("converting nco data to two's complement")
        ys = [twos_comp(y, 24) for y in ys]

    return ys


def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val



# - gateware ------------------------------------------------------------------

class NCO(Elaboratable):
    def __init__(self, clock_frequency, lut_size, bit_depth, twos_complement=False, lut=None):
        # accumulator
        self.accumulator_width = math.ceil(math.log2(clock_frequency))
        self.accumulator_a = Signal(self.accumulator_width)
        self.accumulator_b = Signal(self.accumulator_width)

        # input: frequency
        freq_width = math.ceil(math.log2(clock_frequency / 2))
        self.i_freq_a = Signal(freq_width, reset=220)
        self.i_freq_b = Signal(freq_width, reset=440)

        # output: samples
        self.o_a = Signal(bit_depth)
        self.o_b = Signal(bit_depth)

        # lut
        ys = sinusoid_lut(bit_depth, lut_size, twos_complement)
        # TODO use amaranth.lib.memory.Memory
        #self.lut = Memory(width=bit_depth, depth=lut_size, init=ys)
        self.lut = Array(ys)
        self.lut_width = math.ceil(math.log2(lut_size))

    def elaborate(self, platform):
        m = Module()

        #m.submodules += self.lut

        step_a = Signal.like(self.accumulator_a)
        step_b = Signal.like(self.accumulator_b)

        m.d.comb += [
            step_a.eq(self.i_freq_a),
            step_b.eq(self.i_freq_b),
            self.o_a.eq(self.lut[self.accumulator_a[-self.lut_width:]]),
            self.o_b.eq(self.lut[self.accumulator_b[-self.lut_width:]]),
        ]

        m.d.sync += [
            self.accumulator_a.eq(self.accumulator_a + step_a),
            self.accumulator_b.eq(self.accumulator_b + step_b),
        ]

        return m

    def ports(self):
        return [
            self.i_freq_a,
            self.i_freq_b,
            self.accumulator_a,
            self.accumulator_b,
            self.o_a,
            self.o_b,
        ]


def main():
    clock_frequency = int(48e3)
    lut_size = 1024
    bit_depth = 24

    dut = NCO(clock_frequency, bit_depth=bit_depth, lut_size=lut_size)

    sim = Simulator(dut)
    def proc():
        cycles = clock_frequency // 16

        yield dut.i_freq_a.eq(220)
        yield dut.i_freq_b.eq(440)
        for _ in range(cycles):
            yield Tick()
        yield dut.i_freq_a.eq(247)
        yield dut.i_freq_b.eq(493)
        for _ in range(cycles):
            yield Tick()
        yield dut.i_freq_a.eq(262)
        yield dut.i_freq_b.eq(524)
        for _ in range(cycles):
            yield Tick()

    sim.add_clock(1 / clock_frequency)
    sim.add_process(proc)

    with sim.write_vcd("nco.vcd", "nco.gtkw", traces=dut.ports()):
        sim.run()


if __name__ == "__main__":
    main()
