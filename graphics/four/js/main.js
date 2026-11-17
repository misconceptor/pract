/**
 * Application entry point.
 *
 * Pass A: renderer, scene, camera, lights, textured text mesh, orbit
 *         controls, resize handling, render loop.
 * Pass B: wires up the sidebar controls (initUIControls) so sliders,
 *         number inputs, the composition-order select, and the four
 *         display buttons actually do something.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { createProceduralTexture } from './texture.js';
import { createTextMesh } from './text-mesh.js';
import { initUIControls } from './ui-controls.js';

const STRING = 'Hancharenka';

async function init() {
  const canvas   = document.getElementById('scene-canvas');
  const viewport = document.getElementById('viewport');

  // --- Renderer -----------------------------------------------------
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x0f1117, 1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  // --- Scene + camera -----------------------------------------------
  const scene  = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
  camera.position.set(0, 2, 12);

  // --- Lights -------------------------------------------------------
  scene.add(new THREE.AmbientLight(0xffffff, 0.55));

  const keyLight = new THREE.DirectionalLight(0xffffff, 2.0);
  keyLight.position.set(5, 8, 6);
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0x818cf8, 0.9);
  fillLight.position.set(-6, 2, -4);
  scene.add(fillLight);

  // --- Ground grid --------------------------------------------------
  const grid = new THREE.GridHelper(20, 20, 0x3a4055, 0x22263a);
  grid.position.y = -2.5;
  scene.add(grid);

  // --- Resize -------------------------------------------------------
  function applySize(w, h) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }

  function resizeFromViewport() {
    const r = viewport.getBoundingClientRect();
    applySize(Math.max(1, Math.floor(r.width)),
              Math.max(1, Math.floor(r.height)));
  }

  const ro = new ResizeObserver(resizeFromViewport);
  ro.observe(viewport);
  window.addEventListener('resize', resizeFromViewport);

  // --- Texture + mesh -----------------------------------------------
  const texture = createProceduralTexture();
  let mesh, vertexCount, triangleCount;
  try {
    ({ mesh, vertexCount, triangleCount } =
      await createTextMesh(STRING, texture));
  } catch (err) {
    console.error('[main] text mesh failed:', err);
    throw err;
  }
  scene.add(mesh);

  // --- Sidebar counts -----------------------------------------------
  setText('string-display', STRING);
  setText('string-value', STRING);
  setText('vertex-count', vertexCount.toLocaleString());
  setText('triangle-count', triangleCount.toLocaleString());

  // --- Wait for viewport to have real size, then frame camera ------
  const vpRect = await waitForViewportSize(viewport, 3000);
  applySize(
    Math.max(1, Math.floor(vpRect.width)),
    Math.max(1, Math.floor(vpRect.height)),
  );

  const bbox = new THREE.Box3().setFromObject(mesh);
  const size = bbox.getSize(new THREE.Vector3());
  const center = bbox.getCenter(new THREE.Vector3());

  const vFov  = (camera.fov * Math.PI) / 180;
  const vHalf = Math.tan(vFov / 2);
  const hHalf = vHalf * camera.aspect;
  const fitDist = Math.max(size.y / (2 * vHalf), size.x / (2 * hHalf)) * 1.4;

  camera.position.set(
    center.x,
    center.y + size.y * 0.4,
    center.z + fitDist,
  );
  camera.lookAt(center);
  camera.updateProjectionMatrix();

  // --- OrbitControls -----------------------------------------------
  const controls = new OrbitControls(camera, canvas);
  controls.target.copy(center);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 2;
  controls.maxDistance = 60;
  controls.update();

  // Remember the initial camera state for the "Reset view" button.
  const initialCameraPosition = camera.position.clone();
  const initialCameraTarget   = controls.target.clone();
  function resetCamera() {
    camera.position.copy(initialCameraPosition);
    controls.target.copy(initialCameraTarget);
    controls.update();
  }

  // --- Wire up the sidebar controls ---------------------------------
  initUIControls({
    mesh,
    material: mesh.material,
    texture,
    resetCamera,
  });

  // --- Render loop --------------------------------------------------
  renderer.setAnimationLoop(() => {
    controls.update();
    renderer.render(scene, camera);
  });

  // --- Debug handle -------------------------------------------------
  window.__lab4 = { scene, camera, renderer, mesh, controls, viewport };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function waitForViewportSize(viewport, timeoutMs = 3000) {
  const start = performance.now();
  return new Promise(resolve => {
    const tick = () => {
      const r = viewport.getBoundingClientRect();
      if (r.width >= 10 && r.height >= 10) return resolve(r);
      if (performance.now() - start > timeoutMs) {
        console.warn(`[main] viewport size stuck at ${r.width}×${r.height}`);
        return resolve(r);
      }
      requestAnimationFrame(tick);
    };
    tick();
  });
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

init().catch(err => console.error('[main.js] init failed:', err));