import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ─── Scene Data ───
const scenes = [
  {
    title: 'Suzume',
    desc: 'Supreme AI Companion — Full-Stack Architect, Game Developer, System Automation Force',
    color1: '#6C3AFF', color2: '#3B82F6',
    shape: 'torusKnot'
  },
  {
    title: 'Full-Stack Web',
    desc: 'React · Next.js · Node.js · Databases · APIs — Complete platforms from scratch',
    color1: '#F59E0B', color2: '#EF4444',
    shape: 'icosahedron'
  },
  {
    title: 'Game Development',
    desc: 'Unity · C# · 3D/2D Games · Physics · Animation — Interactive experiences',
    color1: '#10B981', color2: '#059669',
    shape: 'octahedron'
  },
  {
    title: 'System Automation',
    desc: 'PowerShell · Bash · Registry · Firewall · Processes — Full OS control',
    color1: '#EC4899', color2: '#DB2777',
    shape: 'dodecahedron'
  },
  {
    title: 'Data & AI/ML',
    desc: 'Python · Pandas · Web Scraping · ML Models · File Generation',
    color1: '#3B82F6', color2: '#2563EB',
    shape: 'sphere'
  },
  {
    title: 'UI/UX & Design',
    desc: 'CSS · Canvas · Particles · 3D Transforms · Animations — Pixel-perfect interfaces',
    color1: '#8B5CF6', color2: '#6C3AFF',
    shape: 'ring'
  },
  {
    title: '7 Specialist Agents',
    desc: 'worker-js · worker-python · worker-unity · worker-sys · worker-web · builder · reviewer',
    color1: '#06B6D4', color2: '#0891B2',
    shape: 'torus'
  }
];

let currentScene = 0;
let isTransitioning = false;

// ─── Setup ───
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 2, 12);

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: true,
  powerPreference: 'high-performance'
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.prepend(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.maxPolarAngle = Math.PI / 2.2;
controls.minDistance = 4;
controls.maxDistance = 20;
controls.target.set(0, 1, 0);

// ─── Lights ───
scene.add(new THREE.AmbientLight(0x222244, 0.4));

const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
dirLight.position.set(5, 10, 7);
dirLight.castShadow = true;
scene.add(dirLight);

const fillLight = new THREE.DirectionalLight('#6C3AFF', 0.3);
fillLight.position.set(-5, 0, 5);
scene.add(fillLight);

const rimLight = new THREE.DirectionalLight('#3B82F6', 0.4);
rimLight.position.set(0, -5, -5);
scene.add(rimLight);

const pointLight = new THREE.PointLight('#6C3AFF', 0.5, 15);
pointLight.position.set(0, 2, 4);
scene.add(pointLight);

// ─── Particle System ───
const particleCount = 2000;
const particleGeo = new THREE.BufferGeometry();
const positions = new Float32Array(particleCount * 3);
const colors = new Float32Array(particleCount * 3);
const sizes = new Float32Array(particleCount);

for (let i = 0; i < particleCount; i++) {
  positions[i*3] = (Math.random() - 0.5) * 50;
  positions[i*3+1] = (Math.random() - 0.5) * 30;
  positions[i*3+2] = (Math.random() - 0.5) * 50 - 10;

  const c = new THREE.Color().setHSL(0.7 + Math.random() * 0.15, 0.6, 0.4 + Math.random() * 0.3);
  colors[i*3] = c.r;
  colors[i*3+1] = c.g;
  colors[i*3+2] = c.b;

  sizes[i] = Math.random() * 3 + 1;
}

particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

const particleMat = new THREE.PointsMaterial({
  size: 0.1,
  vertexColors: true,
  transparent: true,
  opacity: 0.6,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
  sizeAttenuation: true
});

const particleSystem = new THREE.Points(particleGeo, particleMat);
scene.add(particleSystem);

// ─── Ground ───
const gridHelper = new THREE.GridHelper(20, 20, '#6C3AFF', '#3B82F6');
gridHelper.position.y = -0.5;
gridHelper.material.transparent = true;
gridHelper.material.opacity = 0.15;
scene.add(gridHelper);

const groundGeo = new THREE.PlaneGeometry(20, 20);
const groundMat = new THREE.MeshStandardMaterial({
  color: 0x07070F,
  roughness: 0.8,
  metalness: 0.2,
  transparent: true,
  opacity: 0.5,
});
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.5;
ground.receiveShadow = true;
scene.add(ground);

// ─── Main Object Group ───
const mainGroup = new THREE.Group();
scene.add(mainGroup);

function createShapeGeometry(type) {
  switch (type) {
    case 'torusKnot': return new THREE.TorusKnotGeometry(1.2, 0.4, 128, 16);
    case 'icosahedron': return new THREE.IcosahedronGeometry(1.2, 0);
    case 'octahedron': return new THREE.OctahedronGeometry(1.2, 0);
    case 'dodecahedron': return new THREE.DodecahedronGeometry(1.2, 0);
    case 'sphere': return new THREE.SphereGeometry(1.0, 32, 32);
    case 'ring': return new THREE.TorusGeometry(1.0, 0.3, 16, 48);
    case 'torus': return new THREE.TorusGeometry(1.2, 0.4, 16, 48);
    default: return new THREE.TorusKnotGeometry(1.2, 0.4, 128, 16);
  }
}

function buildScene(index) {
  isTransitioning = true;

  // Animate out
  const titleEl = document.getElementById('sceneTitle');
  const descEl = document.getElementById('sceneDesc');
  titleEl.classList.add('changing');
  descEl.classList.add('changing');

  // Clear old objects with disposal
  while (mainGroup.children.length > 0) {
    const child = mainGroup.children[0];
    if (child.geometry) child.geometry.dispose();
    if (child.material) {
      if (Array.isArray(child.material)) {
        child.material.forEach(m => m.dispose());
      } else {
        child.material.dispose();
      }
    }
    mainGroup.remove(child);
  }

  const data = scenes[index];
  const col1 = new THREE.Color(data.color1);
  const col2 = new THREE.Color(data.color2);

  // Main shape
  const shapeGeo = createShapeGeometry(data.shape);
  const shapeMat = new THREE.MeshPhysicalMaterial({
    color: col1,
    emissive: col2,
    emissiveIntensity: 0.15,
    metalness: 0.7,
    roughness: 0.2,
    clearcoat: 0.3,
    clearcoatRoughness: 0.4,
    transparent: true,
    opacity: 0.95,
  });
  const shape = new THREE.Mesh(shapeGeo, shapeMat);
  shape.position.y = 1.5;
  shape.castShadow = true;
  mainGroup.add(shape);

  // Orbital ring
  const ringGeo = new THREE.TorusGeometry(1.8, 0.04, 16, 64);
  const ringMat = new THREE.MeshPhysicalMaterial({
    color: col2,
    emissive: col1,
    emissiveIntensity: 0.2,
    metalness: 0.9,
    roughness: 0.1,
    transparent: true,
    opacity: 0.5,
  });
  const ring = new THREE.Mesh(ringGeo, ringMat);
  ring.position.y = 1.5;
  ring.rotation.x = Math.PI / 3;
  mainGroup.add(ring);

  // Second ring perpendicular
  const ring2Geo = new THREE.TorusGeometry(1.8, 0.03, 16, 64);
  const ring2Mat = new THREE.MeshPhysicalMaterial({
    color: col1,
    emissive: col2,
    emissiveIntensity: 0.15,
    metalness: 0.7,
    roughness: 0.2,
    transparent: true,
    opacity: 0.35,
  });
  const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
  ring2.position.y = 1.5;
  ring2.rotation.z = Math.PI / 3;
  mainGroup.add(ring2);

  // Orbiting particles
  const orbCount = 12;
  for (let i = 0; i < orbCount; i++) {
    const sphereGeo = new THREE.SphereGeometry(0.06, 8, 8);
    const sphereMat = new THREE.MeshPhysicalMaterial({
      color: col1,
      emissive: col2,
      emissiveIntensity: 0.4,
    });
    const sphere = new THREE.Mesh(sphereGeo, sphereMat);
    const angle = (i / orbCount) * Math.PI * 2;
    sphere.position.set(
      Math.cos(angle) * 2.4,
      1.5 + Math.sin(angle * 3) * 0.4,
      Math.sin(angle) * 2.4
    );
    sphere.userData = {
      angle,
      speed: 0.3 + Math.random() * 0.4,
      radius: 2.4,
      baseY: 1.5,
      phaseOffset: Math.random() * Math.PI * 2
    };
    mainGroup.add(sphere);
  }

  // Glow particle field
  const gpCount = 300;
  const gpPos = new Float32Array(gpCount * 3);
  for (let i = 0; i < gpCount; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.random() * Math.PI * 2;
    const r = 2 + Math.random() * 4;
    gpPos[i*3] = Math.sin(theta) * Math.cos(phi) * r;
    gpPos[i*3+1] = 1.5 + Math.sin(theta) * Math.sin(phi) * r;
    gpPos[i*3+2] = Math.cos(theta) * r;
  }
  const gpGeo = new THREE.BufferGeometry();
  gpGeo.setAttribute('position', new THREE.BufferAttribute(gpPos, 3));
  const gpMat = new THREE.PointsMaterial({
    size: 0.04,
    color: col1,
    transparent: true,
    opacity: 0.35,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const gpSystem = new THREE.Points(gpGeo, gpMat);
  gpSystem.userData = { isGlow: true };
  mainGroup.add(gpSystem);

  // Update UI after a short delay
  setTimeout(() => {
    titleEl.textContent = data.title;
    descEl.textContent = data.desc;
    titleEl.classList.remove('changing');
    descEl.classList.remove('changing');
  }, 200);

  updateDots(index);

  // Entrance animation
  mainGroup.scale.set(0.01, 0.01, 0.01);
  const start = performance.now();
  const duration = 1000;

  function entranceAnim(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const s = eased * (0.9 + 0.1 * Math.sin(progress * Math.PI * 2));
    mainGroup.scale.set(s, s, s);
    if (progress < 1) {
      requestAnimationFrame(entranceAnim);
    } else {
      mainGroup.scale.set(1, 1, 1);
      isTransitioning = false;
    }
  }
  requestAnimationFrame(entranceAnim);
}

// ─── Navigation ───
function goToScene(index) {
  if (index < 0 || index >= scenes.length || isTransitioning) return;
  currentScene = index;
  buildScene(index);
  controls.target.set(0, 1, 0);
}

function nextScene() { goToScene((currentScene + 1) % scenes.length); }
function prevScene() { goToScene((currentScene - 1 + scenes.length) % scenes.length); }

document.getElementById('nextBtn').addEventListener('click', nextScene);
document.getElementById('prevBtn').addEventListener('click', prevScene);

document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight') { e.preventDefault(); nextScene(); }
  if (e.key === 'ArrowLeft') { e.preventDefault(); prevScene(); }
});

function updateDots(active) {
  const container = document.getElementById('dotContainer');
  container.innerHTML = '';
  scenes.forEach((_, i) => {
    const dot = document.createElement('div');
    dot.className = 'ui-dot' + (i === active ? ' active' : '');
    dot.addEventListener('click', () => goToScene(i));
    container.appendChild(dot);
  });
}

// ─── Touch swipe ───
let touchStartX = 0;
document.addEventListener('touchstart', (e) => {
  touchStartX = e.changedTouches[0].screenX;
});
document.addEventListener('touchend', (e) => {
  const diff = e.changedTouches[0].screenX - touchStartX;
  if (Math.abs(diff) > 50) {
    diff > 0 ? prevScene() : nextScene();
  }
});

// ─── Animation Loop ───
const clock = new THREE.Clock();

function animate() {
  const t = clock.getElapsedTime();

  // Rotate main group
  mainGroup.rotation.y += 0.005;

  // Animate children
  mainGroup.children.forEach(child => {
    if (child.userData && child.userData.angle !== undefined) {
      const d = child.userData;
      d.angle += 0.008 * d.speed;
      child.position.x = Math.cos(d.angle) * d.radius;
      child.position.z = Math.sin(d.angle) * d.radius;
      child.position.y = d.baseY + Math.sin(t * d.speed + d.phaseOffset) * 0.3;
    }
    if (child.userData && child.userData.isGlow) {
      child.rotation.y += 0.001;
      child.rotation.x += 0.0005;
    }
  });

  // Main shape animation
  const shape = mainGroup.children[0];
  if (shape) {
    shape.position.y = 1.5 + Math.sin(t * 0.5) * 0.15;
    shape.rotation.x += 0.008;
    shape.rotation.z += 0.005;
  }

  // Ring animations
  const ring = mainGroup.children[1];
  if (ring) {
    ring.rotation.z = t * 0.3;
    ring.rotation.y = t * 0.2;
  }
  const ring2 = mainGroup.children[2];
  if (ring2) {
    ring2.rotation.x = t * 0.25;
    ring2.rotation.z = t * 0.15;
  }

  // Particle drift
  particleSystem.rotation.y += 0.0003;

  // Pulsing light
  pointLight.intensity = 0.4 + Math.sin(t * 0.8) * 0.15;

  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

// ─── Resize ───
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ─── Init ───
setTimeout(() => {
  document.getElementById('loading').classList.add('hidden');
  document.getElementById('uiOverlay').classList.add('visible');
  buildScene(0);
  animate();
}, 2200);
