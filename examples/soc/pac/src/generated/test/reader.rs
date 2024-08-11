#[doc = "Register `reader` reader"]
pub type R = crate::R<READER_SPEC>;
#[doc = "Register `reader` writer"]
pub type W = crate::W<READER_SPEC>;
#[doc = "Field `a` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type A_R = crate::BitReader;
#[doc = "Field `b` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type B_R = crate::BitReader;
#[doc = "Field `c` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type C_R = crate::BitReader;
#[doc = "Field `d` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type D_R = crate::BitReader;
#[doc = "Field `e` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type E_R = crate::BitReader;
#[doc = "Field `f` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type F_R = crate::BitReader;
#[doc = "Field `g` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type G_R = crate::BitReader;
#[doc = "Field `h` reader - TODO amaranth_soc/csr/reg.py:471"]
pub type H_R = crate::BitReader;
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
impl W {}
#[doc = "TODO amaranth_soc/csr/reg.py:471\n\nYou can [`read`](crate::generic::Reg::read) this register and get [`reader::R`](R).  You can [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write), [`write_with_zero`](crate::generic::Reg::write_with_zero) this register using [`reader::W`](W). You can also [`modify`](crate::generic::Reg::modify) this register. See [API](https://docs.rs/svd2rust/#read--modify--write-api)."]
pub struct READER_SPEC;
impl crate::RegisterSpec for READER_SPEC {
    type Ux = u8;
}
#[doc = "`read()` method returns [`reader::R`](R) reader structure"]
impl crate::Readable for READER_SPEC {}
#[doc = "`write(|w| ..)` method takes [`reader::W`](W) writer structure"]
impl crate::Writable for READER_SPEC {
    type Safety = crate::Unsafe;
    const ZERO_TO_MODIFY_FIELDS_BITMAP: u8 = 0;
    const ONE_TO_MODIFY_FIELDS_BITMAP: u8 = 0;
}
#[doc = "`reset()` method sets reader to value 0"]
impl crate::Resettable for READER_SPEC {
    const RESET_VALUE: u8 = 0;
}
