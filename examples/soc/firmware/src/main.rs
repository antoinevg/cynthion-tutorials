#![allow(dead_code)]

#![no_std]
#![no_main]

// - panic handler ------------------------------------------------------------

#[no_mangle]
#[panic_handler]
fn panic(_panic_info: &core::panic::PanicInfo) -> ! {
    unsafe { core::ptr::write_volatile(IO_LEDS as *mut u32, 0b11_1100) };
    loop { }
}

#[export_name = "ExceptionHandler"]
fn custom_exception_handler(_panic_info: &core::panic::PanicInfo) -> ! {
    unsafe { core::ptr::write_volatile(IO_LEDS as *mut u32, 0b11_1110) };
    loop {}
}

#[export_name = "HardFault"]
fn hard_fault() -> ! {
    loop {}
}

pub extern "C" fn rust_begin_unwind() -> ! {
    loop {}
}


// - riscv_rt::main -----------------------------------------------------------

#[riscv_rt::entry]
fn main() -> ! {
    const MSG: &'static str = "Entering main loop.\n";
    uart_tx(MSG);

    // PUSH_PULL = 0b01
    // OPEN_DRAIN = 0b10
    //let mode: u16 = 0b00_00_00_00_00_00_00_00;
    let mode: u16 = 0b01_01_01_01_01_01_01_01;
    //let mode: u16 = 0b10_10_10_10_10_10_10_10;
    unsafe { core::ptr::write_volatile(IO_LEDS_MODE as *mut u16, mode) };
    unsafe { core::ptr::write_volatile(IO_GPIO0_MODE as *mut u16, mode) };

    let mut counter = 0;
    loop {
        unsafe { riscv::asm::delay(1_000_000) };
        unsafe { core::ptr::write_volatile(IO_LEDS_OUTPUT as *mut u8, counter & 0b11_1111) };
        unsafe { core::ptr::write_volatile(IO_GPIO0_OUTPUT as *mut u8, counter) };
        counter += 1;
    }
}

// - peripherals --------------------------------------------------------------

const IO_BASE: usize = 0xf000_0000;

const IO_LEDS: usize           = IO_BASE + 0x000_0000;
const IO_LEDS_MODE: usize      = IO_LEDS + 0x0; // 16 bits wide
const IO_LEDS_INPUT: usize     = IO_LEDS + 0x2; //  8 bits wide
const IO_LEDS_OUTPUT: usize    = IO_LEDS + 0x3; //  8 bits wide
const IO_LEDS_SETCLR: usize    = IO_LEDS + 0x4; // 16 bits wide

const IO_GPIO0: usize          = IO_BASE + 0x000_0100;
const IO_GPIO0_MODE: usize     = IO_GPIO0 + 0x0; // 16 bits wide
const IO_GPIO0_INPUT: usize    = IO_GPIO0 + 0x2; //  8 bits wide
const IO_GPIO0_OUTPUT: usize   = IO_GPIO0 + 0x3; //  8 bits wide
const IO_GPIO0_SETCLR: usize   = IO_GPIO0 + 0x4; // 16 bits wide

const IO_UART: usize           = IO_BASE + 0x000_0200;
const IO_UART_TX_DATA: usize   = IO_UART + 0x00; //  8 bits wide
const IO_UART_RX_DATA: usize   = IO_UART + 0x04; //  8 bits wide
const IO_UART_TX_READY: usize  = IO_UART + 0x08; //  1 bits wide
const IO_UART_RX_AVAIL: usize  = IO_UART + 0x0c; //  1 bits wide
const IO_UART_DIVISOR: usize   = IO_UART + 0x10; // 24 bits wide


fn uart_tx(s: &str) {
    for b in s.bytes() {
        while unsafe { core::ptr::read_volatile(IO_UART_TX_READY as *mut u32) } == 0 {}
        unsafe { core::ptr::write_volatile(IO_UART_TX_DATA as *mut u32, b as u32 & 0b1111_1111) };
    }
}
