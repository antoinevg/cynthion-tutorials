#[repr(C)]
#[doc = "Register block"]
pub struct RegisterBlock {
    reload: RELOAD,
    enable: ENABLE,
    _reserved2: [u8; 0x03],
    counter: COUNTER,
}
impl RegisterBlock {
    #[doc = "0x00 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn reload(&self) -> &RELOAD {
        &self.reload
    }
    #[doc = "0x04 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn enable(&self) -> &ENABLE {
        &self.enable
    }
    #[doc = "0x08 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn counter(&self) -> &COUNTER {
        &self.counter
    }
}
#[doc = "reload (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`reload::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`reload::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@reload`]
module"]
#[doc(alias = "reload")]
pub type RELOAD = crate::Reg<reload::RELOAD_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod reload;
#[doc = "enable (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`enable::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`enable::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@enable`]
module"]
#[doc(alias = "enable")]
pub type ENABLE = crate::Reg<enable::ENABLE_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod enable;
#[doc = "counter (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`counter::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`counter::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@counter`]
module"]
#[doc(alias = "counter")]
pub type COUNTER = crate::Reg<counter::COUNTER_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod counter;
