"""
Lab 3: Basic raster algorithms.

Entry point for the desktop application.

This application demonstrates four classic rasterization algorithms:
    - Step-by-step (naive) line drawing
    - DDA (Digital Differential Analyzer) line algorithm
    - Bresenham's line algorithm
    - Bresenham's circle algorithm

Optional extras implemented later:
    - Castle-Pitway algorithm
    - Anti-aliased (smoothed) line rendering

Run with:
    python main.py
"""

import os
import sys
import traceback

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so that the packages `ui`,
# `algorithms` and `extras` can be imported regardless of the current
# working directory (e.g. when the app is packaged into an .exe).
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ---------------------------------------------------------------------------
# GUI imports
# ---------------------------------------------------------------------------
# Tkinter is used because it ships with the Python standard library and
# requires no third-party dependencies, which keeps packaging to a
# standalone Windows executable simple.
import tkinter as tk
from tkinter import messagebox

from ui.app_window import AppWindow


def main() -> int:
    """Create the main window and start the Tk event loop.

    Returns an exit code: 0 on normal termination, 1 if the app
    could not be started (e.g. missing import or initialization error).
    """
    try:
        root = tk.Tk()
        # AppWindow is responsible for building the whole interface:
        # canvas, controls, grid/axes rendering, timing panel, etc.
        AppWindow(root)
        root.mainloop()
    except Exception:
        # Print the full traceback to the console for debugging,
        # then show a short popup so the user is not left with a silent crash.
        traceback.print_exc()
        try:
            messagebox.showerror(
                "Startup error",
                "The application could not start.\n"
                "Please see the console output for details.",
            )
        except Exception:
            # If even Tkinter cannot be initialized, just fall through.
            pass
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())