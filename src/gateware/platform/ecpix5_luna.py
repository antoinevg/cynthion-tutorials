#
# This file is part of LUNA.
#
# Copyright (c) 2020 Great Scott Gadgets <info@greatscottgadgets.com>
# SPDX-License-Identifier: BSD-3-Clause

""" ecpix5 platform definitions.

This is a non-core platform. To use it, you'll need to set your LUNA_PLATFORM variable:

    > export LUNA_PLATFORM="luna.gateware.platform.ecpix5:ECPIX5_45F_Platform"
    > export LUNA_PLATFORM="luna.gateware.platform.ecpix5:ECPIX5_85F_Platform"
"""

from amaranth import *
from amaranth.build import *
try:
    from amaranth.vendor.lattice_ecp5 import LatticeECP5Platform
except:
    from amaranth.vendor import LatticeECP5Platform

from amaranth_boards.resources import *
from amaranth_boards.ecpix5 import ECPIX545Platform as _ECPIX545Platform
from amaranth_boards.ecpix5 import ECPIX585Platform as _ECPIX585Platform

from luna.gateware.interface.pipe       import AsyncPIPEInterface
from luna.gateware.interface.serdes_phy import ECP5SerDesPIPE

from luna.gateware.platform.core import LUNAPlatform


__all__ = ["ECPIX5_45F_Platform", "ECPIX5_85F_Platform"]


class ECPIX5SuperSpeedPHY(AsyncPIPEInterface):
    """ Superspeed PHY configuration for the ECPIX5. """

    REFCLK_FREQUENCY = 100e6
    SS_FREQUENCY     = 125e6
    FAST_FREQUENCY   = 250e6

    SERDES_DUAL    = 0
    SERDES_CHANNEL = 1


    def __init__(self, platform):

        # Grab the I/O that implements our SerDes interface...
        serdes_io_directions = {
            'ch0':    {'tx':"-", 'rx':"-"},
            'ch1':    {'tx':"-", 'rx':"-"},
            'refclk': '-',
        }
        serdes_io      = platform.request("serdes", self.SERDES_DUAL, dir=serdes_io_directions)
        serdes_channel = getattr(serdes_io, f"ch{self.SERDES_CHANNEL}")

        # Use it to create our soft PHY...
        serdes_phy = ECP5SerDesPIPE(
            tx_pads             = serdes_channel.tx,
            rx_pads             = serdes_channel.rx,
            dual                = self.SERDES_DUAL,
            channel             = self.SERDES_CHANNEL,
            refclk_frequency    = self.FAST_FREQUENCY,
        )

        # ... and bring the PHY interface signals to the MAC domain.
        super().__init__(serdes_phy, width=4, domain="ss")


    def elaborate(self, platform):
        m = super().elaborate(platform)

        # Patch in our soft PHY as a submodule.
        m.submodules.phy = self.phy

        # Drive the PHY reference clock with our fast generated clock.
        m.d.comb += self.clk.eq(ClockSignal("fast"))

        # This board does not have a way to detect Vbus, so assume it's always present.
        m.d.comb += self.phy.power_present.eq(1)

        return m



class _ECPIXExtensions:

    # Create a reference

    additional_resources = [

        #
        # SerDes pins; necessary to synthesize using Diamond.
        #
        # It doesn't seem like these location values are actually used; but Diamond needs them
        # to be *there*. We'll provide correct ones in case it ever decides to use them.
        #
        Resource("serdes", 0,
            #Subsignal("ch0",
            #    Subsignal("rx", DiffPairs("AF6",  "AF7")),
            #    Subsignal("tx", DiffPairs("AD7",  "AD8")),
            #),
            Subsignal("ch1",
                Subsignal("rx", DiffPairs("AF9",  "AF10")),
                Subsignal("tx", DiffPairs("AD10", "AD11")),
            ),
            #Subsignal("refclk", DiffPairs("AF12", "AF13"))
        ),
        Resource("serdes", 1,
            Subsignal("ch0",
                Subsignal("rx", DiffPairs("AF16",  "AF17")),
                Subsignal("tx", DiffPairs("AD16",  "AD17")),
            ),
            Subsignal("ch1",
                Subsignal("rx", DiffPairs("AF18",  "AF19")),
                Subsignal("tx", DiffPairs("AD19", "AD20")),
            ),
            Subsignal("refclk", DiffPairs("AF21", "AF22"))
        ),

        # XXX: temporary, pmod USB for debugging
        DirectUSBResource(0, d_p="T25", d_n="U25", pullup="U24", attrs=Attrs(IO_TYPE="LVCMOS33")),

        # Aliases for our demonstrations / examples.
        Resource("user_io", 0, Pins("D14", dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 1, Pins("B14", dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 2, Pins("E14", dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 3, Pins("B16", dir="io"), Attrs(IO_TYPE="LVCMOS33")),

        # temporary
        Resource("pmod", 0, Pins("T25 U25 U24 V24 T26 U26 V26 W26", dir="o"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("pmod", 1, Pins("U23 V23 U22 V21 W25 W24 W23 W22", dir="o"), Attrs(IO_TYPE="LVCMOS33")),
    ]



class ECPIX5_45F_Platform(_ECPIX545Platform, _ECPIXExtensions, LUNAPlatform):
    name                   = "ECPIX-5 (45F)"

    clock_domain_generator = ECPIX5DomainGenerator
    default_usb3_phy       = ECPIX5SuperSpeedPHY
    default_usb_connection = "ulpi"

    # Create our semantic aliases.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_resources(self.additional_resources)



class ECPIX5_85F_Platform(_ECPIX585Platform, _ECPIXExtensions, LUNAPlatform):
    name                   = "ECPIX-5 (85F)"

    clock_domain_generator = ECPIX5DomainGenerator
    default_usb3_phy       = ECPIX5SuperSpeedPHY
    default_usb_connection = "ulpi"

    # Create our semantic aliases.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_resources(self.additional_resources)
