/* ============================================================
   3D Bluetooth Speaker Hero – Three.js Scene
   ============================================================ */
(function () {
  'use strict';

  // --- Configuration ---
  const CONFIG = {
    autoRotateSpeed: 0.15,
    inertiaDamping: 0.92,
    zoomMin: 2.5,
    zoomMax: 7,
    colors: {
      midnight:   { primary: '#1a1a2e', accent: '#2563eb', led: '#00d4ff', mesh: '#2a2a3e' },
      pearl:      { primary: '#e8e8f0', accent: '#3b82f6', led: '#60a5fa', mesh: '#d4d4e0' },
      darkGray:   { primary: '#1e1e1e', accent: '#6b7280', led: '#38bdf8', mesh: '#2d2d2d' },
      roseGold:   { primary: '#b76e79', accent: '#e8a0b0', led: '#f472b6', mesh: '#c0848c' },
    },
  };

  // --- State ---
  let scene, camera, renderer, speakerGroup, particles, ledRing;
  let isDragging = false;
  let prevX = 0, prevY = 0;
  let velocityX = 0, velocityY = 0;
  let rotationX = 0.2, rotationY = 0;
  let targetZoom = 4.5;
  let currentZoom = 4.5;
  let autoRotate = true;
  let autoRotateTimer = null;
  let isFullscreen = false;
  let animationId = null;
  let clock = new THREE.Clock();
  let currentColor = 'midnight';
  let soundParticles = [];
  let glowPulse = 0;

  // --- DOM ---
  const container = document.getElementById('three-container');
  if (!container) return;

  // --- Color Swatch Listener ---
  document.querySelectorAll('.color-swatch').forEach(function (el) {
    el.addEventListener('click', function () {
      var color = el.dataset.color;
      document.querySelectorAll('.color-swatch').forEach(function (s) { s.classList.remove('active'); });
      el.classList.add('active');
      changeSpeakerColor(color);
    });
  });

  // --- Fullscreen Button ---
  var fsBtn = document.getElementById('speakerFullscreen');
  if (fsBtn) {
    fsBtn.addEventListener('click', function () {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(function () {});
      } else {
        document.exitFullscreen().catch(function () {});
      }
    });
  }

  // --- Three.js Setup ---
  function init() {
    // Scene
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050510, 0.015);

    // Camera
    var aspect = container.clientWidth / container.clientHeight;
    camera = new THREE.PerspectiveCamera(40, aspect, 0.1, 100);
    camera.position.set(0, 1.5, currentZoom);
    camera.lookAt(0, 0.5, 0);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.appendChild(renderer.domElement);

    // Lights
    setupLights();

    // Speaker
    createSpeaker();

    // Particles
    createParticles();

    // Events
    setupEvents();

    // Start
    animate();
  }

  // --- Lights ---
  function setupLights() {
    var ambient = new THREE.AmbientLight(0x4466aa, 0.3);
    scene.add(ambient);

    var keyLight = new THREE.DirectionalLight(0x88bbff, 1.8);
    keyLight.position.set(5, 8, 5);
    keyLight.castShadow = true;
    scene.add(keyLight);

    var fillLight = new THREE.DirectionalLight(0x6688cc, 0.6);
    fillLight.position.set(-4, 2, -3);
    scene.add(fillLight);

    var rimLight = new THREE.DirectionalLight(0x4488ff, 0.8);
    rimLight.position.set(0, -2, 6);
    scene.add(rimLight);

    var topLight = new THREE.DirectionalLight(0x88ccff, 0.4);
    topLight.position.set(0, 8, 0);
    scene.add(topLight);

    // Blue accent glow
    var glowLight = new THREE.PointLight(0x2563eb, 0.5, 8);
    glowLight.position.set(0, 0.2, 2);
    scene.add(glowLight);

    var glowLight2 = new THREE.PointLight(0x0ea5e9, 0.3, 6);
    glowLight2.position.set(0, 1.2, -2);
    scene.add(glowLight2);
  }

  // --- Create Speaker ---
  function createSpeaker() {
    speakerGroup = new THREE.Group();

    var cols = CONFIG.colors[currentColor];

    // ---- Body (Lathe profile) ----
    var bodyProfile = [];
    var segments = 20;
    for (var i = 0; i <= segments; i++) {
      var t = i / segments;
      var angle = t * Math.PI;
      var r, y;
      // Profile: bottom flair → straight → top curve
      if (t < 0.1) {
        y = 0;
        r = 1.2 + Math.sin(t / 0.1 * Math.PI / 2) * 0.15;
      } else if (t < 0.85) {
        y = 0.1 + (t - 0.1) / 0.75 * 1.6;
        r = 1.35 - (t - 0.1) / 0.75 * 0.15;
      } else {
        var topT = (t - 0.85) / 0.15;
        y = 1.7 + topT * 0.15;
        r = 1.2 - topT * 0.2;
      }
      bodyProfile.push(new THREE.Vector2(r, y));
    }
    var bodyGeom = new THREE.LatheGeometry(bodyProfile, 48);
    var bodyMat = new THREE.MeshPhysicalMaterial({
      color: cols.primary,
      metalness: 0.7,
      roughness: 0.25,
      clearcoat: 0.3,
      clearcoatRoughness: 0.4,
      envMapIntensity: 0.8,
    });
    var body = new THREE.Mesh(bodyGeom, bodyMat);
    body.castShadow = true;
    body.receiveShadow = true;
    speakerGroup.add(body);

    // ---- Fabric Mesh Ring ----
    var fabricGeom = new THREE.TorusGeometry(1.05, 0.08, 16, 48);
    var fabricMat = new THREE.MeshPhysicalMaterial({
      color: cols.mesh,
      metalness: 0.1,
      roughness: 0.9,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.6,
    });
    var fabricRing = new THREE.Mesh(fabricGeom, fabricMat);
    fabricRing.position.y = 0.85;
    fabricRing.rotation.x = Math.PI / 2;
    speakerGroup.add(fabricRing);

    var fabricRing2 = new THREE.Mesh(fabricGeom.clone(), fabricMat.clone());
    fabricRing2.position.y = 0.95;
    fabricRing2.rotation.x = Math.PI / 2;
    fabricRing2.scale.set(0.95, 0.95, 1);
    speakerGroup.add(fabricRing2);

    // ---- Driver Cone ----
    var coneGeom = new THREE.CircleGeometry(0.7, 32);
    var coneMat = new THREE.MeshPhysicalMaterial({
      color: '#111118',
      metalness: 0.3,
      roughness: 0.7,
      side: THREE.DoubleSide,
    });
    var cone = new THREE.Mesh(coneGeom, coneMat);
    cone.position.y = 1.02;
    cone.rotation.x = -Math.PI / 2;
    speakerGroup.add(cone);

    // Driver surround
    var surroundGeom = new THREE.RingGeometry(0.68, 0.75, 32);
    var surroundMat = new THREE.MeshPhysicalMaterial({
      color: '#222233',
      metalness: 0.2,
      roughness: 0.8,
      side: THREE.DoubleSide,
    });
    var surround = new THREE.Mesh(surroundGeom, surroundMat);
    surround.position.y = 1.01;
    surround.rotation.x = -Math.PI / 2;
    speakerGroup.add(surround);

    // Driver dust cap
    var capGeom = new THREE.SphereGeometry(0.25, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2);
    var capMat = new THREE.MeshPhysicalMaterial({
      color: '#1a1a2e',
      metalness: 0.6,
      roughness: 0.3,
    });
    var cap = new THREE.Mesh(capGeom, capMat);
    cap.position.y = 1.03;
    cap.scale.set(1, 1, 0.3);
    speakerGroup.add(cap);

    // ---- LED Ring at Bottom ----
    var ledGeom = new THREE.TorusGeometry(1.15, 0.04, 12, 48);
    var ledMat = new THREE.MeshPhysicalMaterial({
      color: cols.led,
      emissive: cols.led,
      emissiveIntensity: 0.8,
      metalness: 0.1,
      roughness: 0.3,
      transparent: true,
      opacity: 0.9,
    });
    ledRing = new THREE.Mesh(ledGeom, ledMat);
    ledRing.position.y = 0.08;
    ledRing.rotation.x = Math.PI / 2;
    speakerGroup.add(ledRing);

    // Inner LED strip
    var ledInnerGeom = new THREE.TorusGeometry(0.95, 0.02, 10, 48);
    var ledInnerMat = new THREE.MeshPhysicalMaterial({
      color: cols.led,
      emissive: cols.led,
      emissiveIntensity: 0.4,
      transparent: true,
      opacity: 0.5,
    });
    var ledInner = new THREE.Mesh(ledInnerGeom, ledInnerMat);
    ledInner.position.y = 0.1;
    ledInner.rotation.x = Math.PI / 2;
    speakerGroup.add(ledInner);

    // ---- Base ----
    var baseGeom = new THREE.CylinderGeometry(1.3, 1.4, 0.15, 32);
    var baseMat = new THREE.MeshPhysicalMaterial({
      color: '#0a0a14',
      metalness: 0.9,
      roughness: 0.2,
    });
    var base = new THREE.Mesh(baseGeom, baseMat);
    base.position.y = -0.07;
    base.receiveShadow = true;
    base.castShadow = true;
    speakerGroup.add(base);

    // Base ring
    var baseRingGeom = new THREE.TorusGeometry(1.35, 0.03, 10, 48);
    var baseRingMat = new THREE.MeshPhysicalMaterial({
      color: cols.accent,
      metalness: 0.8,
      roughness: 0.2,
    });
    var baseRing = new THREE.Mesh(baseRingGeom, baseRingMat);
    baseRing.position.y = 0;
    baseRing.rotation.x = Math.PI / 2;
    speakerGroup.add(baseRing);

    // ---- Top Controls ----
    // Power button
    var btnGeom = new THREE.CylinderGeometry(0.08, 0.08, 0.04, 16);
    var btnMat = new THREE.MeshPhysicalMaterial({
      color: cols.accent,
      metalness: 0.8,
      roughness: 0.2,
      emissive: cols.accent,
      emissiveIntensity: 0.1,
    });
    var powerBtn = new THREE.Mesh(btnGeom, btnMat);
    powerBtn.position.set(0, 1.88, 0);
    speakerGroup.add(powerBtn);

    // Volume buttons
    var volBtnMat = new THREE.MeshPhysicalMaterial({
      color: '#444466',
      metalness: 0.6,
      roughness: 0.3,
    });
    var volUp = new THREE.Mesh(
      new THREE.BoxGeometry(0.12, 0.03, 0.05),
      volBtnMat
    );
    volUp.position.set(0.35, 1.86, 0);
    volUp.rotation.x = 0.1;
    speakerGroup.add(volUp);

    var volDown = new THREE.Mesh(
      new THREE.BoxGeometry(0.12, 0.03, 0.05),
      volBtnMat
    );
    volDown.position.set(-0.35, 1.86, 0);
    volDown.rotation.x = -0.1;
    speakerGroup.add(volDown);

    // ---- Grille dots ----
    var dotMat = new THREE.MeshPhysicalMaterial({
      color: cols.mesh,
      metalness: 0.1,
      roughness: 0.8,
    });
    for (var i = 0; i < 120; i++) {
      var theta = Math.random() * Math.PI * 2;
      var r = 0.3 + Math.random() * 0.7;
      var yPos = 0.3 + Math.random() * 1.1;
      var dot = new THREE.Mesh(new THREE.CircleGeometry(0.012, 6), dotMat);
      dot.position.set(r * Math.cos(theta), yPos, r * Math.sin(theta));
      dot.lookAt(0, yPos, 0);
      speakerGroup.add(dot);
    }

    // Position the group
    speakerGroup.position.y = 0;
    speakerGroup.rotation.x = 0.2;

    scene.add(speakerGroup);
  }

  // --- Particles (Sound Waves) ---
  function createParticles() {
    var particleCount = 200;
    var geom = new THREE.BufferGeometry();
    var positions = new Float32Array(particleCount * 3);
    var sizes = new Float32Array(particleCount);
    var offsets = new Float32Array(particleCount);
    var speeds = new Float32Array(particleCount);

    for (var i = 0; i < particleCount; i++) {
      var angle = Math.random() * Math.PI * 2;
      var radius = 1.6 + Math.random() * 2.5;
      var height = 0.2 + Math.random() * 1.6;
      positions[i * 3] = radius * Math.cos(angle);
      positions[i * 3 + 1] = height;
      positions[i * 3 + 2] = radius * Math.sin(angle);
      sizes[i] = 0.02 + Math.random() * 0.06;
      offsets[i] = Math.random() * Math.PI * 2;
      speeds[i] = 0.3 + Math.random() * 0.7;
    }

    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geom.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    var mat = new THREE.PointsMaterial({
      color: 0x60a5fa,
      size: 0.04,
      transparent: true,
      opacity: 0.4,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });

    particles = new THREE.Points(geom, mat);
    particles.userData = { offsets: offsets, speeds: speeds, initialPos: positions.slice() };
    scene.add(particles);

    // Second layer particles
    var pCount2 = 80;
    var geom2 = new THREE.BufferGeometry();
    var pos2 = new Float32Array(pCount2 * 3);
    for (var j = 0; j < pCount2; j++) {
      var a2 = Math.random() * Math.PI * 2;
      var r2 = 2.5 + Math.random() * 3;
      var h2 = Math.random() * 2;
      pos2[j * 3] = r2 * Math.cos(a2);
      pos2[j * 3 + 1] = h2;
      pos2[j * 3 + 2] = r2 * Math.sin(a2);
    }
    geom2.setAttribute('position', new THREE.BufferAttribute(pos2, 3));
    var mat2 = new THREE.PointsMaterial({
      color: 0x38bdf8,
      size: 0.03,
      transparent: true,
      opacity: 0.15,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });
    var particles2 = new THREE.Points(geom2, mat2);
    particles2.userData = { initialPos: pos2.slice() };
    scene.add(particles2);
  }

  // --- Events ---
  function setupEvents() {
    var el = renderer.domElement;

    // Mouse
    el.addEventListener('mousedown', onDown);
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    el.addEventListener('wheel', onWheel, { passive: false });

    // Touch
    el.addEventListener('touchstart', onTouchDown, { passive: false });
    window.addEventListener('touchmove', onTouchMove, { passive: false });
    window.addEventListener('touchend', onTouchUp, { passive: false });

    // Resize
    window.addEventListener('resize', onResize);
  }

  function onDown(e) {
    isDragging = true;
    prevX = e.clientX;
    prevY = e.clientY;
    velocityX = 0;
    velocityY = 0;
    autoRotate = false;
    clearTimeout(autoRotateTimer);
    el = renderer.domElement.style;
  }

  function onMove(e) {
    if (!isDragging) return;
    var dx = e.clientX - prevX;
    var dy = e.clientY - prevY;
    rotationY += dx * 0.008;
    rotationX += dy * 0.005;
    rotationX = Math.max(-0.5, Math.min(0.8, rotationX));
    velocityX = dy * 0.008;
    velocityY = dx * 0.008;
    prevX = e.clientX;
    prevY = e.clientY;
  }

  function onUp() {
    isDragging = false;
    autoRotateTimer = setTimeout(function () { autoRotate = true; }, 3000);
  }

  function onWheel(e) {
    e.preventDefault();
    targetZoom += e.deltaY * 0.005;
    targetZoom = Math.max(CONFIG.zoomMin, Math.min(CONFIG.zoomMax, targetZoom));
  }

  function onTouchDown(e) {
    if (e.touches.length === 1) {
      isDragging = true;
      prevX = e.touches[0].clientX;
      prevY = e.touches[0].clientY;
      velocityX = 0;
      velocityY = 0;
      autoRotate = false;
      clearTimeout(autoRotateTimer);
    }
  }

  function onTouchMove(e) {
    if (!isDragging || e.touches.length !== 1) return;
    var dx = e.touches[0].clientX - prevX;
    var dy = e.touches[0].clientY - prevY;
    rotationY += dx * 0.008;
    rotationX += dy * 0.005;
    rotationX = Math.max(-0.5, Math.min(0.8, rotationX));
    velocityX = dy * 0.008;
    velocityY = dx * 0.008;
    prevX = e.touches[0].clientX;
    prevY = e.touches[0].clientY;
  }

  function onTouchUp() {
    isDragging = false;
    autoRotateTimer = setTimeout(function () { autoRotate = true; }, 3000);
  }

  function onResize() {
    var w = container.clientWidth;
    var h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }

  // --- Color Change ---
  function changeSpeakerColor(colorName) {
    currentColor = colorName;
    var cols = CONFIG.colors[colorName];
    if (!cols) return;

    // Remove old speaker
    while (speakerGroup.children.length > 0) {
      var child = speakerGroup.children[0];
      if (child.geometry) child.geometry.dispose();
      if (child.material) child.material.dispose();
      speakerGroup.remove(child);
    }
    scene.remove(speakerGroup);
    createSpeaker();
    speakerGroup.rotation.y = rotationY;
    speakerGroup.rotation.x = rotationX;
    scene.add(speakerGroup);
  }

  // --- Animation Loop ---
  function animate() {
    animationId = requestAnimationFrame(animate);

    var delta = clock.getDelta();
    var time = clock.getElapsedTime();

    // Auto-rotate
    if (autoRotate && !isDragging) {
      rotationY += CONFIG.autoRotateSpeed * delta;
    }

    // Inertia
    if (!isDragging) {
      velocityX *= CONFIG.inertiaDamping;
      velocityY *= CONFIG.inertiaDamping;
      rotationX += velocityX;
      rotationY += velocityY;
      rotationX = Math.max(-0.5, Math.min(0.8, rotationX));
    }

    // Zoom interpolation
    currentZoom += (targetZoom - currentZoom) * 0.08;
    camera.position.z = currentZoom;
    camera.position.y = 1.5 + (currentZoom - 4.5) * 0.2;
    camera.lookAt(0, 0.5, 0);

    // Update speaker
    if (speakerGroup) {
      speakerGroup.rotation.y = rotationY;
      speakerGroup.rotation.x = rotationX;
    }

    // LED pulse
    glowPulse = Math.sin(time * 1.5) * 0.3 + 0.7;
    if (ledRing) {
      ledRing.material.emissiveIntensity = glowPulse * 1.2;
      ledRing.scale.set(
        1 + Math.sin(time * 2) * 0.005,
        1 + Math.sin(time * 2) * 0.005,
        1
      );
    }

    // Particles animation
    if (particles) {
      var pos = particles.geometry.attributes.position.array;
      var initPos = particles.userData.initialPos;
      var offsets = particles.userData.offsets;
      var speeds = particles.userData.speeds;
      for (var i = 0; i < pos.length / 3; i++) {
        var idx = i * 3;
        var pulse = Math.sin(time * speeds[i] + offsets[i]) * 0.15;
        var expand = 1 + Math.sin(time * speeds[i] * 0.5 + offsets[i]) * 0.08;
        pos[idx] = initPos[idx] * expand;
        pos[idx + 1] = initPos[idx + 1] + pulse;
        pos[idx + 2] = initPos[idx + 2] * expand;
      }
      particles.geometry.attributes.position.needsUpdate = true;
      particles.material.opacity = 0.25 + Math.sin(time * 0.5) * 0.1;
    }

    renderer.render(scene, camera);
  }

  // --- Cleanup ---
  function cleanup() {
    if (animationId) cancelAnimationFrame(animationId);
    if (renderer) {
      renderer.dispose();
      if (renderer.domElement && renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
    }
  }

  // --- Load Three.js and init ---
  function loadThree() {
    if (typeof THREE !== 'undefined') {
      init();
      return;
    }
    var script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
    script.onload = init;
    script.onerror = function () {
      console.warn('Three.js failed to load, showing fallback');
      container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:rgba(255,255,255,0.3);font-size:1rem;">3D Speaker Unavailable</div>';
    };
    document.head.appendChild(script);
  }

  // Only load when visible (lazy load)
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        loadThree();
        observer.disconnect();
      }
    });
  }, { rootMargin: '200px' });
  observer.observe(container);

  // Expose cleanup
  window.__speakerCleanup = cleanup;
})();
