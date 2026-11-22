"""Interactive 3D Space Orbiter component for Rescue Link.

Renders an interactive WebGL scene featuring a rotating Earth,
a glowing Sun casting realistic daylight and shadows, an orbiting Moon,
and simulated satellite constellations (ISRO NavIC and Starlink) for ASTRA 2026.
"""

import streamlit as st
import streamlit.components.v1 as components


def get_space_orbiter_html() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; user-select:none; }
  body, html { width:100%; height:100%; overflow:hidden; background:#050813; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  #container { width:100%; height:100%; position:relative; }
  canvas { display:block; width:100%; height:100%; }

  /* Glassmorphic Space HUD */
  .hud-badge {
    position:absolute; padding:7px 13px; border-radius:8px;
    background:rgba(8, 14, 26, 0.78); border:1px solid rgba(56, 189, 248, 0.28);
    backdrop-filter:blur(10px); color:#F1F5F9; font-size:11px;
    pointer-events:none; z-index:10; box-shadow:0 4px 20px rgba(0,0,0,0.5);
  }
  .hud-top-left { top:12px; left:14px; }
  .hud-top-right { top:12px; right:14px; text-align:right; }
  .hud-bottom-left { bottom:12px; left:14px; }
  .hud-bottom-right { bottom:12px; right:14px; text-align:right; }

  .hud-dot {
    display:inline-block; width:7px; height:7px; border-radius:50%;
    margin-right:6px; vertical-align:1px;
  }
  .dot-cyan { background:#38BDF8; box-shadow:0 0 8px #38BDF8; }
  .dot-sun { background:#F59E0B; box-shadow:0 0 10px #F59E0B; }
  .dot-moon { background:#94A3B8; box-shadow:0 0 6px #94A3B8; }
  .dot-pulse { animation:blink 1.8s infinite ease-in-out; }
  @keyframes blink { 0%, 100% { opacity:0.3; } 50% { opacity:1; } }

  /* Interactive control pill */
  .hud-controls {
    position:absolute; bottom:12px; left:50%; transform:translateX(-50%);
    display:flex; gap:8px; z-index:20;
  }
  .hud-btn {
    padding:5px 12px; border-radius:6px; font-size:10px; font-weight:700;
    color:#E2E8F0; background:rgba(15, 23, 42, 0.85); border:1px solid rgba(56, 189, 248, 0.3);
    cursor:pointer; backdrop-filter:blur(8px); transition:all 120ms ease;
  }
  .hud-btn:hover {
    background:#0284C7; color:#FFFFFF; border-color:#38BDF8;
    box-shadow:0 0 12px rgba(14, 165, 233, 0.5);
  }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div id="container">
  <!-- HUD Overlays -->
  <div class="hud-badge hud-top-left">
    <div><span class="hud-dot dot-cyan dot-pulse"></span><strong>RESCUE LINK · ORBITAL OPERATIONS</strong></div>
    <div style="color:#94A3B8;font-size:10px;margin-top:2px">ASTRA 2026 · DOMAIN 03 & 04 · VIT BHOPAL</div>
  </div>

  <div class="hud-badge hud-top-right">
    <div><span class="hud-dot dot-sun"></span><strong>SOLAR ILLUMINATION: 1,361 W/m²</strong></div>
    <div style="color:#94A3B8;font-size:10px;margin-top:2px"><span class="hud-dot dot-moon"></span>LUNAR DISTANCE: 384,400 KM</div>
  </div>

  <div class="hud-badge hud-bottom-left">
    <div style="color:#38BDF8;font-weight:700">🛰️ ACTIVE CONSTELLATION: ISRO NavIC + LEO MESH</div>
    <div style="color:#64748B;font-size:10px">STORE-AND-FORWARD BURST BUFFER: 0% LOSS (CRC32 VERIFIED)</div>
  </div>

  <div class="hud-badge hud-bottom-right">
    <div style="color:#94A3B8;font-size:10px">🖱️ CLICK & DRAG TO ROTATE · SCROLL TO ZOOM</div>
  </div>

  <div class="hud-controls">
    <button class="hud-btn" id="btn-pause">⏸ Pause</button>
    <button class="hud-btn" id="btn-pulse">⚡ Telemetry Burst</button>
    <button class="hud-btn" id="btn-reset">🎯 Reset Camera</button>
  </div>
</div>

<script>
(function() {
  const container = document.getElementById('container');
  const width = container.clientWidth || window.innerWidth;
  const height = container.clientHeight || window.innerHeight;

  // Scene & Camera
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x050813, 0.012);

  const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
  camera.position.set(0, 2.8, 8.2);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  container.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.minDistance = 3.6;
  controls.maxDistance = 16.0;
  controls.enablePan = false;

  // 1. Procedural Texture Generator for Earth Surface
  function createEarthTexture() {
    const c = document.createElement('canvas');
    c.width = 2048;
    c.height = 1024;
    const ctx = c.getContext('2d');

    // Deep Ocean Background with subtle gradient
    const oceanGrad = ctx.createLinearGradient(0, 0, 0, 1024);
    oceanGrad.addColorStop(0, '#0a2342');
    oceanGrad.addColorStop(0.5, '#0e315b');
    oceanGrad.addColorStop(1, '#0a2342');
    ctx.fillStyle = oceanGrad;
    ctx.fillRect(0, 0, 2048, 1024);

    // Lat/Lon coordinate grid lines
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.08)';
    ctx.lineWidth = 1;
    for (let x = 0; x < 2048; x += 128) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 1024); ctx.stroke();
    }
    for (let y = 0; y < 1024; y += 128) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(2048, y); ctx.stroke();
    }

    // Draw Landmasses & Continents
    ctx.fillStyle = '#2d5a3f'; // Lush landmass
    ctx.strokeStyle = '#3e6b48';
    ctx.lineWidth = 2;

    function drawPolygon(points, fillCol = '#2d5a3f', borderCol = '#3e6b48') {
      ctx.beginPath();
      ctx.fillStyle = fillCol;
      ctx.strokeStyle = borderCol;
      ctx.moveTo(points[0][0], points[0][1]);
      for (let i = 1; i < points.length; i++) ctx.lineTo(points[i][0], points[i][1]);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }

    // India (Center of ASTRA Operations: Lon ~77E, Lat ~23N)
    // Canvas coords: X = (lon+180)/360 * 2048 = ~1460, Y = (90-lat)/180 * 1024 = ~380
    const indiaPoints = [
      [1430, 320], [1480, 320], [1520, 350], [1510, 420],
      [1480, 490], [1460, 520], [1440, 490], [1410, 420], [1400, 360]
    ];
    drawPolygon(indiaPoints, '#38734c', '#52b788');

    // Asia & Himalayas
    drawPolygon([[1350, 240], [1650, 220], [1750, 320], [1650, 440], [1520, 350], [1430, 320], [1340, 310]]);
    // Africa
    drawPolygon([[1020, 360], [1160, 360], [1220, 460], [1180, 680], [1110, 750], [1030, 640], [980, 440]]);
    // Europe
    drawPolygon([[1020, 220], [1220, 200], [1280, 290], [1140, 340], [1020, 330]]);
    // Americas
    drawPolygon([[380, 180], [620, 200], [540, 380], [450, 420], [320, 300]]); // North
    drawPolygon([[480, 450], [580, 520], [600, 650], [520, 820], [460, 720], [440, 520]]); // South
    // Australia
    drawPolygon([[1680, 660], [1820, 650], [1850, 780], [1720, 820], [1660, 740]]);

    // Highlight Bhopal / India Distress Beacon Pin
    ctx.fillStyle = '#38BDF8';
    ctx.shadowColor = '#38BDF8';
    ctx.shadowBlur = 15;
    ctx.beginPath();
    ctx.arc(1460, 410, 6, 0, Math.PI * 2);
    ctx.fill();

    // Pulse Ring around India
    ctx.strokeStyle = '#FCD34D';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.arc(1460, 410, 14, 0, Math.PI * 2);
    ctx.stroke();

    // City lights on night side
    ctx.shadowBlur = 0;
    ctx.fillStyle = '#FDE047';
    for (let i = 0; i < 400; i++) {
      const rx = 1000 + Math.random() * 800;
      const ry = 200 + Math.random() * 600;
      ctx.fillRect(rx, ry, 1.5, 1.5);
    }

    return new THREE.CanvasTexture(c);
  }

  // 2. Procedural Clouds Texture
  function createCloudTexture() {
    const c = document.createElement('canvas');
    c.width = 1024; c.height = 512;
    const ctx = c.getContext('2d');
    ctx.fillStyle = 'rgba(0,0,0,0)';
    ctx.fillRect(0, 0, 1024, 512);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
    for (let i = 0; i < 180; i++) {
      const x = Math.random() * 1024;
      const y = Math.random() * 512;
      const r = 20 + Math.random() * 60;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
    return new THREE.CanvasTexture(c);
  }

  // 3. Procedural Lunar Texture
  function createMoonTexture() {
    const c = document.createElement('canvas');
    c.width = 512; c.height = 256;
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#8E9AA7';
    ctx.fillRect(0, 0, 512, 256);

    // Craters and maria
    ctx.fillStyle = '#64748B';
    for (let i = 0; i < 70; i++) {
      const x = Math.random() * 512;
      const y = Math.random() * 256;
      const r = 4 + Math.random() * 22;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
    return new THREE.CanvasTexture(c);
  }

  // BUILD THE 3D SCENE OBJECTS
  // A. Deep Cosmic Starfield
  const starGeo = new THREE.BufferGeometry();
  const starCount = 1800;
  const starPos = new Float32Array(starCount * 3);
  for (let i = 0; i < starCount * 3; i += 3) {
    const rad = 60 + Math.random() * 80;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    starPos[i] = rad * Math.sin(phi) * Math.cos(theta);
    starPos[i+1] = rad * Math.sin(phi) * Math.sin(theta);
    starPos[i+2] = rad * Math.cos(phi);
  }
  starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
  const starMat = new THREE.PointsMaterial({ size: 1.2, color: 0xBAE6FD, transparent: true, opacity: 0.85 });
  const starField = new THREE.Points(starGeo, starMat);
  scene.add(starField);

  // B. The Small Sun & Sunlight
  const sunGroup = new THREE.Group();
  sunGroup.position.set(-18, 8, -12); // Positioned in distance casting directional rays

  const sunGeo = new THREE.SphereGeometry(1.2, 32, 32);
  const sunMat = new THREE.MeshBasicMaterial({ color: 0xFFF07A });
  const sunMesh = new THREE.Mesh(sunGeo, sunMat);
  sunGroup.add(sunMesh);

  // Sun Solar Flare Corona
  const coronaCanvas = document.createElement('canvas');
  coronaCanvas.width = 256; coronaCanvas.height = 256;
  const cCtx = coronaCanvas.getContext('2d');
  const cGrad = cCtx.createRadialGradient(128, 128, 10, 128, 128, 128);
  cGrad.addColorStop(0, 'rgba(255, 245, 160, 1.0)');
  cGrad.addColorStop(0.25, 'rgba(245, 158, 11, 0.7)');
  cGrad.addColorStop(0.6, 'rgba(234, 88, 12, 0.25)');
  cGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
  cCtx.fillStyle = cGrad;
  cCtx.fillRect(0, 0, 256, 256);

  const coronaTex = new THREE.CanvasTexture(coronaCanvas);
  const coronaMat = new THREE.SpriteMaterial({ map: coronaTex, blending: THREE.AdditiveBlending, color: 0xFFD166 });
  const coronaSprite = new THREE.Sprite(coronaMat);
  coronaSprite.scale.set(7.5, 7.5, 1);
  sunGroup.add(coronaSprite);
  scene.add(sunGroup);

  // Sunlight Lighting
  const sunPointLight = new THREE.PointLight(0xFFF7ED, 2.5, 80);
  sunPointLight.position.copy(sunGroup.position);
  scene.add(sunPointLight);

  const sunDirLight = new THREE.DirectionalLight(0xFFF7ED, 1.8);
  sunDirLight.position.copy(sunGroup.position);
  sunDirLight.target.position.set(0, 0, 0);
  scene.add(sunDirLight);
  scene.add(sunDirLight.target);

  // Faint ambient light for space contrast
  const ambientLight = new THREE.AmbientLight(0x0C1929, 0.45);
  scene.add(ambientLight);

  // C. Rotating Earth
  const earthGroup = new THREE.Group();
  earthGroup.rotation.z = (23.5 * Math.PI) / 180; // Earth axial tilt

  const earthRadius = 2.0;
  const earthGeo = new THREE.SphereGeometry(earthRadius, 64, 64);
  const earthMat = new THREE.MeshStandardMaterial({
    map: createEarthTexture(),
    roughness: 0.55,
    metalness: 0.1,
  });
  const earthMesh = new THREE.Mesh(earthGeo, earthMat);
  earthGroup.add(earthMesh);

  // Earth Clouds Layer
  const cloudGeo = new THREE.SphereGeometry(earthRadius + 0.025, 48, 48);
  const cloudMat = new THREE.MeshStandardMaterial({
    map: createCloudTexture(),
    transparent: true,
    opacity: 0.55,
    blending: THREE.NormalBlending,
  });
  const cloudMesh = new THREE.Mesh(cloudGeo, cloudMat);
  earthGroup.add(cloudMesh);

  // Earth Atmospheric Halo
  const atmoGeo = new THREE.SphereGeometry(earthRadius + 0.12, 32, 32);
  const atmoMat = new THREE.MeshBasicMaterial({
    color: 0x38BDF8,
    transparent: true,
    opacity: 0.14,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
  });
  const atmoMesh = new THREE.Mesh(atmoGeo, atmoMat);
  earthGroup.add(atmoMesh);

  scene.add(earthGroup);

  // D. Orbiting Moon
  const moonGroup = new THREE.Group();
  const moonRadius = 0.45;
  const moonDistance = 5.8;

  const moonGeo = new THREE.SphereGeometry(moonRadius, 32, 32);
  const moonMat = new THREE.MeshStandardMaterial({
    map: createMoonTexture(),
    roughness: 0.85,
    metalness: 0.05,
  });
  const moonMesh = new THREE.Mesh(moonGeo, moonMat);
  moonMesh.position.set(moonDistance, 0, 0);
  moonGroup.add(moonMesh);

  // Moon Orbit Trail
  const moonOrbitCurve = new THREE.EllipseCurve(0, 0, moonDistance, moonDistance, 0, 2 * Math.PI, false, 0);
  const moonOrbitPoints = moonOrbitCurve.getPoints(100).map(p => new THREE.Vector3(p.x, 0, p.y));
  const moonOrbitGeo = new THREE.BufferGeometry().setFromPoints(moonOrbitPoints);
  const moonOrbitMat = new THREE.LineBasicMaterial({ color: 0x94A3B8, transparent: true, opacity: 0.25 });
  const moonOrbitLine = new THREE.Line(moonOrbitGeo, moonOrbitMat);
  moonOrbitLine.rotation.x = Math.PI / 2;
  scene.add(moonOrbitLine);
  scene.add(moonGroup);

  // E. Satellites (ASTRA 2026 Domains 03 & 04)
  // 1. ISRO NavIC Constellation Satellite (GSO)
  const navicGroup = new THREE.Group();
  navicGroup.rotation.x = 29 * Math.PI / 180; // Inclined GSO
  const navicDist = 3.6;

  // NavIC Orbit Line
  const navicOrbitCurve = new THREE.EllipseCurve(0, 0, navicDist, navicDist, 0, 2 * Math.PI, false, 0);
  const navicOrbitPoints = navicOrbitCurve.getPoints(90).map(p => new THREE.Vector3(p.x, 0, p.y));
  const navicOrbitGeo = new THREE.BufferGeometry().setFromPoints(navicOrbitPoints);
  const navicOrbitMat = new THREE.LineDashedMaterial({ color: 0xFCD34D, dashSize: 0.2, gapSize: 0.1, transparent: true, opacity: 0.5 });
  const navicOrbitLine = new THREE.Line(navicOrbitGeo, navicOrbitMat);
  navicOrbitLine.computeLineDistances();
  navicGroup.add(navicOrbitLine);

  // NavIC Satellite Body
  const satBody = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 0.18), new THREE.MeshStandardMaterial({ color: 0xF59E0B, metalness: 0.8 }));
  const satSolarL = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.08, 0.01), new THREE.MeshStandardMaterial({ color: 0x0284C7, metalness: 0.6 }));
  satSolarL.position.x = -0.28;
  const satSolarR = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.08, 0.01), new THREE.MeshStandardMaterial({ color: 0x0284C7, metalness: 0.6 }));
  satSolarR.position.x = 0.28;
  const satDish = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.01, 0.08, 16), new THREE.MeshBasicMaterial({ color: 0xE2E8F0 }));
  satDish.rotation.x = Math.PI / 2;
  satDish.position.z = 0.12;

  const navicSat = new THREE.Group();
  navicSat.add(satBody); navicSat.add(satSolarL); navicSat.add(satSolarR); navicSat.add(satDish);
  navicSat.position.set(navicDist, 0, 0);
  navicGroup.add(navicSat);
  scene.add(navicGroup);

  // 2. Starlink LEO Constellation Satellite
  const leoGroup = new THREE.Group();
  leoGroup.rotation.x = -53 * Math.PI / 180;
  const leoDist = 2.45;

  const leoOrbitCurve = new THREE.EllipseCurve(0, 0, leoDist, leoDist, 0, 2 * Math.PI, false, 0);
  const leoOrbitPoints = leoOrbitCurve.getPoints(80).map(p => new THREE.Vector3(p.x, 0, p.y));
  const leoOrbitGeo = new THREE.BufferGeometry().setFromPoints(leoOrbitPoints);
  const leoOrbitLine = new THREE.Line(leoOrbitGeo, new THREE.LineBasicMaterial({ color: 0x38BDF8, transparent: true, opacity: 0.35 }));
  leoGroup.add(leoOrbitLine);

  const leoSatMesh = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 16), new THREE.MeshBasicMaterial({ color: 0x38BDF8 }));
  leoSatMesh.position.set(leoDist, 0, 0);
  leoGroup.add(leoSatMesh);
  scene.add(leoGroup);

  // ANIMATION LOOP
  let isRotating = true;
  let moonAngle = 0;
  let navicAngle = 0;
  let leoAngle = 0;
  let burstPulse = false;

  function animate() {
    requestAnimationFrame(animate);

    if (isRotating) {
      // Axial rotation of Earth
      earthMesh.rotation.y += 0.0035;
      cloudMesh.rotation.y += 0.0042; // Clouds drift slightly faster

      // Moon orbits Earth
      moonAngle += 0.0022;
      moonMesh.position.x = Math.cos(moonAngle) * moonDistance;
      moonMesh.position.z = Math.sin(moonAngle) * moonDistance;
      moonMesh.rotation.y += 0.0022; // Tidally locked

      // Satellites orbit
      navicAngle += 0.006;
      navicSat.position.x = Math.cos(navicAngle) * navicDist;
      navicSat.position.y = Math.sin(navicAngle) * navicDist;
      navicSat.rotation.z = navicAngle + Math.PI / 2;

      leoAngle += 0.014;
      leoSatMesh.position.x = Math.cos(leoAngle) * leoDist;
      leoSatMesh.position.y = Math.sin(leoAngle) * leoDist;
    }

    // Solar flare shimmer
    const s = 7.5 + Math.sin(Date.now() * 0.003) * 0.3;
    coronaSprite.scale.set(s, s, 1);

    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  // Resize handler
  window.addEventListener('resize', () => {
    const w = container.clientWidth || window.innerWidth;
    const h = container.clientHeight || window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });

  // UI BUTTON LISTENERS
  document.getElementById('btn-pause').addEventListener('click', function() {
    isRotating = !isRotating;
    this.innerText = isRotating ? '⏸ Pause' : '▶ Rotate';
  });

  document.getElementById('btn-reset').addEventListener('click', function() {
    camera.position.set(0, 2.8, 8.2);
    controls.target.set(0, 0, 0);
    controls.update();
  });

  document.getElementById('btn-pulse').addEventListener('click', function() {
    // Flash satellite beams
    navicSat.scale.set(2, 2, 2);
    leoSatMesh.scale.set(2.5, 2.5, 2.5);
    setTimeout(() => {
      navicSat.scale.set(1, 1, 1);
      leoSatMesh.scale.set(1, 1, 1);
    }, 450);
  });
})();
</script>
</body>
</html>
"""


def render_space_orbiter(height: int = 500) -> None:
    """Render the 3D space orbiter scene inside a Streamlit container."""
    html_code = get_space_orbiter_html()
    components.html(html_code, height=height, scrolling=False)
