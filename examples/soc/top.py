import logging, os, sys

from amaranth             import *
from amaranth.build       import Attrs, Pins, PinsN, Platform, Resource, Subsignal
from amaranth.lib         import wiring
from amaranth.lib.wiring  import Component, In, Out, flipped

from amaranth_soc               import csr, gpio, wishbone
from amaranth_soc.csr.wishbone  import WishboneCSRBridge

from luna.gateware.usb.usb2.device  import USBDevice

from tutorials.gateware.soc.cores  import psram, sram, timer, uart, usb, test
from tutorials.gateware.soc.cpu    import InterruptController, VexRiscv

from tutorials.gateware.platform.cynthion  import SOC_RESOURCES


class GPIOProvider(Component):
    def __init__(self, index): # TODO id, index
        self.index   = index
        super().__init__({
            "pins": In(gpio.PinSignature()).array(8)
        })

    def elaborate(self, platform):
        m = Module()
        user_pmod = platform.request("user_pmod", self.index)
        m.d.comb += user_pmod.oe.eq(1)
        for n in range(8):
            m.d.comb += user_pmod.o[n] .eq(self.pins[n].o)
            m.d.comb += self.pins[n].i .eq(user_pmod.i[n])
            pass
        return m


class LEDProvider(Component):
    def __init__(self, pin_count=8):
        self.pin_count = pin_count
        super().__init__({
            "pins": In(gpio.PinSignature()).array(self.pin_count)
        })

    def elaborate(self, platform):
        m = Module()
        for n in range(self.pin_count):
            try:
                led = platform.request("led", n)
                m.d.comb += led.o.eq(self.pins[n].o)
            except:
                logging.warning(f"Platform does not support led {n}")
        return m


class UARTProvider(Component):
    def __init__(self, index): # TODO id, index
        self.index = index
        super().__init__({
            "pins": In(uart.PinSignature())
        })

    def elaborate(self, platform):
        m = Module()
        uart = platform.request("uart", self.index)
        m.d.comb += [
            self.pins.rx .eq(uart.rx.i),
            uart.tx.o    .eq(self.pins.tx),
        ]
        return m


# TODO I think it would be cooler to have a PhyProvider that can take a UTMI or ULPI platform resource.
class ULPIPhyProvider(Component):
    def __init__(self, id):
        self.id = id
        super().__init__({
            "bus": In(usb.ulpi.Signature())
        })

    def elaborate(self, platform):
        m = Module()
        try:
            ulpi = platform.request(self.id)
            m.d.comb += [
                self.bus.data.i  .eq(ulpi.data.i),      # i TODO check nested
                ulpi.data.o      .eq(self.bus.data.o),  # o TODO check nested
                ulpi.data.oe     .eq(self.bus.data.oe), # o TODO check nested

                # see ulpi.Signature
                # ulpi.clk.o       .eq(self.bus.clk),     # o
                # self.bus.nxt     .eq(ulpi.nxt.i),       # i
                # ulpi.stp.o       .eq(self.bus.stp),     # o
                # self.bus.dir     .eq(ulpi.dir.i),       # i
                # ulpi.rst.o       .eq(self.bus.rst),     # o

                ulpi.clk.o         .eq(self.bus.clk.o),   # o
                self.bus.nxt.i     .eq(ulpi.nxt.i),       # i
                ulpi.stp.o         .eq(self.bus.stp.o),   # o
                self.bus.dir.i     .eq(ulpi.dir.i),       # i
                ulpi.rst.o         .eq(self.bus.rst.o),   # o
            ]
        except:
            logging.warning(f"Platform does not support a {self.id} port for usb")

        return m


# - component: Soc ------------------------------------------------------------

class Soc(Component):
    def __init__(self, clock_frequency, domain="sync"):
        super().__init__({})

        self.clock_frequency = clock_frequency
        self.domain = domain

        # configuration
        self.blockram_base        = 0x00000000
        self.blockram_size        = 0x00010000  # 65536 bytes
        self.hyperram_base        = 0x20000000  # Winbond W956A8MBYA6I
        self.hyperram_size        = 0x08000000  # 8 * 1024 * 1024
        self.csr_base             = 0xf0000000
        self.leds_base            = 0x00000000
        self.gpio0_base           = 0x00000100
        self.uart1_base           = 0x00000200
        self.timer0_base          = 0x00000300
        self.timer0_irq           = 0
        self.timer1_base          = 0x00000400
        self.timer1_irq           = 1
        self.usb0_base            = 0x00000500
        self.usb0_irq             = 2
        self.usb0_ep_control_base = 0x00000600
        self.usb0_ep_control_irq  = 3
        self.usb0_ep_in_base      = 0x00000700
        self.usb0_ep_in_irq       = 4
        self.usb0_ep_out_base     = 0x00000800
        self.usb0_ep_out_irq      = 5
        self.test_base            = 0x00000900
        self.test_irq             = 6

        # cpu
        self.cpu = VexRiscv(
            variant="cynthion+jtag",
            reset_addr=self.blockram_base
        )

        # interrupt controller
        self.interrupt_controller = InterruptController(width=len(self.cpu.irq_external))

        # bus
        self.wb_arbiter  = wishbone.Arbiter(
            addr_width=30,
            data_width=32,
            granularity=8,
            features={"cti", "bte", "err"}
        )
        self.wb_decoder  = wishbone.Decoder(
            addr_width=30,
            data_width=32,
            granularity=8,
            features={"cti", "bte", "err"}
        )

        # blockram
        self.blockram = sram.Peripheral(size=self.blockram_size)
        self.wb_decoder.add(self.blockram.bus, addr=self.blockram_base, name="blockram")

        # hyperram
        self.hyperram = psram.Peripheral(size=self.hyperram_size)
        self.wb_decoder.add(self.hyperram.bus, addr=self.hyperram_base, name="hyperram")

        # csr decoder
        self.csr_decoder = csr.Decoder(addr_width=28, data_width=8)

        # leds
        self.led_count = 6
        self.leds = gpio.Peripheral(pin_count=self.led_count, addr_width=3, data_width=8)
        self.csr_decoder.add(self.leds.bus, addr=self.leds_base, name="leds")

        # gpio0
        self.gpio0 = gpio.Peripheral(pin_count=8, addr_width=3, data_width=8)
        self.csr_decoder.add(self.gpio0.bus, addr=self.gpio0_base, name="gpio0")

        # uart1
        uart_baud_rate = 115200
        divisor = int(clock_frequency // uart_baud_rate)
        self.uart1 = uart.Peripheral(divisor=divisor)
        self.csr_decoder.add(self.uart1.bus, addr=self.uart1_base, name="uart1")

        # timer0
        self.timer0 = timer.Peripheral(width=32)
        self.csr_decoder.add(self.timer0.bus, addr=self.timer0_base, name="timer0")
        self.interrupt_controller.add(self.timer0, number=self.timer0_irq, name="timer0")

        # timer1
        self.timer1 = timer.Peripheral(width=32)
        self.csr_decoder.add(self.timer1.bus, addr=self.timer1_base, name="timer1")
        self.interrupt_controller.add(self.timer1, name="timer1", number=self.timer1_irq)

        # usb0 - target_phy
        self.usb0            = usb.device.Peripheral()
        self.usb0_ep_control = usb.ep_control.Peripheral()
        self.usb0_ep_in      = usb.ep_in.Peripheral()
        self.usb0_ep_out     = usb.ep_out.Peripheral()
        self.csr_decoder.add(self.usb0.bus,            addr=self.usb0_base,            name="usb0")
        self.csr_decoder.add(self.usb0_ep_control.bus, addr=self.usb0_ep_control_base, name="usb0_ep_control")
        self.csr_decoder.add(self.usb0_ep_in.bus,      addr=self.usb0_ep_in_base,      name="usb0_ep_in")
        self.csr_decoder.add(self.usb0_ep_out.bus,     addr=self.usb0_ep_out_base,     name="usb0_ep_out")
        self.interrupt_controller.add(self.usb0,            name="usb0",            number=self.usb0_irq)
        self.interrupt_controller.add(self.usb0_ep_control, name="usb0_ep_control", number=self.usb0_ep_control_irq)
        self.interrupt_controller.add(self.usb0_ep_in,      name="usb0_ep_in",      number=self.usb0_ep_in_irq)
        self.interrupt_controller.add(self.usb0_ep_out,     name="usb0_ep_out",     number=self.usb0_ep_out_irq)

        # test
        self.test = test.Peripheral()
        self.csr_decoder.add(self.test.bus, addr=self.test_base, name="test")
        self.interrupt_controller.add(self.test, name="test", number=self.test_irq)

        # wishbone csr bridge
        self.wb_to_csr = WishboneCSRBridge(self.csr_decoder.bus, data_width=32)
        self.wb_decoder.add(self.wb_to_csr.wb_bus, addr=self.csr_base, sparse=False, name="wb_to_csr")

    def elaborate(self, platform):
        m = Module()

        # bus
        m.submodules += [self.wb_arbiter, self.wb_decoder]
        wiring.connect(m, self.wb_arbiter.bus, self.wb_decoder.bus)

        # cpu
        m.submodules += self.cpu
        self.wb_arbiter.add(self.cpu.ibus)
        self.wb_arbiter.add(self.cpu.dbus)

        # interrupt controller
        m.submodules += self.interrupt_controller
        # TODO wiring.connect(m, self.cpu.irq_external, self.irqs.pending)
        m.d.comb += self.cpu.irq_external.eq(self.interrupt_controller.pending)

        # blockram
        m.submodules += self.blockram

        # hyperram
        m.submodules += self.hyperram

        # csr decoder
        m.submodules += self.csr_decoder

        # leds
        led_provider = LEDProvider(pin_count=self.led_count)
        m.submodules += [led_provider, self.leds]
        for n in range(self.led_count):
            wiring.connect(m, self.leds.pins[n], led_provider.pins[n])

        # gpio0
        #gpio0_provider = GPIOProvider(0)
        #m.submodules += [gpio0_provider, self.gpio0]
        #for n in range(8):
        #    wiring.connect(m, self.gpio0.pins[n], gpio0_provider.pins[n])

        # uart1
        uart1_provider = UARTProvider(1)
        m.submodules += [uart1_provider, self.uart1]
        wiring.connect(m, self.uart1.pins, uart1_provider.pins)

        # timer0
        m.submodules += self.timer0

        # timer1
        m.submodules += self.timer1

        # usb0 - target_phy
        ulpi0_provider = ULPIPhyProvider(platform.default_usb_connection)
        usb0_device = USBDevice(bus=ulpi0_provider.bus)
        usb0_device.add_endpoint(self.usb0_ep_control)
        usb0_device.add_endpoint(self.usb0_ep_in)
        usb0_device.add_endpoint(self.usb0_ep_out)
        m.d.comb += self.usb0.attach(usb0_device) # TODO wiring.connect() ?
        m.submodules += [ulpi0_provider, self.usb0, usb0_device]

        # test
        m.submodules += self.test

        # wishbone csr bridge
        m.submodules += self.wb_to_csr

        # wire up the cpu external reset signal
        try:
            user1_io = platform.request("button_user")
            m.d.comb += self.cpu.ext_reset.eq(user1_io.i)
        except:
            logging.warning("Platform does not support a user button for cpu reset")

        # wire up the cpu jtag signals
        jtag0_io = platform.request("jtag", 0)
        m.d.comb += [
            self.cpu.jtag_tms     .eq(jtag0_io.tms.i),
            self.cpu.jtag_tdi     .eq(jtag0_io.tdi.i),
            jtag0_io.tdo.o        .eq(self.cpu.jtag_tdo),
            self.cpu.jtag_tck     .eq(jtag0_io.tck.i),
        ]

        # Debug
        pmod_io  = platform.request("user_pmod", 0)
        debug_io = platform.request("debug", 0)

        clk_fast = Signal(4)
        clk_sync = Signal(4)
        clk_usb  = Signal(4)
        m.d.fast += clk_fast.eq(clk_fast + 1)
        m.d.sync += clk_sync.eq(clk_sync + 1)
        m.d.usb  += clk_usb .eq(clk_usb + 1)

        m.d.comb += [
            pmod_io.oe    .eq(1),
            pmod_io.o     .eq(self.hyperram.debug_wb),
            debug_io.a.o  .eq(self.hyperram.debug_io[0]),
            debug_io.b.o  .eq(self.hyperram.debug_io[1]),
        ]

        return DomainRenamer({
            "sync": self.domain,
            "fast": "sync", # cynthion hyperram currently only works with the soc at 120 MHz
        })(m)


# - module: Top ---------------------------------------------------------------

class Top(Elaboratable):
    def __init__(self, clock_frequency, domain="sync"):
        self.soc = Soc(clock_frequency=clock_frequency, domain=domain)

    def elaborate(self, platform):
        # add additional resource
        platform.add_resources(SOC_RESOURCES)

        m = Module()

        # generate our domain clocks/resets

        m.submodules.car = platform.clock_domain_generator()
        # CLOCK_FREQUENCIES = {
        #     "fast": 120, # cynthion hyperram currently only works with the soc at 120 MHz
        #     "sync": 60,
        #     "usb":  60,
        # }
        # from luna.gateware.architecture.car import LunaECP5DomainGenerator
        # m.submodules.car = LunaECP5DomainGenerator(clock_frequencies=CLOCK_FREQUENCIES)

        # add soc to design
        m.submodules += self.soc

        return m


# - build ---------------------------------------------------------------------

if __name__ == "__main__":
    from luna                    import configure_default_logging, top_level_cli
    from luna.gateware.platform  import get_appropriate_platform

    # configure logging
    configure_default_logging()
    logging.getLogger().setLevel(logging.DEBUG)

    # enable to build for tiliqua
    if False:
        from tiliqua.tiliqua_platform  import TiliquaPlatform
        os.environ["LUNA_PLATFORM"] = "tiliqua.tiliqua_platform:TiliquaPlatform"

    # select platform
    platform = get_appropriate_platform()
    if platform is None:
        logging.error("Failed to identify a supported platform")
        sys.exit(1)

    # configure domain
    domain = "usb"

    # configure clock frequency
    clock_frequency = int(platform.DEFAULT_CLOCK_FREQUENCIES_MHZ[domain] * 1e6)
    logging.info(f"Building for {platform} with domain {domain} and clock frequency: {clock_frequency}")

    # create design
    design = Top(clock_frequency=clock_frequency, domain=domain)

    # generate soc sdk
    from tutorials.gateware.soc.generate import GenerateSVD
    with open("examples/soc/soc.svd", "w") as f:
        GenerateSVD = GenerateSVD(design).generate(file=f)

    top_level_cli(design)
