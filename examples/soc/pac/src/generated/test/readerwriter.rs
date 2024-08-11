#[doc = "Register `readerwriter` reader"]
pub type R = crate::R<READERWRITER_SPEC>;
#[doc = "Register `readerwriter` writer"]
pub type W = crate::W<READERWRITER_SPEC>;
#[doc = "Field `a` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type A_R = crate::BitReader;
#[doc = "Field `a` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type A_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `b` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type B_R = crate::BitReader;
#[doc = "Field `b` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type B_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `c` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type C_R = crate::BitReader;
#[doc = "Field `c` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type C_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `d` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type D_R = crate::BitReader;
#[doc = "Field `d` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type D_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `e` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type E_R = crate::BitReader;
#[doc = "Field `e` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type E_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `f` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type F_R = crate::BitReader;
#[doc = "Field `f` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type F_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `g` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type G_R = crate::BitReader;
#[doc = "Field `g` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type G_W<'a, REG> = crate::BitWriter<'a, REG>;
#[doc = "Field `h` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type H_R = crate::BitReader;
#[doc = "Field `h` writer - TODO amaranth_soc/csr/reg.py:471"]
pub type H_W<'a, REG> = crate::BitWriter<'a, REG>;
impl R {
    #[doc = "Bit 0 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn a(&self) -> A_R {
        A_R::new((self.bits & 1) != 0)
    }
    #[doc = "Bit 1 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn b(&self) -> B_R {
        B_R::new(((self.bits >> 1) & 1) != 0)
    }
    #[doc = "Bit 2 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn c(&self) -> C_R {
        C_R::new(((self.bits >> 2) & 1) != 0)
    }
    #[doc = "Bit 3 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn d(&self) -> D_R {
        D_R::new(((self.bits >> 3) & 1) != 0)
    }
    #[doc = "Bit 4 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn e(&self) -> E_R {
        E_R::new(((self.bits >> 4) & 1) != 0)
    }
    #[doc = "Bit 5 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn f(&self) -> F_R {
        F_R::new(((self.bits >> 5) & 1) != 0)
    }
    #[doc = "Bit 6 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn g(&self) -> G_R {
        G_R::new(((self.bits >> 6) & 1) != 0)
    }
    #[doc = "Bit 7 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    pub fn h(&self) -> H_R {
        H_R::new(((self.bits >> 7) & 1) != 0)
    }
}
impl W {
    #[doc = "Bit 0 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn a(&mut self) -> A_W<READERWRITER_SPEC> {
        A_W::new(self, 0)
    }
    #[doc = "Bit 1 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn b(&mut self) -> B_W<READERWRITER_SPEC> {
        B_W::new(self, 1)
    }
    #[doc = "Bit 2 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn c(&mut self) -> C_W<READERWRITER_SPEC> {
        C_W::new(self, 2)
    }
    #[doc = "Bit 3 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn d(&mut self) -> D_W<READERWRITER_SPEC> {
        D_W::new(self, 3)
    }
    #[doc = "Bit 4 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn e(&mut self) -> E_W<READERWRITER_SPEC> {
        E_W::new(self, 4)
    }
    #[doc = "Bit 5 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn f(&mut self) -> F_W<READERWRITER_SPEC> {
        F_W::new(self, 5)
    }
    #[doc = "Bit 6 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn g(&mut self) -> G_W<READERWRITER_SPEC> {
        G_W::new(self, 6)
    }
    #[doc = "Bit 7 - TODO amaranth_soc/csr/reg.py:471"]
    #[inline(always)]
    #[must_use]
    pub fn h(&mut self) -> H_W<READERWRITER_SPEC> {
        H_W::new(self, 7)
    }
}
#[doc = "TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`readerwriter::R`](R).  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`readerwriter::W`](W). You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api)."]
pub struct READERWRITER_SPEC;
impl crate::RegisterSpec for READERWRITER_SPEC {
    type Ux = u8;
}
#[doc = "`read()` method returns [`readerwriter::R`](R) reader structure"]
impl crate::Readable for READERWRITER_SPEC {}
#[doc = "`write(|w| ..)` method takes [`readerwriter::W`](W) writer structure"]
impl crate::Writable for READERWRITER_SPEC {
    type Safety = crate::Unsafe;
    const ZERO_TO_MODIFY_FIELDS_BITMAP: u8 = 0;
    const ONE_TO_MODIFY_FIELDS_BITMAP: u8 = 0;
}
#[doc = "`reset()` method sets readerwriter to value 0"]
impl crate::Resettable for READERWRITER_SPEC {
    const RESET_VALUE: u8 = 0;
}
