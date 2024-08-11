#[doc = "Register `endpoint` reader"]
pub type R = crate::R<ENDPOINT_SPEC>;
#[doc = "Register `endpoint` writer"]
pub type W = crate::W<ENDPOINT_SPEC>;
#[doc = "Field `number` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type NUMBER_R = crate::FieldReader;
#[doc = "Field `number` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type NUMBER_W<'a, REG> = crate::FieldWriter<'a, REG, 4>;
#[doc = "Field `_0` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type _0_R = crate::FieldReader;
#[doc = "Field `_0` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type _0_W<'a, REG> = crate::FieldWriter<'a, REG, 4>;
impl R {
    #[doc = "Bits 0:3 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn number(&self) -> NUMBER_R {
        NUMBER_R::new(self.bits & 0x0f)
    }
    #[doc = "Bits 4:7 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn _0(&self) -> _0_R {
        _0_R::new((self.bits >> 4) & 0x0f)
    }
}
impl W {
    #[doc = "Bits 0:3 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn number(&mut self) -> NUMBER_W<ENDPOINT_SPEC> {
        NUMBER_W::new(self, 0)
    }
    #[doc = "Bits 4:7 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn _0(&mut self) -> _0_W<ENDPOINT_SPEC> {
        _0_W::new(self, 4)
    }
}
#[doc = "TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`endpoint::R`](R).  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`endpoint::W`](W). You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api)."]
pub struct ENDPOINT_SPEC;
impl crate::RegisterSpec for ENDPOINT_SPEC {
    type Ux = u8;
}
#[doc = "`read()` method returns [`endpoint::R`](R) reader structure"]
impl crate::Readable for ENDPOINT_SPEC {}
#[doc = "`write(|w| ..)` method takes [`endpoint::W`](W) writer structure"]
impl crate::Writable for ENDPOINT_SPEC {
    type Safety = crate::Unsafe;
    const ZERO_TO_MODIFY_FIELDS_BITMAP: u8 = 0;
    const ONE_TO_MODIFY_FIELDS_BITMAP: u8 = 0;
}
#[doc = "`reset()` method sets endpoint to value 0"]
impl crate::Resettable for ENDPOINT_SPEC {
    const RESET_VALUE: u8 = 0;
}