document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('auth-modal');
  const btnOpen = document.getElementById('btn-open-login');
  const btnClose = document.getElementById('btn-close-modal');

  const stepPhone = document.getElementById('auth-step-phone');
  const stepVerify = document.getElementById('auth-step-verify');

  const formSend = document.getElementById('form-send-otp');
  const formVerify = document.getElementById('form-verify-otp');

  const inputPhone = document.getElementById('input-phone');
  const inputCode = document.getElementById('input-code');

  const errSend = document.getElementById('otp-send-error');
  const errVerify = document.getElementById('otp-verify-error');

  const displayPhone = document.getElementById('display-target-phone');
  const btnBack = document.getElementById('btn-back-to-phone');

  // بررسی وضعیت ورود قبلی در کلاینت
  const savedToken = localStorage.getItem('berimja_access_token');
  const savedUser = localStorage.getItem('berimja_user_info');
  if (savedToken && savedUser && btnOpen) {
    const user = JSON.parse(savedUser);
    const container = btnOpen.parentElement;
    container.innerHTML = `
      <div class="user-badge">
        <i data-lucide="user"></i>
        <span>${user.display_name || user.phone_number}</span>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
  }

  // باز و بسته کردن مودال
  if (btnOpen) {
    btnOpen.addEventListener('click', () => {
      modal.style.display = 'flex';
      stepPhone.style.display = 'block';
      stepVerify.style.display = 'none';
      errSend.style.display = 'none';
      inputPhone.focus();
    });
  }

  if (btnClose) {
    btnClose.addEventListener('click', () => {
      modal.style.display = 'none';
    });
  }

  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.style.display = 'none';
  });

  if (btnBack) {
    btnBack.addEventListener('click', () => {
      stepVerify.style.display = 'none';
      stepPhone.style.display = 'block';
    });
  }

  // مرحله ۱: ارسال شماره و درخواست OTP
  formSend.addEventListener('submit', async (e) => {
    e.preventDefault();
    errSend.style.display = 'none';
    const phone = inputPhone.value.trim();

    try {
      const res = await fetch('/api/accounts/otp/send/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phone })
      });
      const data = await res.json();

      if (res.ok) {
        displayPhone.textContent = phone;
        stepPhone.style.display = 'none';
        stepVerify.style.display = 'block';
        inputCode.value = '';
        inputCode.focus();
      } else {
        errSend.textContent = data.message || data.detail || (data.phone_number ? data.phone_number[0] : 'خطا در ارسال کد.');
        errSend.style.display = 'block';
      }
    } catch {
      errSend.textContent = 'خطا در برقراری ارتباط با سرور.';
      errSend.style.display = 'block';
    }
  });

  // مرحله ۲: اعتبارسنجی کد و دریافت JWT
  formVerify.addEventListener('submit', async (e) => {
    e.preventDefault();
    errVerify.style.display = 'none';
    const phone = inputPhone.value.trim();
    const code = inputCode.value.trim();

    try {
      const res = await fetch('/api/accounts/otp/verify/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phone, code: code })
      });
      const data = await res.json();

      if (res.ok) {
        // ذخیره توکن‌ها
        localStorage.setItem('berimja_access_token', data.access);
        localStorage.setItem('berimja_refresh_token', data.refresh);
        localStorage.setItem('berimja_user_info', JSON.stringify(data.user));

        modal.style.display = 'none';
        // بارگذاری مجدد صفحه جهت تطبیق کامل هدر و فرم‌ها
        window.location.reload();
      } else {
        errVerify.textContent = data.error || data.detail || 'کد واردشده نامعتبر یا منقضی است.';
        errVerify.style.display = 'block';
      }
    } catch {
      errVerify.textContent = 'خطا در برقراری ارتباط با سرور.';
      errVerify.style.display = 'block';
    }
  });
});