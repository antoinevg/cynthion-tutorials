## step 1: pass-through

    python -m examples.i2s.step-1


## step 2: audio output

### I2S Format:

* Low:    Left
* Sample: Falling
* Shift:  One
* First:  MSB
* Align:  Left
* Bits:   24
* Format: Two's complement



## step 3: audio input

What to do with it though? simple vu-meter using the user led's?



## Links

* Buzzer example
  - https://github.com/kbob/nmigen-examples/blob/master/apps/buzzer/buzzer.py
* icebreaker-synth
  - https://github.com/kbob/icebreaker-synth/tree/master
* Eurorack PMOD - USB Soundcard
  - https://github.com/apfelaudio/eurorack-pmod-usb-soundcard
