(function (){
'use strict';

var CONFIG = {
  autoRotateSpeed: 0.2,
  inertiaDamping: 0.9,
  zoomMin: 3,
  zoomMax: 8,
};

var scene, camera, renderer, headphoneGroup, ringGroup, particles;
var isDragging = false;
var prevX = 0, prevY = 0;
var vx = 0, vy = 0;
var rotX = 0.15, rotY = 0;
var targetZoom = 5;
var currentZoom = 5;
var autoRotate = true;
var autoTimer = null;
var animId = null;
var clock = new THREE.Clock();
var container = document.getElementById('three-container');
if (!container) return;

var fsBtn = document.getElementById('speakerFullscreen');
if (fsBtn) fsBtn.addEventListener('click', function(){
  document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
});

function init(){
  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x050510, 0.012);

  var asp = container.clientWidth / container.clientHeight;
  camera = new THREE.PerspectiveCamera(40, asp, 0.1, 100);
  camera.position.set(0, 0.5, currentZoom);
  camera.lookAt(0, 0, 0);

  renderer = new THREE.WebGLRenderer({ antialias:true, alpha:true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.appendChild(renderer.domElement);

  setupLights();
  createHeadphone();
  createNeonRings();
  createParticles();
  setupEvents();
  animate();
}

function setupLights(){
  scene.add(new THREE.AmbientLight(0x4466aa, 0.4));

  var key = new THREE.DirectionalLight(0x88bbff, 2.0);
  key.position.set(4, 6, 5); key.castShadow = true; scene.add(key);

  var fill = new THREE.DirectionalLight(0x6688cc, 0.5);
  fill.position.set(-4, 1, -3); scene.add(fill);

  var rim = new THREE.DirectionalLight(0x4488ff, 0.6);
  rim.position.set(0, -3, 7); scene.add(rim);

  var top = new THREE.DirectionalLight(0x88ccff, 0.3);
  top.position.set(0, 8, 0); scene.add(top);

  var glow1 = new THREE.PointLight(0x2563eb, 0.6, 8);
  glow1.position.set(0, -0.5, 2.5); scene.add(glow1);

  var glow2 = new THREE.PointLight(0x0ea5e9, 0.4, 6);
  glow2.position.set(1.5, 0.5, -2); scene.add(glow2);
}

function createHeadphone(){
  headphoneGroup = new THREE.Group();

  // ---- Headband ----
  var pts = [
    new THREE.Vector3(-1.6, 0.3, 0),
    new THREE.Vector3(-1.0, 1.8, 0.2),
    new THREE.Vector3(0, 2.4, 0),
    new THREE.Vector3(1.0, 1.8, -0.2),
    new THREE.Vector3(1.6, 0.3, 0),
  ];
  var curve = new THREE.CatmullRomCurve3(pts);
  var tubeGeom = new THREE.TubeGeometry(curve, 32, 0.12, 12, false);
  var headbandMat = new THREE.MeshPhysicalMaterial({
    color: '#1a1a2e',
    metalness: 0.85,
    roughness: 0.15,
    clearcoat: 0.4,
    clearcoatRoughness: 0.3,
  });
  var headband = new THREE.Mesh(tubeGeom, headbandMat);
  headband.castShadow = true;
  headphoneGroup.add(headband);

  // Headband cushion top
  var cushionPts = [
    new THREE.Vector3(-0.8, 2.2, 0),
    new THREE.Vector3(0, 2.5, 0),
    new THREE.Vector3(0.8, 2.2, 0),
  ];
  var cCurve = new THREE.CatmullRomCurve3(cushionPts);
  var cTube = new THREE.TubeGeometry(cCurve, 16, 0.18, 10, false);
  var cushionMat = new THREE.MeshPhysicalMaterial({
    color: '#0a0a14',
    metalness: 0.1,
    roughness: 0.9,
  });
  var cushion = new THREE.Mesh(cTube, cushionMat);
  headphoneGroup.add(cushion);

  // ---- Left Earcup ----
  var earcupGroupL = createEarcup(-1.6, 0.2, 0.8);
  headphoneGroup.add(earcupGroupL);

  // ---- Right Earcup ----
  var earcupGroupR = createEarcup(1.6, 0.2, -0.8);
  headphoneGroup.add(earcupGroupR);

  // ---- Yoke arms ----
  var yokeMat = new THREE.MeshPhysicalMaterial({
    color: '#222244',
    metalness: 0.9,
    roughness: 0.1,
  });

  function addYoke(x, zRot){
    var arm = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.8, 0.06), yokeMat);
    arm.position.set(x, 1.5, 0);
    arm.rotation.z = zRot;
    headphoneGroup.add(arm);

    var joint = new THREE.Mesh(new THREE.SphereGeometry(0.08, 12, 12), yokeMat);
    joint.position.set(x, 1.1, 0);
    headphoneGroup.add(joint);
  }
  addYoke(-1.5, 0.15);
  addYoke(1.5, -0.15);

  scene.add(headphoneGroup);
}

function createEarcup(x, y, zRot){
  var g = new THREE.Group();

  // Outer shell
  var shellMat = new THREE.MeshPhysicalMaterial({
    color: '#1a1a2e',
    metalness: 0.8,
    roughness: 0.2,
    clearcoat: 0.3,
    envMapIntensity: 1.0,
  });
  var shell = new THREE.Mesh(new THREE.BoxGeometry(0.7, 1.2, 0.5), shellMat);
  shell.position.set(0, -0.3, 0);
  shell.castShadow = true;
  g.add(shell);

  // Inner cushion
  var cushionMat = new THREE.MeshPhysicalMaterial({
    color: '#0a0a14',
    metalness: 0.05,
    roughness: 0.95,
  });
  var cushion = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.55, 0.2, 24), cushionMat);
  cushion.position.set(0, -0.1, -0.3);
  cushion.rotation.x = 0.1;
  g.add(cushion);

  // Ear pad ring
  var padMat = new THREE.MeshPhysicalMaterial({
    color: '#111122',
    metalness: 0.1,
    roughness: 0.85,
  });
  var pad = new THREE.Mesh(new THREE.TorusGeometry(0.48, 0.04, 10, 28), padMat);
  pad.position.set(0, -0.1, -0.3);
  pad.rotation.x = Math.PI/2;
  g.add(pad);

  // Glass reflection strip
  var glassMat = new THREE.MeshPhysicalMaterial({
    color: '#4488ff',
    metalness: 0.1,
    roughness: 0.05,
    transparent: true,
    opacity: 0.15,
    envMapIntensity: 2.0,
  });
  var glass = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.15, 0.01), glassMat);
  glass.position.set(0, 0.1, 0.26);
  g.add(glass);

  // RGB LED strip
  var ledMat = new THREE.MeshPhysicalMaterial({
    color: '#00d4ff',
    emissive: '#00d4ff',
    emissiveIntensity: 0.8,
    transparent: true,
    opacity: 0.9,
  });
  var ledStrip = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.04, 0.02), ledMat);
  ledStrip.position.set(0, -0.4, 0.26);
  ledStrip.userData.isLed = true;
  g.add(ledStrip);

  // Side LED accent
  var sideLedMat = new THREE.MeshPhysicalMaterial({
    color: '#2563eb',
    emissive: '#2563eb',
    emissiveIntensity: 0.5,
    transparent: true,
    opacity: 0.7,
  });
  var sideLed = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.8, 0.4), sideLedMat);
  sideLed.position.set(0.36, -0.2, 0);
  g.add(sideLed);

  // Grille detail
  var grilleMat = new THREE.MeshPhysicalMaterial({
    color: '#222233',
    metalness: 0.3,
    roughness: 0.7,
  });
  for(var i=0;i<6;i++){
    var bar = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.015, 0.01), grilleMat);
    bar.position.set(0, -0.45 + i*0.08, 0.26);
    g.add(bar);
  }

  g.position.set(x, y, 0);
  g.rotation.y = zRot;
  return g;
}

function createNeonRings(){
  ringGroup = new THREE.Group();

  for(var k=0;k<3;k++){
    var r = 2.0 + k*0.8;
    var ringMat = new THREE.MeshBasicMaterial({
      color: k===0 ? 0x2563eb : (k===1 ? 0x0ea5e9 : 0x60a5fa),
      transparent: true,
      opacity: 0.08 + k*0.02,
      wireframe: false,
      side: THREE.DoubleSide,
    });
    var ring = new THREE.Mesh(new THREE.RingGeometry(r-0.01, r+0.01, 48), ringMat);
    ring.rotation.x = Math.PI/2;
    ring.position.y = -0.3 + k*0.4;
    ring.userData = { speed: 0.3 + k*0.2, phase: k*1.2 };
    ringGroup.add(ring);
  }

  // Outer glow ring
  var glowRingMat = new THREE.MeshBasicMaterial({
    color: 0x3b82f6,
    transparent: true,
    opacity: 0.04,
    side: THREE.DoubleSide,
  });
  var glowRing = new THREE.Mesh(new THREE.RingGeometry(2.8, 3.2, 64), glowRingMat);
  glowRing.rotation.x = Math.PI/2 + 0.2;
  glowRing.position.y = -0.1;
  ringGroup.add(glowRing);

  scene.add(ringGroup);
}

function createParticles(){
  var count = 300;
  var geom = new THREE.BufferGeometry();
  var pos = new Float32Array(count*3);
  var sizes = new Float32Array(count);
  var offsets = new Float32Array(count);
  var speeds = new Float32Array(count);

  for(var i=0;i<count;i++){
    var theta = Math.random() * Math.PI*2;
    var r = 1.8 + Math.random() * 3.5;
    pos[i*3] = r * Math.cos(theta);
    pos[i*3+1] = (Math.random()-0.5) * 2.5;
    pos[i*3+2] = r * Math.sin(theta);
    sizes[i] = 0.02 + Math.random()*0.08;
    offsets[i] = Math.random()*Math.PI*2;
    speeds[i] = 0.2 + Math.random()*0.5;
  }
  geom.setAttribute('position', new THREE.BufferAttribute(pos,3));
  geom.setAttribute('size', new THREE.BufferAttribute(sizes,1));

  var mat = new THREE.PointsMaterial({
    color: 0x60a5fa,
    size: 0.035,
    transparent: true,
    opacity: 0.3,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    sizeAttenuation: true,
  });
  particles = new THREE.Points(geom, mat);
  particles.userData = { offsets: offsets, speeds: speeds, initialPos: pos.slice() };
  scene.add(particles);

  // Smaller outer particles
  var count2 = 100;
  var geom2 = new THREE.BufferGeometry();
  var pos2 = new Float32Array(count2*3);
  for(var j=0;j<count2;j++){
    var a = Math.random()*Math.PI*2;
    var rad = 3.5 + Math.random()*3;
    pos2[j*3] = rad * Math.cos(a);
    pos2[j*3+1] = (Math.random()-0.5)*2;
    pos2[j*3+2] = rad * Math.sin(a);
  }
  geom2.setAttribute('position', new THREE.BufferAttribute(pos2,3));
  var mat2 = new THREE.PointsMaterial({
    color: 0x38bdf8,
    size: 0.02,
    transparent: true,
    opacity: 0.1,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    sizeAttenuation: true,
  });
  var p2 = new THREE.Points(geom2, mat2);
  scene.add(p2);
}

function setupEvents(){
  var el = renderer.domElement;
  el.addEventListener('mousedown', onDown);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onUp);
  el.addEventListener('wheel', onWheel, {passive:false});
  el.addEventListener('touchstart', onTD, {passive:false});
  window.addEventListener('touchmove', onTM, {passive:false});
  window.addEventListener('touchend', onTU, {passive:false});
  window.addEventListener('resize', onResize);
}

function onDown(e){
  isDragging = true;
  prevX = e.clientX; prevY = e.clientY;
  vx = 0; vy = 0;
  autoRotate = false;
  clearTimeout(autoTimer);
}

function onMove(e){
  if(!isDragging) return;
  var dx = e.clientX - prevX;
  var dy = e.clientY - prevY;
  rotY += dx * 0.006;
  rotX += dy * 0.004;
  rotX = Math.max(-0.6, Math.min(0.8, rotX));
  vx = dy * 0.006;
  vy = dx * 0.006;
  prevX = e.clientX; prevY = e.clientY;
}

function onUp(){
  isDragging = false;
  autoTimer = setTimeout(function(){ autoRotate = true; }, 3000);
}

function onWheel(e){
  e.preventDefault();
  targetZoom += e.deltaY * 0.005;
  targetZoom = Math.max(CONFIG.zoomMin, Math.min(CONFIG.zoomMax, targetZoom));
}

function onTD(e){
  if(e.touches.length===1){
    isDragging = true;
    prevX = e.touches[0].clientX; prevY = e.touches[0].clientY;
    vx = 0; vy = 0;
    autoRotate = false;
    clearTimeout(autoTimer);
  }
}

function onTM(e){
  if(!isDragging || e.touches.length!==1) return;
  var dx = e.touches[0].clientX - prevX;
  var dy = e.touches[0].clientY - prevY;
  rotY += dx * 0.006;
  rotX += dy * 0.004;
  rotX = Math.max(-0.6, Math.min(0.8, rotX));
  vx = dy * 0.006;
  vy = dx * 0.006;
  prevX = e.touches[0].clientX; prevY = e.touches[0].clientY;
}

function onTU(){
  isDragging = false;
  autoTimer = setTimeout(function(){ autoRotate = true; }, 3000);
}

function onResize(){
  var w = container.clientWidth, h = container.clientHeight;
  camera.aspect = w/h;
  camera.updateProjectionMatrix();
  renderer.setSize(w,h);
}

function animate(){
  animId = requestAnimationFrame(animate);
  var dt = clock.getDelta();
  var time = clock.getElapsedTime();

  if(autoRotate && !isDragging) rotY += CONFIG.autoRotateSpeed * dt;

  if(!isDragging){
    vx *= CONFIG.inertiaDamping;
    vy *= CONFIG.inertiaDamping;
    rotX += vx; rotY += vy;
    rotX = Math.max(-0.6, Math.min(0.8, rotX));
  }

  currentZoom += (targetZoom - currentZoom) * 0.06;
  camera.position.z = currentZoom;
  camera.position.y = 0.5 + (currentZoom - 5) * 0.15;
  camera.lookAt(0, 0, 0);

  if(headphoneGroup){
    headphoneGroup.rotation.y = rotY;
    headphoneGroup.rotation.x = rotX;

    // Float animation
    var floatY = Math.sin(time * 0.6) * 0.06;
    headphoneGroup.position.y = floatY;
  }

  // Neon rings
  if(ringGroup){
    ringGroup.children.forEach(function(r, idx){
      r.rotation.z = time * (0.15 + idx*0.05);
      r.scale.setScalar(1 + Math.sin(time * 0.3 + idx) * 0.03);
    });
  }

  // Particles
  if(particles){
    var pos = particles.geometry.attributes.position.array;
    var init = particles.userData.initialPos;
    var offs = particles.userData.offsets;
    var spds = particles.userData.speeds;
    for(var i=0; i<pos.length/3; i++){
      var idx = i*3;
      var pulse = Math.sin(time * spds[i] + offs[i]) * 0.2;
      var exp = 1 + Math.sin(time * spds[i]*0.4 + offs[i]) * 0.1;
      pos[idx] = init[idx] * exp;
      pos[idx+1] = init[idx+1] + pulse;
      pos[idx+2] = init[idx+2] * exp;
    }
    particles.geometry.attributes.position.needsUpdate = true;
    particles.material.opacity = 0.2 + Math.sin(time*0.4)*0.08;
  }

  renderer.render(scene, camera);
}

function loadThree(){
  if(typeof THREE !== 'undefined'){ init(); return; }
  var s = document.createElement('script');
  s.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
  s.onload = init;
  s.onerror = function(){
    container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:rgba(255,255,255,0.3);font-size:1rem;">3D Unavailable</div>';
  };
  document.head.appendChild(s);
}

var obs = new IntersectionObserver(function(entries){
  entries.forEach(function(e){ if(e.isIntersecting){ loadThree(); obs.disconnect(); } });
}, {rootMargin:'200px'});
obs.observe(container);

window.__speakerCleanup = function(){
  if(animId) cancelAnimationFrame(animId);
  if(renderer){ renderer.dispose(); if(renderer.domElement.parentNode) renderer.domElement.parentNode.removeChild(renderer.domElement); }
};
})();
