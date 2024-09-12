#[doc = "Register `trace` reader"]
pub type R = crate::R<TRACE_SPEC>;
#[doc = "Register `trace` writer"]
pub type W = crate::W<TRACE_SPEC>;
#[doc = "Field `a` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type A_W<'a, REG> = crate::FieldWriter<'a, REG, 8>;
#[doc = "Field `b` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type B_W<'a, REG> = crate::FieldWriter<'a, REG, 8>;
#[doc = "Field `c` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type C_W<'a, REG> = crate::FieldWriter<'a, REG, 8>;
#[doc = "Field `d` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type D_W<'a, REG> = crate::FieldWriter<'a, REG, 8>;
impl W {
    #[doc = "Bits 0:7 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn a(&mut self) -> A_W<TRACE_SPEC> {
        A_W::new(self, 0)
    }
    #[doc = "Bits 8:15 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn b(&mut self) -> B_W<TRACE_SPEC> {
        B_W::new(self, 8)
    }
    #[doc = "Bits 16:23 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn c(&mut self) -> C_W<TRACE_SPEC> {
        C_W::new(self, 16)
    }
    #[doc = "Bits 24:31 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn d(&mut self) -> D_W<TRACE_SPEC> {
        D_W::new(self, 24)
    }
}
#[doc = "TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`trace::R`](R).  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`trace::W`](W). You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api)."]
pub struct TRACE_SPEC;
impl crate::RegisterSpec for TRACE_SPEC {
    type Ux = u32;
}
#[doc = "`read()` method returns [`trace::R`](R) reader structure"]
impl crate::Readable for TRACE_SPEC {}
#[doc = "`write(|w| ..)` method takes [`trace::W`](W) writer structure"]
impl crate::Writable for TRACE_SPEC {
    type Safety = crate::Unsafe;
    const ZERO_TO_MODIFY_FIELDS_BITMAP: u32 = 0;
    const ONE_TO_MODIFY_FIELDS_BITMAP: u32 = 0;
}
#[doc = "`reset()` method sets trace to value 0"]
impl crate::Resettable for TRACE_SPEC {
    const RESET_VALUE: u32 = 0;
}
