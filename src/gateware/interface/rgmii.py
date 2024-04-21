from amaranth import *


# - module: RxRgmii -----------------------------------------------------------

class RxRgmii(Elaboratable):
    def __init__(self, rx_control_in, rx_data_in, rx_delay=2e-9):
        # inputs
        self.rx_control_in = rx_control_in
        self.rx_data_in    = rx_data_in

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
            i_A         = self.rx_control_in,
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
                i_A         = self.rx_data_in[bit],
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
