/**
 * Unit tests for js/transforms.js.
 *
 * These tests verify two things at once:
 *   1. That our matrices are algebraically correct (position of each
 *      element matches the textbook matrix for the given operation).
 *   2. That our Matrix4 values agree with three.js when set directly,
 *      so nothing surprises us at render time.
 *
 * Matrix values are shown in row-major form for readability via the
 * rows() helper. Internally three.js stores them column-major.
 */

import { describe, it, expect } from 'vitest';
import { Matrix4 } from 'three';
import {
  translationMatrix,
  scaleMatrix,
  rotationX,
  rotationY,
  rotationZ,
  rotationMatrix,
  compose,
} from '../js/transforms.js';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Convert a Matrix4 (column-major) into a row-major 4x4 array. */
function rows(m) {
  const e = m.elements;
  return [
    [e[0], e[4], e[8],  e[12]],
    [e[1], e[5], e[9],  e[13]],
    [e[2], e[6], e[10], e[14]],
    [e[3], e[7], e[11], e[15]],
  ];
}

/** Assert every cell of `m` matches the row-major `expected` grid. */
function expectRows(m, expected) {
  const got = rows(m);
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      expect(got[r][c]).toBeCloseTo(expected[r][c], 10);
    }
  }
}

/** Manual M · column-vector(x, y, z, 1) using column-major storage. */
function applyToPoint(M, { x, y, z }) {
  const e = M.elements;
  return {
    x: e[0] * x + e[4] * y + e[8]  * z + e[12],
    y: e[1] * x + e[5] * y + e[9]  * z + e[13],
    z: e[2] * x + e[6] * y + e[10] * z + e[14],
  };
}

const IDENTITY_ROWS = [
  [1, 0, 0, 0],
  [0, 1, 0, 0],
  [0, 0, 1, 0],
  [0, 0, 0, 1],
];

// ---------------------------------------------------------------------------
// Translation
// ---------------------------------------------------------------------------

describe('translationMatrix', () => {
  it('places (tx, ty, tz) in the right-hand column', () => {
    expectRows(translationMatrix(3, -2, 5), [
      [1, 0, 0,  3],
      [0, 1, 0, -2],
      [0, 0, 1,  5],
      [0, 0, 0,  1],
    ]);
  });

  it('is the identity for zero translation', () => {
    expectRows(translationMatrix(0, 0, 0), IDENTITY_ROWS);
  });
});

// ---------------------------------------------------------------------------
// Scale
// ---------------------------------------------------------------------------

describe('scaleMatrix', () => {
  it('places (sx, sy, sz) on the main diagonal', () => {
    expectRows(scaleMatrix(2, 3, 4), [
      [2, 0, 0, 0],
      [0, 3, 0, 0],
      [0, 0, 4, 0],
      [0, 0, 0, 1],
    ]);
  });

  it('is the identity for unit scale', () => {
    expectRows(scaleMatrix(1, 1, 1), IDENTITY_ROWS);
  });
});

// ---------------------------------------------------------------------------
// Per-axis rotation
// ---------------------------------------------------------------------------

describe('rotationX', () => {
  it('is the identity at 0', () => {
    expectRows(rotationX(0), IDENTITY_ROWS);
  });

  it('by 90° (cos=0, sin=1) maps Y into Z', () => {
    expectRows(rotationX(Math.PI / 2), [
      [1,  0,  0, 0],
      [0,  0, -1, 0],
      [0,  1,  0, 0],
      [0,  0,  0, 1],
    ]);
  });
});

describe('rotationY', () => {
  it('is the identity at 0', () => {
    expectRows(rotationY(0), IDENTITY_ROWS);
  });

  it('by 90° maps Z into X', () => {
    expectRows(rotationY(Math.PI / 2), [
      [ 0, 0, 1, 0],
      [ 0, 1, 0, 0],
      [-1, 0, 0, 0],
      [ 0, 0, 0, 1],
    ]);
  });
});

describe('rotationZ', () => {
  it('is the identity at 0', () => {
    expectRows(rotationZ(0), IDENTITY_ROWS);
  });

  it('by 90° maps X into Y', () => {
    expectRows(rotationZ(Math.PI / 2), [
      [0, -1, 0, 0],
      [1,  0, 0, 0],
      [0,  0, 1, 0],
      [0,  0, 0, 1],
    ]);
  });
});

// ---------------------------------------------------------------------------
// Combined rotation R = Rz · Ry · Rx
// ---------------------------------------------------------------------------

describe('rotationMatrix', () => {
  it('is the identity when all angles are 0', () => {
    expectRows(rotationMatrix(0, 0, 0), IDENTITY_ROWS);
  });

  it('matches rotationZ when only rz is non-zero', () => {
    expectRows(rotationMatrix(0, 0, Math.PI / 2), rows(rotationZ(Math.PI / 2)));
  });

  it('composes as Rz · Ry · Rx (X first, then Y, then Z)', () => {
    const rx = 0.3, ry = -0.7, rz = 1.1;
    const expected = new Matrix4()
      .multiplyMatrices(rotationZ(rz), rotationY(ry))
      .multiply(rotationX(rx));
    expectRows(rotationMatrix(rx, ry, rz), rows(expected));
  });
});

// ---------------------------------------------------------------------------
// compose(): composition order matters
// ---------------------------------------------------------------------------

describe('compose', () => {
  it('TRS with defaults is the identity', () => {
    expectRows(compose([0, 0, 0], [0, 0, 0], [1, 1, 1], 'TRS'), IDENTITY_ROWS);
  });

  it('TRS = T · R · S: translation is not scaled', () => {
    // With identity rotation, T · S has the translation column intact:
    //   [ 2 0 0 1 ]
    //   [ 0 2 0 2 ]
    //   [ 0 0 2 3 ]
    //   [ 0 0 0 1 ]
    expectRows(compose([1, 2, 3], [0, 0, 0], [2, 2, 2], 'TRS'), [
      [2, 0, 0, 1],
      [0, 2, 0, 2],
      [0, 0, 2, 3],
      [0, 0, 0, 1],
    ]);
  });

  it('SRT = S · R · T: translation is scaled', () => {
    // S · T multiplies each translation component by the scale:
    //   [ 2 0 0 2 ]
    //   [ 0 2 0 4 ]
    //   [ 0 0 2 6 ]
    //   [ 0 0 0 1 ]
    expectRows(compose([1, 2, 3], [0, 0, 0], [2, 2, 2], 'SRT'), [
      [2, 0, 0, 2],
      [0, 2, 0, 4],
      [0, 0, 2, 6],
      [0, 0, 0, 1],
    ]);
  });

  it('RTS = R · T · S: with identity R, same as TRS', () => {
    expectRows(compose([1, 2, 3], [0, 0, 0], [2, 2, 2], 'RTS'), [
      [2, 0, 0, 1],
      [0, 2, 0, 2],
      [0, 0, 2, 3],
      [0, 0, 0, 1],
    ]);
  });

  it('TRS and SRT produce different matrices for non-identity rotation', () => {
    const t = [1, 2, 3];
    const r = [0.4, 0.6, -0.2];
    const s = [2, 1.5, 0.5];
    const a = rows(compose(t, r, s, 'TRS'));
    const b = rows(compose(t, r, s, 'SRT'));
    let differs = false;
    for (let i = 0; i < 4; i++) {
      for (let j = 0; j < 4; j++) {
        if (Math.abs(a[i][j] - b[i][j]) > 1e-6) differs = true;
      }
    }
    expect(differs).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// End-to-end: applying the matrix to a point
// ---------------------------------------------------------------------------

describe('matrix · point', () => {
  it('translate maps the origin to (tx, ty, tz)', () => {
    const { x, y, z } = applyToPoint(translationMatrix(3, -2, 5), { x: 0, y: 0, z: 0 });
    expect(x).toBeCloseTo(3);
    expect(y).toBeCloseTo(-2);
    expect(z).toBeCloseTo(5);
  });

  it('scale multiplies each coordinate', () => {
    const { x, y, z } = applyToPoint(scaleMatrix(2, 3, 4), { x: 1, y: 1, z: 1 });
    expect(x).toBeCloseTo(2);
    expect(y).toBeCloseTo(3);
    expect(z).toBeCloseTo(4);
  });

  it('TRS applies S first, then R, then T', () => {
    // s = 2, t = (1,0,0), r = 0: point (1,0,0) → S → (2,0,0) → T → (3,0,0)
    const M = compose([1, 0, 0], [0, 0, 0], [2, 2, 2], 'TRS');
    const { x } = applyToPoint(M, { x: 1, y: 0, z: 0 });
    expect(x).toBeCloseTo(3);
  });

  it('SRT applies T first, then R, then S', () => {
    // t = (1,0,0), s = 2, r = 0: point (1,0,0) → T → (2,0,0) → S → (4,0,0)
    const M = compose([1, 0, 0], [0, 0, 0], [2, 2, 2], 'SRT');
    const { x } = applyToPoint(M, { x: 1, y: 0, z: 0 });
    expect(x).toBeCloseTo(4);
  });
});