# UAC

## Run UAC Example

    python ./examples/uac/usb2.py


### UAC Links

* https://www.youtube.com/watch?v=wn71QBApCRg -- FM => PCM ftw!

## Integer formats

* https://www.geeksforgeeks.org/different-ways-to-represent-signed-integer/
* https://www.youtube.com/watch?v=UtbA3yM3TWA

### Sign Magnitude

* MSB is a sign bit with 0 representing positive and 1 negative.
* e.g. 0100_0001 =  65
* e.g. 1100_0001 = -65
* NB: 0000_0000 = 0, 1000_0000 = -0 !
* Can't add easily in hardware, as we need to check the sign bit with every operation

### 1's Complement

* MSB is the sign bit, 0 positive, 1 negative
* For positive integers: value is magnitude of LSB pattern
* For negative integers: value is the inverse of LSB pattern
* e.g. 0100_0001 =  65
* e.g. 1011_1110 = -65
  - ~.100_0001 = .011_1110
* NB: 0000_0000 = 0, 1111_1111 = -0 !

### 2's Complement

* MSB is the sign bit, 0 positive, 1 negative
* For positive integers: value is magnitude of LSB pattern
* For negative integers: value is the inverse of LSB pattern + 1
* e.g. 0100_0001 =  65
* e.g. 1011_1111 = -65
  - ~.100_0001 = .011_1110 + 1
* Only one zero
* We gain one extra digit in the negative range (-0 becomes -128 for 8 bits)
* Numbers retain cyclic order: after 0b0111_1111 = 127 we have 0b1000_0000 = -128
* addition is simple in hardware
* 2's complement is reversible, just do it again
* ORIGIN STORY: If we add a number with its negative the result should be zero:
      0100_0001 =  65
      1011_1111 = -65
    -----------------
  = 1_0000_0000 = 0 (discard overflow)
* Casting to larger register size is easy:
  Pad new destination bits with MSB of old bits

## Descriptors

=> DeviceDescriptor
     0x1209/0x0001
     LUNA
     USB Audio Class 2 Device Example

   => ConfigurationDescriptor
      => InterfaceAssociationDescriptor
         bInterfaceCount = 3
      => StandardAudioControlInterfaceDescriptor
         bInterfaceNumber = 0
      => Interface #0 - Audio/Control ClassSpecificAudioControlInterfaceDescriptor
         => #1 Clock Source
         => #2 InputTerminal   USB Streaming
         => #3 OutputTerminal  Speaker
         => #4 InputTerminal   Microphone
         => #5 OutputTerminal  USB Streaming
      => Interface #1 - Audio/Streaming
      => Interface #1 - Audio/Streaming (#1)
         => Endpoint 0x01 OUT  -- audio from host
         => Endpoint 0x81 IN   -- feedback
      => Interface #2 - Audio/Streaming
      => Interface #2 - Audio/Streaming (#1)
         => Endpoint 0x82 IN   -- audio to host
