import sys
import time
import usb

import cynthion


VENDOR_ID  = cynthion.shared.usb.bVendorId.example
PRODUCT_ID = cynthion.shared.usb.bProductId.example

LEDS_BASE_ADDR   = 0x10

REQUEST_READ_REG  = 0
REQUEST_WRITE_REG = 1


def main():
    value = int(sys.argv[1]) if len(sys.argv) > 1 else 0x33

    device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if device is None:
        raise IOError("Device not found")


    def _out_request(device, number, value=0, index=0, data=None, timeout=1000):
        request_type = usb.ENDPOINT_OUT | usb.RECIP_DEVICE | usb.TYPE_VENDOR
        return device.ctrl_transfer(request_type, number, value, index, data, timeout=timeout)

    def _in_request(device, number, value=0, index=0, length=0, timeout=1000):
        request_type = usb.ENDPOINT_IN | usb.RECIP_DEVICE | usb.TYPE_VENDOR
        result = device.ctrl_transfer(request_type, number, value, index, length, timeout=timeout)
        return bytes(result)

    # read IN endpoint
    #result = device.read(0x81, 512, timeout=1000)
    #print(f"BULK IN result: {result}")

    # test read
    result = _in_request(device, REQUEST_READ_REG, index=LEDS_BASE_ADDR, length=2)
    result = ', '.join('0x{:02x}'.format(x) for x in result)
    print(f"CONTROL IN result: {result}")

    # test write
    result = _out_request(device, REQUEST_WRITE_REG, value=value, index=LEDS_BASE_ADDR)
    print(f"CONTROL OUT result: {result}")

    # test read
    result = _in_request(device, REQUEST_READ_REG, index=LEDS_BASE_ADDR, length=2)
    result = ', '.join('0x{:02x}'.format(x) for x in result)
    print(f"CONTROL IN result: {result}")


if __name__ == "__main__":
    main()
