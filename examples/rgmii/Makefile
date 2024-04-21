cynthion:
	@rm -rf build/
	LUNA_PLATFORM="cynthion.gateware.platform:CynthionPlatformRev1D2" python ./step-1.py --keep-files

ecpix5:
	@rm -rf build/
	LUNA_PLATFORM="tutorials.gateware.platform.ecpix5:ECPIX585Rev03Platform" python ./step-1.py --keep-files

load:
	#apollo configure build/top.bit
	openFPGALoader -c ft4232 -m build/top.bit
