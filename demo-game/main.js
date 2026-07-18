const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const highScoreEl = document.getElementById('highScore');
const overlay = document.getElementById('overlay');
const overlayTitle = document.getElementById('overlay-title');
const overlaySub = document.getElementById('overlay-sub');

const SIZE = 400;
const GRID = 20;
const CELL = SIZE / GRID;

const HIGH_SCORE_KEY = 'snake_highscore';

let snake, food, direction, nextDirection, directionQueue;
let score, highScore;
let state;
let lastMoveTime;
let moveInterval;
let foodEaten;
let animTime;
let touchStartX, touchStartY;

function initGame() {
  const mid = Math.floor(GRID / 2);
  snake = [
    { x: mid, y: mid },
    { x: mid - 1, y: mid },
    { x: mid - 2, y: mid }
  ];
  direction = { x: 1, y: 0 };
  nextDirection = { x: 1, y: 0 };
  directionQueue = [];
  score = 0;
  foodEaten = 0;
  moveInterval = 150;
  lastMoveTime = 0;
  animTime = 0;
  placeFood();
  updateScoreDisplay();
}

function placeFood() {
  const occupied = new Set(snake.map(s => `${s.x},${s.y}`));
  const free = [];
  for (let x = 0; x < GRID; x++) {
    for (let y = 0; y < GRID; y++) {
      if (!occupied.has(`${x},${y}`)) free.push({ x, y });
    }
  }
  if (free.length === 0) return;
  food = free[Math.floor(Math.random() * free.length)];
}

function updateScoreDisplay() {
  scoreEl.textContent = score;
  highScore = parseInt(localStorage.getItem(HIGH_SCORE_KEY) || '0');
  if (score > highScore) {
    highScore = score;
    localStorage.setItem(HIGH_SCORE_KEY, highScore);
  }
  highScoreEl.textContent = highScore;
}

function getSpeed() {
  return Math.max(60, moveInterval - foodEaten * 4);
}

function moveSnake() {
  const head = { x: snake[0].x + direction.x, y: snake[0].y + direction.y };

  if (head.x < 0 || head.x >= GRID || head.y < 0 || head.y >= GRID) {
    setState('gameover');
    return;
  }

  for (let i = 0; i < snake.length; i++) {
    if (snake[i].x === head.x && snake[i].y === head.y) {
      setState('gameover');
      return;
    }
  }

  snake.unshift(head);

  if (head.x === food.x && head.y === food.y) {
    score += 10;
    foodEaten++;
    updateScoreDisplay();
    placeFood();
  } else {
    snake.pop();
  }
}

function setState(newState) {
  state = newState;
  switch (state) {
    case 'menu':
      overlay.style.display = 'flex';
      overlayTitle.textContent = 'Press SPACE to start';
      overlaySub.textContent = '';
      break;
    case 'playing':
      overlay.style.display = 'none';
      break;
    case 'paused':
      overlay.style.display = 'flex';
      overlayTitle.textContent = 'PAUSED';
      overlaySub.textContent = 'Press P or Escape to resume';
      break;
    case 'gameover':
      overlay.style.display = 'flex';
      overlayTitle.textContent = 'Game Over!';
      overlaySub.textContent = `Score: ${score}  —  Press SPACE to restart`;
      break;
  }
}

function processDirectionQueue() {
  while (directionQueue.length > 0) {
    const dir = directionQueue.shift();
    if (dir.x + direction.x !== 0 || dir.y + direction.y !== 0) {
      nextDirection = dir;
      return;
    }
  }
}

function draw() {
  ctx.clearRect(0, 0, SIZE, SIZE);

  ctx.strokeStyle = '#1a1a1a';
  ctx.lineWidth = 0.5;
  for (let i = 0; i <= GRID; i++) {
    ctx.beginPath();
    ctx.moveTo(i * CELL, 0);
    ctx.lineTo(i * CELL, SIZE);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, i * CELL);
    ctx.lineTo(SIZE, i * CELL);
    ctx.stroke();
  }

  snake.forEach((seg, i) => {
    const t = i / Math.max(snake.length - 1, 1);
    const r = Math.round(30 + 60 * (1 - t));
    const g = Math.round(255);
    const b = Math.round(20 + 40 * (1 - t));
    ctx.fillStyle = `rgb(${r},${g},${b})`;
    const pad = i === 0 ? 1 : 2;
    const rad = i === 0 ? 5 : 3;
    const x = seg.x * CELL + pad;
    const y = seg.y * CELL + pad;
    const w = CELL - pad * 2;
    const h = CELL - pad * 2;
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, rad);
    ctx.fill();
  });

  if (food) {
    const pulse = 1 + 0.08 * Math.sin(animTime * 0.006);
    const centerX = food.x * CELL + CELL / 2;
    const centerY = food.y * CELL + CELL / 2;
    const radius = (CELL / 2 - 3) * pulse;
    ctx.shadowColor = '#ff3333';
    ctx.shadowBlur = 12;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.fillStyle = '#ff3333';
    ctx.fill();
    ctx.shadowBlur = 0;

    ctx.beginPath();
    ctx.arc(centerX - 3, centerY - 3, radius * 0.3, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.fill();
  }

  if (state === 'playing') {
    animTime += 16;
  }
}

function gameLoop(timestamp) {
  if (state === 'playing') {
    const interval = getSpeed();
    if (timestamp - lastMoveTime >= interval) {
      processDirectionQueue();
      direction = { ...nextDirection };
      moveSnake();
      lastMoveTime = timestamp;
    }
  }

  draw();
  requestAnimationFrame(gameLoop);
}

function handleKey(e) {
  const key = e.key;
  const prevent = new Set(['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ', 'p', 'P', 'Escape', 'w', 'W', 'a', 'A', 's', 'S', 'd', 'D']);
  if (prevent.has(key)) e.preventDefault();

  const dirMap = {
    ArrowUp: { x: 0, y: -1 }, 'w': { x: 0, y: -1 }, 'W': { x: 0, y: -1 },
    ArrowDown: { x: 0, y: 1 }, 's': { x: 0, y: 1 }, 'S': { x: 0, y: 1 },
    ArrowLeft: { x: -1, y: 0 }, 'a': { x: -1, y: 0 }, 'A': { x: -1, y: 0 },
    ArrowRight: { x: 1, y: 0 }, 'd': { x: 1, y: 0 }, 'D': { x: 1, y: 0 },
  };

  if (dirMap[key] && (state === 'playing' || state === 'menu')) {
    const dir = dirMap[key];
    if (dir.x + direction.x !== 0 || dir.y + direction.y !== 0) {
      directionQueue.push(dir);
    }
    if (state === 'menu' && dir.x !== 0) {
      initGame();
      setState('playing');
    }
    return;
  }

  if (key === ' ' || key === 'Space') {
    e.preventDefault();
    if (state === 'menu') {
      initGame();
      setState('playing');
    } else if (state === 'gameover') {
      initGame();
      setState('playing');
    }
  }

  if ((key === 'p' || key === 'P' || key === 'Escape') && (state === 'playing' || state === 'paused')) {
    setState(state === 'playing' ? 'paused' : 'playing');
  }
}

function handleTouchStart(e) {
  const touch = e.touches[0];
  touchStartX = touch.clientX;
  touchStartY = touch.clientY;
}

function handleTouchEnd(e) {
  if (!touchStartX || !touchStartY) return;
  const touch = e.changedTouches[0];
  const dx = touch.clientX - touchStartX;
  const dy = touch.clientY - touchStartY;
  const absDx = Math.abs(dx);
  const absDy = Math.abs(dy);
  if (Math.max(absDx, absDy) < 20) return;

  let dir;
  if (absDx > absDy) {
    dir = { x: dx > 0 ? 1 : -1, y: 0 };
  } else {
    dir = { x: 0, y: dy > 0 ? 1 : -1 };
  }

  if (state === 'menu') {
    if (dir.x !== 0) {
      initGame();
      setState('playing');
    }
    return;
  }

  if (state === 'playing') {
    if (dir.x + direction.x !== 0 || dir.y + direction.y !== 0) {
      directionQueue.push(dir);
    }
  }

  if (state === 'gameover') {
    initGame();
    setState('playing');
  }
}

document.addEventListener('keydown', handleKey);
canvas.addEventListener('touchstart', handleTouchStart, { passive: true });
canvas.addEventListener('touchend', handleTouchEnd, { passive: true });

initGame();
setState('menu');
requestAnimationFrame(gameLoop);
