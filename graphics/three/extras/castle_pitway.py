"""
Lab 3 (bonus) — Castle-Pitway line algorithm.

Historical note
---------------
M. L. V. Pitteway's 1967 paper "Algorithm for drawing ellipses or
hyperbolae with a digital plotter" independently described what is now
called Bresenham's line algorithm. The formulation usually taught under
the name "Castle-Pitway" (also spelled Castle-Pittaway) is the version
with the decision parameter written as

    d = 2*dy - dx

updated by

    +2*dy            if d < 0
    +2*(dy - dx)     if d >= 0, and y is stepped by +/-1

for the shallow case (|dx| >= |dy|); the steep case is the same with
x and y swapped.

Castle-Pitway vs. Bresenham
----------------------------
The two algorithms are mathematically equivalent in the "no-tie" case
and produce identical pixel lists. They differ *only* when the
midpoint between two candidate pixels lies exactly on the ideal line,
i.e. when 2*dy == dx (shallow) or 2*dx == dy (steep). At those exact
ties, Castle-Pitway with the strict ``d < 0`` test takes the diagonal
step while Bresenham with the strict ``e2 > -dy`` test does not. Both
choices produce valid 8-connected rasterizations; they simply fall on
opposite sides of the ideal line.

For example, for (0, 0) -> (4, 2):

    castle_pitway_line (0, 0, 4, 2) = [(0,0), (1,1), (2,1), (3,2), (4,2)]
    bresenham_line     (0, 0, 4, 2) = [(0,0), (1,0), (2,1), (3,1), (4,2)]

This tie-breaking difference is intentional and is tested explicitly in
tests/test_castle_pitway.py.

Algorithm
---------
Given two endpoints (x1, y1) and (x2, y2):

1. Convert both endpoints to integer pixel coordinates.
2. dx = |x2 - x1|, dy = |y2 - y1|
   sx = sign(x2 - x1), sy = sign(y2 - y1)
3. If dx >= dy (shallow case):
       d = 2*dy - dx
       plot (x1, y1)
       for step in range(dx):
           if d < 0:
               d += 2*dy
           else:
               d += 2*(dy - dx)
               y += sy
           x += sx
           plot (x, y)
4. Else (steep case):
       d = 2*dx - dy
       plot (x1, y1)
       for step in range(dy):
           if d < 0:
               d += 2*dx
           else:
               d += 2*(dx - dy)
               x += sx
           y += sy
           plot (x, y)

Properties
----------
* **Integer-only arithmetic** in the inner loop. No floats, no division,
  no multiplication (only doublings, which are shifts).
* Emits exactly ``max(|dx|, |dy|) + 1`` pixels, from the first endpoint
  to the second, in traversal order, for any of the eight octants.
* Every consecutive pair is 8-adjacent (no gaps, no jumps).
* Endpoints match the input (after the standard int(round(v)) binding).
* Agrees with ``bresenham_line`` on every input where the midpoint never
  lands exactly on the line. See "Castle-Pitway vs. Bresenham" above
  for the divergence.

Examples
--------
>>> castle_pitway_line(0, 0, 5, 2)
[(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]

>>> castle_pitway_line(3, 3, 3, 3)
[(3, 3)]

>>> castle_pitway_line(0, 0, 0, 4)
[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]

>>> castle_pitway_line(5, 2, 0, 0)          # reverse direction
[(5, 2), (4, 2), (3, 1), (2, 1), (1, 0), (0, 0)]

>>> castle_pitway_line(0, 0, 4, 2)          # tie case, differs from Bresenham
[(0, 0), (1, 1), (2, 1), (3, 2), (4, 2)]
"""

from __future__ import annotations


def castle_pitway_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> list[tuple[int, int]]:
    """Rasterize a straight line with the Castle-Pitway algorithm.

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
    # Bind real input to the integer pixel grid (package-wide contract).
    x1 = int(round(x1))
    y1 = int(round(y1))
    x2 = int(round(x2))
    y2 = int(round(y2))

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    pixels: list[tuple[int, int]] = [(x1, y1)]
    x, y = x1, y1

    if dx >= dy:
        # Shallow case: walk along x, conditionally step y.
        d = 2 * dy - dx
        for _ in range(dx):
            if d < 0:
                d += 2 * dy
            else:
                d += 2 * (dy - dx)
                y += sy
            x += sx
            pixels.append((x, y))
    else:
        # Steep case: walk along y, conditionally step x.
        d = 2 * dx - dy
        for _ in range(dy):
            if d < 0:
                d += 2 * dx
            else:
                d += 2 * (dx - dy)
                x += sx
            y += sy
            pixels.append((x, y))

    return pixels