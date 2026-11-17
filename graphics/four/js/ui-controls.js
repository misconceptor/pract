/**
 * Wire up all sidebar controls: transform sliders + number inputs,
 * composition-order select, reset buttons, wireframe / texture
 * toggles. On every change, recompute the transform matrix, apply it
 * to the mesh, and update the matrix panel.
 *
 * Design notes
 * ------------
 *   - Sliders and number inputs share an id prefix (tx / tx-num).
 *     Both directions of sync are wired, so either control can drive
 *     the other.
 *   - Transform state is derived on every change by reading the
 *     current DOM values. There is no shadow state to keep in sync,
 *     which removes a whole class of bugs.
 *   - Rotation is entered in degrees (per the UI label) and converted
 *     to radians here. transforms.js works in radians only.
 *   - The mesh is switched to matrixAutoUpdate = false so the final
 *     matrix from compose() is applied verbatim; no decomposition to
 *     position/quaternion/scale happens.
 */

import { compose } from './transforms.js';
import { updateMatrixPanel } from './matrix-panel.js';

const DEFAULTS = {
  tx: 0, ty: 0, tz: 0,
  rx: 0, ry: 0, rz: 0,
  sx: 1, sy: 1, sz: 1,
};

const DEFAULT_ORDER = 'TRS';

const DEG_TO_RAD = Math.PI / 180;

/**
 * @param {{
 *   mesh: import('three').Mesh,
 *   material: import('three').MeshStandardMaterial,
 *   texture: import('three').Texture,
 *   resetCamera: () => void,
 * }} deps
 */
export function initUIControls({ mesh, material, texture, resetCamera }) {
  // Take ownership of the mesh matrix.
  mesh.matrixAutoUpdate = false;

  // Cache DOM references once.
  const refs = {};
  for (const key of Object.keys(DEFAULTS)) {
    refs[key] = document.getElementById(key);
    refs[key + '-num'] = document.getElementById(key + '-num');
    if (!refs[key] || !refs[key + '-num']) {
      throw new Error(`Missing DOM element for "${key}" / "${key}-num"`);
    }
  }

  const orderEl = document.getElementById('order');
  const orderLabelEl = document.getElementById('matrix-order-label');
  if (!orderEl || !orderLabelEl) {
    throw new Error('Missing #order or #matrix-order-label');
  }

  // --- Slider <-> number sync --------------------------------------
  for (const key of Object.keys(DEFAULTS)) {
    const slider = refs[key];
    const number = refs[key + '-num'];

    slider.addEventListener('input', () => {
      number.value = slider.value;
      applyTransform();
    });

    number.addEventListener('input', () => {
      const v = parseFloat(number.value);
      if (Number.isFinite(v)) {
        slider.value = String(v);
        applyTransform();
      }
    });
  }

  // --- Composition order -------------------------------------------
  orderEl.addEventListener('change', () => {
    orderLabelEl.textContent = `M = ${formatOrder(orderEl.value)}`;
    applyTransform();
  });

  // --- Reset transform ---------------------------------------------
  document.getElementById('btn-reset-transform')
    .addEventListener('click', () => {
      for (const key of Object.keys(DEFAULTS)) {
        const v = DEFAULTS[key];
        refs[key].value = String(v);
        refs[key + '-num'].value = String(v);
      }
      orderEl.value = DEFAULT_ORDER;
      orderLabelEl.textContent = `M = ${formatOrder(DEFAULT_ORDER)}`;
      applyTransform();
    });

  // --- Reset view ---------------------------------------------------
  document.getElementById('btn-reset-view')
    .addEventListener('click', resetCamera);

  // --- Wireframe toggle --------------------------------------------
  const btnWire = document.getElementById('btn-wireframe');
  btnWire.addEventListener('click', () => {
    material.wireframe = !material.wireframe;
    btnWire.classList.toggle('is-on', material.wireframe);
  });

  // --- Texture toggle ----------------------------------------------
  const btnTex = document.getElementById('btn-texture');
  btnTex.addEventListener('click', () => {
    const isOn = btnTex.classList.toggle('is-on');
    material.map = isOn ? texture : null;
    material.color.set(isOn ? 0xffffff : 0x6366f1);
    material.needsUpdate = true;
  });

  // --- Initial apply so matrix panel and mesh start in a known state
  applyTransform();

  // -----------------------------------------------------------------
  function applyTransform() {
    const t = [
      parseFloat(refs.tx.value) || 0,
      parseFloat(refs.ty.value) || 0,
      parseFloat(refs.tz.value) || 0,
    ];
    const r = [
      (parseFloat(refs.rx.value) || 0) * DEG_TO_RAD,
      (parseFloat(refs.ry.value) || 0) * DEG_TO_RAD,
      (parseFloat(refs.rz.value) || 0) * DEG_TO_RAD,
    ];
    const s = [
      parseFloat(refs.sx.value) || 1,
      parseFloat(refs.sy.value) || 1,
      parseFloat(refs.sz.value) || 1,
    ];

    const M = compose(t, r, s, orderEl.value);

    mesh.matrix.copy(M);
    mesh.matrixWorldNeedsUpdate = true;

    updateMatrixPanel(M);
  }
}

function formatOrder(order) {
  // "TRS" -> "T · R · S"
  return order.split('').join(' · ');
}