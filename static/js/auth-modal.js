// static/js/auth-modal.js
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

  // تنها در صورتی که المان‌های مدال در صفحه حضور داشته باشند، لیسنرها فعال شوند
  if (btnOpen && modal) {
    btnOpen.addEventListener('click', () => {
      modal.style.display = 'flex';
      if (stepPhone) stepPhone.style.display = 'block';
      if (stepVerify) stepVerify.style.display = 'none';
      if (errSend) errSend.style.display = 'none';
      if (inputPhone) inputPhone.focus();
    });
  }

  if (btnClose && modal) {
    btnClose.addEventListener('click', () => {
      modal.style.display = 'none';
    });
  }

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.style.display = 'none';
    });
  }

  if (btnBack && stepPhone && stepVerify) {
    btnBack.addEventListener('click', () => {
      stepVerify.style.display = 'none';
      stepPhone.style.display = 'block';
    });
  }

  if (formSend && inputPhone) {
    formSend.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (errSend) errSend.style.display = 'none';
      const phone = inputPhone.value.trim();

      try {
        const res = await fetch('/api/accounts/otp/send/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone_number: phone })
        });
        const data = await res.json();

        if (res.ok) {
          if (displayPhone) displayPhone.textContent = phone;
          if (stepPhone) stepPhone.style.display = 'none';
          if (stepVerify) stepVerify.style.display = 'block';
          if (inputCode) {
            inputCode.value = '';
            inputCode.focus();
          }
        } else {
          if (errSend) {
            errSend.textContent = data.message || data.detail || 'خطا در ارسال کد.';
            errSend.style.display = 'block';
          }
        }
      } catch {
        if (errSend) {
          errSend.textContent = 'خطا در برقراری ارتباط با سرور.';
          errSend.style.display = 'block';
        }
      }
    });
  }

  if (formVerify && inputCode && inputPhone) {
    formVerify.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (errVerify) errVerify.style.display = 'none';
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
          localStorage.setItem('berimja_access_token', data.access);
          localStorage.setItem('berimja_refresh_token', data.refresh);
          localStorage.setItem('berimja_user_info', JSON.stringify(data.user));
          if (modal) modal.style.display = 'none';
          window.location.reload();
        } else {
          if (errVerify) {
            errVerify.textContent = data.error || data.detail || 'کد واردشده نامعتبر یا منقضی است.';
            errVerify.style.display = 'block';
          }
        }
      } catch {
        if (errVerify) {
          errVerify.textContent = 'خطا در برقراری ارتباط با سرور.';
          errVerify.style.display = 'block';
        }
      }
    });
  }
});