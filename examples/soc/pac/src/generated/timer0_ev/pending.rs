#[doc = "Register `pending` reader"]
pub type R = crate::R<PENDING_SPEC>;
#[doc = "Register `pending` writer"]
pub type W = crate::W<PENDING_SPEC>;
#[doc = "Field `mask` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type MASK_R = crate::FieldReader;
#[doc = "Field `mask` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type MASK_W<'a, REG> = crate::FieldWriter<'a, REG, 2>;
impl R {
    #[doc = "Bits 0:1 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn mask(&self) -> MASK_R {
        MASK_R::new(self.bits & 3)
    }
}
impl W {
    #[doc = "Bits 0:1 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn mask(&mut self) -> MASK_W<PENDING_SPEC> {
        MASK_W::new(self, 0)
    }
}
#[doc = "TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`pending::R`](R).  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`pending::W`](W). You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api)."]
pub struct PENDING_SPEC;
impl crate::RegisterSpec for PENDING_SPEC {
    type Ux = u8;
}
#[doc = "`read()` method returns [`pending::R`](R) reader structure"]
impl crate::Readable for PENDING_SPEC {}
#[doc = "`write(|w| ..)` method takes [`pending::W`](W) writer structure"]
impl crate::Writable for PENDING_SPEC {
    type Safety = crate::Unsafe;
    const ZERO_TO_MODIFY_FIELDS_BITMAP: u8 = 0;
    const ONE_TO_MODIFY_FIELDS_BITMAP: u8 = 0;
}
#[doc = "`reset()` method sets pending to value 0"]
impl crate::Resettable for PENDING_SPEC {
    const RESET_VALUE: u8 = 0;
}
