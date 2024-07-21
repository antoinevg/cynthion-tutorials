#[repr(C)]
#[doc = "Register block"]
pub struct RegisterBlock {
    enable: ENABLE,
    pending: PENDING,
}
impl RegisterBlock {
    #[doc = "0x00 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn enable(&self) -> &ENABLE {
        &self.enable
    }
    #[doc = "0x01 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn pending(&self) -> &PENDING {
        &self.pending
    }
}
#[doc = "enable (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`enable::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`enable::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@enable`]
module"]
#[doc(alias = "enable")]
pub type ENABLE = crate::Reg<enable::ENABLE_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod enable;
#[doc = "pending (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`pending::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`pending::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@pending`]
module"]
#[doc(alias = "pending")]
pub type PENDING = crate::Reg<pending::PENDING_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod pending;
