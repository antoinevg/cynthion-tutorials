#![allow(dead_code)]

#![no_std]
#![no_main]

use panic_halt as _;
use riscv_rt::entry;

use pac;

// - riscv_rt::main -----------------------------------------------------------

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();
    let leds   = &peripherals.LEDS;
    let gpio0  = &peripherals.GPIO0;
    let uart1  = &peripherals.UART1;

    const MSG: &'static str = "Entering main loop.\n";
    uart_tx(&uart1, MSG);

    // configure leds, gpio0
    //
    //   INPUT      = 0b00
    //   PUSH_PULL  = 0b01
    //   OPEN_DRAIN = 0b10
    let mode: u16 = 0b01_01_01_01_01_01_01_01;
    leds.mode().write(|w| unsafe { w.bits(mode) });
    gpio0.mode().write(|w| unsafe { w.bits(mode) });

    let mut direction = true;
    let mut led_state = 0b1100_0000;

    loop {
        unsafe { riscv::asm::delay(6_000_000) };

        if direction {
            led_state >>= 1;
            if led_state == 0b00000011 {
                direction = false;
                uart_tx(&uart1, "left\n");
            }
        } else {
            led_state <<= 1;
            if led_state == 0b11000000 {
                direction = true;
                uart_tx(&uart1, "right\n");
            }
        }

        leds.output().write(|w| unsafe { w.bits(led_state & 0b11_1111) });
        gpio0.output().write(|w| unsafe { w.bits(led_state) });
    }
}


// - helpers ------------------------------------------------------------------

fn uart_tx(uart: &pac::UART1, s: &str) {
    for b in s.bytes() {
        while uart.tx_ready().read().txe() == false {}
        unsafe { uart.tx_data().write(|w| w.data().bits(b)); }
    }
}
