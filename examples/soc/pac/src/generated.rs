#![doc = "Peripheral access API for SOC microcontrollers (generated using svd2rust v0.33.3 ( ))\n\nYou can find an overview of the generated API [here].\n\nAPI features to be included in the [next]
svd2rust release can be generated by cloning the svd2rust [repository], checking out the above commit, and running `cargo doc --open`.\n\n[here]: https://docs.rs/svd2rust/0.33.3/svd2rust/#peripheral-api\n[next]: https://github.com/rust-embedded/svd2rust/blob/master/CHANGELOG.md#unreleased\n[repository]: https://github.com/rust-embedded/svd2rust"]
use core::marker::PhantomData;
use core::ops::Deref;
#[allow(unused_imports)]
use generic::*;
#[doc = r"Common register and bit access and modify traits"]
pub mod generic;
#[cfg(feature = "rt")]
extern "C" {
    fn TIMER0();
    fn TIMER1();
}
#[doc(hidden)]
#[repr(C)]
pub union Vector {
    pub _handler: unsafe extern "C" fn(),
    pub _reserved: usize,
}
#[cfg(feature = "rt")]
#[doc(hidden)]
#[no_mangle]
pub static __EXTERNAL_INTERRUPTS: [Vector; 2] =
    [Vector { _handler: TIMER0 }, Vector { _handler: TIMER1 }];
#[doc(hidden)]
pub mod interrupt;
pub use self::interrupt::Interrupt;
#[doc = "leds"]
pub struct LEDS {
    _marker: PhantomData<*const ()>,
}
unsafe impl Send for LEDS {}
impl LEDS {
    #[doc = r"Pointer to the register block"]
    pub const PTR: *const leds::RegisterBlock = 0xf000_0000 as *const _;
    #[doc = r"Return the pointer to the register block"]
    #[inline(always)]
    pub const fn ptr() -> *const leds::RegisterBlock {
        Self::PTR
    }
    #[doc = r" Steal an instance of this peripheral"]
    #[doc = r""]
    #[doc = r" # Safety"]
    #[doc = r""]
    #[doc = r" Ensure that the new instance of the peripheral cannot be used in a way"]
    #[doc = r" that may race with any existing instances, for example by only"]
    #[doc = r" accessing read-only or write-only registers, or by consuming the"]
    #[doc = r" original peripheral and using critical sections to coordinate"]
    #[doc = r" access between multiple new instances."]
    #[doc = r""]
    #[doc = r" Additionally, other software such as HALs may rely on only one"]
    #[doc = r" peripheral instance existing to ensure memory safety; ensure"]
    #[doc = r" no stolen instances are passed to such software."]
    pub unsafe fn steal() -> Self {
        Self {
            _marker: PhantomData,
        }
    }
}
impl Deref for LEDS {
    type Target = leds::RegisterBlock;
    #[inline(always)]
    fn deref(&self) -> &Self::Target {
        unsafe { &*Self::PTR }
    }
}
impl core::fmt::Debug for LEDS {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> core::fmt::Result {
        f.debug_struct("LEDS").finish()
    }
}
#[doc = "leds"]
pub mod leds;
#[doc = "gpio0"]
pub struct GPIO0 {
    _marker: PhantomData<*const ()>,
}
unsafe impl Send for GPIO0 {}
impl GPIO0 {
    #[doc = r"Pointer to the register block"]
    pub const PTR: *const gpio0::RegisterBlock = 0xf000_0100 as *const _;
    #[doc = r"Return the pointer to the register block"]
    #[inline(always)]
    pub const fn ptr() -> *const gpio0::RegisterBlock {
        Self::PTR
    }
    #[doc = r" Steal an instance of this peripheral"]
    #[doc = r""]
    #[doc = r" # Safety"]
    #[doc = r""]
    #[doc = r" Ensure that the new instance of the peripheral cannot be used in a way"]
    #[doc = r" that may race with any existing instances, for example by only"]
    #[doc = r" accessing read-only or write-only registers, or by consuming the"]
    #[doc = r" original peripheral and using critical sections to coordinate"]
    #[doc = r" access between multiple new instances."]
    #[doc = r""]
    #[doc = r" Additionally, other software such as HALs may rely on only one"]
    #[doc = r" peripheral instance existing to ensure memory safety; ensure"]
    #[doc = r" no stolen instances are passed to such software."]
    pub unsafe fn steal() -> Self {
        Self {
            _marker: PhantomData,
        }
    }
}
impl Deref for GPIO0 {
    type Target = gpio0::RegisterBlock;
    #[inline(always)]
    fn deref(&self) -> &Self::Target {
        unsafe { &*Self::PTR }
    }
}
impl core::fmt::Debug for GPIO0 {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> core::fmt::Result {
        f.debug_struct("GPIO0").finish()
    }
}
#[doc = "gpio0"]
pub mod gpio0;
#[doc = "uart1"]
pub struct UART1 {
    _marker: PhantomData<*const ()>,
}
unsafe impl Send for UART1 {}
impl UART1 {
    #[doc = r"Pointer to the register block"]
    pub const PTR: *const uart1::RegisterBlock = 0xf000_0200 as *const _;
    #[doc = r"Return the pointer to the register block"]
    #[inline(always)]
    pub const fn ptr() -> *const uart1::RegisterBlock {
        Self::PTR
    }
    #[doc = r" Steal an instance of this peripheral"]
    #[doc = r""]
    #[doc = r" # Safety"]
    #[doc = r""]
    #[doc = r" Ensure that the new instance of the peripheral cannot be used in a way"]
    #[doc = r" that may race with any existing instances, for example by only"]
    #[doc = r" accessing read-only or write-only registers, or by consuming the"]
    #[doc = r" original peripheral and using critical sections to coordinate"]
    #[doc = r" access between multiple new instances."]
    #[doc = r""]
    #[doc = r" Additionally, other software such as HALs may rely on only one"]
    #[doc = r" peripheral instance existing to ensure memory safety; ensure"]
    #[doc = r" no stolen instances are passed to such software."]
    pub unsafe fn steal() -> Self {
        Self {
            _marker: PhantomData,
        }
    }
}
impl Deref for UART1 {
    type Target = uart1::RegisterBlock;
    #[inline(always)]
    fn deref(&self) -> &Self::Target {
        unsafe { &*Self::PTR }
    }
}
impl core::fmt::Debug for UART1 {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> core::fmt::Result {
        f.debug_struct("UART1").finish()
    }
}
#[doc = "uart1"]
pub mod uart1;
#[doc = "timer0"]
pub struct TIMER0 {
    _marker: PhantomData<*const ()>,
}
unsafe impl Send for TIMER0 {}
impl TIMER0 {
    #[doc = r"Pointer to the register block"]
    pub const PTR: *const timer0::RegisterBlock = 0xf000_0300 as *const _;
    #[doc = r"Return the pointer to the register block"]
    #[inline(always)]
    pub const fn ptr() -> *const timer0::RegisterBlock {
        Self::PTR
    }
    #[doc = r" Steal an instance of this peripheral"]
    #[doc = r""]
    #[doc = r" # Safety"]
    #[doc = r""]
    #[doc = r" Ensure that the new instance of the peripheral cannot be used in a way"]
    #[doc = r" that may race with any existing instances, for example by only"]
    #[doc = r" accessing read-only or write-only registers, or by consuming the"]
    #[doc = r" original peripheral and using critical sections to coordinate"]
    #[doc = r" access between multiple new instances."]
    #[doc = r""]
    #[doc = r" Additionally, other software such as HALs may rely on only one"]
    #[doc = r" peripheral instance existing to ensure memory safety; ensure"]
    #[doc = r" no stolen instances are passed to such software."]
    pub unsafe fn steal() -> Self {
        Self {
            _marker: PhantomData,
        }
    }
}
impl Deref for TIMER0 {
    type Target = timer0::RegisterBlock;
    #[inline(always)]
    fn deref(&self) -> &Self::Target {
        unsafe { &*Self::PTR }
    }
}
impl core::fmt::Debug for TIMER0 {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> core::fmt::Result {
        f.debug_struct("TIMER0").finish()
    }
}
#[doc = "timer0"]
pub mod timer0;
#[doc = "timer0_ev"]
pub struct TIMER0_EV {
    _marker: PhantomData<*const ()>,
}
unsafe impl Send for TIMER0_EV {}
impl TIMER0_EV {
    #[doc = r"Pointer to the register block"]
    pub const PTR: *const timer0_ev::RegisterBlock = 0xf000_0310 as *const _;
    #[doc = r"Return the pointer to the register block"]
    #[inline(always)]
    pub const fn ptr() -> *const timer0_ev::RegisterBlock {
        Self::PTR
    }
    #[doc = r" Steal an instance of this peripheral"]
    #[doc = r""]
    #[doc = r" # Safety"]
    #[doc = r""]
    #[doc = r" Ensure that the new instance of the peripheral cannot be used in a way"]
    #[doc = r" that may race with any existing instances, for example by only"]
    #[doc = r" accessing read-only or write-only registers, or by consuming the"]
    #[doc = r" original peripheral and using critical sections to coordinate"]
    #[doc = r" access between multiple new instances."]
    #[doc = r""]
    #[doc = r" Additionally, other software such as HALs may rely on only one"]
    #[doc = r" peripheral instance existing to ensure memory safety; ensure"]
    #[doc = r" no stolen instances are passed to such software."]
    pub unsafe fn steal() -> Self {
        Self {
            _marker: PhantomData,
        }
    }
}
impl Deref for TIMER0_EV {
    type Target = timer0_ev::RegisterBlock;
    #[inline(always)]
    fn deref(&self) -> &Self::Target {
        unsafe { &*Self::PTR }
    }
}
impl core::fmt::Debug for TIMER0_EV {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> core::fmt::Result {
        f.debug_struct("TIMER0_EV").finish()
    }
}
#[doc = "timer0_ev"]
pub mod timer0_ev;
#[doc = "timer1"]
pub struct TIMER1 {
    _marker: PhantomData<*const ()>,
}
unsafe impl Send for TIMER1 {}
impl TIMER1 {
    #[doc = r"Pointer to the register block"]
    pub const PTR: *const timer1::RegisterBlock = 0xf000_0400 as *const _;
    #[doc = r"Return the pointer to the register block"]
    #[inline(always)]
    pub const fn ptr() -> *const timer1::RegisterBlock {
        Self::PTR
    }
    #[doc = r" Steal an instance of this peripheral"]
    #[doc = r""]
    #[doc = r" # Safety"]
    #[doc = r""]
    #[doc = r" Ensure that the new instance of the peripheral cannot be used in a way"]
    #[doc = r" that may race with any existing instances, for example by only"]
    #[doc = r" accessing read-only or write-only registers, or by consuming the"]
    #[doc = r" original peripheral and using critical sections to coordinate"]
    #[doc = r" access between multiple new instances."]
    #[doc = r""]
    #[doc = r" Additionally, other software such as HALs may rely on only one"]
    #[doc = r" peripheral instance existing to ensure memory safety; ensure"]
    #[doc = r" no stolen instances are passed to such software."]
    pub unsafe fn steal() -> Self {
        Self {
            _marker: PhantomData,
        }
    }
}
impl Deref for TIMER1 {
    type Target = timer1::RegisterBlock;
    #[inline(always)]
    fn deref(&self) -> &Self::Target {
        unsafe { &*Self::PTR }
    }
}
impl core::fmt::Debug for TIMER1 {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> core::fmt::Result {
        f.debug_struct("TIMER1").finish()
    }
}
#[doc = "timer1"]
pub mod timer1;
#[doc = "timer1_ev"]
pub struct TIMER1_EV {
    _marker: PhantomData<*const ()>,
}
unsafe impl Send for TIMER1_EV {}
impl TIMER1_EV {
    #[doc = r"Pointer to the register block"]
    pub const PTR: *const timer1_ev::RegisterBlock = 0xf000_0410 as *const _;
    #[doc = r"Return the pointer to the register block"]
    #[inline(always)]
    pub const fn ptr() -> *const timer1_ev::RegisterBlock {
        Self::PTR
    }
    #[doc = r" Steal an instance of this peripheral"]
    #[doc = r""]
    #[doc = r" # Safety"]
    #[doc = r""]
    #[doc = r" Ensure that the new instance of the peripheral cannot be used in a way"]
    #[doc = r" that may race with any existing instances, for example by only"]
    #[doc = r" accessing read-only or write-only registers, or by consuming the"]
    #[doc = r" original peripheral and using critical sections to coordinate"]
    #[doc = r" access between multiple new instances."]
    #[doc = r""]
    #[doc = r" Additionally, other software such as HALs may rely on only one"]
    #[doc = r" peripheral instance existing to ensure memory safety; ensure"]
    #[doc = r" no stolen instances are passed to such software."]
    pub unsafe fn steal() -> Self {
        Self {
            _marker: PhantomData,
        }
    }
}
impl Deref for TIMER1_EV {
    type Target = timer1_ev::RegisterBlock;
    #[inline(always)]
    fn deref(&self) -> &Self::Target {
        unsafe { &*Self::PTR }
    }
}
impl core::fmt::Debug for TIMER1_EV {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> core::fmt::Result {
        f.debug_struct("TIMER1_EV").finish()
    }
}
#[doc = "timer1_ev"]
pub mod timer1_ev;
#[no_mangle]
static mut DEVICE_PERIPHERALS: bool = false;
#[doc = r" All the peripherals."]
#[allow(non_snake_case)]
pub struct Peripherals {
    #[doc = "leds"]
    pub LEDS: LEDS,
    #[doc = "gpio0"]
    pub GPIO0: GPIO0,
    #[doc = "uart1"]
    pub UART1: UART1,
    #[doc = "timer0"]
    pub TIMER0: TIMER0,
    #[doc = "timer0_ev"]
    pub TIMER0_EV: TIMER0_EV,
    #[doc = "timer1"]
    pub TIMER1: TIMER1,
    #[doc = "timer1_ev"]
    pub TIMER1_EV: TIMER1_EV,
}
impl Peripherals {
    #[doc = r" Returns all the peripherals *once*."]
    #[cfg(feature = "critical-section")]
    #[inline]
    pub fn take() -> Option<Self> {
        critical_section::with(|_| {
            if unsafe { DEVICE_PERIPHERALS } {
                return None;
            }
            Some(unsafe { Peripherals::steal() })
        })
    }
    #[doc = r" Unchecked version of `Peripherals::take`."]
    #[doc = r""]
    #[doc = r" # Safety"]
    #[doc = r""]
    #[doc = r" Each of the returned peripherals must be used at most once."]
    #[inline]
    pub unsafe fn steal() -> Self {
        DEVICE_PERIPHERALS = true;
        Peripherals {
            LEDS: LEDS {
                _marker: PhantomData,
            },
            GPIO0: GPIO0 {
                _marker: PhantomData,
            },
            UART1: UART1 {
                _marker: PhantomData,
            },
            TIMER0: TIMER0 {
                _marker: PhantomData,
            },
            TIMER0_EV: TIMER0_EV {
                _marker: PhantomData,
            },
            TIMER1: TIMER1 {
                _marker: PhantomData,
            },
            TIMER1_EV: TIMER1_EV {
                _marker: PhantomData,
            },
        }
    }
}
