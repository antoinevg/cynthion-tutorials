pub use lunasoc_hal::*;

lunasoc_hal::impl_serial! {
    Serial1: pac::UART1,
}

pub use lunasoc_hal::smolusb;
use lunasoc_hal::smolusb::device::Speed;
use lunasoc_hal::smolusb::setup::Direction;
use lunasoc_hal::smolusb::traits::{
    ReadControl, ReadEndpoint, UnsafeUsbDriverOperations, UsbDriver, UsbDriverOperations,
    WriteEndpoint,
};
use lunasoc_hal::usb::DEFAULT_TIMEOUT;
lunasoc_hal::impl_usb! {
    Usb0: usb0, pac::USB0, pac::USB0_EP_CONTROL, pac::USB0_EP_IN, pac::USB0_EP_OUT,
}
