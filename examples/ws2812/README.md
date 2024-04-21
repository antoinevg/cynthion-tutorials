## Step 1: Hello LED Matrix

Our final design looks something like this:

    | Framebuffer -> WS2812 -> serial_out | -> | PMOD |



## Step 2: Program LED Matrix from USB

Next, if we want to be able to program it externally we need an interface to the framebuffer.

We could go with a register-based interface and treat each framebuffer location as a register:

    | USB | -> | VENDOR set <framebuffer_address> <value> | -> | Framebuffer -> ... | -> | PMOD |

The advantage here is that we could set led's separately.

Problem is that framebuffer values are 24 bits wide but vendor requests only give us 16 bits each for index and value.

We could take the first 8 bits of the index as the address and combine the other 8 with value which will give us 24 bits but then we could only address a maximum of 255 leds this way.

Yet another option would be to do 3 requests for each led but that would get tired easily!

So what else could we do?

TODO See: /Users/antoine/GreatScott/luna.git/examples/usb/vendor_request.py

Well, vendor requests can also carry a data payload (check, can luna vendor requests do multiple data stages to give us > 64 bytes of data?) so how about:

    | USB | -> | VENDOR write <ws2812_address> <framebuffer_offset> {payload} | -> | Framebuffer -> ... | -> | PMOD |

So we will basically need something like:

1. A wishbone interface to the WS2812's framebuffer
2. When we get the vendor request with the WS2812's framebuffer address (and offset?)
3. We select the starting address for the wishbone interface
3. for each byte of the payload
  a) write it to the framebuffer
  b) increment the starting address

We should also write an interface that allows us to read the framebuffer from the host.

### Why not bulk endpoint?





-------------------------------------------------------------------------------

## Links

* https://nathanpetersen.com/2020/07/17/designing-a-firmware-driver-for-serially-addressable-leds-for-xilinx-zynq-7000/
* https://github.com/mattvenn/ws2812-core
* https://natsfr.wordpress.com/2017/01/21/fpga-overkill-ws2812-axi-controller-enlight-your-zynq/


## References

Suggestion to use "PWEB (Pulse Width Encoded Bits)": https://electronics.stackexchange.com/questions/145714/what-encoding-is-used-in-this-signal
