from amaranth import *


# - module: RxRgmii -----------------------------------------------------------

class RxRgmii(Elaboratable):
    def __init__(self, pad_rx_control, pads_rx_data, rx_delay=2e-9):
        # pads
        self.pad_rx_control = pad_rx_control
        self.pads_rx_data   = pads_rx_data

        # clock phase shift
        self.rx_delay_taps = int(rx_delay/25e-12) # ~25ps per tap
        assert self.rx_delay_taps < 128

        # outputs
        self.rx_control_out = Signal(2)
        self.rx_data_out    = Signal(8)

    def elaborate(self, platform):
        m = Module()

        # - rx_control --

        rx_control_phi = Signal() # phase shifted rx_control signal

        m.submodules += Instance(
            "DELAYG",   # shift phase of control signal to align with eth_rx clock edge
            p_DEL_MODE  = "SCLK_ALIGNED",
            p_DEL_VALUE = self.rx_delay_taps,
            i_A         = self.pad_rx_control,
            o_Z         = rx_control_phi,
        )

        # TODO try out platform.get_iddr(sclk, d, q0, q1)
        m.submodules += Instance(
            "IDDRX1F", # read two bits at a time at double data rate
            i_SCLK = ClockSignal("eth_rx"),
            i_RST  = Const(0),
            i_D    = rx_control_phi,
            o_Q0   = self.rx_control_out[0],
            o_Q1   = self.rx_control_out[1],
        )

        # - rx_data --

        rx_data_phi = Signal(4) # phase shifted rx_data signal
        for bit in range(4):
            m.submodules += Instance(
                "DELAYG", # shift phase of data signal to align with eth_rx clock edge
                p_DEL_MODE  = "SCLK_ALIGNED",
                p_DEL_VALUE = self.rx_delay_taps,
                i_A         = self.pads_rx_data[bit],
                o_Z         = rx_data_phi[bit],
            )

            m.submodules += Instance(
                "IDDRX1F", # read two bits at a time at double data rate
                i_SCLK = ClockSignal("eth_rx"),
                i_RST  = Const(0),
                i_D    = rx_data_phi[bit],
                o_Q0   = self.rx_data_out[bit],
                o_Q1   = self.rx_data_out[bit + 4],
            )

        return m


# - module: TxRgmii -----------------------------------------------------------

class TxRgmii(Elaboratable):
    def __init__(self, pad_tx_control, tx_data_in, tx_delay=2e-9):
        # pads
        self.pad_tx_control = pad_tx_control
        self.pads_tx_data   = pads_tx_data

        # clock phase shift
        self.tx_delay_taps = int(tx_delay/25e-12) # ~25ps per tap
        assert self.tx_delay_taps < 128

        # inputs
        self.tx_control_in = Signal(2)
        self.tx_data_in    = Signal(8)


    def elaborate(self, platform):
        m = Module()

        # - tx_control --

        tx_control_phi = Signal() # phase shifted tx_control signal

        # TODO try out platform.get_oddr()
        m.submodules += Instance(
            "ODDRX1F", # write two bits at a time at double data rate
            i_SCLK = ClockSignal("eth_tx"),
            i_RST  = Const(0),
            i_D0   = self.tx_control_in[0],
            i_D1   = self.tx_control_in[1],
            o_Q    = tx_control_phi,
        )

        m.submodules += Instance(
            "DELAYG",   # shift phase of control signal to align with eth_tx clock edge
            p_DEL_MODE  = "SCLK_ALIGNED",
            p_DEL_VALUE = self.tx_delay_taps,
            i_A         = tx_control_phi,
            o_Z         = self.pads_tx_control,
        )


        # - tx_data --

        tx_data_phi = Signal(4) # phase shifted tx_data signal

        for bit in range(4):
            m.submodules += Instance(
                "ODDRX1F", # write two bits at a time at double data rate
                i_SCLK = ClockSignal("eth_tx"),
                i_RST  = Const(0),
                i_D0   = self.tx_data_in[bit],
                i_D1   = self.tx_data_in[bit + 4],
                o_Q    = tx_data_phi[bit],
            )

            m.submodules += Instance(
                "DELAYG", # shift phase of data signal to align with eth_tx clock edge
                p_DEL_MODE  = "SCLK_ALIGNED",
                p_DEL_VALUE = self.tx_delay_taps,
                i_A         = tx_data_phi[bit],
                o_Z         = self.pads_tx_data[bit],
            )

        return m
