"""
Lab 3: Basic raster algorithms — DDA (Digital Differential Analyzer).

The DDA line algorithm keeps the geometric form of the step-by-step
method but removes the per-pixel division. It computes dx, dy and the
number of steps once, then advances x and y by constant increments in a
loop. That makes the inner loop a pair of additions + roundings, instead
of a multiplication and a division per pixel.

Algorithm
---------
Given two endpoints (x1, y1) and (x2, y2):

1. Convert both endpoints to integer pixel coordinates.
2. dx = x2 - x1, dy = y2 - y1.
3. steps = max(|dx|, |dy|)   (guarantees the dominant axis advances
   exactly one pixel per iteration; the other axis advances by |inc| <= 1).
4. x_inc = dx / steps, y_inc = dy / steps.
5. Start at (x1, y1), and for i = 0 .. steps:
       append (round(x), round(y))
       x += x_inc
       y += y_inc

Properties
----------
* Cost per pixel: one addition per axis + rounding, versus one
  multiplication + one division per pixel for the step-by-step method.
  This is the point of the DDA entry in the timing section of the report.
* Uses floating-point arithmetic. Rounding is done with ``round()``
  (Python's banker's rounding), consistent with the other modules in
  this package.
* Emits exactly ``max(|dx|, |dy|) + 1`` pixels, from the first endpoint
  to the second, in traversal order.
* The final pixel is guaranteed to be exactly (x2, y2), because after
  ``steps`` iterations x = x1 + steps * x_inc = x2 and similarly for y.
* Input endpoints are rounded via ``int(round(v))`` — the package-wide
  rule for binding real-valued input to the discrete pixel grid.

Note on the worked example
--------------------------
For the reference example (0, 0) -> (5, 2) all three line algorithms
agree:

    step_line      (0, 0) -> (5, 2) = [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]
    dda_line       (0, 0) -> (5, 2) = [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]
    bresenham_line (0, 0) -> (5, 2) = [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]

What differs is the *cost model*, not the output: step_line does a
multiplication and a division per pixel, dda_line does two float
additions and a rounding per pixel, bresenham_line does integer
add / compare per pixel. That is the comparison to write up in the
report's timing section.

Examples
--------
>>> dda_line(0, 0, 5, 2)
[(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]

>>> dda_line(3, 3, 3, 3)
[(3, 3)]

>>> dda_line(0, 0, 0, 4)
[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
"""

from __future__ import annotations


def dda_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> list[tuple[int, int]]:
    """Rasterize a straight line with the DDA algorithm.

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

    dx = x2 - x1
    dy = y2 - y1

    # Number of iterations on the dominant axis. ``max`` (not ``ceil``)
    # keeps the dominant axis advancing exactly one pixel per step; the
    # other axis then advances by an amount in [-1, 1].
    steps = max(abs(dx), abs(dy))

    # Degenerate case: the two endpoints collapse to one pixel.
    if steps == 0:
        return [(x1, y1)]

    # Constant increments — computed ONCE. The inner loop below is only
    # additions and roundings; this is the entire performance argument
    # for DDA over the step-by-step method.
    x_inc = dx / steps
    y_inc = dy / steps

    pixels: list[tuple[int, int]] = []
    x = float(x1)
    y = float(y1)

    # ``steps + 1`` pixels are emitted: the starting pixel plus one per
    # increment, ending exactly at (x2, y2).
    for _ in range(steps + 1):
        pixels.append((int(round(x)), int(round(y))))
        x += x_inc
        y += y_inc

    return pixels