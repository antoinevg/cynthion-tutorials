#![cfg_attr(feature = "nightly", feature(error_in_core))]
#![cfg_attr(feature = "nightly", feature(panic_info_message))]
#![no_std]

// - modules ------------------------------------------------------------------

pub mod hal;
pub mod log;

// - re-exports ---------------------------------------------------------------

pub use pac;
