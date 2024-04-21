from amaranth       import *
from amaranth.build import *


class I2SDomainGenerator(Elaboratable):
    def __init__(self):
        self.clkout0 = Signal()
        self.locked  = Signal()

    def elaborate(self, platform):
        m = Module()

        # Create our clock domains.
        m.domains.i2s = self.i2s = ClockDomain()

        # Grab our input clock
        clkin = ClockSignal("fast") # 240 MHz

        clkintfb = Signal()
        clkfb    = Signal()

        # Instantiate the ECP5 PLL.
        #
        # Desired mclk rate for 48kHz audio is: 48_000 * 8 * 32 = 12_288_000
        #
        # parameters from: ecppll -i 240 -o 12.288 -f /dev/stdout --highres
        m.submodules.pll_i2s = Instance(
            "EHXPLLL",

            # Synthesis attributes.
            a_FREQUENCY_PIN_CLKI="240.000000",
            a_FREQUENCY_PIN_CLKOS="12.288",
            a_ICP_CURRENT="12",
            a_LPF_RESISTOR="8",
            a_MFG_ENABLE_FILTEROPAMP="1",
            a_MFG_GMCREF_SEL="2",

            # PLL parameters.
            p_PLLRST_ENA="DISABLED",
            p_INTFB_WAKE="DISABLED",
            p_STDBY_ENABLE="DISABLED",
            p_DPHASE_SOURCE="DISABLED",
            p_OUTDIVIDER_MUXA="DIVA",
            p_OUTDIVIDER_MUXB="DIVB",
            p_OUTDIVIDER_MUXC="DIVC",
            p_OUTDIVIDER_MUXD="DIVD",
            p_CLKI_DIV=25,
            p_CLKOP_ENABLE="ENABLED",
            p_CLKOP_DIV=32,
            p_CLKOP_CPHASE=9,
            p_CLKOP_FPHASE=0,
            p_CLKOS_ENABLE="ENABLED",
            p_CLKOS_DIV=50,
            p_CLKOS_CPHASE=0,
            p_CLKOS_FPHASE=0,
            p_FEEDBK_PATH="CLKOP",
            p_CLKFB_DIV=2,

            # Control signals.
            i_RST=0,
            i_STDBY=0,
            i_CLKI=clkin,
            o_CLKOP=clkfb,
            o_CLKOS=self.clkout0,
            i_CLKFB=clkfb,
            o_CLKINTFB=clkintfb,
            i_PHASESEL0=0,
            i_PHASESEL1=0,
            i_PHASEDIR=1,
            i_PHASESTEP=1,
            i_PHASELOADREG=1,
            i_PLLWAKESYNC=0,
            i_ENCLKOP=0,
            o_LOCK=self.locked,
        )


        # Connect clocks.
        m.d.comb += [
            ClockSignal(domain="i2s").eq(self.clkout0),
        ]

        return m
