#![allow(dead_code, non_upper_case_globals, unused_imports)]

#![no_std]
#![no_main]

use panic_halt as _;
use riscv_rt::entry;

use log::{error, info};

use hello_soc::{hal, pac};

// - constants ----------------------------------------------------------------

const PSRAM_BASE:  usize = 0x2000_0000;
const PSRAM_SIZE:  usize = 0x0800_0000;
const PSRAM_WORDS: usize = PSRAM_SIZE / 4;

// - riscv_rt::pre_init -------------------------------------------------------

#[cfg(feature = "vexriscv")]
#[riscv_rt::pre_init]
unsafe fn pre_main() {
    pac::cpu::vexriscv::flush_icache();
    #[cfg(feature = "vexriscv_dcache")]
    pac::cpu::vexriscv::flush_dcache();
}

// - riscv_rt::main -----------------------------------------------------------

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();

    // initialize logging
    hello_soc::log::init(hal::Serial1::new(peripherals.UART1));
    info!("logging initialized");

    // ila
    let ila = peripherals.ILA;

    // enter main loop
    info!("Peripherals initialized, entering main loop.");

    // simple hyperram test - all word sizes
    const test_size: usize = 16;
    let delay = 100;
    loop {
        ila.control().write(|w| w.trigger().bit(true));

        // 32 bit
        //info!("Testing 32 bit:");
        /*let ptr = PSRAM_BASE as *mut u32;
        let mut buf = [0_u32; test_size];
        unsafe { riscv::asm::delay(delay) };
        for offset in 0..test_size {
            //let value = 0xffff_ffff - offset;
            let value = offset;
            unsafe { ptr.offset(offset as isize).write_volatile(value as u32) };
        }
        pac::cpu::vexriscv::flush_dcache();
        for offset in 0..test_size {
            let value = unsafe { ptr.offset(offset as isize).read_volatile() };
            buf[offset] = value;
        }
        unsafe { riscv::asm::delay(delay) };*/
        //info!("  {:08x?}", buf);

        // 16 bit
        //info!("Testing 16 bit:");
        unsafe { ila.trace().write(|w| w.a().bits(1)); }
        let ptr = PSRAM_BASE as *mut u16;
        let mut buf = [0_u16; test_size];
        //unsafe { riscv::asm::delay(delay) };
        for offset in 0..test_size {
            //let value = 0xffff - offset;
            let value = offset;
            unsafe { ptr.offset(offset as isize).write_volatile(value as u16) };
            //unsafe { ila.trace().write(|w| w.a().bits(offset as u8)); }
        }
        pac::cpu::vexriscv::flush_dcache();
        unsafe { ila.trace().write(|w| w.a().bits(2)); }
        for offset in 0..test_size {
            let value = unsafe { ptr.offset(offset as isize).read_volatile() };
            buf[offset] = value;
        }
        //unsafe { riscv::asm::delay(delay) };
        //info!("  {:04x?}", buf);

        //  8 bit
        //info!("Testing 8 bit:");
        unsafe { ila.trace().write(|w| w.a().bits(3)); }
        let ptr = PSRAM_BASE as *mut u8;
        let mut buf = [0_u8; test_size];
        //unsafe { riscv::asm::delay(delay) };
        for offset in 0..test_size {
            //let value = 0xff - offset;
            let value = offset;
            unsafe { ptr.offset(offset as isize).write_volatile(value as u8) };
        }
        pac::cpu::vexriscv::flush_dcache();
        unsafe { ila.trace().write(|w| w.a().bits(4)); }
        for offset in 0..test_size {
            let value = unsafe { ptr.offset(offset as isize).read_volatile() };
            buf[offset] = value;
        }
        //unsafe { riscv::asm::delay(delay) };
        info!("  {:02x?}\n", buf);

        unsafe { riscv::asm::delay(60_000_000) };
    }

    // full hyperram test
    /*let test_size = (8 * 1024 * 1024) / core::mem::size_of::<u32>();
    let mut error = false;
    loop {
        // hyperram test - 32 bit word
        let ptr = PSRAM_BASE as *mut u32;
        for offset in 0..test_size {
            unsafe { ptr.offset(offset as isize).write_volatile(offset as u32) };
        }
        pac::cpu::vexriscv::flush_dcache();
        for offset in 0..test_size {
            let value = unsafe { ptr.offset(offset as isize).read_volatile() };
            if (offset as u32) != value {
                error!("❌ 32 bit word test: {:#x} is {:#x}", offset, value);
                error = true;
                break;
            }
        }
        if !error {
            info!("✅ 32 bit word test");
        }
        error = false;

        // hyperram test - 16 bit word
        let ptr = PSRAM_BASE as *mut u16;
        for offset in 0..test_size {
            unsafe { ptr.offset(offset as isize).write_volatile(offset as u16) };
        }
        pac::cpu::vexriscv::flush_dcache();
        for offset in 0..test_size {
            let test = (offset % 0xffff ) as u16;
            let value = unsafe { ptr.offset(offset as isize).read_volatile() };
            if test != value {
                error!("❌ 16 bit word test: {:#x} is {:#x}", test, value);
                error = true;
                break;
            }
        }
        if !error {
            info!("✅ 16 bit word test");
        }
        error = false;

        // hyperram test - 8 bit word
        let ptr = PSRAM_BASE as *mut u8;
        for offset in 0..test_size {
            unsafe { ptr.offset(offset as isize).write_volatile(offset as u8) };
        }
        pac::cpu::vexriscv::flush_dcache();
        for offset in 0..test_size {
            let value = unsafe { ptr.offset(offset as isize).read_volatile() };
            if (offset as u8) != value {
                error!("❌  8 bit word test: {:#x} is {:#x}", offset, value);
                error = true;
                break;
            }
        }
        if !error {
            info!("✅ 8 bit word test");
        }
        error = false;
    }*/
}
