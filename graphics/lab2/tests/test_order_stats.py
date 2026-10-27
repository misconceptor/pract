import cv2
import numpy as np
import pytest

from src.order_stats import median_filter, min_filter, max_filter

@pytest.fixture
def random_image():
    # reproducible 50x50 image with random noise
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, (50, 50), dtype=np.uint8)

def test_median_matches_opencv(random_image):
    """Our custom median filter must match OpenCV's exact output."""
    k = 3
    custom = median_filter(random_image, k=k)
    opencv = cv2.medianBlur(random_image, ksize=k)
    
    # Assert that every pixel is identical
    np.testing.assert_array_equal(custom, opencv)

def test_min_matches_opencv(random_image):
    """Our custom min filter matches OpenCV's erode (with a rectangular kernel)."""
    k = 3
    custom = min_filter(random_image, k=k)
    kernel = np.ones((k, k), np.uint8)
    opencv = cv2.erode(random_image, kernel)
    
    np.testing.assert_array_equal(custom, opencv)

def test_max_matches_opencv(random_image):
    """Our custom max filter matches OpenCV's dilate."""
    k = 3
    custom = max_filter(random_image, k=k)
    kernel = np.ones((k, k), np.uint8)
    opencv = cv2.dilate(random_image, kernel)
    
    np.testing.assert_array_equal(custom, opencv)

def test_even_kernel_raises_error(random_image):
    with pytest.raises(ValueError):
        median_filter(random_image, k=4)