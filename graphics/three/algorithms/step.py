"""
Lab 3: Basic raster algorithms — step-by-step (naive) line algorithm.

This module implements the simplest possible line-rasterization method.
It is the pedagogical baseline against which DDA and Bresenham's
algorithms are compared in the report: same input, same output type,
strictly more work per pixel than the later methods.

Algorithm
---------
Given two endpoints (x1, y1) and (x2, y2):

1. Convert both endpoints to integer pixel coordinates.
2. Compute dx = x2 - x1 and dy = y2 - y1.
3. Decide the "dominant" axis:
       - if |dx| >= |dy|, walk x from x1 to x2 one pixel at a time;
       - otherwise,        walk y from y1 to y2 one pixel at a time.
4. For each integer step along the dominant axis, compute the other
   coordinate from the line equation, using floating-point arithmetic:

       shallow case (|dx| >= |dy|):
           y = y1 + (x - x1) * dy / dx
       steep case (|dy| >  |dx|):
           x = x1 + (y - y1) * dx / dy

   and round it to the nearest pixel.

Properties
----------
* Uses floating-point arithmetic and performs one division per pixel.
  (DDA replaces that division with an incremental addition; Bresenham
  replaces it with pure integer arithmetic. This is the point of the
  comparison in the lab report.)
* Draws exactly ``max(|dx|, |dy|) + 1`` pixels, ending at the rounded
  endpoint.
* Returns pixels in traversal order, from the first endpoint to the
  second, regardless of whether the second endpoint is left / right /
  above / below the first.
* The input endpoints are rounded via ``int(round(v))`` — this is the
  documented rule for binding arbitrary (real-valued) input to the
  discrete pixel grid, per the package-level contract.

Examples
--------
>>> step_line(0, 0, 5, 2)
[(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]

>>> step_line(3, 3, 3, 3)
[(3, 3)]

>>> step_line(0, 0, 0, 4)
[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
"""

from __future__ import annotations


def step_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> list[tuple[int, int]]:
    """Rasterize a straight line with the step-by-step (naive) algorithm.

    Parameters
    ----------
    x1, y1 : float
        First endpoint in math coordinates (y grows upward). Rounded to
        the nearest integer pixel before use.
    x2, y2 : float
        Second endpoint, same convention as (x1, y1).

    Returns
    -------
    list[tuple[int, int]]
        Pixel coordinates in traversal order, from (x1, y1) to (x2, y2).
        Always contains at least one pixel.
    """
    # Bind floating-point input to the integer pixel grid. This is the
    # single place where the "real input -> discrete pixel" step happens;
    # everything below works with integers for the dominant axis and
    # floating-point arithmetic for the other one.
    x1 = int(round(x1))
    y1 = int(round(y1))
    x2 = int(round(x2))
    y2 = int(round(y2))

    dx = x2 - x1
    dy = y2 - y1

    # Degenerate case: both endpoints collapse to the same pixel.
    if dx == 0 and dy == 0:
        return [(x1, y1)]

    pixels: list[tuple[int, int]] = []

    if abs(dx) >= abs(dy):
        # Shallow line: iterate along x, compute y from the line equation.
        # The step direction follows the direction of travel so that
        # pixels are emitted in the same order the endpoints were given.
        step = 1 if dx > 0 else -1
        for x in range(x1, x2 + step, step):
            # Parametric form, t in [0, 1] between the two endpoints:
            #   t = (x - x1) / dx
            #   y = y1 + t * dy
            # Equivalent to y1 + (x - x1) * dy / dx.
            t = (x - x1) / dx
            y = y1 + t * dy
            pixels.append((x, int(round(y))))
    else:
        # Steep line: iterate along y, compute x from the line equation.
        step = 1 if dy > 0 else -1
        for y in range(y1, y2 + step, step):
            t = (y - y1) / dy
            x = x1 + t * dx
            pixels.append((int(round(x)), y))

    return pixels