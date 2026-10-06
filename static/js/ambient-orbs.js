document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('ambient-orbs');
  if (!container) return;

  // تنظیمات دایره‌ها با رنگ‌های مشخص‌تر و پوشش سراسری
  const orbConfigs = [
    {
      // هاله زرشکی بالا سمت راست (نفوذ به زیر هدر و هیرو)
      x: 70,
      y: -5,
      size: 560,
      color: 'rgba(225, 29, 72, 0.28)', // زرشکی شاخص
      factorY: 0.18,
      factorX: -0.06
    },
    {
      // هاله رز ملایم چپ (سمت چپ سرچ‌‌بار)
      x: 5,
      y: 20,
      size: 480,
      color: 'rgba(244, 63, 94, 0.24)',
      factorY: -0.12,
      factorX: 0.05
    },
    {
      // هاله میانی (پشت کارت‌ها)
      x: 50,
      y: 50,
      size: 600,
      color: 'rgba(225, 29, 72, 0.20)',
      factorY: 0.22,
      factorX: 0.08
    },
    {
      // هاله سرمه‌ای شیک (کنتراست خنک در سمت راست کارت‌ها)
      x: 82,
      y: 72,
      size: 520,
      color: 'rgba(15, 23, 42, 0.15)',
      factorY: -0.15,
      factorX: -0.05
    },
    {
      // هاله گرم پایین صفحه (نفوذ کامل به زیر فوتر)
      x: 12,
      y: 90,
      size: 580,
      color: 'rgba(244, 63, 94, 0.25)',
      factorY: 0.16,
      factorX: 0.04
    }
  ];

  const orbs = [];

  orbConfigs.forEach((cfg) => {
    const orb = document.createElement('div');
    orb.className = 'ambient-orb';

    orb.style.width = `${cfg.size}px`;
    orb.style.height = `${cfg.size}px`;
    orb.style.backgroundColor = cfg.color;
    orb.style.left = `${cfg.x}vw`;
    orb.style.top = `${cfg.y}vh`;

    container.appendChild(orb);

    orbs.push({
      el: orb,
      factorY: cfg.factorY,
      factorX: cfg.factorX
    });
  });

  let isTicking = false;

  function updatePositions() {
    const scrollY = window.pageYOffset || document.documentElement.scrollTop;

    orbs.forEach((orb) => {
      const moveY = scrollY * orb.factorY;
      const moveX = scrollY * orb.factorX;
      orb.el.style.transform = `translate3d(${moveX.toFixed(1)}px, ${moveY.toFixed(1)}px, 0)`;
    });

    isTicking = false;
  }

  window.addEventListener('scroll', () => {
    if (!isTicking) {
      window.requestAnimationFrame(updatePositions);
      isTicking = true;
    }
  }, { passive: true });

  updatePositions();
});