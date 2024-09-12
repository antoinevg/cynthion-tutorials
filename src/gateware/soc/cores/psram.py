#
# This file is part of LUNA.
#
# Copyright (c) 2020-2024 Great Scott Gadgets <info@greatscottgadgets.com>
# Copyright (c) 2024 S. Holzapfel, apfelaudio UG <info@apfelaudio.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from amaranth             import *
from amaranth.lib         import wiring
from amaranth.lib.wiring  import In, flipped
from amaranth.utils       import exact_log2

from amaranth_soc         import wishbone
from amaranth_soc.memory  import MemoryMap

from ...interface.psram   import HyperRAMDQSInterface, HyperRAMDQSPHY

class Peripheral(wiring.Component):

    """
    Wishbone PSRAM peripheral with burst support.
    """

    def __init__(self, *, size, data_width=32, granularity=8, name="psram"):
        if not isinstance(size, int) or size <= 0 or size & size-1:
            raise ValueError("Size must be an integer power of two, not {!r}"
                             .format(size))
        if size < data_width // granularity:
            raise ValueError("Size {} cannot be lesser than the data width/granularity ratio "
                             "of {} ({} / {})"
                              .format(size, data_width // granularity, data_width, granularity))

        self.size        = size
        self.granularity = granularity
        self.name        = name
        self.mem_depth   = (size * granularity) // data_width

        # memory map
        memory_map = MemoryMap(addr_width=exact_log2(size), data_width=granularity)
        memory_map.add_resource(name=("memory", self.name,), size=size, resource=self)

        # bus
        super().__init__({
            "bus": In(wishbone.Signature(addr_width=exact_log2(self.mem_depth),
                                         data_width=data_width,
                                         granularity=granularity,
                                         features={"cti", "bte"})),
        })
        self.bus.memory_map = memory_map

        # phy and controller
        #self.psram_phy = None
        #self.psram     = None
        self.psram_phy = HyperRAMDQSPHY(bus=None)
        self.psram = psram = HyperRAMDQSInterface(phy=self.psram_phy.phy)


        # debug signals
        self.debug_wb = Signal(8)
        self.debug_io = Signal(2)


    def elaborate(self, platform):
        m = Module()

        # phy and controller
        psram_bus = platform.request('ram', dir={'rwds':'-', 'dq':'-', 'cs':'-'})
        #self.psram_phy = HyperRAMDQSPHY(bus=psram_bus)
        #self.psram = psram = HyperRAMDQSInterface(phy=self.psram_phy.phy)
        self.psram_phy.bus = psram_bus
        psram = self.psram
        m.submodules += [self.psram_phy, self.psram]

        m.d.comb += [
            psram.single_page     .eq(0),
            psram.register_space  .eq(0),
            psram.perform_write   .eq(self.bus.we),
        ]

        # debug
        ready_go  = Signal()
        state_go  = Signal()
        m.d.comb += ready_go .eq(self.bus.cyc & self.bus.stb & psram.idle)

        with m.FSM() as fsm:
            m.d.comb += state_go   .eq(fsm.ongoing("GO")) # debug

            with m.State('IDLE'):
                with m.If(self.bus.cyc & self.bus.stb & psram.idle):
                    m.d.sync += [
                        psram.start_transfer          .eq(1),
                        psram.write_data              .eq(self.bus.dat_w),
                        psram.write_mask              .eq(~self.bus.sel),
                        psram.address                 .eq(self.bus.adr << 1),
                    ]
                    m.next = 'GO'
            with m.State('GO'):
                m.d.sync += psram.start_transfer      .eq(0),
                with m.If(self.bus.cti != wishbone.CycleType.INCR_BURST):
                    m.d.comb += psram.final_word      .eq(1)
                with m.If(psram.read_ready | psram.write_ready):
                    m.d.comb += [
                        self.bus.dat_r         .eq(psram.read_data),
                        self.bus.ack           .eq(1),
                    ]
                    m.d.sync += [
                        psram.write_data              .eq(self.bus.dat_w),
                        psram.write_mask              .eq(~self.bus.sel),
                    ]
                    with m.If(self.bus.cti != wishbone.CycleType.INCR_BURST):
                        m.d.comb += psram.final_word  .eq(1)
                        m.next = 'IDLE'

        # debug
        bus = self.bus
        m.d.comb += [
            #self.debug_wb[0:4]  .eq(psram.address),
            self.debug_wb[0:4]  .eq(psram.write_data),
            self.debug_wb[4:8]  .eq(psram.write_mask),

            self.debug_io[0]   .eq(ready_go),
            self.debug_io[1]   .eq(state_go),
            #self.debug_io[1]   .eq(ClockSignal("sync")),
        ]

        return m
