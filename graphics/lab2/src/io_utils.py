"""Image I/O helpers.

Canonical in-memory format used throughout the project:

    grayscale image  ->  np.ndarray, shape (H, W),    dtype uint8
    colour image ->  np.ndarray, shape (H, W, 3), dtype uint8, RGB order

OpenCV natively uses BGR for colour and H in [0, 180) for HSV, so *all*
conversions to and from OpenCV's conventions live here. The rest of the
codebase only ever sees RGB / grayscale.
"""

from __future__ import annotations

from pathlib import Path
from typing import IO, BinaryIO, Union

import cv2
import numpy as np

__all__ = [
    "load_image",
    "save_image",
    "ensure_uint8",
    "to_gray",
    "to_bgr",
    "to_rgb",
    "to_hsv",
    "is_color",
    "is_gray",
]

ImageSource = Union[str, Path, bytes, BinaryIO, IO[bytes]]

def ensure_uint8(arr: np.ndarray) -> np.ndarray:
    """Clip a numeric array to [0, 255] and cast to uint8 (no-op if already uint8)."""
    if arr.dtype == np.uint8:
        return arr
    return np.clip(arr, 0, 255).astype(np.uint8)

def is_color(img: np.ndarray) -> bool:
    """True if `img` is an (H, W, 3) array."""
    return img.ndim == 3 and img.shape[2] == 3

def is_gray(img: np.ndarray) -> bool:
    """True if `img` is a 2D (H, W) array."""
    return img.ndim == 2


def _read_bytes(source: ImageSource) -> np.ndarray:
    """Return a uint8 buffer of raw file bytes from a path / bytes / file-like."""
    if isinstance(source, (str, Path)):
        data = Path(source).read_bytes()
    elif isinstance(source, bytes):
        data = source
    elif hasattr(source, "getvalue"):           # Streamlit UploadedFile
        data = source.getvalue()
    elif hasattr(source, "read"):               # generic file-like
        data = source.read()
    else:
        raise TypeError(f"Unsupported image source: {type(source)!r}")
    return np.frombuffer(data, dtype=np.uint8)

def load_image(source: ImageSource) -> np.ndarray:
    """Load an image into canonical RGB / grayscale uint8 format.

    Accepts a filesystem path, raw ``bytes``, or any file-like object with
    ``read()`` / ``getvalue()`` (e.g. Streamlit's ``UploadedFile``).

    - single-channel images come back as ``(H, W)`` uint8
    - 3-channel images come back as ``(H, W, 3)`` uint8 in **RGB** order
    - 4-channel images have alpha flattened onto a white background
    """
    buf = _read_bytes(source)
    img = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Could not decode image — unknown or unsupported format")

    if img.ndim == 2:
        return img.astype(np.uint8, copy=False)

    if img.shape[2] == 4:                       # BGRA -> composite onto white
        alpha = img[:, :, 3:4].astype(np.float32) / 255.0
        bgr = img[:, :, :3].astype(np.float32)
        img = (bgr * alpha + 255.0 * (1.0 - alpha)).astype(np.uint8)
    else:
        img = img.astype(np.uint8, copy=False)

    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def save_image(img: np.ndarray, path: Union[str, Path]) -> None:
    """Write a canonical RGB / grayscale array to disk (PNG by default)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    img = ensure_uint8(img)
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    suffix = path.suffix.lower() or ".png"
    ok, encoded = cv2.imencode(suffix, img)
    if not ok:
        raise OSError(f"Failed to encode image for {path} (format={suffix})")
    path.write_bytes(encoded.tobytes())

def to_gray(img: np.ndarray) -> np.ndarray:
    """Convert RGB or grayscale image to 2D grayscale uint8 (ITU-R BT.601)."""
    img = ensure_uint8(img)
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def to_bgr(img: np.ndarray) -> np.ndarray:
    """Canonical RGB -> OpenCV BGR. No-op for grayscale."""
    img = ensure_uint8(img)
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)


def to_rgb(img: np.ndarray) -> np.ndarray:
    """OpenCV BGR -> canonical RGB. No-op for grayscale."""
    img = ensure_uint8(img)
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def to_hsv(img: np.ndarray) -> np.ndarray:
    """RGB -> OpenCV HSV (uint8, H in [0, 180), S/V in [0, 255]).

    Returns the same representation ``cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)``
    produces, so you can convert back with
    ``cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)``. This is the format expected by
    the HSV-based histogram-equalization routine in ``histogram_eq.py``.
    """
    img = ensure_uint8(img)
    if img.ndim == 2:
        raise ValueError("to_hsv() expects an RGB image, got grayscale")
    return cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        sys.exit("usage: python -m src.io_utils <image_path>")

    img = load_image(sys.argv[1])
    print(f"loaded  shape={img.shape} dtype={img.dtype} color={is_color(img)}")

    if is_color(img):
        hsv = to_hsv(img)
        print(f"hsv     shape={hsv.shape} dtype={hsv.dtype} "
              f"H=[{hsv[..., 0].min()}, {hsv[..., 0].max()}]")
        print(f"gray    shape={to_gray(img).shape}")