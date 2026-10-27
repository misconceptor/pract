"""Nonlinear filters based on order statistics.

Implements median, min, max, and general percentile (rank) filters from
scratch using NumPy.
"""

from __future__ import annotations

import numpy as np
from typing import Optional

__all__ = [
    "median_filter",
    "min_filter",
    "max_filter",
    "percentile_filter",
    "apply_to_color",
]

def _apply_padding(img: np.ndarray, k: int, mode: str = "edge") -> np.ndarray:
    """Pad a 2D image so sliding windows fit at the borders.

    Default is 'edge' (repeat the border pixel), which matches OpenCV's
    BORDER_REPLICATE used by cv2.medianBlur / cv2.erode / cv2.dilate.
    """
    pad = k // 2
    return np.pad(img, pad, mode=mode)


def _order_stats_2d(
    img: np.ndarray,
    k: int,
    rank_fn: callable,
    padding_mode: str = "edge",     #  was "reflect", had a bug
) -> np.ndarray:

    """Generic 2D order-statistic filter.
    
    Parameters
    ----------
    img : np.ndarray
        2D grayscale image (uint8 or float).
    k : int
        Kernel size (must be odd).
    rank_fn : callable
        Function that takes a 1D array of sorted values and returns an index or value.
    padding_mode : str
        How to pad the borders (default 'reflect').
    """
    if k % 2 == 0:
        raise ValueError("Kernel size k must be odd.")
    if img.ndim != 2:
        raise ValueError("Input must be a 2D grayscale image.")

    padded = _apply_padding(img, k, mode=padding_mode)
    windows = np.lib.stride_tricks.sliding_window_view(padded, (k, k))
    windows_flat = windows.reshape(img.shape[0], img.shape[1], -1)
    
    return rank_fn(np.sort(windows_flat, axis=-1))


def median_filter(img: np.ndarray, k: int = 3) -> np.ndarray:
    """Apply a 2D median filter.
    
    The median is the middle value of the sorted pixels in the k x k window.
    Perfect for salt-and-pepper noise.
    """
    def get_median(sorted_windows):
        mid_idx = (k * k) // 2
        return sorted_windows[..., mid_idx]
    
    return _order_stats_2d(img, k, get_median)


def min_filter(img: np.ndarray, k: int = 3) -> np.ndarray:
    """Apply a 2D minimum filter (erosion).
    
    Takes the darkest pixel in the window. 
    Expands dark regions and removes "salt" (white) noise.
    """
    def get_min(sorted_windows):
        return sorted_windows[..., 0]
    
    return _order_stats_2d(img, k, get_min)


def max_filter(img: np.ndarray, k: int = 3) -> np.ndarray:
    """Apply a 2D maximum filter (dilation).
    
    Takes the brightest pixel in the window.
    Expands bright regions and removes "pepper" (black) noise.
    """
    def get_max(sorted_windows):
        return sorted_windows[..., -1]
    
    return _order_stats_2d(img, k, get_max)


def percentile_filter(img: np.ndarray, k: int = 3, percentile: float = 50.0) -> np.ndarray:
    """Apply a general percentile (rank) filter.
    
    percentile=0   -> Min filter
    percentile=50  -> Median filter
    percentile=100 -> Max filter
    """
    if not 0.0 <= percentile <= 100.0:
        raise ValueError("Percentile must be between 0 and 100.")

    def get_percentile(sorted_windows):
        idx = int(round((percentile / 100.0) * (k * k - 1)))
        return sorted_windows[..., idx]
    
    return _order_stats_2d(img, k, get_percentile)


def apply_to_color(img: np.ndarray, filter_fn: callable, **kwargs) -> np.ndarray:
    """Apply a 2D filter to each channel of a color image (RGB or HSV)."""
    if img.ndim == 2:
        return filter_fn(img, **kwargs)
        
    channels = [filter_fn(img[..., i], **kwargs) for i in range(img.shape[2])]
    return np.stack(channels, axis=-1)