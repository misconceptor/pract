"""
Lab 3: Basic raster algorithms — Bresenham's line algorithm.

Bresenham's algorithm is the integer-only version of the line
rasterizer. It avoids floating-point arithmetic entirely: the position
of each pixel is chosen by maintaining an integer "error" term that
accumulates the difference between the ideal line and the pixel grid,
and by incrementing x and y only when that term crosses a threshold.

Compared to ``step_line`` (multiplication + division per pixel) and
``dda_line`` (float additions + rounding per pixel), this is pure
integer add / compare per pixel, which is exactly the point of the
timing section in the report.

Algorithm
---------
Given two endpoints (x1, y1) and (x2, y2):

1. Convert both endpoints to integer pixel coordinates.
2. dx = |x2 - x1|, dy = |y2 - y1|
   sx = sign(x2 - x1), sy = sign(y2 - y1)       (direction of travel)
   err = dx - dy                                 (initial imbalance)
3. Plot (x, y). While (x, y) != (x2, y2):
       e2 = 2 * err
       if e2 > -dy:  err -= dy;  x += sx
       if e2 <  dx:  err += dx;  y += sy
       plot (x, y)

The two ``if`` tests decide, independently, whether the current pixel
moves one column, one row, or both (diagonal step). Exactly one pixel
is emitted per iteration of the loop body.

Properties
----------
* **Integer-only arithmetic.** No floats, no division, no multiplication
  inside the loop — the entire per-pixel cost is two comparisons, two
  additions and two doublings (``2 * err``, which a compiler can turn
  into a shift).
* Emits exactly ``max(|dx|, |dy|) + 1`` pixels, from the first endpoint
  to the second, in traversal order, for any of the eight octants.
* The endpoint (x2, y2) is guaranteed to be the last emitted pixel.
* Input endpoints are rounded via ``int(round(v))`` — the package-wide
  rule for binding real-valued input to the discrete pixel grid.

Comparison with the other two line algorithms
---------------------------------------------
For the reference example ``(0, 0) → (5, 2)`` all three algorithms
produce the identical pixel set:

    step_line      (0, 0) → (5, 2)
    dda_line       (0, 0) → (5, 2)
    bresenham_line (0, 0) → (5, 2)
    -> [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]

What differs is the cost model: Bresenham does the same work in integer
arithmetic, which is what makes the per-pixel time in the report drop
noticeably versus the other two.

Examples
--------
>>> bresenham_line(0, 0, 5, 2)
[(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]

>>> bresenham_line(3, 3, 3, 3)
[(3, 3)]

>>> bresenham_line(0, 0, 0, 4)
[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]

>>> bresenham_line(5, 2, 0, 0)          # reverse direction
[(5, 2), (4, 2), (3, 1), (2, 1), (1, 0), (0, 0)]
"""

from __future__ import annotations


def bresenham_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> list[tuple[int, int]]:
    """Rasterize a straight line with Bresenham's integer algorithm.

    Parameters
    ----------
    x1, y1 : float
        First endpoint in math coordinates (y grows upward). Rounded to
        the nearest integer pixel before use.
    x2, y2 : float
        Second endpoint, same convention.

    Returns
    -------
    list[tuple[int, int]]
        Pixel coordinates in traversal order, from (x1, y1) to (x2, y2).
        Always contains at least one pixel.
    """
    # Bind real-valued input to the integer pixel grid (package contract).
    x1 = int(round(x1))
    y1 = int(round(y1))
    x2 = int(round(x2))
    y2 = int(round(y2))

    # Absolute extents — used only for the error accumulator.
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    # Direction of travel on each axis (+1 or -1).
    # If x1 == x2 the value is irrelevant: the corresponding branch below
    # never advances because dx == 0 -> the ``e2 > -dy`` test never fires.
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    # Classic Bresenham error term. Its value at any step is the signed
    # "how far off the true line are we" measure; the two branches below
    # keep it bounded.
    err = dx - dy

    pixels: list[tuple[int, int]] = []
    x, y = x1, y1

    # The loop condition guarantees we stop exactly on the second
    # endpoint; the two branches decide whether the next pixel moves
    # horizontally, vertically, or diagonally.
    while True:
        pixels.append((x, y))
        if x == x2 and y == y2:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

    return pixels