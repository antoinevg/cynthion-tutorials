#[doc = "Register `prime` reader"]
pub type R = crate::R<PRIME_SPEC>;
#[doc = "Register `prime` writer"]
pub type W = crate::W<PRIME_SPEC>;
#[doc = "Field `primed` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type PRIMED_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `_0` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type _0_R = crate::FieldReader;
#[doc = "Field `_0` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type _0_W<'a, REG> = crate::FieldWriter<'a, REG, 7>;
impl R {
    #[doc = "Bits 1:7 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn _0(&self) -> _0_R {
        _0_R::new((self.bits >> 1) & 0x7f)
    }
}
impl W {
    #[doc = "Bit 0 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn primed(&mut self) -> PRIMED_W<PRIME_SPEC> {
        PRIMED_W::new(self, 0)
    }
    #[doc = "Bits 1:7 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn _0(&mut self) -> _0_W<PRIME_SPEC> {
        _0_W::new(self, 1)
    }
}
#[doc = "TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`prime::R`](R).  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`prime::W`](W). You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api)."]
pub struct PRIME_SPEC;
impl crate::RegisterSpec for PRIME_SPEC {
    type Ux = u8;
}
#[doc = "`read()` method returns [`prime::R`](R) reader structure"]
impl crate::Readable for PRIME_SPEC {}
#[doc = "`write(|w| ..)` method takes [`prime::W`](W) writer structure"]
impl crate::Writable for PRIME_SPEC {
    type Safety = crate::Unsafe;
    const ZERO_TO_MODIFY_FIELDS_BITMAP: u8 = 0;
    const ONE_TO_MODIFY_FIELDS_BITMAP: u8 = 0;
}
#[doc = "`reset()` method sets prime to value 0"]
impl crate::Resettable for PRIME_SPEC {
    const RESET_VALUE: u8 = 0;
}
