import random
import time
import usb

VENDOR_ID=0x16d0
PRODUCT_ID=0xf3b

DUMMY_BASE_ADDR   = 0x10

REQUEST_READ_REG  = 0
REQUEST_WRITE_REG = 1
REQUEST_READ_MEM   = 2
REQUEST_WRITE_MEM  = 3


def main():
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

    length = 64

    # test bulk OUT request
    #data = [random.getrandbits(8) for i in range(0, length)]
    data = [(i % 256) for i in range(0, length)]
    #data = [(i % 256) for i in range(length, -1, -1)]
    #print(data)
    result = device.write(0x01, bytearray(data), timeout=1000)
    #print(f"BULK OUT: {result}")

    #time.sleep(0.1)

    # test bulk IN request
    result = device.read(0x81, length, timeout=1000)
    print(f"BULK IN: {len(result)} bytes {result}")


if __name__ == "__main__":
    main()
