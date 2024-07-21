SHELL := /bin/zsh

# - firmware -----------------------------------------------------------------

firmware: firmware.bin

firmware.bin: # memory.x
	cargo objcopy --release -- -Obinary firmware.bin


# - generated files -----------------------------------------------------------

svd2rust:
	rm -rf build pac/src/generated.rs pac/src/generated/
	mkdir build

	svd2rust -i soc.svd -o build/ --target riscv --make_mod --ident-formats-theme legacy
	mv build/mod.rs pac/src/generated.rs
	@# TODO uncomment once we no longer have to poly-fill 'target_has_atomic'
	@#		see: https://github.com/rust-lang/rust/issues/94039
	@# mv build/build.rs pac
	mv build/device.x pac

	form -i pac/src/generated.rs -o pac/src/generated/
	mv pac/src/generated/lib.rs pac/src/generated.rs
	cd pac && cargo fmt -- --emit files


memory.x: $(SOC)
	python top.py --generate-memory-x > $@


# - gateware ------------------------------------------------------------------

top: firmware.bin top.py
	python ./top.py --dry-run --output top.bit
	rm firmware.bin


# - helpers -------------------------------------------------------------------

clean:
	-cargo clean
	-rm -rf memory.x firmware.bin top.bit build/

# loads the SoC bitstream onto the FPGA
program: firmware gateware
	-apollo configure top.bit

# loads the SoC bitstream running onto the FPGA and shows the output in a console
run: firmware gateware
	-apollo configure top.bit
	pyserial-miniterm $(UART) 115200
