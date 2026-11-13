"""
Lab 3: Basic raster algorithms — algorithm package.

This package contains pure, GUI-independent implementations of the four
rasterization algorithms required by the assignment:

    step.py             -> step-by-step (naive) line algorithm
    dda.py              -> DDA (Digital Differential Analyzer) line algorithm
    bresenham_line.py   -> Bresenham's line algorithm
    bresenham_circle.py -> Bresenham's circle algorithm

Shared conventions (IMPORTANT — every module in this package obeys them)
-----------------------------------------------------------------------

1. Coordinate system
   All algorithms work in *math* coordinates:
       - x grows to the right,
       - y grows upward,
       - the origin (0, 0) is at the bottom-left of the logical grid.
   The UI layer is responsible for flipping y when drawing onto the Tk
   canvas (whose y grows downward). Algorithms must NOT do that flip.

2. Input types
   Endpoints / centers are (x, y) tuples of real numbers.
   Radii are real numbers.
   Each algorithm internally converts to integer pixel coordinates using
   ``int(round(v))`` so that arbitrary user input lands on the discrete
   raster grid. This is the single documented rule for "how integer
   coordinates bind to the pixel grid" required by the assignment.

3. Return type
   Every drawing routine returns ``list[tuple[int, int]]`` — the sequence
   of pixel coordinates in the order they would be plotted. Returning a
   full list (rather than yielding) keeps the code easy to:
       - time (``perf_counter`` around one call),
       - visualize (iterate and draw small squares),
       - log in the report ("here are the first N pixels of this line").

4. Purity
   Algorithms do no I/O, no timing, no drawing. They compute and return
   pixel lists. Timing and rendering live in the UI / helper layer.

5. Edge cases
   - Zero-length line: return a single pixel (the endpoint).
   - Circle with r == 0: return a single pixel (the center).
   - Very large inputs are allowed; the caller decides how much to draw.

Re-exports
----------
For convenience the four public functions are also importable directly
from this package::

    from algorithms import bresenham_line, bresenham_circle

The re-exports are intentionally lazy-free (plain imports) because these
modules have no heavy dependencies — they only use ``math``.
"""

from algorithms.step import step_line
from algorithms.dda import dda_line
from algorithms.bresenham_line import bresenham_line
from algorithms.bresenham_circle import bresenham_circle

__all__ = [
    "step_line",
    "dda_line",
    "bresenham_line",
    "bresenham_circle", 
]