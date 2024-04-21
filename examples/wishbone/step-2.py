import sys

from amaranth                        import *
from amaranth.build                  import Attrs, Pins, Platform, Resource, Subsignal
from amaranth.utils                  import bits_for

from amaranth.lib.wiring             import Component, In, connect

from amaranth_soc                    import csr, wishbone
from amaranth_soc.csr.wishbone       import WishboneCSRBridge
from amaranth_soc.memory             import MemoryMap

from luna                            import top_level_cli
from luna.gateware.platform          import NullPin
from luna.gateware.architecture.car  import LunaECP5DomainGenerator

from tutorials.gateware.bridge       import WishboneBridge


# - component: WishboneComponent ----------------------------------------------

class WishboneComponent(Component):
    def __init__(self, *, pads=None):
        self.pads = pads
        super().__init__({
            "bus": In(wishbone.Signature(addr_width=4, data_width=8))
        })
        self.bus.memory_map = MemoryMap(addr_width=4, data_width=8, name="wishbone")

    def elaborate(self, platform):
        m = Module()

        # state
        state = Signal(8, reset=0x33)
        m.d.comb += [
            self.pads.eq(state)
        ]

        # raw bus interface
        write = Signal()
        m.d.comb += write.eq(
            self.bus.cyc    & # transaction is active
            self.bus.stb    & # valid data is being provided
            self.bus.we     & # this is a write
            self.bus.sel[0]   # the relevant data lane is being targeted
        )
        read = Signal()
        m.d.comb += read.eq(
            self.bus.cyc    & # transaction is active
            self.bus.stb    & # valid data is being provided
            ~self.bus.we    & # this is a read
            self.bus.sel[0]   # the relevant data lane is being targeted
        )

        with m.If(write):
            m.d.sync += state.eq(self.bus.dat_w)
            m.d.sync += self.bus.ack.eq(1)
        with m.Elif(read):
            m.d.sync += self.bus.dat_r.eq(state)
            m.d.sync += self.bus.ack.eq(1)
        with m.Else():
            m.d.sync += self.bus.ack.eq(0)

        return m


# - module: Top ---------------------------------------------------------------

class Top(Elaboratable):
    def __init__(self):
        pass

    def elaborate(self, platform):
        m = Module()

        # domain clocks/resets
        clocking = LunaECP5DomainGenerator()
        m.submodules += clocking

        # resources
        leds  = Cat(platform.request_optional("led", i, default=NullPin()).o for i in range(0, 8))

        # usb bridge
        usb_bridge = WishboneBridge()
        m.submodules += usb_bridge

        # wishbone component
        wishbone_component = DomainRenamer("usb")(WishboneComponent(pads=leds))
        m.submodules += wishbone_component

        # wishbone bus decoder
        decoder = wishbone.Decoder(addr_width=8, data_width=16)
        decoder.add(wishbone_component.bus, addr=0x10, sparse=True)
        m.submodules += decoder

        # connect our usb bridge device's vendor request handler to the wishbone decoder
        connect(m, usb_bridge.vendor_request_handler.bus, decoder.bus)

        return m


if __name__ == "__main__":
    top_level_cli(Top)
