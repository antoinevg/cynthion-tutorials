import sys

from amaranth        import *
from amaranth.utils  import bits_for
from amaranth.build  import Attrs, Pins, Platform, Resource, Subsignal

from luna                            import top_level_cli
from luna.gateware.platform          import NullPin
from luna.gateware.architecture.car  import LunaECP5DomainGenerator

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

        return m

if __name__ == "__main__":
    top_level_cli(Top)
