import numpy as np
import pytest

from src.noise import add_salt_pepper, add_gaussian


@pytest.fixture
def gray_image():
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, (64, 64), dtype=np.uint8)


@pytest.fixture
def color_image():
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, (64, 64, 3), dtype=np.uint8)


def test_salt_pepper_is_reproducible(gray_image):
    a = add_salt_pepper(gray_image, density=0.1, rng=np.random.default_rng(0))
    b = add_salt_pepper(gray_image, density=0.1, rng=np.random.default_rng(0))
    np.testing.assert_array_equal(a, b)


def test_salt_pepper_zero_density_is_identity(gray_image):
    out = add_salt_pepper(gray_image, density=0.0, rng=np.random.default_rng(0))
    np.testing.assert_array_equal(out, gray_image)


def test_salt_pepper_full_density_only_extremes(gray_image):
    out = add_salt_pepper(gray_image, density=1.0, rng=np.random.default_rng(0))
    assert set(np.unique(out)).issubset({0, 255})


def test_salt_pepper_density_is_statistically_close(gray_image):
    density = 0.1
    out = add_salt_pepper(gray_image, density=density, rng=np.random.default_rng(0))
    corrupted = np.mean((out == 0) | (out == 255))
    # Bernoulli model: fraction should be close to `density`
    assert abs(corrupted - density) < 0.05


def test_salt_ratio_one_only_salt(gray_image):
    out = add_salt_pepper(
        gray_image, density=0.5, rng=np.random.default_rng(0), salt_ratio=1.0
    )
    # Only 0 or 255, and among those only 255
    changed = out != gray_image
    assert np.all(out[changed] == 255)


def test_salt_ratio_zero_only_pepper(gray_image):
    out = add_salt_pepper(
        gray_image, density=0.5, rng=np.random.default_rng(0), salt_ratio=0.0
    )
    changed = out != gray_image
    assert np.all(out[changed] == 0)


def test_salt_pepper_works_on_color(color_image):
    out = add_salt_pepper(color_image, density=0.1, rng=np.random.default_rng(0))
    assert out.shape == color_image.shape
    assert out.dtype == np.uint8
    # A corrupted pixel should be uniform 0 or 255 across all channels
    all_black = np.all(out == 0, axis=-1)
    all_white = np.all(out == 255, axis=-1)
    assert (all_black | all_white).any()


def test_gaussian_is_reproducible(gray_image):
    a = add_gaussian(gray_image, sigma=20, rng=np.random.default_rng(0))
    b = add_gaussian(gray_image, sigma=20, rng=np.random.default_rng(0))
    np.testing.assert_array_equal(a, b)


def test_gaussian_zero_sigma_is_identity(gray_image):
    out = add_gaussian(gray_image, sigma=0.0, rng=np.random.default_rng(0))
    np.testing.assert_array_equal(out, gray_image)


def test_gaussian_std_matches_sigma(gray_image):
    sigma = 20.0
    out = add_gaussian(gray_image, sigma=sigma, rng=np.random.default_rng(0))
    # Difference should have std close to sigma (allowing for clipping)
    diff = out.astype(np.int16) - gray_image.astype(np.int16)
    assert abs(np.std(diff) - sigma) < 3.0


def test_gaussian_invalid_sigma():
    img = np.zeros((10, 10), dtype=np.uint8)
    with pytest.raises(ValueError):
        add_gaussian(img, sigma=-1)