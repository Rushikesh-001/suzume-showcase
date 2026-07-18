/* ============================================
   NOVACLOUD SAAS — Main JavaScript
   Particles, animations, interactions
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // ==========================================
  // 1. PARTICLE CANVAS SYSTEM
  // ==========================================
  const canvas = document.getElementById('particleCanvas');
  const ctx = canvas.getContext('2d');
  let particles = [];
  let mouseX = 0;
  let mouseY = 0;
  let animationId;

  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  class Particle {
    constructor() {
      this.reset();
    }

    reset() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.size = Math.random() * 2 + 0.5;
      this.speedX = (Math.random() - 0.5) * 0.5;
      this.speedY = (Math.random() - 0.5) * 0.5;
      this.opacity = Math.random() * 0.5 + 0.2;
    }

    update() {
      this.x += this.speedX;
      this.y += this.speedY;

      // Mouse interaction
      const dx = mouseX - this.x;
      const dy = mouseY - this.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 200) {
        const force = (200 - dist) / 200;
        this.x -= dx * force * 0.005;
        this.y -= dy * force * 0.005;
      }

      if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
      if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(108, 58, 255, ${this.opacity})`;
      ctx.fill();
    }
  }

  function initParticles(count = 80) {
    particles = [];
    for (let i = 0; i < count; i++) {
      particles.push(new Particle());
    }
  }

  function connectParticles() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 150) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(108, 58, 255, ${0.06 * (1 - dist / 150)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      p.update();
      p.draw();
    });
    connectParticles();
    animationId = requestAnimationFrame(animateParticles);
  }

  // Track mouse
  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  initParticles(100);
  animateParticles();

  // ==========================================
  // 2. SCROLL REVEAL (Intersection Observer)
  // ==========================================
  const revealElements = document.querySelectorAll('.reveal');

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const delay = parseInt(entry.target.dataset.delay) || 0;
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, delay);
        revealObserver.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  });

  revealElements.forEach(el => revealObserver.observe(el));

  // ==========================================
  // 3. NAVBAR SCROLL EFFECT
  // ==========================================
  const navbar = document.getElementById('navbar');

  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });

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
        // Close mobile menu
        document.getElementById('navLinks').classList.remove('open');
        document.getElementById('hamburger').classList.remove('active');
      }
    });
  });

  // ==========================================
  // 5. MOBILE HAMBURGER MENU
  // ==========================================
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('navLinks');

  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('open');
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
      hamburger.classList.remove('active');
      navLinks.classList.remove('open');
    }
  });

  // ==========================================
  // 6. 3D TILT EFFECT ON FEATURE CARDS
  // ==========================================
  const featureCards = document.querySelectorAll('.feature-card');

  featureCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = (y - centerY) / 10;
      const rotateY = (centerX - x) / 10;
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
    });
  });

  // ==========================================
  // 7. PRICING TOGGLE (Monthly / Yearly)
  // ==========================================
  const pricingToggle = document.getElementById('pricingToggle');
  const prices = document.querySelectorAll('.price');
  const monthlyLabel = document.getElementById('monthlyLabel');
  const yearlyLabel = document.getElementById('yearlyLabel');

  pricingToggle.addEventListener('change', () => {
    const isYearly = pricingToggle.checked;
    prices.forEach(priceEl => {
      const monthlyPrice = priceEl.dataset.monthly;
      const yearlyPrice = priceEl.dataset.yearly;
      priceEl.textContent = isYearly ? yearlyPrice : monthlyPrice;
    });
    monthlyLabel.classList.toggle('active', !isYearly);
    yearlyLabel.classList.toggle('active', isYearly);
  });

  // Initialize labels
  monthlyLabel.classList.add('active');

  // ==========================================
  // 8. COUNTER ANIMATION FOR STATS
  // ==========================================
  const statNumbers = document.querySelectorAll('.stat-number');

  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = parseInt(entry.target.dataset.target);
        animateCounter(entry.target, target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  statNumbers.forEach(el => counterObserver.observe(el));

  function animateCounter(element, target) {
    const duration = 2000;
    const steps = 60;
    const increment = target / steps;
    let current = 0;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      current = Math.min(current + increment, target);
      element.textContent = Math.round(current);
      if (step >= steps) {
        element.textContent = target.toLocaleString();
        clearInterval(timer);
      }
    }, duration / steps);
  }

  // ==========================================
  // 9. TESTIMONIAL CAROUSEL
  // ==========================================
  const track = document.getElementById('testimonialTrack');
  const dots = document.querySelectorAll('.dot');
  let currentSlide = 0;
  let autoSlideInterval;

  function goToSlide(index) {
    currentSlide = index;
    track.style.transform = `translateX(-${index * 100}%)`;
    dots.forEach((dot, i) => {
      dot.classList.toggle('active', i === index);
    });
  }

  function nextSlide() {
    goToSlide((currentSlide + 1) % dots.length);
  }

  function startAutoSlide() {
    autoSlideInterval = setInterval(nextSlide, 4000);
  }

  function stopAutoSlide() {
    clearInterval(autoSlideInterval);
  }

  dots.forEach(dot => {
    dot.addEventListener('click', () => {
      const index = parseInt(dot.dataset.index);
      goToSlide(index);
      stopAutoSlide();
      startAutoSlide();
    });
  });

  startAutoSlide();

  // Pause on hover
  const carousel = document.querySelector('.testimonial-carousel');
  carousel.addEventListener('mouseenter', stopAutoSlide);
  carousel.addEventListener('mouseleave', startAutoSlide);

  // ==========================================
  // 10. PARALLAX ON HERO (mouse move)
  // ==========================================
  const hero = document.querySelector('.hero');
  const heroContent = document.querySelector('.hero-content');
  const shapes = document.querySelectorAll('.shape');

  hero.addEventListener('mousemove', (e) => {
    const rect = hero.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;

    heroContent.style.transform = `translate(${x * 20}px, ${y * 20}px)`;

    shapes.forEach((shape, i) => {
      const speed = (i + 1) * 10;
      shape.style.transform = `translate(${x * speed}px, ${y * speed}px)`;
    });
  });

  hero.addEventListener('mouseleave', () => {
    heroContent.style.transform = 'translate(0, 0)';
    shapes.forEach(shape => {
      shape.style.transform = 'translate(0, 0)';
    });
  });

  // ==========================================
  // 11. PARALLAX ON SCROLL
  // ==========================================
  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    shapes.forEach((shape, i) => {
      const speed = (i + 1) * 0.05;
      shape.style.transform += ` translateY(${scrollY * speed}px)`;
    });
  });

  console.log('🚀 NovaCloud SaaS — All systems initialized');
});
