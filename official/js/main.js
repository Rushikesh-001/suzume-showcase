document.addEventListener('DOMContentLoaded', () => {

  // ============================================
  // 1. PARTICLE CANVAS — Hero Background
  // ============================================
  function initParticles() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let mouseX = 0, mouseY = 0;
    let animId;

    function resize() {
      const hero = canvas.parentElement;
      canvas.width = hero.offsetWidth;
      canvas.height = hero.offsetHeight;
    }

    function createParticles(count) {
      particles = [];
      for (let i = 0; i < count; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.6,
          vy: (Math.random() - 0.5) * 0.6,
          radius: Math.random() * 2.5 + 1,
          alpha: Math.random() * 0.5 + 0.3
        });
      }
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const isDark = document.documentElement.getAttribute('data-theme') !== 'light';

      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        const dx = mouseX - p.x;
        const dy = mouseY - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          p.x -= dx * 0.005;
          p.y -= dy * 0.005;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = isDark ? `rgba(124, 58, 237, ${p.alpha})` : `rgba(79, 70, 229, ${p.alpha * 0.6})`;
        ctx.fill();

        for (const other of particles) {
          const dx2 = p.x - other.x;
          const dy2 = p.y - other.y;
          const dist2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);
          if (dist2 < 150) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(other.x, other.y);
            ctx.strokeStyle = isDark
              ? `rgba(124, 58, 237, ${(1 - dist2 / 150) * 0.2})`
              : `rgba(79, 70, 229, ${(1 - dist2 / 150) * 0.12})`;
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }
      animId = requestAnimationFrame(draw);
    }

    function start() {
      resize();
      createParticles(100);
      draw();
    }

    window.addEventListener('resize', () => {
      resize();
      createParticles(100);
    });

    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
    });

    start();
    return { stop: () => cancelAnimationFrame(animId) };
  }

  // ============================================
  // 2. TYPEWRITER EFFECT
  // ============================================
  function initTypewriter() {
    const el = document.querySelector('.typewriter-text');
    if (!el) return;
    const text = 'Supreme AI Orchestrator';
    let index = 0;
    let isDeleting = false;

    function type() {
      if (!isDeleting) {
        el.textContent = text.substring(0, index + 1);
        index++;
        if (index === text.length) {
          setTimeout(() => { isDeleting = true; type(); }, 3000);
          return;
        }
        setTimeout(type, 80);
      } else {
        el.textContent = text.substring(0, index - 1);
        index--;
        if (index === 0) {
          isDeleting = false;
          setTimeout(type, 500);
          return;
        }
        setTimeout(type, 40);
      }
    }
    setTimeout(type, 500);
  }

  // ============================================
  // 3. 3D PERSPECTIVE TILT
  // ============================================
  function init3DTilt() {
    const cards = document.querySelectorAll('.bento-card, .demo-card');
    cards.forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -6;
        const rotateY = ((x - centerX) / centerX) * 6;
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
      });
    });

    const heroTitle = document.querySelector('.hero-title .title-text');
    if (heroTitle) {
      document.querySelector('.hero')?.addEventListener('mousemove', (e) => {
        const rect = heroTitle.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -12;
        const rotateY = ((x - centerX) / centerX) * 12;
        heroTitle.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
      });
    }
  }

  // ============================================
  // 4. SCROLL REVEAL
  // ============================================
  function initScrollReveal() {
    const els = document.querySelectorAll('.reveal');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    els.forEach(el => observer.observe(el));
  }

  // ============================================
  // 5. ANIMATED COUNTERS
  // ============================================
  function initCounters() {
    const statNumbers = document.querySelectorAll('.stat-number');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.getAttribute('data-target')) || 0;
          const suffix = el.getAttribute('data-suffix') || '';
          const duration = 2000;
          const startTime = performance.now();

          function animate(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(eased * target);
            el.textContent = current + suffix;
            if (progress < 1) {
              requestAnimationFrame(animate);
            } else {
              el.textContent = target + suffix;
            }
          }
          requestAnimationFrame(animate);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    statNumbers.forEach(el => observer.observe(el));
  }

  // ============================================
  // 6. THEME TOGGLE
  // ============================================
  function initThemeToggle() {
    const toggle = document.getElementById('theme-toggle');
    if (!toggle) return;
    const icon = toggle.querySelector('.theme-icon');

    const savedTheme = localStorage.getItem('suzume-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    icon.textContent = savedTheme === 'dark' ? '☀️' : '🌙';

    toggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      icon.textContent = next === 'dark' ? '☀️' : '🌙';
      localStorage.setItem('suzume-theme', next);
    });
  }

  // ============================================
  // 7. MAGNETIC BUTTONS
  // ============================================
  function initMagneticButtons() {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
      btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        btn.style.transform = `translate(${x / 8}px, ${y / 8}px)`;
      });
      btn.addEventListener('mouseleave', () => {
        btn.style.transform = 'translate(0, 0)';
      });
    });
  }

  // ============================================
  // 8. SMOOTH SCROLL
  // ============================================
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(anchor.getAttribute('href'));
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          document.querySelector('.nav-links')?.classList.remove('open');
          document.querySelector('.hamburger')?.classList.remove('active');
        }
      });
    });
  }

  // ============================================
  // 9. MOBILE HAMBURGER
  // ============================================
  function initHamburger() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    if (!hamburger || !navLinks) return;

    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('active');
      navLinks.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
        hamburger.classList.remove('active');
        navLinks.classList.remove('open');
      }
    });
  }

  // ============================================
  // 10. VIDEO PLAYER — FIXED VERSION
  // ============================================
  function initVideoPlayer() {
    const container = document.getElementById('video-container');
    if (!container) return;

    const video = document.getElementById('showcaseVideo');
    const overlay = document.getElementById('videoOverlay');
    const playBtn = document.getElementById('vcPlayBtn');
    const progressBar = document.getElementById('vcProgress');
    const progressFill = document.getElementById('vcProgressFill');
    const timeDisplay = document.getElementById('vcTime');

    if (!video) return;

    // Format time helper
    function formatTime(seconds) {
      const m = Math.floor(seconds / 60);
      const s = Math.floor(seconds % 60);
      return `${m}:${s.toString().padStart(2, '0')}`;
    }

    // Toggle play/pause
    function togglePlay() {
      if (video.paused) {
        video.play().catch(e => console.log('Play prevented:', e));
      } else {
        video.pause();
      }
    }

    // Update UI based on play state
    function updatePlayState() {
      if (video.paused) {
        container.classList.remove('playing');
        if (playBtn) playBtn.textContent = '▶';
      } else {
        container.classList.add('playing');
        if (playBtn) playBtn.textContent = '⏸';
      }
    }

    // Update progress
    function updateProgress() {
      if (video.duration) {
        const pct = (video.currentTime / video.duration) * 100;
        if (progressFill) progressFill.style.width = pct + '%';
        if (timeDisplay) {
          timeDisplay.textContent = formatTime(video.currentTime) + ' / ' + formatTime(video.duration);
        }
      }
    }

    // Click on overlay to play
    if (overlay) {
      overlay.addEventListener('click', togglePlay);
    }

    // Play/pause button
    if (playBtn) {
      playBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        togglePlay();
      });
    }

    // Click on video to toggle
    video.addEventListener('click', togglePlay);

    // Progress bar click
    if (progressBar) {
      progressBar.addEventListener('click', (e) => {
        const rect = progressBar.getBoundingClientRect();
        const pct = (e.clientX - rect.left) / rect.width;
        if (video.duration) {
          video.currentTime = pct * video.duration;
        }
      });
    }

    // Events
    video.addEventListener('play', updatePlayState);
    video.addEventListener('pause', updatePlayState);
    video.addEventListener('timeupdate', updateProgress);
    video.addEventListener('ended', () => {
      container.classList.remove('playing');
      if (playBtn) playBtn.textContent = '▶';
      if (timeDisplay && video.duration) {
        timeDisplay.textContent = '0:00 / ' + formatTime(video.duration);
      }
      if (progressFill) progressFill.style.width = '0%';
    });

    // Load metadata for duration display
    video.addEventListener('loadedmetadata', () => {
      if (timeDisplay && video.duration) {
        timeDisplay.textContent = '0:00 / ' + formatTime(video.duration);
      }
    });

    // Initial display
    if (timeDisplay && video.duration) {
      timeDisplay.textContent = '0:00 / ' + formatTime(video.duration);
    }

    // Keyboard: space to toggle
    document.addEventListener('keydown', (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === ' ' || e.key === 'Space') {
        const rect = container.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
        if (isVisible) {
          e.preventDefault();
          togglePlay();
        }
      }
    });
  }

  // ============================================
  // 11. NAVBAR PARALLAX (hide on scroll down)
  // ============================================
  function initNavParallax() {
    let lastScroll = 0;
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', () => {
      const currentScroll = window.pageYOffset;
      if (currentScroll > lastScroll && currentScroll > 100) {
        navbar.style.transform = 'translateY(-100%)';
      } else {
        navbar.style.transform = 'translateY(0)';
      }
      lastScroll = currentScroll;
    }, { passive: true });
  }

  // ============================================
  // INIT ALL
  // ============================================
  initParticles();
  initTypewriter();
  init3DTilt();
  initScrollReveal();
  initCounters();
  initThemeToggle();
  initMagneticButtons();
  initSmoothScroll();
  initHamburger();
  initVideoPlayer();
  initNavParallax();

  console.log('Suzume website initialized successfully.');
});
