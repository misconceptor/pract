"""Histogram equalization for grayscale and color images.

Implements the CDF-based equalization algorithm from scratch using NumPy.
Includes the specific comparison required by the lab:
  - RGB per-channel equalization
  - HSV V-channel-only equalization
"""

from __future__ import annotations

import cv2
import numpy as np
from .io_utils import to_gray, to_hsv

__all__ = [
    "equalize_gray",
    "equalize_rgb_per_channel",
    "equalize_hsv_v_only",
]

def equalize_gray(gray: np.ndarray) -> np.ndarray:
    """CDF-based histogram equalization matching OpenCV's formula.

    OpenCV subtracts the count of the first non-zero bin so that the lowest
    non-empty intensity maps to 0. This gives a fuller stretch than the
    textbook formula and produces byte-identical output to cv2.equalizeHist.
    """
    gray = to_gray(gray)

    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    nonzero = np.nonzero(hist)[0]
    if len(nonzero) == 0:        #because empty is impossible 
        return gray.copy()

    i0 = nonzero[0]
    c0 = hist[i0]
    total = hist.sum()
    denom = total - c0

    if denom == 0:                     
        return gray.copy()

    cdf = hist.cumsum()
    scale = 255.0 / denom
    lut = np.round((cdf - c0) * scale).clip(0, 255).astype(np.uint8)
    return lut[gray]


def _equalize_hsv_v_only_in_hsv(rgb: np.ndarray) -> np.ndarray:
    """Return HSV array with only the V channel equalized.

    Exposed as a helper so tests can verify that H and S are untouched in HSV
    space, without going through an RGB round-trip that quantizes to uint8.
    """
    hsv = to_hsv(rgb)
    hsv[..., 2] = equalize_gray(hsv[..., 2])
    return hsv


def equalize_hsv_v_only(rgb: np.ndarray) -> np.ndarray:
    """Equalize only V in HSV and convert back to RGB (colour-preserving)."""
    if rgb.ndim == 2:
        return equalize_gray(rgb)
    hsv = _equalize_hsv_v_only_in_hsv(rgb)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

def equalize_rgb_per_channel(rgb: np.ndarray) -> np.ndarray:
    """Equalize each R, G, B channel independently (can distort colors)."""
    if rgb.ndim == 2:
        return equalize_gray(rgb)

    channels = [equalize_gray(rgb[..., i]) for i in range(3)]
    return np.stack(channels, axis=-1)


def equalize_hsv_v_only(rgb: np.ndarray) -> np.ndarray:
    """Equalize only the V channel in HSV (preserves hue/saturation)."""
    if rgb.ndim == 2:
        return equalize_gray(rgb)

    hsv = to_hsv(rgb)
    hsv[..., 2] = equalize_gray(hsv[..., 2])
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)