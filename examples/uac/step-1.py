#!/usr/bin/env python3
#
# This file is part of LUNA.
#
# Copyright (c) 2020 Great Scott Gadgets <info@greatscottgadgets.com>
# SPDX-License-Identifier: BSD-3-Clause

import os

from amaranth                            import Cat, Const, DomainRenamer, Elaboratable, Module, Signal

from usb_protocol.emitters               import DeviceDescriptorCollection
from usb_protocol.emitters.descriptors   import uac2, standard
from usb_protocol.types                  import (
    USBDirection,
    USBRequestRecipient,
    USBRequestType,
    USBStandardRequests,
    USBSynchronizationType,
    USBTransferType,
    USBUsageType,
)
from usb_protocol.types.descriptors.uac2 import AudioClassSpecificRequestCodes

from luna                                import top_level_cli
from luna.usb2                           import USBDevice, USBIsochronousInEndpoint

from luna.gateware.usb.stream            import USBInStreamInterface
from luna.gateware.usb.usb2.endpoints.stream_isochronous import  (
    USBIsochronousOutStreamEndpoint,
    USBIsochronousInStreamEndpoint,
)
from luna.gateware.usb.usb2.request      import USBRequestHandler, StallOnlyRequestHandler
from luna.gateware.stream.generator      import StreamSerializer

from tutorials.gateware.util import NCO


class RequestHandlers(USBRequestHandler):
    """ TODO
    """

    def elaborate(self, platform):
        m = Module()

        interface         = self.interface
        setup             = self.interface.setup

        m.submodules.transmitter = transmitter = \
            StreamSerializer(data_length=14, domain="usb", stream_type=USBInStreamInterface, max_length_width=14)

        #
        # Class request handlers.
        #
        with m.If(setup.type == USBRequestType.STANDARD):
            with m.If((setup.recipient == USBRequestRecipient.INTERFACE) &
                      (setup.request == USBStandardRequests.SET_INTERFACE)):

                # claim interface
                if hasattr(interface, "claim"):
                    m.d.comb += interface.claim.eq(1)

                # Always ACK the data out...
                with m.If(interface.rx_ready_for_response):
                    m.d.comb += interface.handshakes_out.ack.eq(1)

                # ... and accept whatever the request was.
                with m.If(interface.status_requested):
                    m.d.comb += self.send_zlp()

        with m.Elif(setup.type == USBRequestType.CLASS):
            # claim interface
            if hasattr(interface, "claim"):
                m.d.comb += interface.claim.eq(1)

            request_clock_freq = (setup.value == 0x100) & (setup.index == 0x0100)

            with m.Switch(setup.request):
                with m.Case(AudioClassSpecificRequestCodes.RANGE):
                    m.d.comb += transmitter.stream.attach(self.interface.tx)

                    with m.If(request_clock_freq):
                        m.d.comb += [
                            Cat(transmitter.data).eq(
                                Cat(Const(0x1, 16), # no triples
                                    Const(48000, 32), # MIN
                                    Const(48000, 32), # MAX
                                    Const(0, 32))),   # RES
                            transmitter.max_length.eq(setup.length)
                        ]
                    with m.Else():
                        m.d.comb += interface.handshakes_out.stall.eq(1)

                    # ... trigger it to respond when data's requested...
                    with m.If(interface.data_requested):
                        m.d.comb += transmitter.start.eq(1)

                    # ... and ACK our status stage.
                    with m.If(interface.status_requested):
                        m.d.comb += interface.handshakes_out.ack.eq(1)

                with m.Case(AudioClassSpecificRequestCodes.CUR):
                    m.d.comb += transmitter.stream.attach(self.interface.tx)
                    with m.If(request_clock_freq & (setup.length == 4)):
                        m.d.comb += [
                            Cat(transmitter.data[0:4]).eq(Const(48000, 32)),
                            transmitter.max_length.eq(4)
                        ]
                    with m.Else():
                        m.d.comb += interface.handshakes_out.stall.eq(1)

                    # ... trigger it to respond when data's requested...
                    with m.If(interface.data_requested):
                        m.d.comb += transmitter.start.eq(1)

                    # ... and ACK our status stage.
                    with m.If(interface.status_requested):
                        m.d.comb += interface.handshakes_out.ack.eq(1)

                with m.Case():
                    #
                    # Stall unhandled requests.
                    #
                    with m.If(interface.status_requested | interface.data_requested):
                        m.d.comb += interface.handshakes_out.stall.eq(1)

                return m


class USBAudioClass2DeviceExample(Elaboratable):
    """ Simple device the emulates a USB Audio Class 2 Audio Interface.

    Sends a simple stereo sine wave to the host.
    """

    TRANSFERS_PER_MICROFRAME = 104
    SUBSLOT_SIZE = 4
    BIT_RESOLUTION = 24

    def __init__(self):
        pass

    def create_descriptors(self):
        """ Create the descriptors we want to use for our device. """

        descriptors = DeviceDescriptorCollection()

        with descriptors.DeviceDescriptor() as d:
            d.idVendor           = 0x1209 # https://pid.codes/1209/
            d.idProduct          = 0x0001 # pid.codes Test PID 1

            d.iManufacturer      = "LUNA"
            d.iProduct           = "USB Audio Class 2 Device Example"
            d.iSerialNumber      = "no serial"

            d.bDeviceClass       = 0xef # Miscellaneous
            d.bDeviceSubclass    = 0x02 # Interface Association Descriptor
            d.bDeviceProtocol    = 0x01 # Interface Association Descriptor

            d.bNumConfigurations = 1

        with descriptors.ConfigurationDescriptor() as c:

            # - Interface Association --

            # interface association descriptor
            i = uac2.InterfaceAssociationDescriptorEmitter()
            i.bInterfaceCount = 3 # audio control, audio input, audio output
            c.add_subordinate_descriptor(i)

            # standard audio control interface descriptor
            i = uac2.StandardAudioControlInterfaceDescriptorEmitter()
            i.bInterfaceNumber = 0
            c.add_subordinate_descriptor(i)


            # - Interface #0 class-specific audio control interface descriptor --

            i = uac2.ClassSpecificAudioControlInterfaceDescriptorEmitter()

            #   -- 1.CS clock source
            clockSource = uac2.ClockSourceDescriptorEmitter()
            clockSource.bClockID     = 1
            clockSource.bmAttributes = uac2.ClockAttributes.INTERNAL_FIXED_CLOCK
            clockSource.bmControls   = uac2.ClockFrequencyControl.HOST_READ_ONLY
            i.add_subordinate_descriptor(clockSource)

            #   -- 2.IT streaming input port from the host to the USB interface
            inputTerminal               = uac2.InputTerminalDescriptorEmitter()
            inputTerminal.bTerminalID   = 2
            inputTerminal.wTerminalType = uac2.USBTerminalTypes.USB_STREAMING
            inputTerminal.bNrChannels   = 2
            inputTerminal.bCSourceID    = 1
            i.add_subordinate_descriptor(inputTerminal)

            #   -- 3.OT audio output port from the USB interface to the outside world
            outputTerminal               = uac2.OutputTerminalDescriptorEmitter()
            outputTerminal.bTerminalID   = 3
            outputTerminal.wTerminalType = uac2.OutputTerminalTypes.SPEAKER
            outputTerminal.bSourceID     = 2
            outputTerminal.bCSourceID    = 1
            i.add_subordinate_descriptor(outputTerminal)

            #   -- 4.IT IT audio input port from the outside world to the USB interface
            inputTerminal               = uac2.InputTerminalDescriptorEmitter()
            inputTerminal.bTerminalID   = 4
            inputTerminal.wTerminalType = uac2.InputTerminalTypes.MICROPHONE
            inputTerminal.bNrChannels   = 2
            inputTerminal.bCSourceID    = 1
            i.add_subordinate_descriptor(inputTerminal)

            #   -- 5.OT OT audio output port from the USB interface to the host
            outputTerminal               = uac2.OutputTerminalDescriptorEmitter()
            outputTerminal.bTerminalID   = 5
            outputTerminal.wTerminalType = uac2.USBTerminalTypes.USB_STREAMING
            outputTerminal.bSourceID     = 4
            outputTerminal.bCSourceID    = 1
            i.add_subordinate_descriptor(outputTerminal)
            c.add_subordinate_descriptor(i)


            # - Interface #1 -- host audio output channels descriptor

            #   -- Interface Descriptor (Streaming, OUT, quiet setting)
            quietAudioStreamingInterface                  = uac2.AudioStreamingInterfaceDescriptorEmitter()
            quietAudioStreamingInterface.bInterfaceNumber = 1
            c.add_subordinate_descriptor(quietAudioStreamingInterface)

            #   -- Interface Descriptor (Streaming, OUT, active setting)
            activeAudioStreamingInterface                   = uac2.AudioStreamingInterfaceDescriptorEmitter()
            activeAudioStreamingInterface.bInterfaceNumber  = 1
            activeAudioStreamingInterface.bAlternateSetting = 1
            activeAudioStreamingInterface.bNumEndpoints     = 2
            c.add_subordinate_descriptor(activeAudioStreamingInterface)

            #   -- AudioStreaming Interface Descriptor (General)
            audioStreamingInterface               = uac2.ClassSpecificAudioStreamingInterfaceDescriptorEmitter()
            audioStreamingInterface.bTerminalLink = 2
            audioStreamingInterface.bFormatType   = uac2.FormatTypes.FORMAT_TYPE_I
            audioStreamingInterface.bmFormats     = uac2.TypeIFormats.PCM
            audioStreamingInterface.bNrChannels   = 2
            c.add_subordinate_descriptor(audioStreamingInterface)

            #   -- AudioStreaming Interface Descriptor (Type I)
            typeIStreamingInterface  = uac2.TypeIFormatTypeDescriptorEmitter()
            typeIStreamingInterface.bSubslotSize   = self.SUBSLOT_SIZE
            typeIStreamingInterface.bBitResolution = self.BIT_RESOLUTION
            c.add_subordinate_descriptor(typeIStreamingInterface)

            #   -- Endpoint Descriptor (Audio OUT from host)
            audioOutEndpoint = standard.EndpointDescriptorEmitter()
            audioOutEndpoint.bEndpointAddress     = USBDirection.OUT.to_endpoint_address(1) # EP 0x01 OUT
            audioOutEndpoint.bmAttributes         = USBTransferType.ISOCHRONOUS  | \
                                                    (USBSynchronizationType.ASYNC << 2) | \
                                                    (USBUsageType.DATA << 4)
            audioOutEndpoint.wMaxPacketSize = self.TRANSFERS_PER_MICROFRAME
            audioOutEndpoint.bInterval       = 1
            c.add_subordinate_descriptor(audioOutEndpoint)

            #   -- AudioControl Endpoint Descriptor
            audioControlEndpoint = uac2.ClassSpecificAudioStreamingIsochronousAudioDataEndpointDescriptorEmitter()
            c.add_subordinate_descriptor(audioControlEndpoint)

            #   -- Endpoint Descriptor (Feedback IN)
            feedbackInEndpoint = standard.EndpointDescriptorEmitter()
            feedbackInEndpoint.bEndpointAddress  = USBDirection.IN.to_endpoint_address(1) # EP 0x81 IN
            feedbackInEndpoint.bmAttributes      = USBTransferType.ISOCHRONOUS  | \
                                                   (USBSynchronizationType.NONE << 2)  | \
                                                   (USBUsageType.FEEDBACK << 4)
            feedbackInEndpoint.wMaxPacketSize    = 4
            feedbackInEndpoint.bInterval         = 4
            c.add_subordinate_descriptor(feedbackInEndpoint)


            # - Interface #2 IN -- host audio input channels descriptor

            #   -- Interface Descriptor (Streaming, IN, quiet setting)
            quietAudioStreamingInterface                  = uac2.AudioStreamingInterfaceDescriptorEmitter()
            quietAudioStreamingInterface.bInterfaceNumber = 2
            c.add_subordinate_descriptor(quietAudioStreamingInterface)

            #   -- Interface Descriptor (Streaming, IN, active setting)
            activeAudioStreamingInterface                   = uac2.AudioStreamingInterfaceDescriptorEmitter()
            activeAudioStreamingInterface.bInterfaceNumber  = 2
            activeAudioStreamingInterface.bAlternateSetting = 1
            activeAudioStreamingInterface.bNumEndpoints     = 1
            c.add_subordinate_descriptor(activeAudioStreamingInterface)

            #   -- AudioStreaming Interface Descriptor (General)
            audioStreamingInterface               = uac2.ClassSpecificAudioStreamingInterfaceDescriptorEmitter()
            audioStreamingInterface.bTerminalLink = 5
            audioStreamingInterface.bFormatType   = uac2.FormatTypes.FORMAT_TYPE_I
            audioStreamingInterface.bmFormats     = uac2.TypeIFormats.PCM
            audioStreamingInterface.bNrChannels   = 2
            c.add_subordinate_descriptor(audioStreamingInterface)

            #   -- AudioStreaming Interface Descriptor (Type I)
            typeIStreamingInterface  = uac2.TypeIFormatTypeDescriptorEmitter()
            typeIStreamingInterface.bSubslotSize   = self.SUBSLOT_SIZE
            typeIStreamingInterface.bBitResolution = self.BIT_RESOLUTION
            c.add_subordinate_descriptor(typeIStreamingInterface)

            #   -- Endpoint Descriptor (Audio IN to host)
            audioOutEndpoint = standard.EndpointDescriptorEmitter()
            audioOutEndpoint.bEndpointAddress     = USBDirection.IN.to_endpoint_address(2) # EP 0x82 IN
            audioOutEndpoint.bmAttributes         = USBTransferType.ISOCHRONOUS  | \
                                                    (USBSynchronizationType.ASYNC << 2) | \
                                                    (USBUsageType.DATA << 4)
            audioOutEndpoint.wMaxPacketSize = self.TRANSFERS_PER_MICROFRAME
            audioOutEndpoint.bInterval      = 1
            c.add_subordinate_descriptor(audioOutEndpoint)

            #   -- AudioControl Endpoint Descriptor
            audioControlEndpoint = uac2.ClassSpecificAudioStreamingIsochronousAudioDataEndpointDescriptorEmitter()
            c.add_subordinate_descriptor(audioControlEndpoint)

        return descriptors



    def elaborate(self, platform):
        m = Module()

        # Generate our domain clocks/resets.
        m.submodules.car = platform.clock_domain_generator()

        # Create our USB device interface...
        #ulpi = platform.request(platform.default_usb_connection) # target
        ulpi = platform.request("aux_phy")
        m.submodules.usb = usb = USBDevice(bus=ulpi)

        # Add our standard control endpoint to the device.
        descriptors = self.create_descriptors()
        ep_control = usb.add_control_endpoint()
        ep_control.add_standard_request_handlers(descriptors, blacklist=[
            lambda setup: (setup.type == USBRequestType.STANDARD) &
                          (setup.request == USBStandardRequests.SET_INTERFACE)
        ])

        # Attach our class request handlers.
        ep_control.add_request_handler(RequestHandlers())

        # Attach class-request handlers that stall any vendor or reserved requests,
        # as we don't have or need any.
        stall_condition = lambda setup : \
            (setup.type == USBRequestType.VENDOR) | \
            (setup.type == USBRequestType.RESERVED)
        ep_control.add_request_handler(StallOnlyRequestHandler(stall_condition))

        ep1_out = USBIsochronousOutStreamEndpoint(
            endpoint_number=1, # EP 0x01 OUT - audio from host
            max_packet_size=self.TRANSFERS_PER_MICROFRAME)
        usb.add_endpoint(ep1_out)

        ep1_in = USBIsochronousInEndpoint(
            endpoint_number=1, # EP 0x81 IN - feedback to host
            max_packet_size=4)
        usb.add_endpoint(ep1_in)

        ep2_in = USBIsochronousInStreamEndpoint(
            endpoint_number=2, # EP 2 0x81 IN - audio to host
            max_packet_size=self.TRANSFERS_PER_MICROFRAME)
        usb.add_endpoint(ep2_in)

        # Connect our device as a high speed device.
        m.d.comb += [
            ep1_in.bytes_in_frame.eq(4),  # feedback is 32 bits = 4 bytes
            ep2_in.bytes_in_frame.eq(48), # 2x 24 bit samples = 48 bytes
            ep1_out.stream.ready .eq(1),
            usb.connect          .eq(1),
            usb.full_speed_only  .eq(0),
        ]

        # ep1_in - feedback to host
        feedbackValue = Signal(32)
        bitPos        = Signal(5)
        # 48000 / 2000 = 24 - aka what the actual fuckness are you trying to do here dude?
        m.d.comb += [
            feedbackValue.eq(24 << 14),
            bitPos.eq(ep1_in.address << 3),
            ep1_in.value.eq(0xff & (feedbackValue >> bitPos))
        ]

        # - ep2_in - audio to host --------------------------------------------

        # NCO
        nco = NCO(60000000, bit_depth=24, lut_size=512)
        m.submodules.nco = DomainRenamer({"sync": "usb"})(nco)
        m.d.usb += nco.i_freq_a.eq(220)
        m.d.usb += nco.i_freq_b.eq(440)
        left = nco.o_a
        right = nco.o_b

        # frame counters
        next_channel = Signal()
        next_byte = Signal(2)

        # frame nco data
        #
        # Format is:
        #    00:08  - padding
        #    08:15  - lsb
        #    16:23
        #    24:31  - msb
        frame = Signal(32)
        with m.If(next_channel == 0):
            m.d.comb += frame[8:].eq(left)
        with m.Else():
            m.d.comb += frame[8:].eq(right)

        # stream frame
        m.d.comb += [
            ep2_in.stream.valid.eq(1),
            ep2_in.stream.payload.eq(frame.word_select(next_byte, 8)),
        ]
        with m.If(ep2_in.stream.ready):
            m.d.usb += next_byte.eq(next_byte + 1)
            with m.If(next_byte == 3):
                m.d.usb += next_channel.eq(~next_channel)

        return m


if __name__ == "__main__":
    top_level_cli(USBAudioClass2DeviceExample)
