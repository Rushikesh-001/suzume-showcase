// ═══════════════════════════════════════════
// PIXEL CANVAS — Drawing Application
// ═══════════════════════════════════════════

const GRID_SIZE = 32;
const CELL_SIZE = 10; // canvas is 320x320 = 32*10

const canvas = document.getElementById('pixelCanvas');
const ctx = canvas.getContext('2d');

let currentTool = 'pencil';
let brushSize = 2;
let currentColor = '#6C3AFF';
let isDrawing = false;
let undoStack = [];
let redoStack = [];
const MAX_UNDO = 30;

// ─── Canvas State ───
let pixelData = []; // 2D array of color strings

function initPixelData() {
  pixelData = [];
  for (let y = 0; y < GRID_SIZE; y++) {
    pixelData[y] = [];
    for (let x = 0; x < GRID_SIZE; x++) {
      pixelData[y][x] = '#1a1a2e'; // default dark color
    }
  }
}

function saveState() {
  const state = pixelData.map(row => [...row]);
  undoStack.push(state);
  if (undoStack.length > MAX_UNDO) undoStack.shift();
  redoStack = []; // clear redo on new action
}

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw pixels
  for (let y = 0; y < GRID_SIZE; y++) {
    for (let x = 0; x < GRID_SIZE; x++) {
      ctx.fillStyle = pixelData[y][x];
      ctx.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
    }
  }

  // Draw grid lines
  ctx.strokeStyle = 'rgba(255,255,255,0.08)';
  ctx.lineWidth = 0.5;
  for (let i = 0; i <= GRID_SIZE; i++) {
    ctx.beginPath();
    ctx.moveTo(i * CELL_SIZE, 0);
    ctx.lineTo(i * CELL_SIZE, canvas.height);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, i * CELL_SIZE);
    ctx.lineTo(canvas.width, i * CELL_SIZE);
    ctx.stroke();
  }
}

// ─── Drawing Logic ───
function getGridPos(clientX, clientY) {
  const rect = canvas.getBoundingClientRect();
  const x = Math.floor((clientX - rect.left) / rect.width * GRID_SIZE);
  const y = Math.floor((clientY - rect.top) / rect.height * GRID_SIZE);
  return { x, y };
}

function drawPixel(gridX, gridY, color) {
  if (gridX < 0 || gridX >= GRID_SIZE || gridY < 0 || gridY >= GRID_SIZE) return;

  const size = brushSize;
  const half = Math.floor(size / 2);

  for (let dy = -half; dy < size - half; dy++) {
    for (let dx = -half; dx < size - half; dx++) {
      const px = gridX + dx;
      const py = gridY + dy;
      if (px >= 0 && px < GRID_SIZE && py >= 0 && py < GRID_SIZE) {
        if (currentTool === 'eraser') {
          pixelData[py][px] = '#1a1a2e';
        } else {
          pixelData[py][px] = color;
        }
      }
    }
  }
}

// ─── Flood Fill ───
function floodFill(startX, startY, fillColor) {
  if (startX < 0 || startX >= GRID_SIZE || startY < 0 || startY >= GRID_SIZE) return;
  const targetColor = pixelData[startY][startX];
  if (targetColor === fillColor) return;

  const queue = [{ x: startX, y: startY }];
  const visited = new Set();

  while (queue.length > 0) {
    const { x, y } = queue.shift();
    const key = `${x},${y}`;
    if (visited.has(key)) continue;
    if (x < 0 || x >= GRID_SIZE || y < 0 || y >= GRID_SIZE) continue;
    if (pixelData[y][x] !== targetColor) continue;

    visited.add(key);
    pixelData[y][x] = fillColor;

    queue.push({ x: x + 1, y });
    queue.push({ x: x - 1, y });
    queue.push({ x, y: y + 1 });
    queue.push({ x, y: y - 1 });
  }
}

// ─── Eyedropper ───
function eyedropper(gridX, gridY) {
  if (gridX < 0 || gridX >= GRID_SIZE || gridY < 0 || gridY >= GRID_SIZE) return;
  currentColor = pixelData[gridY][gridX];
  updateColorUI();
}

// ─── Mouse Events ───
canvas.addEventListener('mousedown', (e) => {
  const pos = getGridPos(e.clientX, e.clientY);

  if (currentTool === 'fill') {
    saveState();
    floodFill(pos.x, pos.y, currentColor);
    render();
    return;
  }

  if (currentTool === 'eyedropper') {
    eyedropper(pos.x, pos.y);
    return;
  }

  isDrawing = true;
  saveState();
  drawPixel(pos.x, pos.y, currentColor);
  render();
  updatePos(pos);
});

canvas.addEventListener('mousemove', (e) => {
  const pos = getGridPos(e.clientX, e.clientY);
  updatePos(pos);

  if (isDrawing && (currentTool === 'pencil' || currentTool === 'eraser')) {
    drawPixel(pos.x, pos.y, currentColor);
    render();
  }
});

canvas.addEventListener('mouseup', () => { isDrawing = false; });
canvas.addEventListener('mouseleave', () => {
  isDrawing = false;
  document.getElementById('gridPos').textContent = '—';
});

// ─── Touch Support ───
canvas.addEventListener('touchstart', (e) => {
  e.preventDefault();
  const touch = e.touches[0];
  const pos = getGridPos(touch.clientX, touch.clientY);

  if (currentTool === 'fill') {
    saveState();
    floodFill(pos.x, pos.y, currentColor);
    render();
    return;
  }
  if (currentTool === 'eyedropper') {
    eyedropper(pos.x, pos.y);
    return;
  }

  isDrawing = true;
  saveState();
  drawPixel(pos.x, pos.y, currentColor);
  render();
}, { passive: false });

canvas.addEventListener('touchmove', (e) => {
  e.preventDefault();
  if (!isDrawing) return;
  const touch = e.touches[0];
  const pos = getGridPos(touch.clientX, touch.clientY);
  drawPixel(pos.x, pos.y, currentColor);
  render();
}, { passive: false });

canvas.addEventListener('touchend', () => { isDrawing = false; });

// ─── UI Updates ───
function updatePos(pos) {
  document.getElementById('gridPos').textContent = `${pos.x}, ${pos.y}`;
}

function updateColorUI() {
  document.getElementById('colorDisplay').style.background = currentColor;
  document.querySelectorAll('.color-swatch').forEach(s => {
    s.classList.toggle('active', s.dataset.color === currentColor);
  });
}

// ─── Tool Selection ───
document.querySelectorAll('.tool-btn[data-tool]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tool-btn[data-tool]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentTool = btn.dataset.tool;
  });
});

// ─── Brush Size ───
document.querySelectorAll('.brush-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.brush-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    brushSize = parseInt(btn.dataset.size);
  });
});

// ─── Color Selection ───
document.querySelectorAll('.color-swatch').forEach(swatch => {
  swatch.addEventListener('click', () => {
    currentColor = swatch.dataset.color;
    updateColorUI();
  });
});

document.getElementById('customColor').addEventListener('input', (e) => {
  currentColor = e.target.value;
  document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
  updateColorUI();
});

// ─── Undo / Redo ───
function undo() {
  if (undoStack.length === 0) return;
  const currentState = pixelData.map(row => [...row]);
  redoStack.push(currentState);

  pixelData = undoStack.pop().map(row => [...row]);
  render();
}

function redo() {
  if (redoStack.length === 0) return;
  const currentState = pixelData.map(row => [...row]);
  undoStack.push(currentState);

  pixelData = redoStack.pop().map(row => [...row]);
  render();
}

document.getElementById('undoBtn').addEventListener('click', undo);
document.getElementById('redoBtn').addEventListener('click', redo);
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'z') { e.preventDefault(); undo(); }
  if ((e.ctrlKey || e.metaKey) && e.key === 'y') { e.preventDefault(); redo(); }
});

// ─── Clear ───
document.getElementById('clearBtn').addEventListener('click', () => {
  if (confirm('Clear the entire canvas?')) {
    saveState();
    initPixelData();
    render();
  }
});

// ─── Export ───
document.getElementById('exportBtn').addEventListener('click', () => {
  // Create a properly scaled export canvas
  const exportCanvas = document.createElement('canvas');
  const scale = 16;
  exportCanvas.width = GRID_SIZE * scale;
  exportCanvas.height = GRID_SIZE * scale;
  const ectx = exportCanvas.getContext('2d');

  for (let y = 0; y < GRID_SIZE; y++) {
    for (let x = 0; x < GRID_SIZE; x++) {
      ectx.fillStyle = pixelData[y][x];
      ectx.fillRect(x * scale, y * scale, scale, scale);
    }
  }

  const link = document.createElement('a');
  link.download = 'pixel-art.png';
  link.href = exportCanvas.toDataURL('image/png');
  link.click();
});

// ─── Init ───
initPixelData();
render();
updateColorUI();
