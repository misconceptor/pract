/**
 * Procedural texture generation.
 *
 * The texture is drawn entirely in code onto an off-screen canvas,
 * then wrapped in a THREE.CanvasTexture. No image files are needed,
 * which keeps the project self-contained and easy to grade.
 *
 * The pattern is designed to make UV mapping visible on the extruded
 * text: a diagonal hue gradient, a regular grid of lines, and small
 * accent dots at every grid intersection. If the UVs on the text are
 * correct, you see the grid follow the letter surfaces; if they were
 * wrong (e.g. all zero), you would see a single flat colour instead.
 *
 * The texture is square and its content spans the full [0,1] UV range,
 * so it maps cleanly onto every face of the extruded geometry.
 */

import * as THREE from 'three';

const DEFAULT_CONFIG = {
  size: 512,          // canvas resolution (square)
  tiles: 8,           // grid divisions across the texture
  hueStart: 220,      // gradient start hue (blue)
  hueEnd: 280,        // gradient end hue (violet)
  accent: '#ffffff',  // colour of grid lines and dots
};

/**
 * Build a new procedural texture.
 *
 * @param {Partial<typeof DEFAULT_CONFIG>} config
 * @returns {THREE.CanvasTexture}
 */
export function createProceduralTexture(config = {}) {
  const cfg = { ...DEFAULT_CONFIG, ...config };

  const canvas = document.createElement('canvas');
  canvas.width = cfg.size;
  canvas.height = cfg.size;
  const ctx = canvas.getContext('2d');

  // --- Diagonal hue gradient ----------------------------------------
  const grad = ctx.createLinearGradient(0, 0, cfg.size, cfg.size);
  grad.addColorStop(0.0, `hsl(${cfg.hueStart}, 70%, 55%)`);
  grad.addColorStop(1.0, `hsl(${cfg.hueEnd}, 70%, 45%)`);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, cfg.size, cfg.size);

  // --- Grid lines ---------------------------------------------------
  const cell = cfg.size / cfg.tiles;
  ctx.strokeStyle = hexToRgba(cfg.accent, 0.18);
  ctx.lineWidth = 2;
  for (let i = 0; i <= cfg.tiles; i++) {
    const p = i * cell;
    ctx.beginPath();
    ctx.moveTo(p, 0);
    ctx.lineTo(p, cfg.size);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, p);
    ctx.lineTo(cfg.size, p);
    ctx.stroke();
  }

  // --- Accent dots at intersections ---------------------------------
  ctx.fillStyle = hexToRgba(cfg.accent, 0.45);
  for (let i = 0; i <= cfg.tiles; i++) {
    for (let j = 0; j <= cfg.tiles; j++) {
      ctx.beginPath();
      ctx.arc(i * cell, j * cell, 3, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.anisotropy = 8;
  texture.needsUpdate = true;
  return texture;
}

/** '#rrggbb' + alpha 0..1 -> 'rgba(r, g, b, a)' */
function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}