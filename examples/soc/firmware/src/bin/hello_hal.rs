#![allow(dead_code)]

#![no_std]
#![no_main]

use panic_halt as _;
use riscv_rt::entry;

use log::{info, debug};

use pac;
//use hal;

// - riscv_rt::main -----------------------------------------------------------

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();
    let leds   = &peripherals.LEDS;
    let gpio0  = &peripherals.GPIO0;
    let timer0 = &peripherals.TIMER0;

    // initialize logging
    hello_soc::log::init(hello_soc::Serial1::new(peripherals.UART1));

    // configure leds, gpio0
    //
    //   INPUT      = 0b00
    //   PUSH_PULL  = 0b01
    //   OPEN_DRAIN = 0b10
    let mode: u16 = 0b01_01_01_01_01_01_01_01;
    leds.mode().write(|w| unsafe { w.bits(mode) });
    gpio0.mode().write(|w| unsafe { w.bits(mode) });

    // configure timer0
    //timer0.reload().write(|w| unsafe { w.value().bits(0xffffffff) });
    timer0.reload().write(|w| unsafe { w.value().bits(0x3000_0000) });
    timer0.enable().write(|w| w.enable().bit(true));

    let mut direction = true;
    let mut led_state = 0b1100_0000;

    info!("Entering main loop.");

    loop {
        unsafe { riscv::asm::delay(6_000_000) };

        if direction {
            led_state >>= 1;
            if led_state == 0b00000011 {
                direction = false;
                let counter = timer0.counter().read().value().bits();
                info!("left: 0x{:08x}", counter);
            }
        } else {
            led_state <<= 1;
            if led_state == 0b11000000 {
                direction = true;
                let counter = timer0.counter().read().value().bits();
                debug!("right: 0x{:08x}", counter);
            }
        }

        leds.output().write(|w| unsafe { w.bits(led_state & 0b11_1111) });
        gpio0.output().write(|w| unsafe { w.bits(led_state) });
    }
}
