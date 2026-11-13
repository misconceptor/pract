"""Lab 3: Basic raster algorithms — GUI package.

Currently one module:

    app_window.py -> AppWindow class, the whole main window.

The package exists so that ``from ui.app_window import AppWindow`` works
from ``main.py`` regardless of the current working directory, and so a
future split (e.g. ``ui/canvas_view.py``, ``ui/controls.py``) can be
introduced without changing imports in ``main.py``.
"""