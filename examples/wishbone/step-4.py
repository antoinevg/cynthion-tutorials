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

# - register: LedRegister -----------------------------------------------------

class LedRegister(csr.reg.Register, access="rw"):
    def __init__(self, reset=0):
        super().__init__({
            "led0": csr.Field(csr.action.RW, 1, init=reset),
            "led1": csr.Field(csr.action.RW, 1, init=reset),
            "led2": csr.Field(csr.action.RW, 1, init=reset),
            "led3": csr.Field(csr.action.RW, 1, init=reset),
            "led4": csr.Field(csr.action.RW, 1, init=reset),
            "led5": csr.Field(csr.action.RW, 1, init=reset),
        })


# - component: WishbonePeripheral ---------------------------------------------

class WishbonePeripheral(Component):
    def __init__(self, *, pads=None):
        self.pads = pads
        super().__init__({
            "bus": In(wishbone.Signature(addr_width=4, data_width=8))
        })

        # registers
        registers = csr.Builder(addr_width=4, data_width=8)
        self.reg_leds = registers.add("leds", LedRegister(reset=1))

        # csr bridge
        self.csr_bridge = csr.Bridge(registers.as_memory_map())
        self.bus.memory_map = self.csr_bridge.bus.memory_map

        # add wishbone bridge
        self.wb_bridge = WishboneCSRBridge(self.csr_bridge.bus)

    def elaborate(self, platform):
        m = Module()

        m.submodules += [self.csr_bridge, self.wb_bridge]

        # peripheral state
        state = Signal(8, reset=0x33)
        m.d.comb += [
            self.pads.eq(state)
        ]

        # connect registers to peripheral state
        combined = Cat([field.data for _name, field in self.reg_leds.field.flatten()])
        m.d.comb += [
            state[0:3].eq(combined[0:3]),
            state[3].eq(self.reg_leds.f.led3.data),
            state[4].eq(self.reg_leds.f.led4.data),
            state[5].eq(self.reg_leds.f.led5.data),
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

        # wishbone peripheral
        wishbone_peripheral = DomainRenamer("usb")(WishbonePeripheral(pads=leds))
        m.submodules += wishbone_peripheral

        # wishbone bus decoder
        decoder = wishbone.Decoder(addr_width=8, data_width=16)
        decoder.add(wishbone_peripheral.wb_bridge.wb_bus, addr=0x10, sparse=True)
        m.submodules += decoder

        # connect our usb bridge device's vendor request handler to the wishbone decoder
        connect(m, usb_bridge.vendor_request_handler.bus, decoder.bus)

        return m


if __name__ == "__main__":
    top_level_cli(Top)
