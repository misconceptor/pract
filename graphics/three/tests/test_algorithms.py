"""pytest suite for the Lab 3 raster algorithms.

Run everything (this file + the doctests inside algorithms/*.py) with:

    pytest

from the project root.

Currently covers the three line algorithms. Circle tests will be added
once algorithms/bresenham_circle.py is written.
"""

import pytest

from algorithms import step_line, dda_line, bresenham_line, bresenham_circle


LINE_FNS = [step_line, dda_line, bresenham_line]

# (x1, y1, x2, y2, expected pixel count = max(|dx|, |dy|) + 1)
LINE_CASES = [
    (0, 0, 0, 0, 1),       # degenerate: same point at origin
    (3, 3, 3, 3, 1),       # degenerate: same point off origin
    (0, 0, 5, 0, 6),       # horizontal, rightward
    (5, 0, 0, 0, 6),       # horizontal, leftward
    (0, 0, 0, 4, 5),       # vertical, upward
    (0, 4, 0, 0, 5),       # vertical, downward
    (0, 0, 5, 2, 6),       # shallow, quadrant I
    (0, 0, 2, 5, 6),       # steep,   quadrant I
    (0, 0, -5, -2, 6),     # shallow, quadrant III
    (0, 0, -2, -5, 6),     # steep,   quadrant III
    (-3, -2, 2, 3, 6),     # diagonal across quadrants
    (5, 2, 0, 0, 6),       # reverse direction
]


@pytest.mark.parametrize("fn", LINE_FNS)
@pytest.mark.parametrize("x1,y1,x2,y2,count", LINE_CASES)
def test_pixel_count(fn, x1, y1, x2, y2, count):
    """Every line algorithm emits max(|dx|, |dy|) + 1 pixels."""
    assert len(fn(x1, y1, x2, y2)) == count


@pytest.mark.parametrize("fn", LINE_FNS)
@pytest.mark.parametrize("x1,y1,x2,y2,count", LINE_CASES)
def test_endpoints(fn, x1, y1, x2, y2, count):
    """First pixel == (x1, y1), last == (x2, y2), in input order."""
    pixels = fn(x1, y1, x2, y2)
    assert pixels[0] == (x1, y1)
    assert pixels[-1] == (x2, y2)


@pytest.mark.parametrize("fn", LINE_FNS)
@pytest.mark.parametrize("x1,y1,x2,y2,count", LINE_CASES)
def test_pixels_are_int_pairs(fn, x1, y1, x2, y2, count):
    """Every pixel is a 2-tuple of Python ints (never floats)."""
    for x, y in fn(x1, y1, x2, y2):
        assert isinstance(x, int) and isinstance(y, int)


@pytest.mark.parametrize("fn", LINE_FNS)
@pytest.mark.parametrize("x1,y1,x2,y2,count", [
    (0, 0, 5, 2, 6),
    (0, 0, 2, 5, 6),
    (-3, -2, 2, 3, 6),
    (5, 2, 0, 0, 6),
])
def test_consecutive_pixels_are_adjacent(fn, x1, y1, x2, y2, count):
    """Consecutive pixels differ by at most 1 on each axis.

    This is the defining property of a *connected* rasterization: no
    gaps, no jumps.
    """
    pixels = fn(x1, y1, x2, y2)
    for (xa, ya), (xb, yb) in zip(pixels, pixels[1:]):
        assert abs(xb - xa) <= 1
        assert abs(yb - ya) <= 1


@pytest.mark.parametrize("x1,y1,x2,y2,count", [
    (0, 0, 5, 2, 6),
    (0, 0, 4, 0, 5),
    (0, 0, 0, 4, 5),
    (0, 0, 1, 1, 2),
    (-3, -2, 2, 3, 6),
])
def test_three_line_algorithms_agree(x1, y1, x2, y2, count):
    """On non-boundary inputs the three line algorithms agree pixel-for-pixel.

    DDA accumulates float error and Bresenham uses integer arithmetic,
    so they *could* diverge at an exact half-pixel rounding boundary.
    None of the inputs above hit such a boundary.
    """
    assert (
        step_line(x1, y1, x2, y2)
        == dda_line(x1, y1, x2, y2)
        == bresenham_line(x1, y1, x2, y2)
    )


@pytest.mark.parametrize("fn", LINE_FNS)
def test_float_inputs_are_rounded(fn):
    """The package contract: int(round(v)) binds real input to the grid."""
    assert fn(0.4, 0.6, 3.4, 2.6) == fn(0, 1, 3, 3)
    assert fn(-0.4, -0.6, -3.4, -2.6) == fn(0, -1, -3, -3)


REFERENCE = [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]


@pytest.mark.parametrize("fn", LINE_FNS)
def test_reference_example(fn):
    """The worked example from the report: (0,0) -> (5,2)."""
    assert fn(0, 0, 5, 2) == REFERENCE


# ----------------------------------------------------------------------
# Circle tests
# ----------------------------------------------------------------------
#
# Expected pixel counts for the CIRCLE_CASES table below were derived by
# walking through the algorithm by hand (see the module docstring of
# algorithms/bresenham_circle.py for the r = 3 walk-through). The counts
# are not directly derived from a formula because the exact number
# depends on where the decision parameter crosses zero, which in turn
# depends on r.

# (cx, cy, r, expected distinct pixel count)
CIRCLE_CASES = [
    (0, 0, 0, 1),    # degenerate: single pixel at center
    (0, 0, 1, 4),    # four axis points
    (0, 0, 2, 12),
    (0, 0, 3, 16),
    (0, 0, 4, 24),
    (0, 0, 5, 28),
    (0, 0, 10, 56),
    (10, -5, 5, 28),  # non-origin center
]


@pytest.mark.parametrize("cx,cy,r,count", CIRCLE_CASES)
def test_circle_pixel_count(cx, cy, r, count):
    """Every circle produces the expected number of distinct pixels."""
    assert len(bresenham_circle(cx, cy, r)) == count


@pytest.mark.parametrize("cx,cy,r,count", CIRCLE_CASES)
def test_circle_pixels_are_int_pairs(cx, cy, r, count):
    for x, y in bresenham_circle(cx, cy, r):
        assert isinstance(x, int) and isinstance(y, int)


@pytest.mark.parametrize("cx,cy,r,count", CIRCLE_CASES)
def test_circle_pixels_are_distinct(cx, cy, r, count):
    """The returned list must not contain duplicates."""
    pixels = bresenham_circle(cx, cy, r)
    assert len(pixels) == len(set(pixels))


@pytest.mark.parametrize("cx,cy,r,count", CIRCLE_CASES)
def test_circle_pixels_are_on_or_near_circle(cx, cy, r, count):
    """Every pixel satisfies Bresenham's error bound.

    For a point at distance D from the center, the midpoint algorithm
    guarantees |D - r| <= 1/2 + O(1/r), so in squared-distance space
    |x^2 + y^2 - r^2| stays within about r. We use a small safety
    margin of +2.
    """
    for x, y in bresenham_circle(cx, cy, r):
        dx = x - cx
        dy = y - cy
        err = abs(dx * dx + dy * dy - r * r)
        assert err <= r + 2, (
            f"pixel ({x},{y}) too far from circle of r={r} at ({cx},{cy}): "
            f"squared-distance error {err}"
        )


@pytest.mark.parametrize("cx,cy,r", [
    (0, 0, 1),
    (0, 0, 2),
    (0, 0, 3),
    (0, 0, 5),
    (7, -3, 6),
])
def test_circle_symmetric(cx, cy, r):
    """Every pixel appears with all of its 8-fold symmetric images.

    The eight images of (dx, dy) around (cx, cy) are:
        (+-dx, +-dy) and (+-dy, +-dx), with independent signs.
    This is the property that lets the algorithm compute only one octant.
    """
    pixels = set(bresenham_circle(cx, cy, r))
    for x, y in pixels:
        dx, dy = x - cx, y - cy
        expected = {
            (cx + dx, cy + dy), (cx - dx, cy + dy),
            (cx + dx, cy - dy), (cx - dx, cy - dy),
            (cx + dy, cy + dx), (cx - dy, cy + dx),
            (cx + dy, cy - dx), (cx - dy, cy - dx),
        }
        assert expected.issubset(pixels), (
            f"missing symmetric counterparts of ({x},{y}) "
            f"for circle at ({cx},{cy}) r={r}"
        )


@pytest.mark.parametrize("cx,cy,r", [
    (5, 5, 0),
    (0, 0, 1),
    (3, -3, 5),
    (100, 200, 10),
])
def test_circle_translation_invariance(cx, cy, r):
    """Translating the center by (cx, cy) translates every pixel."""
    base = set(bresenham_circle(0, 0, r))
    shifted = set(bresenham_circle(cx, cy, r))
    expected = {(x + cx, y + cy) for x, y in base}
    assert shifted == expected


def test_circle_r_zero_is_single_pixel_at_center():
    assert bresenham_circle(3, 4, 0) == [(3, 4)]
    assert bresenham_circle(-1, -1, 0) == [(-1, -1)]


def test_circle_negative_radius_raises():
    with pytest.raises(ValueError):
        bresenham_circle(0, 0, -1)


def test_circle_float_inputs_are_rounded():
    """Package contract: real input is bound to the integer grid."""
    assert bresenham_circle(0.4, 0.6, 2.6) == bresenham_circle(0, 1, 3)
    assert bresenham_circle(-0.4, -0.6, 2.4) == bresenham_circle(0, -1, 2)


def test_circle_reference_r1():
    """Reference example from the module docstring."""
    assert bresenham_circle(0, 0, 1) == [(-1, 0), (0, -1), (0, 1), (1, 0)]


def test_circle_reference_r2():
    """Reference example from the module docstring."""
    assert bresenham_circle(0, 0, 2) == [
        (-2, -1), (-2, 0), (-2, 1),
        (-1, -2), (-1, 2),
        (0, -2), (0, 2),
        (1, -2), (1, 2),
        (2, -1), (2, 0), (2, 1),
    ]