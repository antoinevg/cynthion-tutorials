## step 1: pass-through

Simple example that just connects sdi to sdo.

    python -m examples.i2s.step-1

## step 2: audio output

Outputs an NCO via I2sTransmitter.

### I2S Format:

* Low:    Left
* Sample: Falling
* Shift:  One
* First:  MSB
* Align:  Left
* Bits:   24
* Format: Two's complement


## step 3: audio input

Pass-through example that outputs data received on I2sReceiver to I2sTransmitter.



## Links

* Buzzer example
  - https://github.com/kbob/nmigen-examples/blob/master/apps/buzzer/buzzer.py
* icebreaker-synth
  - https://github.com/kbob/icebreaker-synth/tree/master
* Eurorack PMOD - USB Soundcard
  - https://github.com/apfelaudio/eurorack-pmod-usb-soundcard
