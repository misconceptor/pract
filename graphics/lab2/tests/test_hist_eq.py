import cv2
import numpy as np
import pytest

from src.histogram_eq import equalize_gray, equalize_rgb_per_channel, equalize_hsv_v_only
from src.io_utils import to_gray

@pytest.fixture
def random_image():
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, (50, 50), dtype=np.uint8)

def test_equalize_gray_matches_opencv(random_image):
    """Our CDF equalization must match OpenCV's equalizeHist."""
    custom = equalize_gray(random_image)
    opencv = cv2.equalizeHist(random_image)
    
    np.testing.assert_array_equal(custom, opencv)

def test_equalize_rgb_preserves_shape():
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    out = equalize_rgb_per_channel(img)
    assert out.shape == (10, 10, 3)
    assert out.dtype == np.uint8


def test_equalize_hsv_preserves_hue_saturation():
    """In HSV space, H and S must be exactly preserved; only V may change.

    We inspect the intermediate HSV array from `_equalize_hsv_v_only_in_hsv`
    rather than the RGB round-trip result, because HSV<->RGB conversion on
    8-bit data introduces hue instability on low-saturation pixels. This is
    a property of the color space, not of the algorithm.
    """
    from src.histogram_eq import _equalize_hsv_v_only_in_hsv

    rng = np.random.default_rng(0)
    img = rng.integers(0, 256, (20, 20, 3), dtype=np.uint8)

    hsv_orig = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hsv_eq = _equalize_hsv_v_only_in_hsv(img)

    np.testing.assert_array_equal(
        hsv_orig[..., 0], hsv_eq[..., 0],
        err_msg="Hue channel must not be modified by V-only equalization",
    )
    np.testing.assert_array_equal(
        hsv_orig[..., 1], hsv_eq[..., 1],
        err_msg="Saturation channel must not be modified by V-only equalization",
    )
    # sanity: V should have changed on a random image
    assert not np.array_equal(hsv_orig[..., 2], hsv_eq[..., 2]), \
        "V channel should change on a non-trivial image"