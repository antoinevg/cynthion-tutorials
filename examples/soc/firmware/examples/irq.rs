#![allow(dead_code)]

#![no_std]
#![no_main]

use panic_halt as _;
use riscv_rt::entry;

use log::{info, error};

use pac;

// - interrupt handler --------------------------------------------------------

#[allow(non_snake_case)]
#[no_mangle]
fn MachineExternal() {
    let leds   = unsafe { pac::LEDS::steal() };
    let timer0_ev = unsafe { pac::TIMER0_EV::steal() };
    let timer1_ev = unsafe { pac::TIMER1_EV::steal() };

    if pac::csr::interrupt::is_pending(pac::Interrupt::TIMER0) {
        timer0_ev.pending().modify(|r, w| unsafe { w.mask().bits(r.mask().bits()) });
        leds.output().write(|w| unsafe { w.bits(0b11_1000) });
    } else if pac::csr::interrupt::is_pending(pac::Interrupt::TIMER1) {
        timer1_ev.pending().modify(|r, w| unsafe { w.mask().bits(r.mask().bits()) });
        leds.output().write(|w| unsafe { w.bits(0b00_0111) });
    } else {
        error!("MachineExternal - unknown interrupt");
    }
}



// - riscv_rt::main -----------------------------------------------------------

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();
    let leds      = &peripherals.LEDS;
    let timer0    = &peripherals.TIMER0;
    let timer0_ev = &peripherals.TIMER0_EV;
    let timer1    = &peripherals.TIMER1;
    let timer1_ev = &peripherals.TIMER1_EV;

    // initialize logging
    hello_soc::log::init(hello_soc::Serial1::new(peripherals.UART1));

    // configure leds
    //
    //   INPUT      = 0b00
    //   PUSH_PULL  = 0b01
    //   OPEN_DRAIN = 0b10
    let mode: u16 = 0b01_01_01_01_01_01_01_01;
    leds.mode().write(|w| unsafe { w.bits(mode) });

    // configure timers
    let t = pac::clock::sysclk() as f32 / 3.2;
    timer0.reload().write(|w| unsafe { w.value().bits(t as u32) });
    timer0.enable().write(|w| w.enable().bit(true));
    timer1.reload().write(|w| unsafe { w.value().bits(pac::clock::sysclk()) });
    timer1.enable().write(|w| w.enable().bit(true));

    // enable timer events
    timer0_ev.enable().write(|w| unsafe { w.mask().bits(0b11) }); // event: sub_0
    timer1_ev.enable().write(|w| unsafe { w.mask().bits(0b11) }); // event: sub_0 TODO sub_1

    // enable interrupts
    unsafe {
        // set mstatus register: interrupt enable
        riscv::interrupt::enable();

        // set mie register: machine external interrupts enable
        riscv::register::mie::set_mext();

        // write csr: enable timer interrupts
        pac::csr::interrupt::enable(pac::Interrupt::TIMER0);
        pac::csr::interrupt::enable(pac::Interrupt::TIMER1);
    }

    info!("Peripherals initialized, entering main loop.");

    let mut uptime = 1;
    loop {
        info!("Uptime: {} seconds", uptime);

        unsafe {
            riscv::asm::delay(pac::clock::sysclk());
        }
        uptime += 1;
    }
}
