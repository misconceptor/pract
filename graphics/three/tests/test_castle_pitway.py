"""Tests for the bonus Castle-Pitway line algorithm.

Covers:
    * the basic contract (count, endpoints, connectivity, int types);
    * agreement with bresenham_line on non-tie inputs;
    * the *documented* divergence on exact-tie inputs.

The tie-divergence tests are not bugs to be fixed — they characterize
the known difference between the two formulations and are described in
extras/castle_pitway.py under "Castle-Pitway vs. Bresenham".
"""

import pytest

from algorithms import bresenham_line
from extras import castle_pitway_line


# (x1, y1, x2, y2)
LINE_CASES = [
    (0, 0, 0, 0),
    (3, 3, 3, 3),
    (0, 0, 5, 0),
    (5, 0, 0, 0),
    (0, 0, 0, 5),
    (0, 5, 0, 0),
    (0, 0, 5, 2),
    (0, 0, 2, 5),
    (0, 0, -5, -2),
    (0, 0, -2, -5),
    (-3, -2, 2, 3),
    (5, 2, 0, 0),
    (1, 1, 3, 5),
    (10, 3, 20, 8),
    (0, 0, 4, 2),
]


@pytest.mark.parametrize("x1,y1,x2,y2", LINE_CASES)
def test_endpoints(x1, y1, x2, y2):
    pixels = castle_pitway_line(x1, y1, x2, y2)
    assert pixels[0] == (x1, y1)
    assert pixels[-1] == (x2, y2)


@pytest.mark.parametrize("x1,y1,x2,y2", LINE_CASES)
def test_pixel_count(x1, y1, x2, y2):
    expected = max(abs(x2 - x1), abs(y2 - y1)) + 1
    assert len(castle_pitway_line(x1, y1, x2, y2)) == expected


@pytest.mark.parametrize("x1,y1,x2,y2", LINE_CASES)
def test_int_pairs(x1, y1, x2, y2):
    for x, y in castle_pitway_line(x1, y1, x2, y2):
        assert isinstance(x, int) and isinstance(y, int)


@pytest.mark.parametrize("x1,y1,x2,y2", LINE_CASES)
def test_8_connected(x1, y1, x2, y2):
    pixels = castle_pitway_line(x1, y1, x2, y2)
    for (xa, ya), (xb, yb) in zip(pixels, pixels[1:]):
        assert abs(xb - xa) <= 1
        assert abs(yb - ya) <= 1


def test_reference_example():
    assert castle_pitway_line(0, 0, 5, 2) == [
        (0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2),
    ]


def test_degenerate():
    assert castle_pitway_line(7, 7, 7, 7) == [(7, 7)]


def test_vertical():
    assert castle_pitway_line(0, 0, 0, 4) == [
        (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
    ]


def test_horizontal():
    assert castle_pitway_line(0, 0, 4, 0) == [
        (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
    ]


def test_reverse_direction():
    assert castle_pitway_line(5, 2, 0, 0) == [
        (5, 2), (4, 2), (3, 1), (2, 1), (1, 0), (0, 0),
    ]


def test_float_inputs_rounded():
    assert castle_pitway_line(0.4, 0.6, 3.4, 2.6) == \
        castle_pitway_line(0, 1, 3, 3)


# ---------------------------------------------------------------------------
# Agreement with Bresenham on non-tie inputs
# ---------------------------------------------------------------------------
# Every case below has 2*dy != dx (shallow) and 2*dx != dy (steep), so
# the midpoint decision never lands exactly on the ideal line and the
# two algorithms must produce identical pixels.

AGREE_CASES = [
    (0, 0, 5, 2),   # d0 = -1
    (0, 0, 2, 5),   # steep, d0 = -1
    (0, 0, 5, 0),   # horizontal
    (0, 0, 0, 5),   # vertical
    (0, 0, -5, -2), # reverse direction
    (0, 0, -2, -5), # steep, reverse
    (5, 2, 0, 0),   # reverse of reference
]


@pytest.mark.parametrize("x1,y1,x2,y2", AGREE_CASES)
def test_agrees_with_bresenham_on_nontie(x1, y1, x2, y2):
    assert castle_pitway_line(x1, y1, x2, y2) == \
        bresenham_line(x1, y1, x2, y2)


# ---------------------------------------------------------------------------
# Documented divergence on exact-tie inputs
# ---------------------------------------------------------------------------
# Each case below has 2*dy == dx (or 2*dx == dy in the steep case), so
# the decision parameter starts at 0 and Castle-Pitway takes the
# diagonal step that Bresenham does not. The exact pixel sets are
# asserted so a future refactor cannot silently change the behaviour
# without updating the documentation.

DIVERGE_CASES = [
    # (x1, y1, x2, y2, castle_pitway_pixels, bresenham_pixels)
    (
        (0, 0, 4, 2),
        [(0, 0), (1, 1), (2, 1), (3, 2), (4, 2)],
        [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2)],
    ),
    (
        (0, 0, 6, 3),
        [(0, 0), (1, 1), (2, 1), (3, 2), (4, 2), (5, 3), (6, 3)],
        [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2), (6, 3)],
    ),
    (
        (1, 1, 3, 5),
        [(1, 1), (2, 2), (2, 3), (3, 4), (3, 5)],
        [(1, 1), (1, 2), (2, 3), (2, 4), (3, 5)],
    ),
    (
        (10, 3, 20, 8),
        [(10, 3), (11, 4), (12, 4), (13, 5), (14, 5),
         (15, 6), (16, 6), (17, 7), (18, 7), (19, 8), (20, 8)],
        [(10, 3), (11, 3), (12, 4), (13, 4), (14, 5),
         (15, 5), (16, 6), (17, 6), (18, 7), (19, 7), (20, 8)],
    ),
]


@pytest.mark.parametrize("coords,cp_expected,br_expected", DIVERGE_CASES)
def test_documented_divergence(coords, cp_expected, br_expected):
    """Castle-Pitway and Bresenham differ on exact-tie inputs.

    Both outputs are valid 8-connected rasterizations of the same
    segment. This test pins the exact pixel sets for the cases quoted
    in the module docstring so a future change is loud.
    """
    assert castle_pitway_line(*coords) == cp_expected
    assert bresenham_line(*coords) == br_expected
    # Same endpoints, same count, different interiors.
    assert cp_expected[0] == br_expected[0]
    assert cp_expected[-1] == br_expected[-1]
    assert len(cp_expected) == len(br_expected)
    assert cp_expected != br_expected