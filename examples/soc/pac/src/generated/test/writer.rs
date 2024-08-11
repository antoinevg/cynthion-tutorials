#[doc = "Register `writer` reader"]
pub type R = crate::R<WRITER_SPEC>;
#[doc = "Register `writer` writer"]
pub type W = crate::W<WRITER_SPEC>;
#[doc = "Field `a` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type A_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `_0` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type _0_R = crate::FieldReader;
#[doc = "Field `_0` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type _0_W<'a, REG> = crate::FieldWriter<'a, REG, 7>;
#[doc = "Field `b` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type B_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `c` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type C_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `d` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type D_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `e` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type E_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `f` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type F_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `g` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type G_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `h` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type H_W<'a, REG> = crate::BitWriter<'a, REG>;
impl R {
    #[doc = "Bits 1:7 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn _0(&self) -> _0_R {
        _0_R::new(((self.bits >> 1) & 0x7f) as u8)
    }
}
impl W {
    #[doc = "Bit 0 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn a(&mut self) -> A_W<WRITER_SPEC> {
        A_W::new(self, 0)
    }
    #[doc = "Bits 1:7 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn _0(&mut self) -> _0_W<WRITER_SPEC> {
        _0_W::new(self, 1)
    }
    #[doc = "Bit 8 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn b(&mut self) -> B_W<WRITER_SPEC> {
        B_W::new(self, 8)
    }
    #[doc = "Bit 9 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn c(&mut self) -> C_W<WRITER_SPEC> {
        C_W::new(self, 9)
    }
    #[doc = "Bit 10 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn d(&mut self) -> D_W<WRITER_SPEC> {
        D_W::new(self, 10)
    }
    #[doc = "Bit 11 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn e(&mut self) -> E_W<WRITER_SPEC> {
        E_W::new(self, 11)
    }
    #[doc = "Bit 12 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn f(&mut self) -> F_W<WRITER_SPEC> {
        F_W::new(self, 12)
    }
    #[doc = "Bit 13 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn g(&mut self) -> G_W<WRITER_SPEC> {
        G_W::new(self, 13)
    }
    #[doc = "Bit 14 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn h(&mut self) -> H_W<WRITER_SPEC> {
        H_W::new(self, 14)
    }
}
#[doc = "TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`writer::R`](R).  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`writer::W`](W). You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api)."]
pub struct WRITER_SPEC;
impl crate::RegisterSpec for WRITER_SPEC {
    type Ux = u16;
}
#[doc = "`read()` method returns [`writer::R`](R) reader structure"]
impl crate::Readable for WRITER_SPEC {}
#[doc = "`write(|w| ..)` method takes [`writer::W`](W) writer structure"]
impl crate::Writable for WRITER_SPEC {
    type Safety = crate::Unsafe;
    const ZERO_TO_MODIFY_FIELDS_BITMAP: u16 = 0;
    const ONE_TO_MODIFY_FIELDS_BITMAP: u16 = 0;
}
#[doc = "`reset()` method sets writer to value 0"]
impl crate::Resettable for WRITER_SPEC {
    const RESET_VALUE: u16 = 0;
}
