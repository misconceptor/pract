"""Tests for the bonus anti-aliased (Wu) line algorithm."""

import math

import pytest

from extras import antialiased_line


# Representative non-degenerate cases spanning both octants and all
# four quadrants, plus the axis-aligned edges.
LINE_CASES = [
    (0, 0, 5, 2),    # shallow, quadrant I
    (0, 0, 2, 5),    # steep, quadrant I
    (0, 0, -5, -2),  # shallow, quadrant III
    (0, 0, -2, -5),  # steep, quadrant III
    (-3, -2, 2, 3),  # diagonal across quadrants
    (5, 2, 0, 0),    # reverse direction
    (0, 0, 5, 0),    # horizontal
    (0, 0, 0, 5),    # vertical
    (0, 0, 4, 2),    # exact-tie gradient (0.5)
]


@pytest.mark.parametrize("x1,y1,x2,y2", LINE_CASES)
def test_alphas_in_range(x1, y1, x2, y2):
    for _, _, a in antialiased_line(x1, y1, x2, y2):
        assert 0.0 < a <= 1.0


@pytest.mark.parametrize("x1,y1,x2,y2", LINE_CASES)
def test_pixel_types(x1, y1, x2, y2):
    for x, y, a in antialiased_line(x1, y1, x2, y2):
        assert isinstance(x, int) and isinstance(y, int)
        assert isinstance(a, float)


@pytest.mark.parametrize("x1,y1,x2,y2", LINE_CASES)
def test_dominant_axis_fully_covered(x1, y1, x2, y2):
    """Every integer on the dominant axis has at least one pixel."""
    pixels = antialiased_line(x1, y1, x2, y2)
    if abs(x2 - x1) >= abs(y2 - y1):
        xs = {x for x, _, _ in pixels}
        expected = set(range(min(x1, x2), max(x1, x2) + 1))
        assert expected.issubset(xs)
    else:
        ys = {y for _, y, _ in pixels}
        expected = set(range(min(y1, y2), max(y1, y2) + 1))
        assert expected.issubset(ys)


@pytest.mark.parametrize("x1,y1,x2,y2", LINE_CASES)
def test_pixels_near_ideal_line(x1, y1, x2, y2):
    """Every touched pixel is within 1.5 units of the infinite ideal line."""
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return
    for x, y, _ in antialiased_line(x1, y1, x2, y2):
        d = abs(dy * (x - x1) - dx * (y - y1)) / length
        assert d < 1.5, f"pixel ({x},{y}) too far from line: d={d}"


@pytest.mark.parametrize("x1,y1,x2,y2", LINE_CASES)
def test_no_duplicate_pixels(x1, y1, x2, y2):
    pixels = antialiased_line(x1, y1, x2, y2)
    keys = [(x, y) for x, y, _ in pixels]
    assert len(keys) == len(set(keys))


# ---------------------------------------------------------------------------
# Exact reference outputs
# ---------------------------------------------------------------------------

def test_horizontal():
    assert antialiased_line(0, 0, 4, 0) == [
        (0, 0, 0.5), (1, 0, 1.0), (2, 0, 1.0), (3, 0, 1.0), (4, 0, 0.5),
    ]


def test_vertical():
    assert antialiased_line(0, 0, 0, 4) == [
        (0, 0, 0.5), (0, 1, 1.0), (0, 2, 1.0), (0, 3, 1.0), (0, 4, 0.5),
    ]


def test_degenerate():
    assert antialiased_line(3, 3, 3, 3) == [(3, 3, 1.0)]


def test_reference_shallow():
    """The worked example from the module docstring."""
    assert antialiased_line(0, 0, 4, 2) == [
        (0, 0, 0.5), (1, 0, 0.5), (1, 1, 0.5),
        (2, 1, 1.0), (3, 1, 0.5), (3, 2, 0.5), (4, 2, 0.5),
    ]


# ---------------------------------------------------------------------------
# Conservation of "ink"
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("x1,y1,x2,y2", [
    (0, 0, 5, 2),
    (0, 0, 2, 5),
    (0, 0, 5, 5),
    (0, 0, 5, 0),
    (0, 0, 0, 5),
    (-3, -2, 2, 3),
])
def test_alpha_sum_matches_dominant_axis(x1, y1, x2, y2):
    """Total coverage equals the length of the dominant axis.

    Wu's algorithm spreads exactly one pixel of "ink" per column of the
    fast axis. With integer endpoints, the two endpoint columns
    contribute half each, so the total is exactly ``max(|dx|, |dy|)``.
    """
    pixels = antialiased_line(x1, y1, x2, y2)
    total = sum(a for _, _, a in pixels)
    expected = max(abs(x2 - x1), abs(y2 - y1))
    assert abs(total - expected) < 1e-9


# ---------------------------------------------------------------------------
# Endpoint handling
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("x1,y1,x2,y2", [
    (0, 0, 5, 2),
    (0, 0, 2, 5),
    (-3, -2, 2, 3),
])
def test_endpoints_touched(x1, y1, x2, y2):
    """At least one pixel is plotted in the column of each endpoint."""
    pixels = antialiased_line(x1, y1, x2, y2)
    if abs(x2 - x1) >= abs(y2 - y1):
        xs = {x for x, _, _ in pixels}
        assert x1 in xs and x2 in xs
    else:
        ys = {y for _, y, _ in pixels}
        assert y1 in ys and y2 in ys


# ---------------------------------------------------------------------------
# Float input rounding
# ---------------------------------------------------------------------------

def test_float_inputs_rounded():
    assert antialiased_line(0.4, 0.6, 3.4, 2.6) == \
        antialiased_line(0, 1, 3, 3)