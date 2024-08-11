//! smolusb hal implementation for luna eptri peripherals

/// Re-export smolusb error type
pub use smolusb::error::ErrorKind as Error;

/*use smolusb::device::Speed;
use smolusb::setup::Direction;
use smolusb::traits::{
    ReadControl, ReadEndpoint, UnsafeUsbDriverOperations, UsbDriver, UsbDriverOperations,
    WriteEndpoint,
};

use crate::pac;
use pac::interrupt::Interrupt;*/

/// Default timeout for USB operations
pub const DEFAULT_TIMEOUT: usize = 1_000_000;

/// Macro to generate smolusb hal wrappers for `pac::USBx` peripherals
///
/// For example:
///
///     impl_usb! {
///         Usb0: USB0, USB0_EP_CONTROL, USB0_EP_IN, USB0_EP_OUT,
///         Usb1: USB1, USB1_EP_CONTROL, USB1_EP_IN, USB1_EP_OUT,
///     }
///
#[macro_export]
macro_rules! impl_usb {
    ($(
        $USBX:ident: $IDX:ident, $USBX_DEVICE:ty, $USBX_EP_CONTROL:ty, $USBX_EP_IN:ty, $USBX_EP_OUT:ty,
    )+) => {
        $(
            pub struct $USBX {
                pub device: $USBX_DEVICE,
                pub ep_control: $USBX_EP_CONTROL,
                pub ep_in: $USBX_EP_IN,
                pub ep_out: $USBX_EP_OUT,
                pub device_speed: Speed,
            }

            impl $USBX {
                /// Create a new `Usb` instance.
                pub fn new(
                    device: $USBX_DEVICE,
                    ep_control: $USBX_EP_CONTROL,
                    ep_in: $USBX_EP_IN,
                    ep_out: $USBX_EP_OUT,
                ) -> Self {
                    Self {
                        device,
                        ep_control,
                        ep_in,
                        ep_out,
                        device_speed: Speed::Unknown,
                    }
                }

                /// Release all peripherals and consume self.
                pub fn free(
                    self,
                ) -> (
                    $USBX_DEVICE,
                    $USBX_EP_CONTROL,
                    $USBX_EP_IN,
                    $USBX_EP_OUT,
                ) {
                    (self.device, self.ep_control, self.ep_in, self.ep_out)
                }

                /// Obtain a static [`Usb0`] instance for use in e.g. interrupt handlers
                ///
                /// # Safety
                ///
                /// 'Tis thine responsibility, that which thou doth summon.
                #[inline(always)]
                pub unsafe fn summon() -> Self {
                    Self {
                        device: <$USBX_DEVICE>::steal(),
                        ep_control: <$USBX_EP_CONTROL>::steal(),
                        ep_in: <$USBX_EP_IN>::steal(),
                        ep_out: <$USBX_EP_OUT>::steal(),
                        device_speed: Speed::Unknown,
                    }
                }
            }

            impl $USBX {
                /// Enable all device interrupt events.
                pub fn enable_events(&self) {
                    // clear all pending event
                    self.device.ev_pending().modify(|r, w| w.mask().bit(r.mask().bit()));
                    self.ep_control.ev_pending().modify(|r, w| w.mask().bit(r.mask().bit()));
                    self.ep_in.ev_pending().modify(|r, w| w.mask().bit(r.mask().bit()));
                    self.ep_out.ev_pending().modify(|r, w| w.mask().bit(r.mask().bit()));

                    // enable all events
                    self.device.ev_enable().write(|w| w.mask().bit(true));
                    self.ep_control.ev_enable().write(|w| w.mask().bit(true));
                    self.ep_in.ev_enable().write(|w| w.mask().bit(true));
                    self.ep_out.ev_enable().write(|w| w.mask().bit(true));
                }

                /// Disable all device interrupt events.
                pub fn disable_events(&self) {
                    // clear all pending event
                    self.device.ev_pending().modify(|r, w| w.mask().bit(r.mask().bit()));
                    self.ep_control.ev_pending().modify(|r, w| w.mask().bit(r.mask().bit()));
                    self.ep_in.ev_pending().modify(|r, w| w.mask().bit(r.mask().bit()));
                    self.ep_out.ev_pending().modify(|r, w| w.mask().bit(r.mask().bit()));

                    // disable all events
                    self.device.ev_enable().write(|w| w.mask().bit(false));
                    self.ep_control.ev_enable().write(|w| w.mask().bit(false));
                    self.ep_in.ev_enable().write(|w| w.mask().bit(false));
                    self.ep_out.ev_enable().write(|w| w.mask().bit(false));
                }

                /// Returns the address of the control endpoint.
                #[must_use]
                pub fn ep_control_address(&self) -> u8 {
                    self.ep_control.status().read().address().bits()
                }
            }

            // - trait: UsbDriverOperations -----------------------------------

            impl UsbDriverOperations for $USBX {
                /// Connect the device.
                fn connect(&mut self, device_speed: Speed) {
                    // set the device speed
                    self.device_speed = device_speed;
                    match device_speed {
                        Speed::High => {
                            self.device.control().modify(|_, w| w.full_speed_only().bit(false));
                            self.device.control().modify(|_, w| w.low_speed_only().bit(false));
                        },
                        Speed::Full => {
                            self.device.control().modify(|_, w| w.full_speed_only().bit(true));
                            self.device.control().modify(|_, w| w.low_speed_only().bit(false));
                        },
                        Speed::Low => {
                            self.device.control().write(|w| w.full_speed_only().bit(false));
                            self.device.control().write(|w| w.low_speed_only().bit(true));
                        }
                        _ => {
                            log::warn!("Requested unsupported device speed '{:?}'. Ignoring request and setting device to 'Speed::High'.", device_speed);
                            self.device_speed = Speed::High;
                        }
                    }

                    // disconnect device
                    self.device.control().modify(|_, w| w.connect().bit(false));

                    // disable endpoint events
                    self.disable_events();

                    // reset FIFOs
                    self.ep_control.reset().write(|w| w.high().bit(true));
                    self.ep_in.reset()     .write(|w| w.high().bit(true));
                    self.ep_out.reset()    .write(|w| w.high().bit(true));

                    // connect device
                    self.device.control().modify(|_, w| w.connect().bit(true));
                }

                /// Disconnect the device.
                fn disconnect(&mut self) {
                    // reset speed
                    self.device.control().modify(|_, w| w.full_speed_only().bit(false));
                    self.device.control().modify(|_, w| w.low_speed_only().bit(false));
                    self.device_speed = Speed::Unknown;

                    // disable endpoint events
                    self.disable_events();

                    // reset device address to 0
                    self.set_address(0);

                    // disconnect device
                    self.device.control().modify(|_, w| w.connect().bit(false));

                    // reset FIFOs
                    self.ep_control.reset().write(|w| w.high().bit(true));
                    self.ep_in.reset()     .write(|w| w.high().bit(true));
                    self.ep_out.reset()    .write(|w| w.high().bit(true));
                }

                /// Perform a bus reset of the device.
                fn bus_reset(&self) {
                    // disable interrupt events
                    self.disable_events();

                    // reset device address to 0
                    self.set_address(0);

                    // reset FIFOs
                    self.ep_control.reset().write(|w| w.high().bit(true));
                    self.ep_in.reset()     .write(|w| w.high().bit(true));
                    self.ep_out.reset()    .write(|w| w.high().bit(true));

                    // clear status for all IN endpoints
                    for endpoint in 0..(smolusb::EP_MAX_ENDPOINTS as u8) {
                        unsafe { self.clear_tx_ack_active(endpoint); }
                    }

                    // re-enable interrupt events
                    self.enable_events();

                    log::trace!("UsbInterface0::bus_reset()");
                }

                /// Acknowledge the status stage of an incoming control request.
                fn ack(&self, endpoint_number: u8, direction: Direction) {
                    match direction {
                        // DeviceToHost - IN request, prime the endpoint so we can receive a zlp from the host
                        Direction::DeviceToHost => {
                            self.ep_out_prime_receive(endpoint_number);
                        }
                        // HostToDevice - OUT request, send a ZLP from the device to the host
                        Direction::HostToDevice => {
                            self.write(endpoint_number, [].into_iter());
                        }
                    }
                }

                /// Set the device address.
                fn set_address(&self, address: u8) {
                    self.ep_out
                        .control()
                        .modify(|_, w| unsafe { w.address().bits(address & 0x7f) });
                    self.ep_control
                        .control()
                        .modify(|_, w| unsafe { w.address().bits(address & 0x7f) });
                }

                /// Stall the given IN endpoint number.
                fn stall_endpoint_in(&self, endpoint_number: u8) {
                    self.ep_in.endpoint().write(|w| unsafe { w.number().bits(endpoint_number) });
                    self.ep_in.stall().write(|w| w.stalled().bit(true));
                }

                /// Stall the given OUT endpoint number.
                fn stall_endpoint_out(&self, endpoint_number: u8) {
                    self.ep_out.endpoint().write(|w| unsafe { w.number().bits(endpoint_number) });
                    self.ep_out.stall().write(|w| w.stalled().bit(true));
                }

                /// Clear the PID toggle bit for the given endpoint address.
                ///
                /// TODO this works most of the time, but not always ...
                /// TODO pass in endpoint number and direction separately
                ///
                /// Also see: <https://github.com/greatscottgadgets/luna/issues/166>
                fn clear_feature_endpoint_halt(&self, endpoint_address: u8) {
                    let endpoint_number = endpoint_address & 0xf;

                    if (endpoint_address & 0x80) == 0 {  // HostToDevice
                        self.ep_out.endpoint().write(|w| unsafe { w.number().bits(endpoint_number) });
                        self.ep_out.pid().write(|w| w.toggle().bit(false));

                    } else { // DeviceToHost
                        self.ep_in.endpoint().write(|w| unsafe { w.number().bits(endpoint_number) });
                        self.ep_in.pid().write(|w| w.toggle().bit(false));
                    }
                }
            }

            // - trait: UnsafeUsbDriverOperations -----------------------------

            #[allow(non_snake_case)]
            mod $IDX {
                use lunasoc_hal::smolusb::EP_MAX_ENDPOINTS;

                #[cfg(target_has_atomic)]
                #[allow(clippy::declare_interior_mutable_const)]
                const ATOMIC_FALSE: core::sync::atomic::AtomicBool = core::sync::atomic::AtomicBool::new(false);

                #[cfg(not(target_has_atomic))]
                pub static mut TX_ACK_ACTIVE: [bool; EP_MAX_ENDPOINTS] = [false; EP_MAX_ENDPOINTS];
                #[cfg(target_has_atomic)]
                pub static TX_ACK_ACTIVE: [core::sync::atomic::AtomicBool; EP_MAX_ENDPOINTS] =
                    [ATOMIC_FALSE; EP_MAX_ENDPOINTS];

            }

            impl UnsafeUsbDriverOperations for $USBX {
                #[inline(always)]
                unsafe fn set_tx_ack_active(&self, endpoint_number: u8) {
                    #[cfg(not(target_has_atomic))]
                    {
                        let endpoint_number = endpoint_number as usize;
                        riscv::interrupt::free(|| {
                            $IDX::TX_ACK_ACTIVE[endpoint_number] = true;
                        });
                    }
                    #[cfg(target_has_atomic)]
                    {
                        use core::sync::atomic::Ordering;
                        let endpoint_number = endpoint_number as usize;
                        $IDX::TX_ACK_ACTIVE[endpoint_number].store(true, Ordering::Relaxed);
                    }
                }
                #[inline(always)]
                unsafe fn clear_tx_ack_active(&self, endpoint_number: u8) {
                    #[cfg(not(target_has_atomic))]
                    {
                        let endpoint_number = endpoint_number as usize;
                        riscv::interrupt::free(|| {
                            $IDX::TX_ACK_ACTIVE[endpoint_number] = false;
                        });
                    }
                    #[cfg(target_has_atomic)]
                    {
                        use core::sync::atomic::Ordering;
                        let endpoint_number = endpoint_number as usize;
                        $IDX::TX_ACK_ACTIVE[endpoint_number].store(false, Ordering::Relaxed);
                    }
                }
                #[inline(always)]
                unsafe fn is_tx_ack_active(&self, endpoint_number: u8) -> bool {
                    #[cfg(not(target_has_atomic))]
                    {
                        let endpoint_number = endpoint_number as usize;
                        let active = riscv::interrupt::free(|| {
                            $IDX::TX_ACK_ACTIVE[endpoint_number]
                        });
                        active
                    }
                    #[cfg(target_has_atomic)]
                    {
                        use core::sync::atomic::Ordering;
                        let endpoint_number = endpoint_number as usize;
                        $IDX::TX_ACK_ACTIVE[endpoint_number].load(Ordering::Relaxed)
                    }
                }
            }

            // - trait: Read/Write traits -------------------------------------

            impl ReadControl for $USBX {
                /// Read a setup packet from the control endpoint.
                fn read_control(&self, buffer: &mut [u8]) -> usize {
                    // drain fifo
                    let mut bytes_read = 0;
                    let mut overflow = 0;
                    while self.ep_control.status().read().have().bit() {
                        if bytes_read >= buffer.len() {
                            let _drain = self.ep_control.data().read().byte().bits();
                            overflow += 1;
                        } else {
                            buffer[bytes_read] = self.ep_control.data().read().byte().bits();
                            bytes_read += 1;
                        }
                    }

                    if bytes_read != buffer.len() {
                        log::warn!("  RX {} CONTROL {} bytes read - expected {}",
                              stringify!($USBX),
                              bytes_read, buffer.len());
                    }

                    if overflow == 0 {
                        log::trace!("  RX {} CONTROL {} bytes read", stringify!($USBX), bytes_read);
                    } else {
                        log::warn!("  RX {} CONTROL {} bytes read + {} bytes overflow",
                              stringify!($USBX),
                              bytes_read, overflow);
                    }

                    bytes_read + overflow
                }
            }

            impl ReadEndpoint for $USBX {
                /// Prepare OUT endpoint to receive a single packet.
                #[inline(always)]
                fn ep_out_prime_receive(&self, endpoint_number: u8) {
                    // 0. clear receive fifo in case the previous transaction wasn't handled
                    if self.ep_out.status().read().have().bit() {
                        log::warn!("  {} priming out endpoint {} with unread data", stringify!($USBX), endpoint_number);

                        /*let mut rx_buffer: [u8; smolusb::EP_MAX_PACKET_SIZE] = [0; smolusb::EP_MAX_PACKET_SIZE];
                        let bytes_read = self.read(endpoint_number, &mut rx_buffer);
                        log::warn!("  got {} bytes: -> {:?}",
                              bytes_read,
                              &rx_buffer[0..bytes_read],
                        );*/
                        self.ep_out.reset().write(|w| w.high().bit(true));
                    }

                    // 1. select endpoint
                    self.ep_out
                        .endpoint()
                        .write(|w| unsafe { w.number().bits(endpoint_number) });

                    // 2. prime endpoint
                    self.ep_out.prime().write(|w| w.primed().bit(true));

                    // 3. re-enable ep_out interface
                    self.ep_out.enable().write(|w| w.enabled().bit(true));
                }

                #[inline(always)]
                fn read(&self, endpoint_number: u8, buffer: &mut [u8]) -> usize {
                    let mut bytes_read = 0;
                    let mut did_overflow = true;
                    for b in buffer.iter_mut() {
                        if self.ep_out.status().read().have().bit() {
                            *b = self.ep_out.data().read().byte().bits();
                            bytes_read += 1;
                        } else {
                            did_overflow = false;
                            break;
                        }
                    }

                    // drain fifo if needed
                    let mut overflow = 0;
                    while did_overflow && self.ep_out.status().read().have().bit() {
                        let _drain = self.ep_out.data().read().byte().bits();
                        overflow += 1;
                    }

                    if overflow == 0 {
                        log::trace!("  RX {} OUT {} {} bytes read", stringify!($USBX), endpoint_number, bytes_read);
                    } else {
                        log::warn!("  RX {} OUT {} {} bytes read + {} bytes overflow",
                              stringify!($USBX),
                              endpoint_number, bytes_read, overflow);
                    }

                    bytes_read + overflow
                }
            }

            impl WriteEndpoint for $USBX {
                fn write<'a, I>(&self, endpoint_number: u8, iter: I) -> usize
                where
                    I: Iterator<Item = u8>
                {
                    let max_packet_size = match (self.device_speed, endpoint_number) {
                        (_, 0) => 64,
                        (Speed::High, _) => smolusb::EP_MAX_PACKET_SIZE,
                        (Speed::Full, _) => 64,
                        (_, _) => {
                            log::warn!("{}::write unsupported device speed: {:?}", stringify!($USBX), self.device_speed);
                            64
                        }
                    };
                    self.write_with_packet_size(endpoint_number, iter, max_packet_size)
                }

                fn write_with_packet_size<'a, I>(&self, endpoint_number: u8, iter: I, packet_size: usize) -> usize
                where
                    I: Iterator<Item = u8>
                {
                    unsafe { self.set_tx_ack_active(endpoint_number); }

                    // check if output FIFO is empty
                    // FIXME return a GreatError::DeviceOrResourceBusy on timeout
                    let mut timeout = 0;
                    while self.ep_in.status().read().have().bit() {
                        if timeout == 0 {
                            log::warn!("  {} clear tx", stringify!($USBX));
                        } else if timeout > DEFAULT_TIMEOUT {
                            self.ep_in.reset().write(|w| w.high().bit(true));
                            log::error!("  {} clear tx timeout", stringify!($USBX));
                        }
                        timeout += 1;
                    }

                    let mut bytes_written: usize = 0;
                    for byte in iter {
                        self.ep_in.data().write(|w| unsafe { w.byte().bits(byte) });
                        bytes_written += 1;

                        // check if we've written a packet yet and need to send it
                        if bytes_written % packet_size == 0 {
                            log::debug!("1a");
                            // prime the IN endpoint to send it
                            self.ep_in
                                .endpoint()
                                .write(|w| unsafe { w.number().bits(endpoint_number) });

                            // wait for transmission to complete
                            let mut timeout = 0;
                            while self.ep_in.status().read().have().bit() {
                                timeout += 1;
                                if timeout > DEFAULT_TIMEOUT {
                                    log::error!(
                                        "{}::write timed out after {} bytes",
                                        stringify!($USBX),
                                        bytes_written
                                    );
                                    // TODO return an error
                                    return bytes_written;
                                }
                            }
                        }
                    }

                    // finally, prime IN endpoint to either send
                    // remaining queued data or a ZLP if the fifo
                    // is empty and transmission is complete
                    self.ep_in
                        .endpoint()
                        .write(|w| unsafe { w.number().bits(endpoint_number) });
                    while unsafe { self.is_tx_ack_active(endpoint_number) } {}

                    bytes_written
                }

            }

            // mark implementation as complete
            impl UsbDriver for $USBX {}
        )+
    }
}