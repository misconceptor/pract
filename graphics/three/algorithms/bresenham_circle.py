"""
Lab 3: Basic raster algorithms — Bresenham's (midpoint) circle algorithm.

Bresenham's circle algorithm is the integer-only version of the circle
rasterizer. It exploits the 8-fold symmetry of a circle: pixels are
computed only for the first octant (where 0 <= x <= y) and the remaining
seven octants are obtained by reflection. The position of each pixel is
chosen by maintaining an integer "decision parameter" that tracks
whether the midpoint between two candidate pixels is inside or outside
the ideal circle.

Compared to drawing each pixel from ``x² + y² = r²``, this uses only
integer additions, subtractions and comparisons per pixel — no square
roots, no divisions, no floating point.

Algorithm
---------
Given a center (cx, cy) and a radius r:

1. Convert the center and the radius to integer pixel coordinates
   (radius is rounded; negative radii are rejected).
2. Start in the first octant at (x, y) = (0, r) with the initial
   decision parameter d = 3 - 2*r.
3. While x <= y:
       plot the 8 symmetric images of (x, y):
           (cx + x, cy + y), (cx - x, cy + y),
           (cx + x, cy - y), (cx - x, cy - y),
           (cx + y, cy + x), (cx - y, cy + x),
           (cx + y, cy - x), (cx - y, cy - x)
       if d < 0:
           d += 4*x + 6
       else:
           d += 4*(x - y) + 10
           y -= 1
       x += 1
4. Return the unique pixels, sorted for determinism.

Walk-through for r = 3, center (0, 0)
-------------------------------------
    init:  x = 0, y = 3, d = 3 - 2*3 = -3

    step 1: x = 0, y = 3, d = -3
            plot reflections of (0, 3):
            (0, 3), (0, -3), (3, 0), (-3, 0)
            (the diagonal reflections collapse onto the same pixels,
             so only 4 distinct points come out of this step)
            d < 0  ->  d += 4*0 + 6  ->  d = 3
            x += 1

    step 2: x = 1, y = 3, d = 3
            plot reflections of (1, 3):
            (1, 3), (-1, 3), (1, -3), (-1, -3),
            (3, 1), (-3, 1), (3, -1), (-3, -1)        (8 distinct)
            d >= 0 ->  d += 4*(1 - 3) + 10  ->  d = 5
            y -= 1
            x += 1

    step 3: x = 2, y = 2, d = 5
            plot reflections of (2, 2):
            (2, 2), (-2, 2), (2, -2), (-2, -2)        (4 distinct, x == y)
            d >= 0 ->  d += 4*(2 - 2) + 10  ->  d = 15
            y -= 1
            x += 1

    step 4: x = 3, y = 1   ->  x > y, loop ends

    total: 4 + 8 + 4 = 16 distinct pixels.

Properties
----------
* **Integer-only arithmetic** in the inner loop. No floats, no division,
  no multiplication.
* Exploits 8-fold symmetry: at most ``r / sqrt(2)`` iterations of the
  loop body to cover the whole circle.
* When ``x == y`` or ``x == 0`` or ``y == 0`` some of the 8 symmetric
  images coincide. The returned list contains only distinct pixels —
  a Python ``set`` is used internally to drop the duplicates, then the
  result is sorted.
* Returned pixels are sorted by ``(x, y)``, so the output is
  deterministic. The raster image itself is of course unordered; the
  sort exists only to make tests and doctests reproducible.
* Center is rounded via ``int(round(v))`` and the radius via
  ``int(round(r))``, in line with the package-wide "bind real input to
  the discrete pixel grid" rule.
* A negative radius is a caller bug and raises ``ValueError``.
* Radius 0 returns a single pixel at the center — the natural degenerate
  case, consistent with how the line algorithms handle zero length.

Examples
--------
>>> bresenham_circle(0, 0, 0)
[(0, 0)]

>>> bresenham_circle(0, 0, 1)
[(-1, 0), (0, -1), (0, 1), (1, 0)]

>>> bresenham_circle(0, 0, 2)
[(-2, -1), (-2, 0), (-2, 1), (-1, -2), (-1, 2), (0, -2), (0, 2), (1, -2), (1, 2), (2, -1), (2, 0), (2, 1)]

>>> len(bresenham_circle(0, 0, 3))
16
"""

from __future__ import annotations


def bresenham_circle(
    cx: float,
    cy: float,
    r: float,
) -> list[tuple[int, int]]:
    """Rasterize a circle with Bresenham's midpoint algorithm.

    Parameters
    ----------
    cx, cy : float
        Center of the circle in math coordinates (y grows upward).
        Rounded to the nearest integer pixel before use.
    r : float
        Radius. Must be non-negative. Rounded to the nearest integer
        pixel before use.

    Returns
    -------
    list[tuple[int, int]]
        Distinct pixel coordinates on the circle, sorted by ``(x, y)``.
        Always contains at least one pixel (the center, when ``r == 0``).

    Raises
    ------
    ValueError
        If the (rounded) radius is negative.
    """
    # Bind real-valued input to the integer pixel grid (package contract).
    cx = int(round(cx))
    cy = int(round(cy))
    r = int(round(r))

    if r < 0:
        raise ValueError(f"Circle radius must be non-negative, got {r}")

    # Degenerate case: zero radius collapses to a single pixel.
    if r == 0:
        return [(cx, cy)]

    # Use a set to deduplicate the symmetric images that coincide when
    # x == 0, y == 0, or x == y. Sorting at the end gives deterministic
    # output, which simplifies tests and the write-up.
    pixels: set[tuple[int, int]] = set()

    x = 0
    y = r
    # Midpoint decision parameter. The two update rules below keep ``d``
    # proportional to the signed distance of the midpoint between
    # (x + 1, y) and (x + 1, y - 1) from the ideal circle.
    d = 3 - 2 * r

    while x <= y:
        # Eight symmetric images of (x, y) around the center.
        pixels.add((cx + x, cy + y))
        pixels.add((cx - x, cy + y))
        pixels.add((cx + x, cy - y))
        pixels.add((cx - x, cy - y))
        pixels.add((cx + y, cy + x))
        pixels.add((cx - y, cy + x))
        pixels.add((cx + y, cy - x))
        pixels.add((cx - y, cy - x))

        if d < 0:
            # Midpoint is inside the circle: choose the "east" pixel.
            d += 4 * x + 6
        else:
            # Midpoint is on or outside the circle: choose the
            # "south-east" pixel and step y down.
            d += 4 * (x - y) + 10
            y -= 1
        x += 1

    return sorted(pixels)