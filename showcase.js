/* ============================================
   SUZUME SHOWREEL — Cinematic Engine
   Scene transitions, particles, reveals
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // ==========================================
  // 1. PARTICLE CANVAS
  // ==========================================
  const canvas = document.getElementById('particleCanvas');
  const ctx = canvas.getContext('2d');
  let particles = [];
  let mouseX = 0, mouseY = 0;

  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.size = Math.random() * 2 + 0.5;
      this.speedX = (Math.random() - 0.5) * 0.5;
      this.speedY = (Math.random() - 0.5) * 0.5;
      this.opacity = Math.random() * 0.4 + 0.1;
      this.hue = Math.random() * 60 + 240;
    }
    update() {
      this.x += this.speedX;
      this.y += this.speedY;
      const dx = mouseX - this.x;
      const dy = mouseY - this.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 200) {
        const force = (200 - dist) / 200;
        this.x -= dx * force * 0.004;
        this.y -= dy * force * 0.004;
      }
      if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
      if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
    }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${this.hue}, 70%, 60%, ${this.opacity})`;
      ctx.fill();
    }
  }

  function initParticles(count = 60) {
    particles = [];
    for (let i = 0; i < count; i++) particles.push(new Particle());
  }

  function connectParticles() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 130) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(108, 58, 255, ${0.04 * (1 - dist / 130)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => { p.update(); p.draw(); });
    connectParticles();
    requestAnimationFrame(animateParticles);
  }

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  initParticles(70);
  animateParticles();

  // ==========================================
  // 2. NAVBAR SCROLL EFFECT
  // ==========================================
  const nav = document.querySelector('.showreel-nav');

  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 100);
  });

  // ==========================================
  // 3. SCROLL REVEAL — Intersection Observer
  // ==========================================
  const revealElements = document.querySelectorAll(
    '.cap-card, .flow-node, .team-card, .project-card'
  );

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const delay = parseInt(entry.target.dataset.delay) || 0;
        setTimeout(() => {
          entry.target.classList.add('revealed');
        }, delay);
        revealObserver.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -60px 0px'
  });

  revealElements.forEach(el => revealObserver.observe(el));

  // ==========================================
  // 4. SMOOTH SCROLL FOR NAV LINKS
  // ==========================================
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      const targetId = link.getAttribute('href');
      if (targetId === '#') return;
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ==========================================
  // 5. CINEMATIC FADE BETWEEN SCENES
  // ==========================================
  const scenes = document.querySelectorAll('.scene');

  const sceneObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const allScenes = document.querySelectorAll('.scene');
        allScenes.forEach(s => s.classList.remove('scene-active'));
        entry.target.classList.add('scene-active');
      }
    });
  }, { threshold: 0.3 });

  scenes.forEach(s => sceneObserver.observe(s));

  // ==========================================
  // 6. DEMO CARD PARALLAX ON HOVER
  // ==========================================
  document.querySelectorAll('.demo-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      const preview = card.querySelector('.demo-preview');
      if (preview) {
        preview.style.transform = `scale(1.02) translate(${x * 8}px, ${y * 8}px)`;
      }
    });

    card.addEventListener('mouseleave', () => {
      const preview = card.querySelector('.demo-preview');
      if (preview) {
        preview.style.transform = 'scale(1) translate(0, 0)';
      }
    });
  });

  // ==========================================
  // 7. TITLE CHARACTER SEQUENCE (Trigger on load)
  // ==========================================
  // Already handled by CSS animation-delay

  // ==========================================
  // 8. VIDEO TIMELINE — Auto-advance feel
  // ==========================================
  // Progress bar that shows scroll progress
  const progressBar = document.createElement('div');
  progressBar.className = 'scroll-progress';
  progressBar.style.cssText = `
    position: fixed;
    bottom: 0;
    left: 0;
    height: 2px;
    background: linear-gradient(90deg, #6C3AFF, #3B82F6, #10B981);
    z-index: 10000;
    width: 0%;
    transition: width 0.1s linear;
    box-shadow: 0 0 10px rgba(108,58,255,0.5);
  `;
  document.body.appendChild(progressBar);

  window.addEventListener('scroll', () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (scrollTop / docHeight) * 100;
    progressBar.style.width = `${Math.min(progress, 100)}%`;
  });

  // ==========================================
  // 9. KEYBOARD NAVIGATION
  // ==========================================
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown' || e.key === ' ') {
      e.preventDefault();
      const nextScene = document.querySelector('.scene:not(.scene-active)');
      if (nextScene) nextScene.scrollIntoView({ behavior: 'smooth' });
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      const scenes = document.querySelectorAll('.scene');
      let currentIdx = -1;
      scenes.forEach((s, i) => {
        if (s.classList.contains('scene-active')) currentIdx = i;
      });
      if (currentIdx > 0) {
        scenes[currentIdx - 1].scrollIntoView({ behavior: 'smooth' });
      }
    }
  });

  // ==========================================
  // 10. PARALLAX ON BG GLOWS
  // ==========================================
  document.querySelectorAll('.scene').forEach(scene => {
    scene.addEventListener('mousemove', (e) => {
      const glows = scene.querySelectorAll('.bg-glow');
      const rect = scene.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      glows.forEach((glow, i) => {
        const speed = (i + 1) * 20;
        glow.style.transform = `translate(${x * speed}px, ${y * speed}px)`;
      });
    });
  });

  // ==========================================
  // 11. FADE IN ON LOAD
  // ==========================================
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 1s ease';
  setTimeout(() => { document.body.style.opacity = '1'; }, 100);

  console.log('🎬 SUZUME Showreel — Loaded');
  console.log('📍 Scenes:', scenes.length);
  console.log('⌨️  Arrow keys to navigate scenes');
});
