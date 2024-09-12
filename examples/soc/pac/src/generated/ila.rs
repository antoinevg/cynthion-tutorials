#[repr(C)]
#[doc = "Register block"]
pub struct RegisterBlock {
    control: CONTROL,
    _reserved1: [u8; 0x03],
    trace: TRACE,
}
impl RegisterBlock {
    #[doc = "0x00 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn control(&self) -> &CONTROL {
        &self.control
    }
    #[doc = "0x04 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn trace(&self) -> &TRACE {
        &self.trace
    }
}
#[doc = "control (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`control::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`control::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@control`]
module"]
#[doc(alias = "control")]
pub type CONTROL = crate::Reg<control::CONTROL_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod control;
#[doc = "trace (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`trace::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`trace::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@trace`]
module"]
#[doc(alias = "trace")]
pub type TRACE = crate::Reg<trace::TRACE_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod trace;
