"""Mission overview: current incidents, communication links and response capacity."""

from html import escape
from pathlib import Path
import base64

import streamlit as st
import streamlit.components.v1 as components

from backend.connectivity import get_state
from backend.db import seed_demo_data
from backend.rescue import get_metrics
from backend.sos import get_all_requests
from utils.helpers import (
    section_heading,
    status_badge_html,
    priority_badge,
    comm_badge,
    rescue_badge,
)


def _render_earth_sun_hero() -> None:
    """Render a real interactive 3D Earth with a small orbiting Sun and stars."""
    image_path = Path(__file__).resolve().parents[1] / "assets" / "earth_texture.webp"
    if not image_path.is_file():
        st.title("Mission overview")
        st.caption("A clear picture of incoming emergencies, communication links and response capacity.")
        return

    image_data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    markup = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; background: transparent; }
  .rl-hero {
    position: relative; width: 100%; height: 430px; overflow: hidden;
    border: 1px solid rgba(105,157,190,.36); border-radius: 18px;
    background: radial-gradient(ellipse at 74% 48%, #102c45 0%, #08192b 43%, #040b15 100%);
    color: #f4f9fc; isolation: isolate;
    box-shadow: 0 14px 34px rgba(5,20,34,.18);
  }
  .rl-space-canvas { position:absolute; inset:0 0 0 37%; width:63%; height:100%; z-index:1; touch-action:none; }
  .rl-copy {
    position:relative; z-index:3; height:100%; width:47%; display:flex; flex-direction:column;
    justify-content:center; padding:34px 30px 34px 36px; pointer-events:none;
    background:linear-gradient(90deg, rgba(5,14,25,.98) 0%, rgba(5,14,25,.90) 64%, rgba(5,14,25,0) 100%);
  }
  .rl-eyebrow { color:#9fc9df; font-size:10px; letter-spacing:.17em; font-weight:800; text-transform:uppercase; }
  .rl-title { margin:13px 0 10px; color:#f7fbff; font-size:clamp(27px,3vw,38px); line-height:1.08; font-weight:760; letter-spacing:-.045em; }
  .rl-description { color:#d1e1ec; max-width:390px; font-size:14px; line-height:1.62; }
  .rl-note { display:inline-flex; align-self:flex-start; margin-top:19px; border:1px solid rgba(174,215,236,.25); border-radius:99px; padding:7px 10px; background:rgba(190,225,242,.08); color:#cfe4ef; font-size:9px; font-weight:700; letter-spacing:.06em; }
  .rl-hint { position:absolute; z-index:4; right:17px; bottom:14px; color:rgba(222,239,249,.78); font:600 10px/1.3 system-ui,sans-serif; letter-spacing:.025em; background:rgba(4,14,25,.54); border:1px solid rgba(174,215,236,.18); padding:7px 10px; border-radius:99px; pointer-events:none; }
  .rl-controls { position:absolute; z-index:5; right:16px; top:14px; display:flex; gap:7px; }
  .rl-controls button { border:1px solid rgba(174,215,236,.3); color:#d9edf7; background:rgba(5,17,30,.65); border-radius:8px; padding:6px 9px; font:600 10px system-ui,sans-serif; cursor:pointer; backdrop-filter:blur(8px); }
  .rl-controls button:hover { background:rgba(34,75,103,.82); }
  .rl-fallback { position:absolute; z-index:2; right:6%; top:50%; transform:translateY(-50%); width:52%; color:#b5d2e2; font:12px system-ui,sans-serif; text-align:center; }
  @media(max-width:760px) {
    .rl-hero { height:500px; }
    .rl-space-canvas { inset:0; width:100%; opacity:.82; }
    .rl-copy { width:100%; height:100%; justify-content:flex-start; padding:27px 23px; background:linear-gradient(180deg,rgba(5,14,25,.96) 0%,rgba(5,14,25,.78) 42%,rgba(5,14,25,.02) 100%); }
    .rl-title { font-size:29px; }
    .rl-description { max-width:340px; }
    .rl-hint { bottom:12px; }
  }
</style>
<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"}}
</script>
</head>
<body>
<section class="rl-hero" aria-label="Interactive 3D Earth and orbiting Sun">
  <div class="rl-space-canvas" id="rl-space-canvas"></div>
  <div class="rl-copy">
    <div class="rl-eyebrow">RESCUE LINK · EARTH OBSERVATION</div>
    <div class="rl-title">One planet.<br>One connected response.</div>
    <div class="rl-description">Satellite-assisted emergency coordination, from the first SOS to field response — even when terrestrial networks are unavailable.</div>
    <div class="rl-note">INTERACTIVE 3D GLOBE · OPERATIONAL DATA BELOW</div>
  </div>
  <div class="rl-controls">
    <button id="rl-reset" type="button" title="Reset globe view">Reset view</button>
    <button id="rl-spin" type="button" title="Toggle automatic globe rotation">Pause spin</button>
  </div>
  <div class="rl-hint">Drag to rotate · Scroll to zoom</div>
  <div class="rl-fallback" id="rl-fallback">Loading interactive globe…</div>
</section>
<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

const host = document.getElementById('rl-space-canvas');
const fallback = document.getElementById('rl-fallback');
const textureData = 'data:image/webp;base64,__EARTH_TEXTURE__';

try {
  if (!host) throw new Error('Globe canvas container was not found');
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 100);
  camera.position.set(0, 0, 6.3);

  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.8));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  renderer.setClearColor(0x000000, 0);
  renderer.domElement.style.cssText = 'display:block;width:100%;height:100%;touch-action:none;cursor:grab;outline:none;';
  renderer.domElement.setAttribute('aria-label', 'Interactive 3D Earth. Drag to rotate and scroll to zoom.');
  host.appendChild(renderer.domElement);

  const world = new THREE.Group();
  scene.add(world);

  const texture = await new Promise((resolve, reject) => {
    new THREE.TextureLoader().load(textureData, resolve, undefined, reject);
  });
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 8);

  const earth = new THREE.Mesh(
    new THREE.SphereGeometry(1.48, 112, 112),
    new THREE.MeshPhongMaterial({
      map: texture,
      shininess: 16,
      specular: new THREE.Color(0x345879)
    })
  );
  earth.rotation.y = -0.26;
  world.add(earth);

  const atmosphere = new THREE.Mesh(
    new THREE.SphereGeometry(1.535, 96, 96),
    new THREE.ShaderMaterial({
      vertexShader: `varying vec3 vNormal; varying vec3 vViewPosition; void main(){ vec4 mvPosition=modelViewMatrix*vec4(position,1.0); vNormal=normalize(normalMatrix*normal); vViewPosition=-mvPosition.xyz; gl_Position=projectionMatrix*mvPosition; }`,
      fragmentShader: `varying vec3 vNormal; varying vec3 vViewPosition; void main(){ float rim=pow(1.0-max(dot(normalize(vNormal),normalize(vViewPosition)),0.0),2.15); gl_FragColor=vec4(0.12,0.48,1.0,rim*0.62); }`,
      transparent: true,
      side: THREE.BackSide,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    })
  );
  world.add(atmosphere);

  scene.add(new THREE.AmbientLight(0x91abc7, 1.0));
  const keyLight = new THREE.DirectionalLight(0xffe0b5, 2.1);
  keyLight.position.set(4, 2.5, 5);
  scene.add(keyLight);
  const blueFill = new THREE.DirectionalLight(0x3d79bd, 0.6);
  blueFill.position.set(-4, -1, -3);
  scene.add(blueFill);

  // Dense but restrained starfield behind the planet.
  const count = 1500;
  const points = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const radius = 7 + Math.random() * 17;
    const u = Math.random() * 2 - 1;
    const a = Math.random() * Math.PI * 2;
    const q = Math.sqrt(1 - u * u);
    points[i * 3] = radius * q * Math.cos(a);
    points[i * 3 + 1] = radius * u;
    points[i * 3 + 2] = radius * q * Math.sin(a) - 4;
  }
  const starGeometry = new THREE.BufferGeometry();
  starGeometry.setAttribute('position', new THREE.BufferAttribute(points, 3));
  const stars = new THREE.Points(
    starGeometry,
    new THREE.PointsMaterial({ color: 0xd8ebff, size: 0.026, transparent: true, opacity: 0.9, sizeAttenuation: true })
  );
  scene.add(stars);

  // The Sun is deliberately smaller than Earth and follows a visible tilted ellipse.
  const orbit = new THREE.Group();
  scene.add(orbit);
  const orbitCurve = new THREE.EllipseCurve(0, 0, 2.18, 0.72, 0, Math.PI * 2, false, 0.15);
  const orbitPoints = orbitCurve.getPoints(240).map(p => new THREE.Vector3(p.x, p.y, 0));
  const orbitLine = new THREE.LineLoop(
    new THREE.BufferGeometry().setFromPoints(orbitPoints),
    new THREE.LineBasicMaterial({ color: 0xd9ad72, transparent: true, opacity: 0.48 })
  );
  orbitLine.rotation.x = THREE.MathUtils.degToRad(18);
  orbitLine.rotation.y = THREE.MathUtils.degToRad(-12);
  scene.add(orbitLine);

  const sun = new THREE.Mesh(
    new THREE.SphereGeometry(0.145, 40, 40),
    new THREE.MeshBasicMaterial({ color: 0xffc267 })
  );
  scene.add(sun);
  const sunLight = new THREE.PointLight(0xffbd68, 22, 13, 2);
  scene.add(sunLight);
  const glowCanvas = document.createElement('canvas');
  glowCanvas.width = glowCanvas.height = 128;
  const gctx = glowCanvas.getContext('2d');
  const glow = gctx.createRadialGradient(64, 64, 1, 64, 64, 63);
  glow.addColorStop(0, 'rgba(255,244,205,0.95)');
  glow.addColorStop(0.2, 'rgba(255,190,92,0.52)');
  glow.addColorStop(1, 'rgba(255,163,60,0)');
  gctx.fillStyle = glow;
  gctx.fillRect(0, 0, 128, 128);
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({
    map: new THREE.CanvasTexture(glowCanvas),
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  }));
  halo.scale.set(0.95, 0.95, 1);
  sun.add(halo);

  function resize() {
    const w = Math.max(host.clientWidth, 1);
    const h = Math.max(host.clientHeight, 1);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);
  }
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(host);
  window.addEventListener('resize', resize);
  resize();

  // Pointer controls are implemented directly so drag rotation works without OrbitControls imports.
  let dragging = false;
  let lastX = 0;
  let lastY = 0;
  let targetRotationX = 0;
  let targetRotationY = -0.26;
  let zoom = 6.3;
  renderer.domElement.addEventListener('pointerdown', event => {
    dragging = true;
    lastX = event.clientX;
    lastY = event.clientY;
    renderer.domElement.setPointerCapture(event.pointerId);
    renderer.domElement.style.cursor = 'grabbing';
  });
  renderer.domElement.addEventListener('pointermove', event => {
    if (!dragging) return;
    const dx = event.clientX - lastX;
    const dy = event.clientY - lastY;
    lastX = event.clientX;
    lastY = event.clientY;
    targetRotationY += dx * 0.006;
    targetRotationX = THREE.MathUtils.clamp(targetRotationX + dy * 0.006, -1.15, 1.15);
  });
  function stopDrag() {
    dragging = false;
    renderer.domElement.style.cursor = 'grab';
  }
  renderer.domElement.addEventListener('pointerup', stopDrag);
  renderer.domElement.addEventListener('pointercancel', stopDrag);
  renderer.domElement.addEventListener('wheel', event => {
    event.preventDefault();
    zoom = THREE.MathUtils.clamp(zoom + event.deltaY * 0.006, 4.6, 9.2);
    camera.position.z = zoom;
  }, { passive: false });
  renderer.domElement.addEventListener('dblclick', () => {
    targetRotationX = 0;
    targetRotationY = -0.26;
    zoom = 6.3;
    camera.position.z = zoom;
  });

  let elapsed = 0;
  let previous = 0;
  let spinning = true;
  const spinButton = document.getElementById('rl-spin');
  const resetButton = document.getElementById('rl-reset');
  spinButton.textContent = 'Pause spin';
  spinButton.addEventListener('click', () => {
    spinning = !spinning;
    spinButton.textContent = spinning ? 'Pause spin' : 'Resume spin';
  });
  resetButton.addEventListener('click', () => {
    targetRotationX = 0;
    targetRotationY = -0.26;
    zoom = 6.3;
    camera.position.set(0, 0, zoom);
  });

  fallback.style.display = 'none';
  function animate(now) {
    requestAnimationFrame(animate);
    const dt = Math.min((now - previous) / 1000 || 0, 0.05);
    previous = now;
    if (spinning) {
      elapsed += dt;
      targetRotationY += dt * 0.12;
      stars.rotation.y += dt * 0.0015;
    }
    world.rotation.x += (targetRotationX - world.rotation.x) * 0.12;
    world.rotation.y += (targetRotationY - world.rotation.y) * 0.12;
    const angle = elapsed * 0.22;
    const sunX = 2.18 * Math.cos(angle);
    const sunY = 0.72 * Math.sin(angle);
    const sunZ = 0.35 * Math.sin(angle);
    sun.position.set(sunX, sunY, sunZ);
    sunLight.position.copy(sun.position);
    renderer.render(scene, camera);
  }
  requestAnimationFrame(animate);
  fallback.style.display = 'none';
} catch (error) {
  console.error('Rescue Link 3D globe failed to load:', error);
  fallback.style.display = 'block';
  fallback.textContent = '3D globe could not start. Check the browser console and internet connection.';
}
</script>
</body>
</html>"""
    markup = markup.replace("__EARTH_TEXTURE__", image_data)
    components.html(markup, height=448, scrolling=False)
def _channel_card(name: str, label: str, enabled: bool, description: str,
                  simulated: bool = False) -> str:
    if enabled:
        state_html = '<span class="rl-status" style="background:#EAF3EE;color:#347154">Available</span>'
        dot_color = "#4A9878"
    else:
        state_html = '<span class="rl-status" style="background:#F1F3F5;color:#788795">Standby</span>'
        dot_color = "#9AA8B3"
    sim_note = '<div class="rl-network-description">Simulation only</div>' if simulated else ""
    return f"""
    <div class="rl-network-card">
      <div class="rl-network-label">{escape(label)}</div>
      <div class="rl-network-name"><span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{dot_color};margin-right:7px;vertical-align:1px"></span>{escape(name)}</div>
      {state_html}
      <div class="rl-network-description">{escape(description)}</div>
      {sim_note}
    </div>
    """


def _incident_row(request: dict) -> str:
    level = str(request.get("priority", "low")).lower()
    badge = status_badge_html(priority_badge(level), level)
    description = request.get("description") or request.get("category", "Emergency report")
    description = escape(str(description))
    return f"""
    <div class="rl-incident-line">
      <div style="min-width:0">
        <div class="rl-incident-title">{escape(str(request.get('category', 'Incident')))}</div>
        <div class="rl-incident-meta">{escape(str(request.get('id', '')))} · {description[:92]}</div>
        <div class="rl-incident-meta">{int(request.get('people_affected') or 1)} people · {escape(rescue_badge(str(request.get('rescue_status', 'open'))))} · {escape(comm_badge(str(request.get('comm_status', 'pending'))))}</div>
      </div>
      <div>{badge}</div>
    </div>
    """


def show() -> None:
    _render_earth_sun_hero()

    metrics = get_metrics()
    state = get_state()
    requests = get_all_requests()

    # Snapshot metrics come directly from the SQLite-backed application state.
    metric_cols = st.columns(4, gap="medium")
    metric_values = [
        ("Recorded SOS", metrics["total"], "All requests in the local register"),
        ("Critical priority", metrics["critical"], "Requests flagged for urgent review"),
        ("Awaiting transmission", metrics["pending_transmission"], "Saved locally, not yet synced"),
        ("Teams available", metrics["available_teams"], "Rescue units ready for assignment"),
    ]
    for col, (label, value, note) in zip(metric_cols, metric_values):
        with col, st.container(border=True):
            st.metric(label, value)
            st.caption(note)

    section_heading("Communication network", "Cellular and internet are preferred routes. Satellite is the fallback in this prototype.")
    network_cols = st.columns(3, gap="medium")
    network = [
        ("Cellular network", "TERRESTRIAL LINK", bool(state["cellular"]), "4G / 5G mobile coverage"),
        ("Internet / Wi-Fi", "DATA LINK", bool(state["internet"]), "Broadband or local Wi-Fi"),
        ("Satellite link", "FALLBACK LINK", bool(state["satellite"]), "Satellite channel for store-and-forward", True),
    ]
    for col, item in zip(network_cols, network):
        with col:
            st.markdown(_channel_card(*item), unsafe_allow_html=True)

    active_count = sum(bool(state[key]) for key in ("cellular", "internet", "satellite"))
    if active_count:
        route_text = "At least one communication route is available. New SOS requests can be transmitted."
        route_badge = status_badge_html(f"{active_count} / 3 links available", "low")
    else:
        route_text = "All communication routes are unavailable. New SOS requests will remain safely queued locally."
        route_badge = status_badge_html("Offline mode", "critical")
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:10px 0 23px">'
        f'{route_badge}<span style="font-size:12px;color:#718295">{escape(route_text)}</span></div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.3, 0.9], gap="large")
    with left:
        section_heading("Incident activity", "Latest SOS requests saved in the local register.")
        if requests:
            with st.container(border=True):
                for request in requests[:6]:
                    st.markdown(_incident_row(request), unsafe_allow_html=True)
        else:
            with st.container(border=True):
                st.markdown(
                    """
                    <div class="rl-empty-state">
                      <div class="rl-empty-kicker">NO INCIDENTS RECORDED</div>
                      <div class="rl-empty-title">Your operations feed is ready.</div>
                      <div class="rl-empty-copy">Submit an SOS from the Citizen Portal, or load the three clearly labelled sample incidents to explore triage, mapping, transmission and team dispatch. Sample records are illustrative — they are not live emergency reports.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Load sample scenario", type="primary", use_container_width=True):
                    seed_demo_data()
                    st.rerun()
                st.caption("No sample data is added unless you choose to load it.")

    with right:
        section_heading("Response workflow", "From first report to field resolution.")
        with st.container(border=True):
            steps = [
                ("01", "Capture", "Record incident type, location and people affected."),
                ("02", "Store & forward", "Queue the request locally when every link is unavailable."),
                ("03", "Triage & dispatch", "Review priority, assign an available rescue team."),
                ("04", "Resolve", "Update response status and retain the communication history."),
            ]
            for number, title, copy in steps:
                st.markdown(
                    f'<div class="rl-step"><div class="rl-step-number">{number}</div>'
                    f'<div><div class="rl-step-title">{escape(title)}</div>'
                    f'<div class="rl-step-copy">{escape(copy)}</div></div></div>',
                    unsafe_allow_html=True,
                )

    st.markdown("")
    section_heading("Resilience layers", "The demo can record requests across changing communication conditions.")
    layer_cols = st.columns(3, gap="medium")
    layers = [
        ("01", "Terrestrial", "Cellular network", "Fast first route when mobile coverage is available."),
        ("02", "Connected", "Internet / Wi-Fi", "Alternative route for transmitting and synchronising requests."),
        ("03", "Satellite fallback", "Simulated channel", "Demonstrates the fallback workflow; no live satellite hardware is connected."),
    ]
    for col, (number, title, tag, copy) in zip(layer_cols, layers):
        with col, st.container(border=True):
            st.markdown(f'<div class="rl-network-label">RESILIENCE LAYER {number}</div>', unsafe_allow_html=True)
            st.markdown(f"**{title}**")
            st.caption(tag)
            st.write(copy)
