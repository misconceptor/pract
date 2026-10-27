"""Synthetic noise generators for controlled experiments.

Two classical noise models:

- Salt and pepper (impulse): a fraction of pixels is forced to 0 or 255.
  Median / min / max filters are specifically designed for this.
- Gaussian: additive zero-mean white noise spread over the whole image.
  Median barely helps; smoothing filters do better.

Every generator accepts a ``np.random.Generator`` so results are exactly
reproducible — an important point for a lab report where "noisy image N"
must be identical across runs.
"""

from __future__ import annotations

import numpy as np

__all__ = ["add_salt_pepper", "add_gaussian"]


def add_salt_pepper(
    img: np.ndarray,
    density: float = 0.05,
    rng: np.random.Generator | None = None,
    salt_ratio: float = 0.5,
) -> np.ndarray:
    """Add salt-and-pepper (impulse) noise to an image.

    Uses the standard Bernoulli model: each pixel is independently corrupted
    with probability ``density``, and each corrupted pixel is set to 255
    ("salt") with probability ``salt_ratio`` or to 0 ("pepper") otherwise.

    Parameters
    ----------
    img : np.ndarray
        2D grayscale or 3D colour image (uint8). Works for both.
    density : float
        Total fraction of corrupted pixels, in [0, 1]. ``0.05`` corrupts ~5 %
        of pixels.
    rng : np.random.Generator, optional
        Reproducible random source. If ``None``, a fresh source is created.
        Pass ``np.random.default_rng(seed)`` to make experiments reproducible.
    salt_ratio : float
        Fraction of the corrupted pixels set to white. ``0.5`` splits evenly
        between salt and pepper; ``1.0`` gives pure salt; ``0.0`` pure pepper.

    Returns
    -------
    np.ndarray
        New image with the same shape and dtype; corrupted pixels are 0 or 255.
    """
    if not 0.0 <= density <= 1.0:
        raise ValueError("density must be in [0, 1]")
    if not 0.0 <= salt_ratio <= 1.0:
        raise ValueError("salt_ratio must be in [0, 1]")

    rng = rng or np.random.default_rng()
    h, w = img.shape[:2]

    # Each pixel corrupted independently with probability `density`
    corrupt = rng.random((h, w)) < density
    # Among corrupted, split into salt and pepper
    salt = corrupt & (rng.random((h, w)) < salt_ratio)
    pepper = corrupt & ~salt

    out = img.copy()
    out[salt] = 255
    out[pepper] = 0
    return out


def add_gaussian(
    img: np.ndarray,
    sigma: float = 20.0,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Add zero-mean additive white Gaussian noise.

    Parameters
    ----------
    img : np.ndarray
        Image (uint8). Works for grayscale (2D) and colour (3D).
    sigma : float
        Standard deviation of the Gaussian noise in intensity units
        [0, 255]. Typical values: 10 (mild), 20 (moderate), 50 (severe).
    rng : np.random.Generator, optional
        Reproducible random source.

    Returns
    -------
    np.ndarray
        uint8 image with additive Gaussian noise, clipped to [0, 255].
    """
    if sigma < 0:
        raise ValueError("sigma must be non-negative")

    rng = rng or np.random.default_rng()
    noise = rng.normal(loc=0.0, scale=sigma, size=img.shape)
    noisy = img.astype(np.float32) + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)