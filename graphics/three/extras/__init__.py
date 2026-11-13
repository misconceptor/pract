"""Lab 3: Basic raster algorithms — bonus extras.

Modules:

    castle_pitway.py -> castle_pitway_line
    antialiasing.py  -> antialiased_line

Both modules share the same conventions as ``algorithms/``: math
coordinates (y up), real input bound to the integer grid via
``int(round(v))``, no I/O / timing / rendering, pure functions.

Exceptions to the shared return type:

    castle_pitway_line -> list[tuple[int, int]]          (as algorithms/)
    antialiased_line   -> list[tuple[int, int, float]]   (x, y, alpha)
"""

from extras.antialiasing import antialiased_line
from extras.castle_pitway import castle_pitway_line

__all__ = ["antialiased_line", "castle_pitway_line"]