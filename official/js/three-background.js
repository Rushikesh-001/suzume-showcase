/**
 * Three.js 3D Hero Background for Suzume Official Site
 * Rotating torus knot + particle sphere with mouse interaction
 */
(function() {
  'use strict';

  // Only run if Three.js loaded successfully
  if (typeof THREE === 'undefined') {
    console.warn('Three.js not loaded, skipping 3D background');
    return;
  }

  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;

  // ─── Scene Setup ───
  const scene = new THREE.Scene();
  
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 6;

  const renderer = new THREE.WebGLRenderer({ 
    canvas, 
    alpha: true, 
    antialias: true 
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;

  // ─── Mouse Tracking ───
  const mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
  
  document.addEventListener('mousemove', (e) => {
    mouse.targetX = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.targetY = -(e.clientY / window.innerHeight) * 2 + 1;
  });

  // ─── Torus Knot ───
  const geometry = new THREE.TorusKnotGeometry(1.2, 0.4, 180, 24);
  const material = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(0x6d3aff),
    emissive: new THREE.Color(0x3a1aff),
    emissiveIntensity: 0.15,
    metalness: 0.3,
    roughness: 0.4,
    clearcoat: 0.8,
    clearcoatRoughness: 0.2,
    transparent: true,
    opacity: 0.85,
  });
  const torusKnot = new THREE.Mesh(geometry, material);
  torusKnot.position.y = 0.2;
  scene.add(torusKnot);

  // ─── Secondary Outer Ring ───
  const ringGeo = new THREE.TorusGeometry(1.8, 0.05, 64, 100);
  const ringMat = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(0x8b5cf6),
    emissive: new THREE.Color(0x6d3aff),
    emissiveIntensity: 0.08,
    metalness: 0.5,
    roughness: 0.3,
    transparent: true,
    opacity: 0.3,
    wireframe: false,
  });
  const ring = new THREE.Mesh(ringGeo, ringMat);
  ring.rotation.x = Math.PI / 3;
  ring.rotation.z = Math.PI / 4;
  scene.add(ring);

  // ─── Particle Sphere ───
  const particleCount = 1800;
  const particlesGeo = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);
  const sizes = new Float32Array(particleCount);

  const color1 = new THREE.Color(0x8b5cf6); // purple
  const color2 = new THREE.Color(0x3b82f6); // blue
  const color3 = new THREE.Color(0xec4899); // pink

  for (let i = 0; i < particleCount; i++) {
    // Distribute on sphere surface with some randomness
    const radius = 3.0 + Math.random() * 1.5;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    
    positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = radius * Math.cos(phi);
    
    // Colors
    const c = Math.random() < 0.33 ? color1 : Math.random() < 0.5 ? color2 : color3;
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
    
    sizes[i] = 0.02 + Math.random() * 0.04;
  }

  particlesGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  particlesGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  particlesGeo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

  const particleMat = new THREE.PointsMaterial({
    size: 0.035,
    vertexColors: true,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true,
    depthWrite: false,
  });
  const particleSystem = new THREE.Points(particlesGeo, particleMat);
  scene.add(particleSystem);

  // ─── Connecting Lines (subtle web) ───
  const linePositions = [];
  const posAttr = particlesGeo.attributes.position;
  const maxDist = 1.2;
  
  for (let i = 0; i < 200; i++) {
    const idx1 = Math.floor(Math.random() * particleCount);
    const idx2 = Math.floor(Math.random() * particleCount);
    const x1 = posAttr.array[idx1 * 3];
    const y1 = posAttr.array[idx1 * 3 + 1];
    const z1 = posAttr.array[idx1 * 3 + 2];
    const x2 = posAttr.array[idx2 * 3];
    const y2 = posAttr.array[idx2 * 3 + 1];
    const z2 = posAttr.array[idx2 * 3 + 2];
    
    const dx = x2 - x1, dy = y2 - y1, dz = z2 - z1;
    const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
    
    if (dist < maxDist) {
      linePositions.push(x1, y1, z1, x2, y2, z2);
    }
  }

  const lineGeo = new THREE.BufferGeometry();
  lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
  const lineMat = new THREE.LineBasicMaterial({
    color: 0x6d3aff,
    transparent: true,
    opacity: 0.08,
  });
  const lineSystem = new THREE.LineSegments(lineGeo, lineMat);
  scene.add(lineSystem);

  // ─── Ambient Light ───
  const ambientLight = new THREE.AmbientLight(0x404060);
  scene.add(ambientLight);
  
  const dirLight = new THREE.DirectionalLight(0x8b5cf6, 2);
  dirLight.position.set(5, 5, 5);
  scene.add(dirLight);
  
  const dirLight2 = new THREE.DirectionalLight(0x3b82f6, 1);
  dirLight2.position.set(-5, -3, -5);
  scene.add(dirLight2);

  // ─── Resize Handler ───
  function resize() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }
  window.addEventListener('resize', resize);

  // ─── Animation Loop ───
  let time = 0;

  function animate() {
    requestAnimationFrame(animate);
    time += 0.005;

    // Smooth mouse follow
    mouse.x += (mouse.targetX - mouse.x) * 0.05;
    mouse.y += (mouse.targetY - mouse.y) * 0.05;

    // Rotate torus knot
    torusKnot.rotation.x += 0.005;
    torusKnot.rotation.y += 0.01;
    torusKnot.rotation.z += 0.003;

    // Mouse parallax on torus
    torusKnot.rotation.x += mouse.y * 0.01;
    torusKnot.rotation.y += mouse.x * 0.02;
    torusKnot.position.x += (mouse.x * 0.3 - torusKnot.position.x) * 0.03;
    torusKnot.position.y += (mouse.y * 0.3 - torusKnot.position.y) * 0.03;

    // Rotate ring
    ring.rotation.x += 0.002;
    ring.rotation.y += 0.004;
    ring.rotation.z += 0.001;

    // Rotate particle sphere (slow)
    particleSystem.rotation.x += 0.0005;
    particleSystem.rotation.y += 0.001;
    particleSystem.rotation.z += 0.0003;

    // Pulsing glow on torus
    const pulse = 0.6 + 0.4 * Math.sin(time * 2);
    material.emissiveIntensity = 0.08 + 0.12 * pulse;
    ringMat.emissiveIntensity = 0.04 + 0.08 * pulse;

    // Connecting lines follow particle rotation
    lineSystem.rotation.copy(particleSystem.rotation);

    renderer.render(scene, camera);
  }

  animate();
})();
