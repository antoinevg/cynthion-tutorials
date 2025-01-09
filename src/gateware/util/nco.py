import math

from amaranth       import *
from amaranth.sim   import *
from amaranth.utils import log2_int


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
    gain = 0.501187 # - 6dB
    ys = [y * gain for y in ys]

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
    def __init__(self, clock_frequency, lut_length=512, bit_depth=24, twos_complement=False, lut=None):
        self.bit_depth = bit_depth

        # lut
        ys = sinusoid_lut(bit_depth, lut_length, twos_complement)
        # TODO use amaranth.lib.memory.Memory
        #self.lut = Memory(width=bit_depth, depth=lut_size, init=ys)
        self.lut = Array(ys)

        # calculate accumulator parameters
        self.index_bits = log2_int(lut_length)   # 512     = 9
        self.phi_bits   = 32
        self.phi_tau    = 1 << self.phi_bits

        # input: frequency (in terms of phi_delta)
        self.phi0_delta  = Signal(self.phi_bits)
        self.phi1_delta  = Signal(self.phi_bits)

        # output: sample
        self.output0 = Signal(bit_depth)
        self.output1 = Signal(bit_depth)


    def elaborate(self, platform):
        m = Module()

        # accumulator
        phi0 = Signal(self.phi_bits)
        phi1 = Signal(self.phi_bits)
        m.d.sync += [
            phi0.eq(phi0 + self.phi0_delta),
            phi1.eq(phi1 + self.phi1_delta),
        ]

        # calculate index
        index0 = Signal(self.index_bits)
        index1 = Signal(self.index_bits)
        m.d.comb += [
            index0.eq(phi0[-self.index_bits:]),
            index1.eq(phi1[-self.index_bits:]),
        ]

        # output sample
        m.d.comb += [
            self.output0.eq(self.lut[index0]),
            self.output1.eq(self.lut[index1]),
        ]

        return m
