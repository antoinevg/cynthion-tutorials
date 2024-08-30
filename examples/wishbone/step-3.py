import sys

from amaranth                        import *
from amaranth.build                  import Attrs, Pins, Platform, Resource, Subsignal
from amaranth.utils                  import bits_for

from amaranth.lib.wiring             import Component, In, Out, connect

from amaranth_soc                    import csr, wishbone
from amaranth_soc.csr.wishbone       import WishboneCSRBridge
from amaranth_soc.memory             import MemoryMap

from luna                            import top_level_cli
from luna.gateware.platform          import NullPin
from luna.gateware.architecture.car  import LunaECP5DomainGenerator

from tutorials.gateware.bridge       import WishboneBridge


# - component: SimpleRegister ----------------------------------------------------

class SimpleRegister(Component):
    def __init__(self, width, name):
        super().__init__({
            "element": Out(csr.Element.Signature(width, "rw")),
            "r_count": Out(unsigned(8)),
            "w_count": Out(unsigned(8)),
            "data":    Out(width)
        })
        self._name = name

    def elaborate(self, platform):
        m = Module()

        with m.If(self.element.r_stb):
            m.d.sync += self.r_count.eq(self.r_count + 1)
        m.d.comb += self.element.r_data.eq(self.data)

        with m.If(self.element.w_stb):
            m.d.sync += self.w_count.eq(self.w_count + 1)
            m.d.sync += self.data.eq(self.element.w_data)

        return m

    def __repr__(self):
        return f"SimpleRegister('{self._name}')"


# - component: WishboneComponent -------------------------------------------------

class WishboneComponent(Component):
    def __init__(self, *, pads=None):
        self.pads = pads
        super().__init__({
            "bus": In(wishbone.Signature(addr_width=4, data_width=8))
        })

        # registers
        self.state_reg = SimpleRegister(width=8, name="state")

        # memory map
        self.bus.memory_map = MemoryMap(addr_width=4, data_width=8, name="wishbone")
        self.bus.memory_map.add_resource(self.state_reg, name=("state",), size=1)

        # multiplexer + wishbone bridge
        self.csr_mux = csr.Multiplexer(self.bus.memory_map)
        self.csr_bridge = WishboneCSRBridge(self.csr_mux.bus)

    def elaborate(self, platform):
        m = Module()

        m.submodules += [self.state_reg, self.csr_mux, self.csr_bridge]

        # state
        state = Signal(8, reset=0x33)
        m.d.comb += [
            state.eq(self.state_reg.data),
            self.pads.eq(state)
        ]


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
        decoder.add(wishbone_component.csr_bridge.wb_bus, addr=0x10, sparse=True)
        m.submodules += decoder

        # connect our usb bridge device's vendor request handler to the wishbone decoder
        connect(m, usb_bridge.vendor_request_handler.bus, decoder.bus)

        return m


if __name__ == "__main__":
    top_level_cli(Top)
