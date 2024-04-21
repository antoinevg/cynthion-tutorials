import io, logging, os, signal, sys, traceback, unittest

import dpkt
import usb1

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import IP, Ether

from luna import configure_default_logging

from pygreat.comms_backends.usb1 import USB1CommsBackend as backend
from pygreat.errors import DeviceNotFoundError

import cynthion

VENDOR_ID  = cynthion.shared.usb.bVendorId.cynthion
PRODUCT_ID = cynthion.shared.usb.bProductId.cynthion

BULK_ENDPOINT_NUMBER  = 1
BULK_ENDPOINT_ADDRESS = 0x80 | BULK_ENDPOINT_NUMBER
MAX_BULK_PACKET_SIZE  = 4096


# - PacketParser --------------------------------------------------------------

def parse_packet(packet):
    header   = int.from_bytes(packet[0:2], byteorder="little")
    preamble = packet[2:9] # 0x55 0x55 0x55 0x55 0x55 0x55 0xD5
    packet = packet[9:]
    prefix = f"{header - 7} bytes\t"

    # - scapy --
    #ip = IP(packet)
    #logging.info(f"{prefix}: {ip}")
    #ip.hide_defaults()
    #ip.show()
    #logging.info(f"{prefix}: {ip.fields}")
    #logging.info(f"{prefix}: {ip.src} => {ip.dst}")
    #ip.show2()

    ether = Ether(packet)
    logging.info(f"{prefix}: {ether}")
    #ether.hide_defaults()
    #ether.show2()

    # - dpkt --
    # https://dpkt.readthedocs.io/en/latest/print_packets.html

    # ethertype: https://en.wikipedia.org/wiki/EtherType

    #ethernet = dpkt.ethernet.Ethernet(packet)
    #logging.info(f"{prefix}: {mac_addr(ethernet.src)} > {mac_addr(ethernet.dst)} ({hex(ethernet.type)})")

    #if isinstance(ethernet.data, dpkt.ip.IP):
    #    ip = ethernet.data
    #    logging.info(f"    IP: {inet_to_str(ip.src)} > {inet_to_str(ip.dst)}")


def mac_addr(address):
    """Convert a MAC address to a readable/printable string

       Args:
           address (str): a MAC address in hex form (e.g. '\x01\x02\x03\x04\x05\x06')
       Returns:
           str: Printable/readable MAC address
    """
    from dpkt.compat import compat_ord
    return ':'.join('%02x' % compat_ord(b) for b in address)


def inet_to_str(inet):
    """Convert inet object to a string

        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    import socket

    # first try ipv4 and then ipv6
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)


# - PacketBuffer --------------------------------------------------------------

class PacketBuffer:
    def __init__(self, delimiter):
        self.delimiter = delimiter
        self.buffer = bytearray()

    def append(self, packet):
        self.buffer += bytearray(packet)

    def next(self):
        while True:
            packet = self._readuntil(self.delimiter)
            if not packet:
                return None
            return packet

    def _readuntil(self, pattern):
        buffer_len  = len(self.buffer)
        pattern_len = len(pattern)
        offset = 0

        while offset < buffer_len - pattern_len:
            if pattern == self.buffer[offset:pattern_len+offset]:
                packet = bytes(self.buffer[0:offset])
                self.buffer = self.buffer[pattern_len+offset:]
                return packet
            offset += 1

        return None


# - main ----------------------------------------------------------------------

def transfer_completed(transfer):
    length        = transfer.getActualLength()
    packet_buffer = transfer.getUserData()

    # handle transfer
    if length > 0:
        logging.info(f"bulk read transfer received {length} bytes")

        # append to packet buffer
        response = transfer.getBuffer()
        packet_buffer.append(response)

        # get next packet
        while True:
            packet = packet_buffer.next()
            if packet is None:
                # load more data
                break
            # display packet
            if len(packet) >= 64:
                parse_packet(packet)
                pass
            else:
                logging.error(f"short packet: {len(packet)} -> {list(packet)}")

    # re-submit transfer
    transfer.submit()


def main(context, device_handle):
    # packet buffer
    delimiter = bytes([33, 33, 33, 33, 33, 33, 33, 33])
    packet_buffer = PacketBuffer(delimiter)

    # submit transfer
    transfer = device_handle.getTransfer()
    transfer.setBulk(
        endpoint=BULK_ENDPOINT_ADDRESS,
        buffer_or_len=MAX_BULK_PACKET_SIZE,
        callback=transfer_completed,
        user_data=packet_buffer,
        timeout=100
    )
    transfer.submit()

    # poll context event handler
    while True:
        context.handleEvents()


if __name__ == "__main__":
    USB_CONTEXT   = None
    DEVICE_HANDLE = None

    # configure logging
    configure_default_logging(level=os.getenv("LOG_LEVEL", "DEBUG").upper())

    # handle SIGINT
    def sigint(sig, frame):
        print("SIGINT")
        if DEVICE_HANDLE is not None:
            DEVICE_HANDLE.releaseInterface(0)
        if USB_CONTEXT is not None:
            USB_CONTEXT.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, sigint)

    # open USB device
    USB_CONTEXT = usb1.USBContext().open()
    DEVICE_HANDLE = USB_CONTEXT.openByVendorIDAndProductID(VENDOR_ID, PRODUCT_ID)
    if DEVICE_HANDLE is None:
        raise DeviceNotFoundError()
    DEVICE_HANDLE.claimInterface(0)

    main(USB_CONTEXT, DEVICE_HANDLE)
