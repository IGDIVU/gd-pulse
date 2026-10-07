/* ============================================
   GD PULSE — ANIMATIONS + AUTO CONFIRM
   ============================================ */

// ===== SCROLL PROGRESS =====
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

// ===== AUTO-INJECT CONFIRM DIALOG =====
(function autoInjectConfirm() {
  if (document.getElementById('confirmOverlay')) return;
  const html = `
    <div class="confirm-overlay" id="confirmOverlay">
      <div class="confirm-box">
        <div class="warn-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:30px;height:30px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
        <h3 id="confirmTitle">Are you sure?</h3>
        <p id="confirmMessage">This action cannot be undone.</p>
        <div class="confirm-actions">
          <button class="btn-cancel" onclick="closeConfirm()">Cancel</button>
          <button class="btn-confirm" id="confirmYes">Yes</button>
        </div>
      </div>
    </div>`;
  document.body.insertAdjacentHTML('beforeend', html);
  document.getElementById('confirmYes').addEventListener('click', () => {
    if (window._pendingAction) {
      const action = window._pendingAction;
      closeConfirm();
      action();
    }
  });
})();

window._pendingAction = null;

function showConfirm(title, message, btnText, callback) {
  const overlay = document.getElementById('confirmOverlay');
  if (!overlay) return;
  document.getElementById('confirmTitle').innerText = title;
  document.getElementById('confirmMessage').innerText = message;
  document.getElementById('confirmYes').innerText = btnText;
  window._pendingAction = callback;
  overlay.classList.add('active');
}
function closeConfirm() {
  const overlay = document.getElementById('confirmOverlay');
  if (overlay) overlay.classList.remove('active');
  window._pendingAction = null;
}
function confirmLogout(e) {
  if (e) e.preventDefault();
  showConfirm("Logout?", "Kya tum sach me logout karna chahte ho?", "Yes, Logout", () => {
    window.location.href = "/logout";
  });
}

// ===== THEME TOGGLE =====
(function initTheme() {
  const savedTheme = localStorage.getItem('gd-theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
})();

let isSwitching = false;

function toggleTheme(e) {
  if (isSwitching) return;
  isSwitching = true;
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'light' ? 'dark' : 'light';
  let x = window.innerWidth - 60, y = 60;
  if (e && e.clientX) { x = e.clientX; y = e.clientY; }
  playMagicSound(current);
  const btn = e ? e.target.closest('.theme-toggle') : null;
  if (btn) { btn.classList.add('spinning'); setTimeout(() => btn.classList.remove('spinning'), 900); }
  triggerScreenShake();
  createCircleExpand(x, y, current);
  createRippleRings(x, y, current);
  createStarBurst(x, y, current);
  createConfetti(x, y);
  createParticles(x, y, current);
  createFlash();
  setTimeout(() => {
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('gd-theme', next);
    updateThemeIcon(next);
    triggerStaggerColors();
  }, 400);
  setTimeout(() => { isSwitching = false; }, 1600);
}

function playMagicSound(currentTheme) {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const whoosh = ctx.createOscillator();
    const whooshGain = ctx.createGain();
    whoosh.type = 'sine';
    whoosh.frequency.setValueAtTime(200, ctx.currentTime);
    whoosh.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.4);
    whooshGain.gain.setValueAtTime(0, ctx.currentTime);
    whooshGain.gain.linearRampToValueAtTime(0.15, ctx.currentTime + 0.1);
    whooshGain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
    whoosh.connect(whooshGain);
    whooshGain.connect(ctx.destination);
    whoosh.start(ctx.currentTime);
    whoosh.stop(ctx.currentTime + 0.5);
    setTimeout(() => {
      [880, 1108, 1318, 1567, 1760].forEach((freq, i) => {
        const sparkle = ctx.createOscillator();
        const sGain = ctx.createGain();
        sparkle.type = 'triangle';
        sparkle.frequency.setValueAtTime(freq, ctx.currentTime);
        sGain.gain.setValueAtTime(0, ctx.currentTime);
        sGain.gain.linearRampToValueAtTime(0.08, ctx.currentTime + 0.02);
        sGain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
        sparkle.connect(sGain);
        sGain.connect(ctx.destination);
        sparkle.start(ctx.currentTime + i * 0.06);
        sparkle.stop(ctx.currentTime + i * 0.06 + 0.3);
      });
    }, 250);
  } catch (err) {}
}

function triggerScreenShake() {
  document.body.style.animation = 'screenShake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97)';
  setTimeout(() => { document.body.style.animation = ''; }, 500);
}

function createCircleExpand(x, y, currentTheme) {
  const color = currentTheme === 'light' ? '#8b5cf6' : '#0f0a1f';
  const circle = document.createElement('div');
  circle.style.cssText = `position:fixed;left:${x}px;top:${y}px;width:40px;height:40px;margin-left:-20px;margin-top:-20px;border-radius:50%;background:radial-gradient(circle,${color} 0%,${color}dd 60%,transparent 100%);pointer-events:none;z-index:99990;opacity:0.9;transform:scale(0);animation:circleExpand 1.1s cubic-bezier(0.4,0,0.2,1) forwards;`;
  document.body.appendChild(circle);
  setTimeout(() => circle.remove(), 1200);
}
function createRippleRings(x, y, currentTheme) {
  const color = currentTheme === 'light' ? '#8b5cf6' : '#a78bfa';
  for (let i = 0; i < 3; i++) {
    setTimeout(() => {
      const ring = document.createElement('div');
      ring.style.cssText = `position:fixed;left:${x}px;top:${y}px;width:20px;height:20px;margin-left:-10px;margin-top:-10px;border-radius:50%;border:3px solid ${color};pointer-events:none;z-index:99992;transform:scale(0);box-shadow:0 0 30px ${color};animation:ringExpand 1s cubic-bezier(0.4,0,0.2,1) forwards;`;
      document.body.appendChild(ring);
      setTimeout(() => ring.remove(), 1100);
    }, i * 150);
  }
}
function createStarBurst(x, y, currentTheme) {
  const colors = currentTheme === 'light' ? ['#8b5cf6', '#ec4899', '#22d3ee', '#fbbf24'] : ['#a78bfa', '#22d3ee', '#ec4899', '#fbbf24'];
  for (let i = 0; i < 8; i++) {
    const angle = (Math.PI * 2 * i) / 8;
    const distance = 150 + Math.random() * 100;
    const px = Math.cos(angle) * distance, py = Math.sin(angle) * distance;
    const color = colors[i % colors.length];
    const star = document.createElement('div');
    star.innerText = '\u2726';
    star.style.cssText = `position:fixed;left:${x}px;top:${y}px;font-size:28px;color:${color};text-shadow:0 0 20px ${color},0 0 40px ${color};pointer-events:none;z-index:99993;--px:${px}px;--py:${py}px;animation:starFly 1.2s cubic-bezier(0.2,0.8,0.3,1) forwards;`;
    document.body.appendChild(star);
    setTimeout(() => star.remove(), 1300);
  }
}
function createConfetti(x, y) {
  const colors = ['#8b5cf6', '#a78bfa', '#ec4899', '#22d3ee', '#fbbf24', '#10b981', '#f472b6'];
  for (let i = 0; i < 100; i++) {
    const piece = document.createElement('div');
    const color = colors[Math.floor(Math.random() * colors.length)];
    const size = 6 + Math.random() * 10;
    const angle = Math.random() * Math.PI * 2;
    const velocity = 100 + Math.random() * 400;
    const px = Math.cos(angle) * velocity, py = Math.sin(angle) * velocity - 200;
    const rotation = Math.random() * 720 - 360;
    const duration = 1.5 + Math.random() * 1.5;
    const shape = Math.random() > 0.5 ? '50%' : '2px';
    piece.style.cssText = `position:fixed;left:${x}px;top:${y}px;width:${size}px;height:${size}px;background:${color};border-radius:${shape};pointer-events:none;z-index:99994;--px:${px}px;--py:${py + 600}px;--rot:${rotation}deg;animation:confettiFall ${duration}s cubic-bezier(0.2,0.8,0.3,1) forwards;box-shadow:0 0 ${size/2}px ${color};`;
    document.body.appendChild(piece);
    setTimeout(() => piece.remove(), duration * 1000 + 100);
  }
}
function createParticles(x, y, currentTheme) {
  const colors = currentTheme === 'light' ? ['#8b5cf6', '#a78bfa', '#ec4899', '#c4b5fd'] : ['#a78bfa', '#22d3ee', '#ec4899', '#8b5cf6'];
  for (let i = 0; i < 40; i++) {
    const p = document.createElement('div');
    const angle = (Math.PI * 2 * i) / 40 + Math.random() * 0.5;
    const distance = 200 + Math.random() * 400;
    const px = Math.cos(angle) * distance, py = Math.sin(angle) * distance;
    const size = 4 + Math.random() * 8;
    const color = colors[Math.floor(Math.random() * colors.length)];
    const duration = 0.8 + Math.random() * 0.6;
    p.style.cssText = `position:fixed;left:${x}px;top:${y}px;width:${size}px;height:${size}px;border-radius:50%;background:${color};box-shadow:0 0 ${size*2}px ${color};pointer-events:none;z-index:99991;--px:${px}px;--py:${py}px;animation:particleFly ${duration}s cubic-bezier(0.2,0.8,0.3,1) forwards;`;
    document.body.appendChild(p);
    setTimeout(() => p.remove(), duration * 1000 + 100);
  }
}
function createFlash() {
  const flash = document.createElement('div');
  flash.style.cssText = `position:fixed;inset:0;background:radial-gradient(circle at center,rgba(139,92,246,0.5),rgba(236,72,153,0.3),transparent);pointer-events:none;z-index:99989;opacity:0;animation:flashPulse 0.9s ease-out;`;
  document.body.appendChild(flash);
  setTimeout(() => flash.remove(), 1000);
}
function triggerStaggerColors() {
  document.querySelectorAll('header, .card, .tool-card, .stat-card, .box, .welcome, .container, footer, .tab, .btn, .avatar, .search-box input, .nav-links a').forEach((el, i) => {
    el.style.transition = `background-color 0.5s ease ${i * 0.03}s, color 0.5s ease ${i * 0.03}s, border-color 0.5s ease ${i * 0.03}s, box-shadow 0.5s ease ${i * 0.03}s`;
    setTimeout(() => { el.style.transition = ''; }, 1500 + i * 30);
  });
}
function updateThemeIcon(theme) {
  document.querySelectorAll('.theme-toggle').forEach(btn => {
    const iconName = theme === 'dark' ? 'sun' : 'moon';
    if (window.ICONS && window.ICONS[iconName]) {
      btn.innerHTML = window.ICONS[iconName];
    } else {
      btn.innerHTML = theme === 'dark' ? '\u2600' : '\uD83C\uDF19';
    }
    btn.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
  });
}

// ===== AUTO-FIX AVATAR (Logout confirm) =====
(function autoFixAvatar() {
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a.avatar').forEach(a => {
      const href = a.getAttribute('href');
      if (href === '/logout') {
        a.setAttribute('href', '#');
        a.setAttribute('onclick', 'confirmLogout(event)');
      }
    });
    // Remove any emoji in theme-toggle
    document.querySelectorAll('.theme-toggle').forEach(btn => {
      const txt = btn.textContent.trim();
      if (txt === '🌙' || txt === '☀️' || txt === '☀') {
        btn.innerHTML = '';
      }
    });
  });
})();

// ===== INJECT KEYFRAMES =====
(function injectMagicKeyframes() {
  if (document.getElementById('magic-keyframes')) return;
  const style = document.createElement('style');
  style.id = 'magic-keyframes';
  style.textContent = `
    @keyframes circleExpand { 0%{transform:scale(0);opacity:0.9;} 60%{transform:scale(30);opacity:0.7;} 100%{transform:scale(80);opacity:0;} }
    @keyframes ringExpand { 0%{transform:scale(0);opacity:1;} 100%{transform:scale(15);opacity:0;} }
    @keyframes particleFly { 0%{transform:translate(0,0) scale(1);opacity:1;} 100%{transform:translate(var(--px),var(--py)) scale(0);opacity:0;} }
    @keyframes starFly { 0%{transform:translate(0,0) scale(1) rotate(0deg);opacity:1;} 100%{transform:translate(var(--px),var(--py)) scale(0.5) rotate(360deg);opacity:0;} }
    @keyframes confettiFall { 0%{transform:translate(0,0) rotate(0deg);opacity:1;} 100%{transform:translate(var(--px),var(--py)) rotate(var(--rot));opacity:0;} }
    @keyframes flashPulse { 0%{opacity:0;} 30%{opacity:0.4;} 100%{opacity:0;} }
    @keyframes screenShake { 0%,100%{transform:translate(0,0);} 10%{transform:translate(-5px,-3px);} 20%{transform:translate(4px,2px);} 30%{transform:translate(-3px,3px);} 40%{transform:translate(3px,-2px);} 50%{transform:translate(-4px,1px);} 60%{transform:translate(2px,3px);} 70%{transform:translate(-2px,-2px);} 80%{transform:translate(3px,1px);} 90%{transform:translate(-1px,-1px);} }
    @keyframes rippleAnim { to { transform: scale(2.5); opacity: 0; } }
  `;
  document.head.appendChild(style);
})();

// ===== SCROLL REVEAL =====
(function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add('active');
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
  function observeAll() {
    document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale, .stagger')
      .forEach(el => observer.observe(el));
  }
  document.addEventListener('DOMContentLoaded', observeAll);
  setTimeout(observeAll, 500);
})();

// ===== COUNT-UP =====
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

// ===== PARALLAX =====
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

// ===== RIPPLE =====
(function initRipple() {
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.calc-btn, .action-btn, .btn, .login-box button, .tab');
    if (!btn) return;
    const ripple = document.createElement('span');
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    ripple.style.cssText = `position:absolute;width:${size}px;height:${size}px;border-radius:50%;background:rgba(255,255,255,0.5);left:${x}px;top:${y}px;pointer-events:none;transform:scale(0);animation:rippleAnim 0.7s ease-out;z-index:1;`;
    if (getComputedStyle(btn).position === 'static') btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 700);
  });
})();

// ===== MAGNETIC =====
(function initMagnetic() {
  if (window.innerWidth < 900) return;
  document.querySelectorAll('.btn, .icon-btn, .theme-toggle, .avatar').forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate(${x * 0.25}px, ${y * 0.25}px)`;
    });
    btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
  });
})();

// ===== CARD TILT =====
(function initTilt() {
  if (window.innerWidth < 900) return;
  document.querySelectorAll('.card, .tool-card, .stat-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left, y = e.clientY - rect.top;
      const rotX = ((y - rect.height / 2) / (rect.height / 2)) * -6;
      const rotY = ((x - rect.width / 2) / (rect.width / 2)) * 6;
      card.style.transform = `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateY(-6px) scale(1.02)`;
    });
    card.addEventListener('mouseleave', () => { card.style.transform = ''; });
  });
})();

// ===== SMOOTH SCROLL =====
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

// ===== ACTIVE NAV =====
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

// ===== PAGE LOAD =====
document.addEventListener('DOMContentLoaded', () => {
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.5s ease';
  requestAnimationFrame(() => { document.body.style.opacity = '1'; });
  const theme = document.documentElement.getAttribute('data-theme') || 'light';
  updateThemeIcon(theme);
});
