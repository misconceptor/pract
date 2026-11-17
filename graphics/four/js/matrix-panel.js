/**
 * Write a THREE.Matrix4 into the 16 <td> cells of the sidebar matrix
 * card.
 *
 * The DOM ids are m<row><col> (e.g. m03 is row 0, column 3). three.js
 * stores matrices column-major, so elements[col*4 + row] maps to id
 * m<row><col>. This module is the ONLY place where that mapping is
 * applied — everything else in the app works with Matrix4 objects.
 *
 * Values are printed with 3 decimal places, matching the initial HTML
 * placeholder. Values whose magnitude is below 1e-10 are printed as
 * "0.000" (instead of "-0.000") to keep the panel clean.
 */

const ZERO_EPSILON = 1e-10;

/**
 * @param {import('three').Matrix4} matrix
 */
export function updateMatrixPanel(matrix) {
  const e = matrix.elements;
  for (let row = 0; row < 4; row++) {
    for (let col = 0; col < 4; col++) {
      const el = document.getElementById(`m${row}${col}`);
      if (!el) continue;
      const v = e[col * 4 + row];
      const clean = Math.abs(v) < ZERO_EPSILON ? 0 : v;
      el.textContent = clean.toFixed(3);
    }
  }
}