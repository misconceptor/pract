"""Linear contrast stretching for grayscale and color images."""

from __future__ import annotations

import numpy as np
from .io_utils import to_gray, ensure_uint8

__all__ = [
    "linear_contrast_stretch",
    "linear_contrast_stretch_rgb",
]


def linear_contrast_stretch(gray: np.ndarray, low_pct: float = 2.0, high_pct: float = 98.0) -> np.ndarray:
    """Apply robust linear contrast stretching to a grayscale image.
    
    Finds the intensity values at the `low_pct` and `high_pct` percentiles,
    and stretches them to cover the full [0, 255] range. Values outside
    these percentiles are clipped. This avoids being ruined by single
    outlier pixels (like a stray white reflection).
    """
    if low_pct >= high_pct:
        raise ValueError("low_pct must be less than high_pct")

    gray = to_gray(gray).astype(np.float32)

    p_low, p_high = np.percentile(gray, [low_pct, high_pct])
    
    if p_high == p_low:
        return gray.astype(np.uint8)

    stretched = (gray - p_low) * (255.0 / (p_high - p_low))
    return ensure_uint8(stretched)


def linear_contrast_stretch_rgb(rgb: np.ndarray, low_pct: float = 2.0, high_pct: float = 98.0) -> np.ndarray:
    """Apply linear contrast stretching to each RGB channel independently.
    
    NOTE: For the color part of your lab, you will compare this (RGB stretch)
    against applying it only to the V channel in HSV.
    """
    if rgb.ndim == 2:
        return linear_contrast_stretch(rgb, low_pct, high_pct)

    channels = [linear_contrast_stretch(rgb[..., i], low_pct, high_pct) for i in range(3)]
    return np.stack(channels, axis=-1)