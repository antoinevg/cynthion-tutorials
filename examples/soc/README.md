## Notes

Build gateware:

    python -m examples.soc.top --dry-run --output top.bit
    apollo configure ./top.bit
    # _or_
    cynthion run --bitstream ./top.bit


Run firmware:

    # start openocd
    openocd -f ./.cargo/openocd-jtag+serial.cfg

    # run firmware
    cargo run --release --example irq



## Architecture

- Top
  - Soc
    - wb_arbiter <-> wb_decoder
      - cpu.ibus
      - cpu.dbus
    - wb_decoder <-> wb_arbiter
      - mainram
      - wb_to_csr
        - csr_decoder
          - leds
          - gpio0
