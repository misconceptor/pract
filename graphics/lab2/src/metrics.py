"""Image quality metrics and statistics."""

from __future__ import annotations

import numpy as np
from .io_utils import to_gray

__all__ = [
    "mse",
    "psnr",
    "entropy",
    "std_dev",
    "histogram_stats",
]


def mse(img1: np.ndarray, img2: np.ndarray) -> float:
    """Mean Squared Error between two images (computed in grayscale).

    Both inputs are converted to grayscale first, so a colour image can be
    compared against a grayscale noisy version without errors. This mirrors
    the convention used in most denoising papers.
    """
    a = to_gray(img1).astype(np.float64)
    b = to_gray(img2).astype(np.float64)
    if a.shape != b.shape:
        raise ValueError(f"Shape mismatch after grayscale: {a.shape} vs {b.shape}")
    return float(np.mean((a - b) ** 2))


def psnr(img1: np.ndarray, img2: np.ndarray) -> float:
    """Peak Signal-to-Noise Ratio (in dB), computed in grayscale."""
    error = mse(img1, img2)
    if error == 0:
        return float("inf")
    return float(10.0 * np.log10((255.0 ** 2) / error))


def entropy(img: np.ndarray) -> float:
    """Shannon entropy of a grayscale image."""
    gray = to_gray(img)
    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    hist = hist / hist.sum()
    hist = hist[hist > 0]
    return float(-np.sum(hist * np.log2(hist)))


def std_dev(img: np.ndarray) -> float:
    """Standard deviation of pixel intensities."""
    return float(np.std(to_gray(img)))


def histogram_stats(img: np.ndarray) -> dict:
    """Return a dictionary of useful stats for the report."""
    gray = to_gray(img)
    return {
        "min": int(gray.min()),
        "max": int(gray.max()),
        "mean": float(gray.mean()),
        "std": float(np.std(gray)),
        "entropy": entropy(gray),
    }