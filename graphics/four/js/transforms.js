/**
 * Pure transformation-matrix builders.
 *
 * Every function here is stateless, takes plain numbers, and returns
 * a fresh THREE.Matrix4. No DOM, no mesh — that makes the module
 * trivially unit-testable and easy to point to in the report.
 *
 * Conventions
 * -----------
 *   - Matrices are 4x4, stored column-major by three.js.
 *   - Rotation angles are received in RADIANS (degrees are converted
 *     in ui-controls.js so this module stays unit-agnostic).
 *   - Composition M = A · B means "B applied first, then A" when
 *     multiplying a column vector on the right: M · v = A · (B · v).
 *   - Rotation order is fixed at R = Rz · Ry · Rx, i.e. X applied
 *     first, then Y, then Z (three.js Euler "XYZ").
 *
 * Composition orders exposed by `compose()`
 * -----------------------------------------
 *   "TRS"   M = T · R · S    scale first, then rotate, then translate
 *                            (standard model transform)
 *   "SRT"   M = S · R · T    translate first, then rotate, then scale
 *   "RTS"   M = R · T · S    scale, then translate, then rotate
 */

import { Matrix4 } from 'three';

/**
 * Translation matrix.
 *
 *   [ 1 0 0 tx ]
 *   [ 0 1 0 ty ]
 *   [ 0 0 1 tz ]
 *   [ 0 0 0  1 ]
 */
export function translationMatrix(tx, ty, tz) {
  return new Matrix4().set(
    1,  0,  0,  tx,
    0,  1,  0,  ty,
    0,  0,  1,  tz,
    0,  0,  0,  1,
  );
}

/**
 * Scale matrix.
 *
 *   [ sx  0  0  0 ]
 *   [  0 sy  0  0 ]
 *   [  0  0 sz  0 ]
 *   [  0  0  0  1 ]
 */
export function scaleMatrix(sx, sy, sz) {
  return new Matrix4().set(
    sx,  0,  0,  0,
     0, sy,  0,  0,
     0,  0, sz,  0,
     0,  0,  0,  1,
  );
}

/**
 * Rotation about X axis by angle `a` (radians).
 *
 *   [ 1   0    0   0 ]
 *   [ 0  cos -sin  0 ]
 *   [ 0  sin  cos  0 ]
 *   [ 0   0    0   1 ]
 */
export function rotationX(a) {
  const c = Math.cos(a);
  const s = Math.sin(a);
  return new Matrix4().set(
    1,  0,   0,  0,
    0,  c,  -s,  0,
    0,  s,   c,  0,
    0,  0,   0,  1,
  );
}

/**
 * Rotation about Y axis by angle `a` (radians).
 *
 *   [  cos  0  sin  0 ]
 *   [   0   1   0   0 ]
 *   [ -sin  0  cos  0 ]
 *   [   0   0   0   1 ]
 */
export function rotationY(a) {
  const c = Math.cos(a);
  const s = Math.sin(a);
  return new Matrix4().set(
     c,  0,  s,  0,
     0,  1,  0,  0,
    -s,  0,  c,  0,
     0,  0,  0,  1,
  );
}

/**
 * Rotation about Z axis by angle `a` (radians).
 *
 *   [ cos -sin  0  0 ]
 *   [ sin  cos  0  0 ]
 *   [  0    0   1  0 ]
 *   [  0    0   0  1 ]
 */
export function rotationZ(a) {
  const c = Math.cos(a);
  const s = Math.sin(a);
  return new Matrix4().set(
    c, -s,  0,  0,
    s,  c,  0,  0,
    0,  0,  1,  0,
    0,  0,  0,  1,
  );
}

/**
 * Combined rotation R = Rz · Ry · Rx (X first, then Y, then Z).
 * This matches three.js Euler order "XYZ".
 */
export function rotationMatrix(rx, ry, rz) {
  const Rx = rotationX(rx);
  const Ry = rotationY(ry);
  const Rz = rotationZ(rz);
  // (Rz · Ry) · Rx
  return new Matrix4().multiplyMatrices(Rz, Ry).multiply(Rx);
}

/**
 * Compose T, R, S into a single matrix in the requested order.
 *
 * @param {[number,number,number]} t - translation (tx, ty, tz)
 * @param {[number,number,number]} r - rotation in RADIANS (rx, ry, rz)
 * @param {[number,number,number]} s - scale (sx, sy, sz)
 * @param {'TRS'|'SRT'|'RTS'} order
 * @returns {Matrix4}
 */
export function compose(t, r, s, order = 'TRS') {
  const T = translationMatrix(...t);
  const R = rotationMatrix(...r);
  const S = scaleMatrix(...s);
  const M = new Matrix4();

  switch (order) {
    case 'SRT':
      // M = S · R · T
      M.multiplyMatrices(S, R).multiply(T);
      break;
    case 'RTS':
      // M = R · T · S
      M.multiplyMatrices(R, T).multiply(S);
      break;
    case 'TRS':
    default:
      // M = T · R · S
      M.multiplyMatrices(T, R).multiply(S);
      break;
  }
  return M;
}