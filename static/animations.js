/* ============================================
   GD PULSE — HYBRID ANIMATIONS
   With MAGIC theme transition
   ============================================ */

// ===== SCROLL PROGRESS BAR =====
(function initScrollProgress() {
  const bar = document.createElement('div');
  bar.className = 'scroll-progress';
  document.body.appendChild(bar);

  window.addEventListener('scroll', () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    bar.style.width = progress + '%';
  });
})();

// ===== THEME TOGGLE with MAGIC animation =====
(function initTheme() {
  const savedTheme = localStorage.getItem('gd-theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
})();

function toggleTheme(e) {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'light' ? 'dark' : 'light';

  // Get click position for ripple origin
  let x = window.innerWidth / 2;
  let y = window.innerHeight / 2;
  if (e && e.clientX) {
    x = e.clientX;
    y = e.clientY;
  }

  // Create magic ripple
  createThemeRipple(x, y);

  // Spin the toggle button
  const btn = e ? e.target.closest('.theme-toggle') : null;
  if (btn) {
    btn.classList.add('spinning');
    setTimeout(() => btn.classList.remove('spinning'), 800);
  }

  // Wait a tiny bit before changing theme (so ripple starts first)
  setTimeout(() => {
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('gd-theme', next);
    updateThemeIcon(next);
  }, 150);
}

function createThemeRipple(x, y) {
  const ripple = document.createElement('div');
  ripple.className = 'theme-ripple active';
  ripple.style.left = x + 'px';
  ripple.style.top = y + 'px';
  ripple.style.width = '100px';
  ripple.style.height = '100px';
  ripple.style.marginLeft = '-50px';
  ripple.style.marginTop = '-50px';
  ripple.style.background = `radial-gradient(circle, ${
    document.documentElement.getAttribute('data-theme') === 'dark'
      ? '#a78bfa'
      : '#8b5cf6'
  } 0%, transparent 70%)`;
  document.body.appendChild(ripple);
  setTimeout(() => ripple.remove(), 1000);
}

function updateThemeIcon(theme) {
  document.querySelectorAll('.theme-toggle').forEach(btn => {
    btn.innerText = theme === 'dark' ? '☀️' : '🌙';
    btn.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
  });
}

// ===== SCROLL REVEAL =====
(function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  });

  function observeAll() {
    document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale, .stagger')
      .forEach(el => observer.observe(el));
  }

  document.addEventListener('DOMContentLoaded', observeAll);
  setTimeout(observeAll, 500);
})();

// ===== COUNT-UP ANIMATION =====
function animateCount(el, target, duration = 2000) {
  const startTime = performance.now();
  const suffix = el.getAttribute('data-suffix') || '';

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(eased * target);
    el.innerText = current + suffix;
    if (progress < 1) requestAnimationFrame(update);
    else el.innerText = target + suffix;
  }
  requestAnimationFrame(update);
}

(function initCountUp() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
        entry.target.classList.add('counted');
        const text = entry.target.innerText;
        const num = parseInt(text.replace(/[^0-9]/g, ''));
        const suffix = text.replace(/[0-9]/g, '');
        if (!isNaN(num) && num > 0) {
          entry.target.setAttribute('data-suffix', suffix);
          animateCount(entry.target, num, 1800);
        }
      }
    });
  }, { threshold: 0.5 });

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.stat-card .value').forEach(el => observer.observe(el));
  });
})();

// ===== PARALLAX ORB =====
(function initParallax() {
  const orbs = document.querySelectorAll('.parallax-orb');
  if (!orbs.length) return;

  document.addEventListener('mousemove', (e) => {
    const x = (e.clientX / window.innerWidth - 0.5) * 60;
    const y = (e.clientY / window.innerHeight - 0.5) * 60;
    orbs.forEach((orb, i) => {
      const speed = (i + 1) * 0.5;
      orb.style.transform = `translate(${x * speed}px, ${y * speed}px)`;
    });
  });
})();

// ===== RIPPLE EFFECT =====
(function initRipple() {
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.calc-btn, .action-btn, .btn, .login-box button, .tab');
    if (!btn) return;

    const ripple = document.createElement('span');
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.5);
      left: ${x}px;
      top: ${y}px;
      pointer-events: none;
      transform: scale(0);
      animation: rippleAnim 0.7s ease-out;
      z-index: 1;
    `;

    if (getComputedStyle(btn).position === 'static') {
      btn.style.position = 'relative';
    }
    btn.style.overflow = 'hidden';
    btn.appendChild(ripple);

    setTimeout(() => ripple.remove(), 700);
  });

  const style = document.createElement('style');
  style.textContent = `
    @keyframes rippleAnim {
      to { transform: scale(2.5); opacity: 0; }
    }
  `;
  document.head.appendChild(style);
})();

// ===== MAGNETIC BUTTONS =====
(function initMagnetic() {
  if (window.innerWidth < 900) return;

  document.querySelectorAll('.btn, .icon-btn, .theme-toggle, .avatar').forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate(${x * 0.25}px, ${y * 0.25}px)`;
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = '';
    });
  });
})();

// ===== CARD 3D TILT =====
(function initTilt() {
  if (window.innerWidth < 900) return;

  document.querySelectorAll('.card, .tool-card, .stat-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const rotX = ((y - rect.height / 2) / (rect.height / 2)) * -6;
      const rotY = ((x - rect.width / 2) / (rect.width / 2)) * 6;
      card.style.transform = `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateY(-6px) scale(1.02)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });
})();

// ===== SMOOTH SCROLL for Nav =====
(function initSmoothScroll() {
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href^="#"]');
    if (!link) return;
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
})();

// ===== ACTIVE NAV on Scroll =====
(function initActiveNav() {
  const sections = document.querySelectorAll('section[id]');
  if (!sections.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        document.querySelectorAll('.nav-links a').forEach(a => {
          a.classList.toggle('active', a.getAttribute('href') === `#${id}`);
        });
      }
    });
  }, { threshold: 0.3 });

  sections.forEach(s => observer.observe(s));
})();

// ===== PAGE LOAD FADE-IN =====
document.addEventListener('DOMContentLoaded', () => {
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.5s ease';
  requestAnimationFrame(() => {
    document.body.style.opacity = '1';
  });
  const theme = document.documentElement.getAttribute('data-theme') || 'light';
  updateThemeIcon(theme);
});
