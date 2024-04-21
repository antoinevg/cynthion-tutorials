from amaranth       import *
from amaranth.build import *

try:
    from amaranth.vendor.lattice_ecp5 import LatticeECP5Platform
except:
    from amaranth.vendor import LatticeECP5Platform
from amaranth_boards.resources import *
from amaranth_boards.ecpix5 import ECPIX585Platform as _ECPIX585Platform

from luna.gateware.platform import LUNAPlatform

from .ecpix5_luna import ECPIX5DomainGenerator


# - platform ------------------------------------------------------------------

# See:
#
#  * https://github.com/greatscottgadgets/luna/blob/hw-r0.4/luna/gateware/platform/ecpix5.py
#  * https://github.com/amaranth-lang/amaranth-boards/blob/main/amaranth_boards/ecpix5.py

class ECPIX585Rev03Platform(_ECPIX585Platform, LUNAPlatform):
    name                   = "ECPIX-5 (85F)"

    clock_domain_generator = ECPIX5DomainGenerator

    #default_usb3_phy       = ECPIX5SuperSpeedPHY
    default_usb_connection = "ulpi"

    additional_resources = [
        ULPIResource("ulpi-inverted-clk-direction", 0,
            data="M26 L25 L26 K25 K26 J23 P25 H25",
            clk="H24", clk_dir="o", dir="F22", nxt="F23",
            stp="H23", rst="E23", rst_invert=False,
            attrs=Attrs(IO_TYPE="LVCMOS33", SLEWRATE="SLOW")),

        *LEDResources(pins="T23 U21 K21 P21 R21 W21 K24 R23", invert=True, attrs=Attrs(IO_TYPE="LVCMOS33", PULLMODE="UP")),

        Resource("user_io", 0, Pins("1 2 3 4 7 8 9 10", conn=("pmod", 0), dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 1, Pins("1 2 3 4 7 8 9 10", conn=("pmod", 1), dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 2, Pins("1 2 3 4 7 8 9 10", conn=("pmod", 2), dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 3, Pins("1 2 3 4 7 8 9 10", conn=("pmod", 3), dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 4, Pins("1 2 3 4 7 8 9 10", conn=("pmod", 4), dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 5, Pins("1 2 3 4 7 8 9 10", conn=("pmod", 5), dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 6, Pins("1 2 3 4 7 8 9 10", conn=("pmod", 6), dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 7, Pins("1 2 3 4 7 8 9 10", conn=("pmod", 7), dir="io"), Attrs(IO_TYPE="LVCMOS33")),
    ]

    # Create our semantic aliases.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_resources(self.additional_resources)

    def toolchain_program(self, products, name):
        import os, subprocess
        tool = os.environ.get("OPENFPGALOADER", "openFPGALoader")
        with products.extract("{}.bit".format(name)) as bitstream_filename:
            subprocess.check_call([tool, '-c', 'ft4232', '-m', bitstream_filename])


# - rgmii ---------------------------------------------------------------------

RGMII_RESOURCES = [
    Resource("eth_rgmii", 1,
        # PMOD 2
        Subsignal("rx_data", Pins("1 8 2 9", conn=("pmod", 2), dir="i")),
        Subsignal("rx_ctrl", Pins("7",       conn=("pmod", 2), dir="i")),
        Subsignal("intb",    Pins("3",       conn=("pmod", 2), dir="i")),
        Subsignal("mdio",    Pins("10",      conn=("pmod", 2), dir="io")),
        Subsignal("mdc",     Pins("4",       conn=("pmod", 2), dir="o")),
        # PMOD 3
        Subsignal("rx_clk",  Pins("1",       conn=("pmod", 3), dir="i")),
        Subsignal("tx_clk",  Pins("7",       conn=("pmod", 3), dir="o")),
        Subsignal("tx_data", Pins("2 8 3 9", conn=("pmod", 3), dir="o")),
        Subsignal("tx_ctrl", Pins("4",       conn=("pmod", 3), dir="o")),
        Subsignal("rst",    PinsN("10",      conn=("pmod", 3), dir="o")),
        Attrs(IO_TYPE="LVCMOS33")
    ),
]
