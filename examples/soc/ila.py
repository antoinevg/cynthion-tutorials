import logging

from amaranth                      import *

from luna.gateware.platform        import get_appropriate_platform
from luna.gateware.usb.devices.ila import USBIntegratedLogicAnalyzer
from luna.gateware.usb.devices.ila import USBIntegratedLogicAnalyzerFrontend

from .top import Top


if __name__ == "__main__":
    # configuration
    domain = "usb"

    # select platform
    platform = get_appropriate_platform()
    if platform is None:
        logging.error("Failed to identify a supported platform")
        sys.exit(1)

    # configure clock frequency
    clock_frequency = int(platform.DEFAULT_CLOCK_FREQUENCIES_MHZ[domain] * 1e6)
    logging.info(f"Building for {platform} with domain {domain} and clock frequency: {clock_frequency}")

    # create dut
    dut = Top(clock_frequency=clock_frequency, domain=domain)

    frontend = USBIntegratedLogicAnalyzerFrontend(
        ila   = dut.ila,
        delay = 3,
    )
    frontend.interactive_display()
