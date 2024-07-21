import logging, sys

from amaranth             import *
from amaranth.build       import Attrs, Pins, PinsN, Platform, Resource, Subsignal
from amaranth.lib         import wiring
from amaranth.lib.wiring  import Component, In, Out

from amaranth_soc               import csr, gpio, wishbone
from amaranth_soc.csr.wishbone  import WishboneCSRBridge

from tutorials.gateware.soc.cores  import sram, timer, uart
from tutorials.gateware.soc.cpu    import InterruptController, VexRiscv

from tutorials.gateware.platform.cynthion  import SOC_RESOURCES


class GPIOProvider(Component):
    def __init__(self, id):
        self.id   = id
        super().__init__({
            "pins": In(gpio.PinSignature()).array(8)
        })

    def elaborate(self, platform):
        m = Module()
        user_pmod = platform.request("user_pmod", self.id)
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
            led = platform.request("led", n)
            m.d.comb += led.o.eq(self.pins[n].o)
        return m


class UARTProvider(Component):
    def __init__(self, id):
        self.id = id
        super().__init__({
            "pins": In(uart.PinSignature())
        })

    def elaborate(self, platform):
        m = Module()
        uart = platform.request("uart", self.id)
        m.d.comb += [
            self.pins.rx .eq(uart.rx.i),
            uart.tx.o    .eq(self.pins.tx),
        ]
        return m


# - component: Soc ------------------------------------------------------------

class Soc(Component):
    def __init__(self, clock_frequency, domain="sync"):
        super().__init__({})

        self.clock_frequency = clock_frequency
        self.domain = domain

        # configuration
        self.mainram_base  = 0x00000000
        self.mainram_size  = 0x4000
        self.csr_base      = 0xf0000000
        self.leds_base     = 0x0000000
        self.gpio0_base    = 0x0000100
        self.uart1_base    = 0x0000200
        self.timer0_base   = 0x0000300
        self.timer0_irq    = 0
        self.timer1_base   = 0x0000400
        self.timer1_irq    = 1

        # cpu
        self.cpu = VexRiscv(
            variant="cynthion+jtag",
            reset_addr=self.mainram_base
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

        # mainram
        self.mainram = sram.Peripheral(size=self.mainram_size)
        self.wb_decoder.add(self.mainram.bus, addr=self.mainram_base, name="mainram")

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
        # FIXME figure out the best strategy for combining these into a single csr interface
        #
        # The way lambdasoc did it was simply to have peripherals instead expose a wb interface
        # and then just append each of the peripheral's csr interfaces to it.
        self.csr_decoder.add(self.timer0.bus,    addr=self.timer0_base,      name="timer0")
        self.csr_decoder.add(self.timer0.events, addr=self.timer0_base + 16, name="timer0_ev")
        self.interrupt_controller.add(self.timer0, name="timer0", number=self.timer0_irq)

        # timer1
        self.timer1 = timer.Peripheral(width=32)
        self.csr_decoder.add(self.timer1.bus,    addr=self.timer1_base,      name="timer1")
        self.csr_decoder.add(self.timer1.events, addr=self.timer1_base + 16, name="timer1_ev")
        self.interrupt_controller.add(self.timer1, name="timer1", number=self.timer1_irq)

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

        # mainram
        m.submodules += self.mainram

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

        # debug
        pmod_io  = platform.request("user_pmod", 0)
        debug_io = platform.request("debug", 0)
        m.d.comb += [
            pmod_io.oe    .eq(1),
            pmod_io.o[0]  .eq(self.timer0._sub_0.i),
            pmod_io.o[1]  .eq(self.timer0._sub_0.trg),
            pmod_io.o[2]  .eq(self.timer0._events._enable.element.r_data),
            pmod_io.o[3]  .eq(self.timer0._events._pending.element.r_data[0]),
            pmod_io.o[4]  .eq(self.timer0._events._pending.element.r_data[1]),

            pmod_io.o[5]  .eq(self.timer0.irq),
            pmod_io.o[6]  .eq(self.interrupt_controller.pending),

            pmod_io.o[7]  .eq(self.timer1.irq),

            #debug_io.a.o  .eq(self.timer0.irq),
            #debug_io.b.o  .eq(self.timer1.irq),
        ]

        return DomainRenamer({"sync": self.domain})(m)


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
