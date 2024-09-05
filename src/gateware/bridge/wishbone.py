import os

from amaranth                           import Elaboratable, Module, Signal, Cat
from amaranth.lib.wiring                import Out, Signature, connect

from amaranth_soc                       import csr, wishbone
from amaranth_soc.csr.wishbone          import WishboneCSRBridge

from usb_protocol.emitters              import DeviceDescriptorCollection
from usb_protocol.types                 import USBRequestType

from luna.usb2                          import USBDevice, USBStreamInEndpoint, USBStreamOutEndpoint
from luna.gateware.stream.generator     import StreamSerializer
from luna.gateware.usb.request.control  import ControlRequestHandler
from luna.gateware.usb.usb2.transfer    import USBInStreamInterface

import cynthion

class VendorRequestHandler(ControlRequestHandler):
    REQUEST_READ_REG   = 0
    REQUEST_WRITE_REG  = 1
    REQUEST_READ_MEM   = 2
    REQUEST_WRITE_MEM  = 3

    def __init__(self):
        super().__init__()
        self.signature = Signature({
            "bus": Out(wishbone.Signature(addr_width=8, data_width=16))
        }).create()
        self.bus = self.signature.bus

    def elaborate(self, platform):
        m = Module()

        interface = self.interface
        setup     = self.interface.setup
        read_data = Signal.like(self.bus.dat_r)

        # Handler for read register requests.
        m.submodules.transmitter = transmitter = \
            StreamSerializer(data_length=2, domain="usb", stream_type=USBInStreamInterface, max_length_width=2)

        with m.If(setup.type == USBRequestType.VENDOR):
            if hasattr(interface, "claim"):
                m.d.comb += interface.claim.eq(1)

            with m.FSM(domain="usb"):
                # wait for control request
                with m.State("IDLE"):
                    with m.If(setup.received):
                        with m.Switch(setup.request):
                            with m.Case(VendorRequestHandler.REQUEST_READ_REG):
                                m.d.usb += [
                                    self.bus.cyc                .eq(1),
                                    self.bus.stb                .eq(1),
                                    self.bus.we                 .eq(0),
                                    self.bus.sel                .eq(1),
                                    self.bus.adr                .eq(setup.index),
                                ]
                                m.next = "READ_REG_WAIT_FOR_ACK"
                            with m.Case(VendorRequestHandler.REQUEST_WRITE_REG):
                                m.d.usb += [
                                    self.bus.cyc                .eq(1),
                                    self.bus.stb                .eq(1),
                                    self.bus.we                 .eq(1),
                                    self.bus.sel                .eq(1),
                                    self.bus.adr                .eq(setup.index),
                                    self.bus.dat_w              .eq(setup.value),
                                ]
                                m.next = "WRITE_REG_WAIT_FOR_ACK"
                            with m.Case(VendorRequestHandler.REQUEST_READ_MEM):
                                m.d.usb += [
                                    self.bus.cyc                .eq(1),
                                    self.bus.stb                .eq(1),
                                    self.bus.we                 .eq(0),
                                    self.bus.sel                .eq(1),
                                    self.bus.adr                .eq(Cat(setup.index, setup.value)),
                                ]
                                m.next = "READ_MEM_WAIT_FOR_ACK"
                            with m.Case(VendorRequestHandler.REQUEST_WRITE_MEM):
                                m.d.usb += [
                                    self.bus.cyc                .eq(1),
                                    self.bus.stb                .eq(1),
                                    self.bus.we                 .eq(1),
                                    self.bus.sel                .eq(1),
                                    self.bus.adr                .eq(Cat(setup.index, setup.value)),
                                ]
                                m.next = "WRITE_MEM_WAIT_FOR_ACK"
                            with m.Default():
                                m.next = "UNHANDLED"

                # wait for bus ack
                with m.State("READ_REG_WAIT_FOR_ACK"):
                    with m.If(self.bus.ack):
                        m.d.usb += [
                            self.bus.cyc    .eq(0),
                            self.bus.stb    .eq(0),
                            read_data       .eq(self.bus.dat_r),
                        ]
                        m.next = "READ_REG_FINISH"
                with m.State("WRITE_REG_WAIT_FOR_ACK"):
                    with m.If(self.bus.ack):
                        m.d.usb += [
                            self.bus.cyc    .eq(0),
                            self.bus.stb    .eq(0),
                        ]
                        m.next = "WRITE_REG_FINISH"
                with m.State("READ_MEM_WAIT_FOR_ACK"):
                    with m.If(self.bus.ack):
                        m.d.usb += [
                            self.bus.cyc    .eq(0),
                            self.bus.stb    .eq(0),
                            read_data       .eq(self.bus.dat_r),
                        ]
                        m.next = "READ_MEM_FINISH"
                with m.State("WRITE_MEM_WAIT_FOR_ACK"):
                    with m.If(self.bus.ack):
                        m.d.usb += [
                            self.bus.cyc    .eq(0),
                            self.bus.stb    .eq(0),
                        ]
                        m.next = "WRITE_MEM_FINISH"

                # handle control request
                with m.State("READ_REG_FINISH"):
                    self.handle_simple_data_request(m, transmitter, read_data, length=len(read_data)//8)

                with m.State("WRITE_REG_FINISH"):
                    # provide an response to the STATUS stage.
                    with m.If(interface.status_requested):
                        m.d.comb += self.send_zlp()
                        m.next = "IDLE"

                with m.State("READ_MEM_FINISH"):
                    self.handle_simple_data_request(m, transmitter, read_data, length=len(read_data)//8)

                with m.State("WRITE_MEM_FINISH"):
                    # receive control data
                    with m.If(interface.rx.valid & interface.rx.next):
                        payload = interface.rx.payload

                    # once the receive is complete, respond with an ack
                    with m.If(interface.rx_ready_for_response):
                        m.d.comb += interface.handshakes_out.ack.eq(1)

                    # when we reach the status stage send a zlp
                    with m.If(interface.status_requested):
                        m.d.comb += self.send_zlp()
                        m.next = "IDLE"

                with m.State("UNHANDLED"):
                    # stall unhandled requests.
                    with m.If(interface.status_requested | interface.data_requested):
                        m.d.comb += interface.handshakes_out.stall.eq(1)
                        m.next = "IDLE"

        return m


class WishboneBridge(Elaboratable):
    BULK_ENDPOINT_NUMBER = 1
    MAX_BULK_PACKET_SIZE = 512

    def __init__(self):
        self.vendor_request_handler = VendorRequestHandler()

        self.stream_in = USBStreamInEndpoint(
            endpoint_number=self.BULK_ENDPOINT_NUMBER,
            max_packet_size=self.MAX_BULK_PACKET_SIZE
        )
        self.stream_out = USBStreamOutEndpoint(
            endpoint_number=self.BULK_ENDPOINT_NUMBER,
            max_packet_size=self.MAX_BULK_PACKET_SIZE
        )


    def create_descriptors(self):
        """ Create the descriptors we want to use for our device. """

        descriptors = DeviceDescriptorCollection()

        #
        # We'll add the major components of the descriptors we want.
        # The collection we build here will be necessary to create a standard endpoint.
        #

        # We'll need a device descriptor...
        with descriptors.DeviceDescriptor() as d:
            d.idVendor           = cynthion.shared.usb.bVendorId.example
            d.idProduct          = cynthion.shared.usb.bProductId.example

            d.iManufacturer      = "Great Scott Gadgets"
            d.iProduct           = "Cynthion Wishbone Bridge"
            d.iSerialNumber      = "no serial"

            d.bNumConfigurations = 1

        # ... and a description of the USB configuration we'll provide.
        with descriptors.ConfigurationDescriptor() as c:

            with c.InterfaceDescriptor() as i:
                i.bInterfaceNumber = 0

                # Bulk IN to host (tx, from our side)
                with i.EndpointDescriptor() as e:
                    e.bEndpointAddress = 0x80 | self.BULK_ENDPOINT_NUMBER
                    e.wMaxPacketSize   = self.MAX_BULK_PACKET_SIZE

                # Bulk OUT from host (rx, from our side)
                with i.EndpointDescriptor() as e:
                    e.bEndpointAddress = self.BULK_ENDPOINT_NUMBER
                    e.wMaxPacketSize   = self.MAX_BULK_PACKET_SIZE

        return descriptors


    def elaborate(self, platform):
        m = Module()

        # Create our USB device interface...
        ulpi = platform.request("target_phy")
        m.submodules.usb = usb = USBDevice(bus=ulpi)

        # Add our standard control endpoint to the device.
        descriptors = self.create_descriptors()
        control_ep = usb.add_standard_control_endpoint(descriptors)

        # Add our vendor request handler.
        #vendor_request_handler = VendorRequestHandler()
        control_ep.add_request_handler(self.vendor_request_handler)

        # Add a stream IN endpoint to our device.
        usb.add_endpoint(self.stream_in)

        # Always generate a monotonic count for our IN stream, which
        # counts every time our stream endpoint accepts a data byte.
        # counter = Signal(8)
        # with m.If(self.stream_in.stream.ready):
        #     m.d.usb += counter.eq(counter + 1)
        # m.d.comb += [
        #     self.stream_in.stream.valid    .eq(1),
        #     self.stream_in.stream.payload  .eq(counter)
        # ]

        # Add a stream OUT endpoint to our device.
        usb.add_endpoint(self.stream_out)

        # Where shall we stream this? Or shall we let the caller connect to this?
        # with m.If(stream_ep.stream.valid):
        #     m.d.usb += [
        #         leds     .eq(stream_ep.stream.payload),
        #         user_io  .eq(stream_ep.stream.payload),
        #     ]
        # # Always accept data as it comes in.
        # m.d.comb += stream_ep.stream.ready.eq(1)

        # Connect our device as a high speed device by default.
        m.d.comb += [
            usb.connect          .eq(1),
            usb.full_speed_only  .eq(1 if os.getenv('LUNA_FULL_ONLY') else 0),
        ]

        return m
