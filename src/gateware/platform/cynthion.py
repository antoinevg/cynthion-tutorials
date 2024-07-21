from amaranth       import *
from amaranth.build import *


# - i2s -----------------------------------------------------------------------

# TODO
def I2SResource(*args, mclk, lrck, sclk, sdi, sdo, clkdir='i', attrs=None, conn=None):
    assert clk_dir in ('i', 'o')

    io = []
    io.append(Subsignal("mclk",  Pins(mclk,  dir=clk_dir, conn=conn, assert_width=1))) # 5
    io.append(Subsignal("lrck",  Pins(lrck,  dir=clk_dir, conn=conn, assert_width=1))) # 6
    io.append(Subsignal("sclk",  Pins(sclk,  dir=clk_dir, conn=conn, assert_width=1))) # 7
    io.append(Subsignal("sdo",   Pins(sdo,   dir="o",     conn=conn, assert_width=1))) # 8
    io.append(Subsignal("sdi",   Pins(sdi,   dir="i",     conn=conn, assert_width=1))) # 4
    if attrs is not None:
        io.append(attrs)

    return Resource.family(*args, default_name="i2s", ios=io)


# TODO use Connector
I2S_RESOURCES = [
    # PMOD A
    Resource("i2s", 0,
        Subsignal("da_mclk",  Pins("1",  conn=("pmod", 0), dir="o", assert_width=1)),
        Subsignal("da_lrck",  Pins("2",  conn=("pmod", 0), dir="o", assert_width=1)),
        Subsignal("da_sclk",  Pins("3",  conn=("pmod", 0), dir="o", assert_width=1)),
        Subsignal("da_sdi",   Pins("4",  conn=("pmod", 0), dir="o", assert_width=1)),
        Subsignal("ad_mclk",  Pins("7",  conn=("pmod", 0), dir="o", assert_width=1)),
        Subsignal("ad_lrck",  Pins("8",  conn=("pmod", 0), dir="o", assert_width=1)),
        Subsignal("ad_sclk",  Pins("9",  conn=("pmod", 0), dir="o", assert_width=1)),
        Subsignal("ad_sdo",   Pins("10", conn=("pmod", 0), dir="i", assert_width=1)),
    ),
    # PMOD B
    Resource("i2s", 1,
        Subsignal("da_mclk",  Pins("1",  conn=("pmod", 1), dir="o", assert_width=1)),
        Subsignal("da_lrck",  Pins("2",  conn=("pmod", 1), dir="o", assert_width=1)),
        Subsignal("da_sclk",  Pins("3",  conn=("pmod", 1), dir="o", assert_width=1)),
        Subsignal("da_sdi",   Pins("4",  conn=("pmod", 1), dir="o", assert_width=1)),
        Subsignal("ad_mclk",  Pins("7",  conn=("pmod", 1), dir="o", assert_width=1)),
        Subsignal("ad_lrck",  Pins("8",  conn=("pmod", 1), dir="o", assert_width=1)),
        Subsignal("ad_sclk",  Pins("9",  conn=("pmod", 1), dir="o", assert_width=1)),
        Subsignal("ad_sdo",   Pins("10", conn=("pmod", 1), dir="i", assert_width=1)),
    ),
]


# - rgmii ---------------------------------------------------------------------

RGMII_RESOURCES = [
    Resource(
        # PMOD A
        "eth_rgmii", 0,
        Subsignal("rx_clk",  Pins("1",       conn=("pmod", 0), dir="i")),
        Subsignal("tx_clk",  Pins("7",       conn=("pmod", 0), dir="o")),
        Subsignal("tx_data", Pins("2 8 3 9", conn=("pmod", 0), dir="o")),
        Subsignal("tx_ctrl", Pins("4",       conn=("pmod", 0), dir="o")),
        Subsignal("rst",    PinsN("10",      conn=("pmod", 0), dir="o")),

        # PMOD B
        Subsignal("rx_data", Pins("1 8 2 9", conn=("pmod", 1), dir="i")),
        Subsignal("rx_ctrl", Pins("7",       conn=("pmod", 1), dir="i")),
        Subsignal("intb",    Pins("3",       conn=("pmod", 1), dir="i")),
        Subsignal("mdio",    Pins("10",      conn=("pmod", 1), dir="io")),
        Subsignal("mdc",     Pins("4",       conn=("pmod", 1), dir="o")),
        Attrs(IO_TYPE="LVCMOS33")
    ),
]


# - soc -----------------------------------------------------------------------

SOC_RESOURCES = [
    # PMOD B: UART
    Resource("uart", 1,
        Subsignal("rx",  Pins("1", conn=("pmod", 1), dir="i")),
        Subsignal("tx",  Pins("2", conn=("pmod", 1), dir="o")),
        Attrs(IO_TYPE="LVCMOS33")
    ),

    # PMOD B: DEBUG
    Resource("debug", 0,
        Subsignal("a",  Pins("3", conn=("pmod", 1), dir="o")),
        Subsignal("b",  Pins("4", conn=("pmod", 1), dir="o")),
        Attrs(IO_TYPE="LVCMOS33")
    ),

    # PMOD B: JTAG
    Resource("jtag", 0,
        Subsignal("tms",  Pins("7",  conn=("pmod", 1), dir="i")),
        Subsignal("tdi",  Pins("8",  conn=("pmod", 1), dir="i")),
        Subsignal("tdo",  Pins("9",  conn=("pmod", 1), dir="o")),
        Subsignal("tck",  Pins("10", conn=("pmod", 1), dir="i")),
        Attrs(IO_TYPE="LVCMOS33")
    ),
]
