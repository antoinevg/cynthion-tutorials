import time
import errno


import usb
from datetime import datetime
from enum import IntEnum, IntFlag

from amaranth                          import Signal, Elaboratable, Module
from amaranth.build.res                import ResourceError
from usb_protocol.emitters             import DeviceDescriptorCollection
from usb_protocol.types                import USBRequestType

from luna.usb2                         import USBDevice, USBStreamInEndpoint
from luna                              import top_level_cli

from luna.gateware.usb.request.control import ControlRequestHandler
from luna.gateware.usb.stream          import USBInStreamInterface
from luna.gateware.stream.generator    import StreamSerializer
from luna.gateware.utils.cdc           import synchronize
from luna.gateware.interface.ulpi      import UTMITranslator

import cynthion
USB_VENDOR_ID  = cynthion.shared.usb.bVendorId.cynthion
USB_PRODUCT_ID = cynthion.shared.usb.bProductId.cynthion

BULK_ENDPOINT_NUMBER  = 1
BULK_ENDPOINT_ADDRESS = 0x80 | BULK_ENDPOINT_NUMBER
MAX_BULK_PACKET_SIZE  = 512


class StreamBridge(Elaboratable):

    def __init__(self):
        self.stream_ep = USBStreamInEndpoint(
            endpoint_number=BULK_ENDPOINT_NUMBER,
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
                    e.bEndpointAddress = BULK_ENDPOINT_ADDRESS
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

        # Add a stream endpoint to our device.
        usb.add_endpoint(self.stream_ep)

        m.d.comb += [
            # Connect device
            usb.connect                 .eq(1),
        ]

        # Return our elaborated module.
        return m
