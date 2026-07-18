/* ============================================
   SUZUME PRESENTATION — Main JavaScript
   Slide engine, particles, animations
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // ==========================================
  // 1. PARTICLE CANVAS
  // ==========================================
  const canvas = document.getElementById('particleCanvas');
  const ctx = canvas.getContext('2d');
  let particles = [];
  let mouseX = 0;
  let mouseY = 0;

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
      this.size = Math.random() * 2.5 + 0.5;
      this.speedX = (Math.random() - 0.5) * 0.4;
      this.speedY = (Math.random() - 0.5) * 0.4;
      this.opacity = Math.random() * 0.4 + 0.1;
      this.hue = Math.random() * 60 + 240; // purple-blue range
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
        this.x -= dx * force * 0.003;
        this.y -= dy * force * 0.003;
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
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(108, 58, 255, ${0.04 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  let animationId;

  function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      p.update();
      p.draw();
    });
    connectParticles();
    animationId = requestAnimationFrame(animateParticles);
  }

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  initParticles(80);
  animateParticles();

  // ==========================================
  // 2. SLIDE ENGINE
  // ==========================================
  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.nav-dot');
  const progressBar = document.getElementById('progressBar');
  const slideCounter = document.getElementById('slideCounter');
  let currentSlide = 0;
  const totalSlides = slides.length;
  let isTransitioning = false;
  let autoplayInterval = null;
  let autoplayActive = false;

  function updateSlide(index, direction) {
    if (isTransitioning || index === currentSlide) return;
    if (index < 0 || index >= totalSlides) return;

    isTransitioning = true;

    const current = slides[currentSlide];
    const next = slides[index];

    // Direction classes for exit animation
    const exitDir = direction === 'next' ? 'exit-left' : 'exit-right';

    // Remove active from current, add exit direction
    current.classList.remove('active');
    current.classList.add(exitDir);

    // Make next slide active
    next.classList.remove('exit-left', 'exit-right');
    next.classList.add('active');

    // Trigger staggered entrance animations by reflow
    void next.offsetWidth;

    // Update state
    currentSlide = index;

    // Update UI
    updateProgress();
    updateDots();
    updateCounter();

    // Cleanup exit classes after transition
    setTimeout(() => {
      current.classList.remove(exitDir);
      isTransitioning = false;
    }, 800);
  }

  function goToSlide(index) {
    if (index === currentSlide) return;
    const direction = index > currentSlide ? 'next' : 'prev';
    updateSlide(index, direction);
  }

  function nextSlide() {
    if (currentSlide < totalSlides - 1) {
      goToSlide(currentSlide + 1);
    }
  }

  function prevSlide() {
    if (currentSlide > 0) {
      goToSlide(currentSlide - 1);
    }
  }

  function updateProgress() {
    const progress = ((currentSlide + 1) / totalSlides) * 100;
    progressBar.style.width = `${progress}%`;
  }

  function updateDots() {
    dots.forEach((dot, i) => {
      dot.classList.toggle('active', i === currentSlide);
    });
  }

  function updateCounter() {
    slideCounter.textContent = `${currentSlide + 1} / ${totalSlides}`;
  }

  // ==========================================
  // 3. KEYBOARD NAVIGATION
  // ==========================================
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'ArrowDown') {
      e.preventDefault();
      nextSlide();
    }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      prevSlide();
    }
    if (e.key === 'p' || e.key === 'P') {
      toggleAutoplay();
    }
    if (e.key === 'Home') {
      goToSlide(0);
    }
    if (e.key === 'End') {
      goToSlide(totalSlides - 1);
    }
  });

  // ==========================================
  // 4. DOT NAVIGATION
  // ==========================================
  dots.forEach(dot => {
    dot.addEventListener('click', () => {
      const index = parseInt(dot.dataset.index);
      goToSlide(index);
      stopAutoplay();
    });
  });

  // ==========================================
  // 5. TOUCH / SWIPE SUPPORT
  // ==========================================
  let touchStartX = 0;
  let touchStartY = 0;

  document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
  }, { passive: true });

  document.addEventListener('touchend', (e) => {
    const diffX = touchStartX - e.changedTouches[0].screenX;
    const diffY = touchStartY - e.changedTouches[0].screenY;
    // Only trigger if horizontal swipe is dominant
    if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
      if (diffX > 0) {
        nextSlide();
      } else {
        prevSlide();
      }
      stopAutoplay();
    }
  }, { passive: true });

  // ==========================================
  // 6. AUTOPLAY
  // ==========================================
  function toggleAutoplay() {
    if (autoplayActive) {
      stopAutoplay();
    } else {
      startAutoplay();
    }
  }

  function startAutoplay() {
    if (autoplayInterval) clearInterval(autoplayInterval);
    autoplayActive = true;
    autoplayInterval = setInterval(() => {
      if (currentSlide >= totalSlides - 1) {
        goToSlide(0);
      } else {
        nextSlide();
      }
    }, 4000);
    // Show status
    console.log('▶️ Autoplay started');
  }

  function stopAutoplay() {
    if (autoplayInterval) {
      clearInterval(autoplayInterval);
      autoplayInterval = null;
    }
    autoplayActive = false;
  }

  // ==========================================
  // 7. TYPEWRITER EFFECT (Slide 1)
  // ==========================================
  const typewriterEl = document.getElementById('typewriterText');
  const phrases = [
    'Your Supreme AI Companion',
    'Master Software Architect',
    'Absolute Automation Force',
    'Full-Stack Engineering Powerhouse'
  ];
  let phraseIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  let typewriterTimer;

  function typewriterEffect() {
    const currentPhrase = phrases[phraseIndex];

    if (!isDeleting) {
      // Typing
      charIndex++;
      typewriterEl.textContent = currentPhrase.substring(0, charIndex);
      if (charIndex === currentPhrase.length) {
        // Pause at end
        isDeleting = true;
        clearTimeout(typewriterTimer);
        typewriterTimer = setTimeout(typewriterEffect, 2000);
        return;
      }
    } else {
      // Deleting
      charIndex--;
      typewriterEl.textContent = currentPhrase.substring(0, charIndex);
      if (charIndex === 0) {
        isDeleting = false;
        phraseIndex = (phraseIndex + 1) % phrases.length;
        clearTimeout(typewriterTimer);
        typewriterTimer = setTimeout(typewriterEffect, 500);
        return;
      }
    }

    const speed = isDeleting ? 30 : 60;
    typewriterTimer = setTimeout(typewriterEffect, speed);
  }

  // Start typewriter only when slide 1 is active
  let typewriterStarted = false;

  function checkTypewriter() {
    if (currentSlide === 0 && !typewriterStarted) {
      typewriterStarted = true;
      typewriterEffect();
    } else if (currentSlide !== 0 && typewriterStarted) {
      // Don't stop it, let it run
    }
  }

  // Watch for slide changes to start typewriter
  const observer = new MutationObserver(() => {
    checkTypewriter();
  });

  slides[0].classList.contains('active') && checkTypewriter();

  // ==========================================
  // 8. RESTART BUTTON
  // ==========================================
  const restartBtn = document.getElementById('restartBtn');
  restartBtn.addEventListener('click', () => {
    goToSlide(0);
    stopAutoplay();
  });

  // ==========================================
  // 9. SCROLL WHEEL NAVIGATION
  // ==========================================
  let scrollTimeout = null;

  document.addEventListener('wheel', (e) => {
    if (scrollTimeout) return;
    scrollTimeout = setTimeout(() => {
      scrollTimeout = null;
    }, 1000);

    if (e.deltaY > 0) {
      nextSlide();
    } else {
      prevSlide();
    }
    stopAutoplay();
  }, { passive: true });

  // ==========================================
  // 10. INITIALIZE
  // ==========================================
  // Set initial state
  updateProgress();
  updateDots();
  updateCounter();

  // Make first slide elements animate in
  setTimeout(() => {
    slides[0].querySelectorAll('.trait-card, .flow-step, .agent-card, .power-card, .showcase-card');
  }, 100);

  console.log('🎯 Suzume Presentation — Ready');
  console.log(`📊 ${totalSlides} slides loaded`);
  console.log('⌨️  Arrow keys to navigate, P for autoplay');

  // ==========================================
  // 11. PARALLAX ON MOUSE MOVE FOR BG SHAPES
  // ==========================================
  document.querySelectorAll('.slide').forEach(slide => {
    slide.addEventListener('mousemove', (e) => {
      const shapes = slide.querySelectorAll('.bg-shape');
      const rect = slide.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;

      shapes.forEach((shape, i) => {
        const speed = (i + 1) * 15;
        shape.style.transform = `translate(${x * speed}px, ${y * speed}px)`;
      });
    });
  });
});
