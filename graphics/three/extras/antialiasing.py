"""
Lab 3 (bonus) — anti-aliased line drawing (Xiaolin Wu's algorithm).

Unlike the four core algorithms, which emit one hard-edged pixel per
step, Wu's algorithm emits *two* pixels per step, each with a fractional
opacity (alpha) that models how much of that pixel cell is covered by
the ideal line. Rendering those pixels with the corresponding opacity
produces a visually smoothed line, especially noticeable at shallow
angles.

How it works
------------
For every integer x in the span of the line (or every integer y in the
steep case), Wu's algorithm computes the exact intersection of the
ideal line with the vertical column at x. That intersection falls at
some real y; the two pixels ``(x, floor(y))`` and ``(x, floor(y) + 1)``
share the coverage of the column between them:

    alpha_low  = 1 - frac(y)      (lower pixel)
    alpha_high =     frac(y)      (upper pixel)

Because ``frac(y) + (1 - frac(y)) = 1``, the two pixels always sum to
exactly one pixel of "ink" per column: the anti-aliased line preserves
total coverage, only its distribution changes.

Endpoints are handled with an extra weighting ``xgap`` that softens the
first and last columns of the line, so a line that starts or ends in
the middle of a cell blends into the surrounding pixels instead of
snapping to a hard edge.

Return type
-----------
``list[tuple[int, int, float]]`` — the pixel's (x, y) followed by an
alpha in (0, 1]. Pixels whose coverage rounds to zero are omitted.
Multiple passes over the same cell (possible for degenerate or very
short lines) accumulate, capped at alpha = 1.0.

The rest of the package contract is unchanged: math coordinates (y up),
``int(round(v))`` binds real input to the integer pixel grid, no I/O,
no timing, no rendering.

Why this is a "bonus"
---------------------
Bresenham / DDA / step all produce *aliased* lines: each pixel is
either on or off, so a shallow line looks stair-stepped. Wu's
algorithm trades a little more work per step for a visibly smoother
result. The UI renders the alpha channel by blending the pixel colour
against the canvas background, which is why the visual difference is
easy to spot at shallow slopes.

Examples
--------
>>> antialiased_line(0, 0, 4, 0)
[(0, 0, 0.5), (1, 0, 1.0), (2, 0, 1.0), (3, 0, 1.0), (4, 0, 0.5)]

>>> antialiased_line(0, 0, 0, 4)
[(0, 0, 0.5), (0, 1, 1.0), (0, 2, 1.0), (0, 3, 1.0), (0, 4, 0.5)]

>>> antialiased_line(3, 3, 3, 3)
[(3, 3, 1.0)]

>>> antialiased_line(0, 0, 4, 2)        # shallow, smoothing visible
[(0, 0, 0.5), (1, 0, 0.5), (1, 1, 0.5), (2, 1, 1.0), (3, 1, 0.5), (3, 2, 0.5), (4, 2, 0.5)]
"""

from __future__ import annotations

import math


def _ipart(x: float) -> int:
    """Floor(x) — the integer part below x (works for negatives)."""
    return math.floor(x)


def _fpart(x: float) -> float:
    """Fractional part of x, in [0, 1)."""
    return x - math.floor(x)


def _rfpart(x: float) -> float:
    """Reflected fractional part, in (0, 1]."""
    return 1.0 - _fpart(x)


def antialiased_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> list[tuple[int, int, float]]:
    """Rasterize a straight line with Xiaolin Wu's anti-aliased algorithm.

    Parameters
    ----------
    x1, y1 : float
        First endpoint in math coordinates (y grows upward). Rounded to
        the nearest integer pixel before use.
    x2, y2 : float
        Second endpoint, same convention.

    Returns
    -------
    list[tuple[int, int, float]]
        ``(x, y, alpha)`` triples, sorted by ``(x, y)``. Alpha is in
        (0, 1]; pixels with zero coverage are omitted.
    """
    # Bind real input to the integer pixel grid (package-wide contract).
    x1 = int(round(x1))
    y1 = int(round(y1))
    x2 = int(round(x2))
    y2 = int(round(y2))

    # Accumulate coverage per pixel. In practice Wu's algorithm visits
    # each cell at most once per column, but degenerate cases (where
    # xpxl1 == xpxl2) can write twice; the dict handles that.
    coverage: dict[tuple[int, int], float] = {}

    def plot(x: int, y: int, alpha: float) -> None:
        if alpha <= 0.0:
            return
        key = (int(x), int(y))
        coverage[key] = min(1.0, coverage.get(key, 0.0) + alpha)

    # Wu's algorithm works in the first octant (x is the fast axis).
    # Swap axes for steep lines; swap endpoints for x1 > x2.
    steep = abs(y2 - y1) > abs(x2 - x1)
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    dx = x2 - x1
    dy = y2 - y1
    # Gradient of the line in the (possibly swapped) frame. If dx == 0
    # the caller has effectively passed a single point; use gradient 1
    # so the endpoint handling still produces a sensible pixel.
    gradient = dy / dx if dx != 0 else 1.0

    # ------------------------------------------------------------------
    # First endpoint
    # ------------------------------------------------------------------
    xend = int(round(x1))
    yend = y1 + gradient * (xend - x1)
    xgap = _rfpart(x1 + 0.5)
    xpxl1 = xend
    ypxl1 = _ipart(yend)
    if steep:
        plot(ypxl1,     xpxl1, _rfpart(yend) * xgap)
        plot(ypxl1 + 1, xpxl1, _fpart(yend)  * xgap)
    else:
        plot(xpxl1, ypxl1,     _rfpart(yend) * xgap)
        plot(xpxl1, ypxl1 + 1, _fpart(yend)  * xgap)
    intery = yend + gradient  # first y-intersection for the main loop

    # ------------------------------------------------------------------
    # Second endpoint
    # ------------------------------------------------------------------
    xend = int(round(x2))
    yend = y2 + gradient * (xend - x2)
    xgap = _fpart(x2 + 0.5)
    xpxl2 = xend
    ypxl2 = _ipart(yend)
    if steep:
        plot(ypxl2,     xpxl2, _rfpart(yend) * xgap)
        plot(ypxl2 + 1, xpxl2, _fpart(yend)  * xgap)
    else:
        plot(xpxl2, ypxl2,     _rfpart(yend) * xgap)
        plot(xpxl2, ypxl2 + 1, _fpart(yend)  * xgap)

    # ------------------------------------------------------------------
    # Main loop — two pixels per integer step of the fast axis.
    # ------------------------------------------------------------------
    if steep:
        for x in range(xpxl1 + 1, xpxl2):
            plot(_ipart(intery),     x, _rfpart(intery))
            plot(_ipart(intery) + 1, x, _fpart(intery))
            intery += gradient
    else:
        for x in range(xpxl1 + 1, xpxl2):
            plot(x, _ipart(intery),     _rfpart(intery))
            plot(x, _ipart(intery) + 1, _fpart(intery))
            intery += gradient

    return sorted((x, y, alpha) for (x, y), alpha in coverage.items())