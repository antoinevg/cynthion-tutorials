#![cfg_attr(feature = "nightly", feature(error_in_core))]
#![cfg_attr(feature = "nightly", feature(panic_info_message))]
#![no_std]

// - modules ------------------------------------------------------------------

pub mod log;



// - hal peripherals ----------------------------------------------------------

hal::impl_serial! {
    Serial1: pac::UART1,
}
