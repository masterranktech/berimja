
  // فعال‌سازی سراسری آیکون‌ها
  if (window.lucide) {
    lucide.createIcons();
  }

  // کنترل تعاملی دکمه پرش به بالا (Back to Top Island)
  document.addEventListener('DOMContentLoaded', () => {
    const backToTopBtn = document.getElementById('btn-back-to-top');

    if (backToTopBtn) {
      const toggleBackToTop = () => {
        // اگر اسکرول بیشتر از ۳۵۰ پیکسل بود، دکمه نمایان می‌شود
        if (window.scrollY > 350) {
          backToTopBtn.classList.add('visible');
        } else {
          backToTopBtn.classList.remove('visible');
        }
      };

      // پایش موقعیت اسکرول
      window.addEventListener('scroll', toggleBackToTop, { passive: true });

      // هدایت نرم به ابتدای صفحه در زمان کلیک
      backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
      });
    }
  });
