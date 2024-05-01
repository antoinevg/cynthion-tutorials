from amaranth               import Signal, Elaboratable, Module
from amaranth.build.res     import ResourceError
from usb_protocol.emitters  import DeviceDescriptorCollection

from luna.usb2              import USBDevice
from luna.usb2              import USBStreamInEndpoint, USBStreamOutEndpoint

import cynthion


USB_VENDOR_ID  = cynthion.shared.usb.bVendorId.cynthion
USB_PRODUCT_ID = cynthion.shared.usb.bProductId.cynthion

BULK_OUT_ENDPOINT_NUMBER  = 1
BULK_OUT_ENDPOINT_ADDRESS = BULK_OUT_ENDPOINT_NUMBER
BULK_IN_ENDPOINT_NUMBER   = 1
BULK_IN_ENDPOINT_ADDRESS  = 0x80 | BULK_IN_ENDPOINT_NUMBER
MAX_BULK_PACKET_SIZE  = 512


class StreamBridge(Elaboratable):

    def __init__(self):
        self.stream_in = USBStreamInEndpoint(
            endpoint_number=BULK_IN_ENDPOINT_NUMBER,
            max_packet_size=MAX_BULK_PACKET_SIZE
        )
        self.stream_out = USBStreamOutEndpoint(
            endpoint_number=BULK_OUT_ENDPOINT_NUMBER,
            max_packet_size=MAX_BULK_PACKET_SIZE
        )


    def create_descriptors(self):
        descriptors = DeviceDescriptorCollection()

        # device descriptor
        with descriptors.DeviceDescriptor() as d:
            d.idVendor           = USB_VENDOR_ID
            d.idProduct          = USB_PRODUCT_ID

            d.iManufacturer      = "Great Scott Gadgets"
            d.iProduct           = "Cynthion Stream Bridge"
            d.iSerialNumber      = "[autodetect serial here]"
            d.bcdDevice          = 0.02

            d.bNumConfigurations = 1


        # configuration descriptor
        with descriptors.ConfigurationDescriptor() as c:

            with c.InterfaceDescriptor() as i:
                i.bInterfaceNumber = 0

                with i.EndpointDescriptor() as e:
                    e.bEndpointAddress = BULK_IN_ENDPOINT_ADDRESS
                    e.wMaxPacketSize   = MAX_BULK_PACKET_SIZE

        return descriptors


    def elaborate(self, platform):
        m = Module()

        # Create our USB uplink interface...
        # TODO pass this in via constructor
        try:
            ulpi = platform.request("aux_phy")   # cynthion
        except:
            ulpi = platform.request("ulpi")      # ecpix5
        m.submodules.usb = usb = USBDevice(bus=ulpi)

        # Add our standard control endpoint to the device.
        descriptors = self.create_descriptors()
        control_endpoint = usb.add_standard_control_endpoint(descriptors)

        # Add stream endpoints to our device.
        usb.add_endpoint(self.stream_in)
        usb.add_endpoint(self.stream_out)

        m.d.comb += [
            # Connect device
            usb.connect                 .eq(1),
        ]

        # Return our elaborated module.
        return m
