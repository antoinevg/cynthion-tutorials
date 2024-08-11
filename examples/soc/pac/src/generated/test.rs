#[repr(C)]
#[doc = "Register block"]
pub struct RegisterBlock {
    writer: WRITER,
    readerwriter: READERWRITER,
    reader: READER,
    _reserved3: [u8; 0x0c],
    ev_enable: EV_ENABLE,
    ev_pending: EV_PENDING,
}
impl RegisterBlock {
    #[doc = "0x00 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn writer(&self) -> &WRITER {
        &self.writer
    }
    #[doc = "0x02 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn readerwriter(&self) -> &READERWRITER {
        &self.readerwriter
    }
    #[doc = "0x03 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn reader(&self) -> &READER {
        &self.reader
    }
    #[doc = "0x10 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn ev_enable(&self) -> &EV_ENABLE {
        &self.ev_enable
    }
    #[doc = "0x11 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub const fn ev_pending(&self) -> &EV_PENDING {
        &self.ev_pending
    }
}
#[doc = "writer (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`writer::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`writer::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@writer`]
module"]
#[doc(alias = "writer")]
pub type WRITER = crate::Reg<writer::WRITER_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod writer;
#[doc = "readerwriter (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`readerwriter::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`readerwriter::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@readerwriter`]
module"]
#[doc(alias = "readerwriter")]
pub type READERWRITER = crate::Reg<readerwriter::READERWRITER_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod readerwriter;
#[doc = "reader (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`reader::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`reader::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@reader`]
module"]
#[doc(alias = "reader")]
pub type READER = crate::Reg<reader::READER_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod reader;
#[doc = "ev_enable (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`ev_enable::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`ev_enable::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@ev_enable`]
module"]
#[doc(alias = "ev_enable")]
pub type EV_ENABLE = crate::Reg<ev_enable::EV_ENABLE_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod ev_enable;
#[doc = "ev_pending (rw) register accessor: TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`ev_pending::R`].  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`ev_pending::W`]. You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [`mod@ev_pending`]
module"]
#[doc(alias = "ev_pending")]
pub type EV_PENDING = crate::Reg<ev_pending::EV_PENDING_SPEC>;
#[doc = "TODO amaranth_soc/csr/reg.py:471"]
pub mod ev_pending;
