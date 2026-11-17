/**
 * Build a 3D mesh from a string.
 *
 * Pipeline:
 *   1. Load the typeface JSON (cached after the first call).
 *   2. Feed it to TextGeometry with an extrusion depth and a small
 *      bevel, producing real vertices + UVs + normals from the font
 *      outline.
 *   3. Center the geometry on the origin so rotation is around the
 *      visual center rather than the bottom-left baseline.
 *   4. Wrap it in a Mesh with a MeshStandardMaterial using the
 *      provided texture.
 *
 * This is the "array of vertex coordinates" part of the assignment:
 * after step 2, geometry.attributes.position is a flat Float32Array
 * of xyz triples — one per vertex — and geometry.index (when present)
 * is the triangle index list.
 *
 * API note: three.js renamed TextGeometry's extrusion parameter from
 * "height" to "depth" in r145. Passing "height" is silently ignored
 * and the geometry is extruded to depth = 50 (the default), which
 * makes the object 50 world units deep. We use "depth" here.
 */

import * as THREE from 'three';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';

const FONT_URL = 'assets/fonts/helvetiker_regular.typeface.json';

// Module-level cache — the font JSON is ~60 KB and only needs loading
// once per page load.
let _fontPromise = null;

function loadFont(url) {
  if (!_fontPromise) {
    const loader = new FontLoader();
    _fontPromise = loader.loadAsync(url).catch(err => {
      _fontPromise = null; // allow retry on failure
      throw new Error(`Failed to load font "${url}": ${err.message}`);
    });
  }
  return _fontPromise;
}

const DEFAULT_OPTIONS = {
  size: 1.0,          // cap height of the text in world units
  depth: 0.25,        // extrusion depth (was: "height" before r145)
  curveSegments: 10,  // smoothness of curved glyph outlines
  bevelEnabled: true,
  bevelThickness: 0.02,
  bevelSize: 0.015,
  bevelSegments: 3,
};

/**
 * Build a textured 3D mesh for `string`.
 *
 * @param {string} string
 * @param {THREE.Texture} texture
 * @param {Partial<typeof DEFAULT_OPTIONS>} [options]
 * @returns {Promise<{
 *   mesh: THREE.Mesh,
 *   geometry: THREE.BufferGeometry,
 *   vertexCount: number,
 *   triangleCount: number,
 * }>}
 */
export async function createTextMesh(string, texture, options = {}) {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const font = await loadFont(FONT_URL);

  const geometry = new TextGeometry(string, { font, ...opts });

  // Center the geometry on the origin. The font baseline is at y=0
  // and the text runs along +x, so without this the mesh would rotate
  // around its bottom-left corner, which looks wrong on screen.
  geometry.computeBoundingBox();
  const bb = geometry.boundingBox;
  const cx = (bb.max.x + bb.min.x) / 2;
  const cy = (bb.max.y + bb.min.y) / 2;
  const cz = (bb.max.z + bb.min.z) / 2;
  geometry.translate(-cx, -cy, -cz);

  // Recompute bounds after translation so callers see the centered
  // bounding box (useful for camera framing in main.js).
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();

  const material = new THREE.MeshStandardMaterial({
    map: texture,
    metalness: 0.2,
    roughness: 0.45,
    side: THREE.DoubleSide, // so back faces of open bevels don't vanish
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = 'text-mesh';

  const vertexCount = geometry.attributes.position.count;
  const triangleCount = geometry.index
    ? geometry.index.count / 3
    : geometry.attributes.position.count / 3;

  console.log(
    `[text-mesh] "${string}": ${vertexCount} vertices, ` +
    `${triangleCount} triangles, size = ` +
    `${(bb.max.x - bb.min.x).toFixed(2)} × ` +
    `${(bb.max.y - bb.min.y).toFixed(2)} × ` +
    `${(bb.max.z - bb.min.z).toFixed(2)}`
  );

  return { mesh, geometry, vertexCount, triangleCount };
}