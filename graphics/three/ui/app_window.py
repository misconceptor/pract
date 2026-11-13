"""
Lab 3: Basic raster algorithms — main application window.

Responsive, DPI-aware Tk UI.

Scaling model
-------------
Three independent factors combine into ``self.ui_scale``:

    ui_scale = dpi_scale * user_or_auto_scale

* ``dpi_scale``          — measured once at startup from
                           ``root.winfo_fpixels('1i') / 96``. Capped to
                           [1.0, 2.0] so 4K high-DPI displays look
                           proportional, not comically large.
* ``user_scale``         — set by the S / M / L buttons in the footer.
                           When set, auto-scaling is disabled.
* ``auto_scale``         — computed from the window dimensions on every
                           (debounced) resize. Grows from 1.0 at the
                           reference window size up to 1.6 on very
                           large displays. Active only when the user
                           has *not* clicked a manual size.

Every size in the UI is routed through ``self._s(n)`` which multiplies
by ``self.ui_scale`` and rounds to an int. That way fonts, paddings,
minsize, canvas baseline — everything — scales together.

Layout
------
Root uses grid:

    row 0  header       sticky="ew"
    row 1  main         sticky="nsew"   weight=1
    row 2  footer       sticky="ew"

``main`` is also grid:

    col 0  canvas       weight=1        sticky="nsew"
    col 1  sidebar      weight=0        sticky="nsew"
                        minsize=self._s(320)

``sidebar`` is grid:

    row 0  controls card    sticky="ew"
    row 1  info card        sticky="nsew"  weight=1

``controls card`` uses grid with ``weight=1`` on entry columns, so the
parameter fields stretch to fill the card. That is what prevents the
right-hand clipping on large displays.

Everything else (algorithm buttons, timing readout, footer slider) uses
grid or pack with explicit fill/expand; no fixed pixel widths on
content-bearing widgets.

The rest of the file (rendering, timing, coordinate transform) is
unchanged from the previous version.
"""

from __future__ import annotations

import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk

from algorithms import (
    bresenham_circle,
    bresenham_line,
    dda_line,
    step_line,
)
from extras import castle_pitway_line, antialiased_line


# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
BG            = "#F7F8FA"
SURFACE       = "#FFFFFF"
SURFACE_ALT   = "#F3F4F6"
BORDER        = "#E5E7EB"
TEXT          = "#111827"
TEXT_MUTED    = "#6B7280"
ACCENT        = "#4F46E5"
ACCENT_DARK   = "#4338CA"
ACCENT_LIGHT  = "#EEF2FF"

GRID_COLOR    = "#F3F4F6"
AXES_COLOR    = "#9CA3AF"
AXIS_LABEL    = "#6B7280"
PIXEL         = "#6366F1"
PIXEL_OUTLINE = "#4338CA"
IDEAL         = "#EF4444"

# Baseline sizes at ui_scale == 1.0. Every one of these goes through
# _s() when used, so the whole UI scales together.
BASE_PAD            = 16
BASE_CARD_WIDTH     = 340
BASE_CANVAS_SIZE    = 560
BASE_MIN_WIN_W      = 900
BASE_MIN_WIN_H      = 650
BASE_FONT_SMALL     = 9
BASE_FONT_BASE      = 10
BASE_FONT_TITLE     = 18
BASE_FONT_VALUE     = 12
BASE_ENTRY_WIDTH    = 8
BASE_ALGO_PADDING_Y = 8

REF_WINDOW_W = 1400
REF_WINDOW_H = 900
MAX_AUTO_SCALE = 1.6

# ---------------------------------------------------------------------------
# Algorithm registry
# ---------------------------------------------------------------------------
_ALGORITHMS = {
    "step":             step_line,
    "dda":              dda_line,
    "bresenham_line":   bresenham_line,
    "bresenham_circle": bresenham_circle,
    "castle_pitway":    castle_pitway_line,
    "antialiased":      antialiased_line,
}

_SHORT_LABELS = {
    "step":             "Step",
    "dda":              "DDA",
    "bresenham_line":   "Bresenham",
    "bresenham_circle": "Circle",
    "castle_pitway":    "Castle-Pitway",
    "antialiased":      "Wu AA",
}

_FULL_LABELS = {
    "step":             "Step-by-step line",
    "dda":              "DDA line",
    "bresenham_line":   "Bresenham line",
    "bresenham_circle": "Bresenham circle",
    "castle_pitway": "Castle-Pitway line",
    "antialiased":      "Wu anti-aliased line",
}

# ---------------------------------------------------------------------------
# Font selection
# ---------------------------------------------------------------------------
_SANS_CANDIDATES = (
    "Inter", "Cantarell", "Ubuntu", "Noto Sans",
    "Segoe UI", "SF Pro Text", "Helvetica Neue",
    "DejaVu Sans", "Liberation Sans", "Arial",
)
_MONO_CANDIDATES = (
    "JetBrains Mono", "Fira Code", "Cascadia Mono", "SF Mono",
    "Menlo", "Consolas", "Ubuntu Mono", "DejaVu Sans Mono",
)


def _pick_font(root: tk.Tk, candidates: tuple[str, ...], fallback: str) -> str:
    available = set(tkfont.families(root))
    for name in candidates:
        if name in available:
            return name
    return fallback


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class AppWindow:
    """Main application window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Lab 3 — Raster Algorithms")
        self.root.configure(bg=BG)

        # Scaling state. ``user_scale_override`` is None until the user
        # clicks S / M / L. ``auto_window_scale`` tracks window size.
        self.dpi_scale = self._detect_dpi_scale()
        self.user_scale_override: float | None = None
        self.auto_window_scale: float = 1.0
        self._resize_after_id: str | None = None

        self.ui_scale = self._effective_scale()

        self.root.minsize(self._s(BASE_MIN_WIN_W), self._s(BASE_MIN_WIN_H))

        self._setup_fonts()
        self._setup_style()
        self._init_state()
        self._build_layout()

        self.root.bind("<Configure>", self._on_root_configure)

        self._on_draw()  # initial draw

    # ------------------------------------------------------------------
    # Scaling helpers
    # ------------------------------------------------------------------
    def _s(self, n: int) -> int:
        """Scale a baseline (96 DPI, 1.0x) pixel value."""
        return max(1, int(round(n * self.ui_scale)))

    def _effective_scale(self) -> float:
        if self.user_scale_override is not None:
            return self.dpi_scale * self.user_scale_override
        return self.dpi_scale * self.auto_window_scale

    def _detect_dpi_scale(self) -> float:
        """Measure the display's DPI and return a clamped scale factor."""
        try:
            dpi = float(self.root.winfo_fpixels("1i"))
            return max(1.0, min(2.0, dpi / 96.0))
        except Exception:
            return 1.0

    # ------------------------------------------------------------------
    # Fonts and styles
    # ------------------------------------------------------------------
    def _setup_fonts(self) -> None:
        self.font_family = _pick_font(self.root, _SANS_CANDIDATES, "TkDefaultFont")
        self.mono_family = _pick_font(self.root, _MONO_CANDIDATES, "TkFixedFont")

        # Resize the default Tk font objects so old-style tk.Label widgets
        # pick up the correct family AND size automatically.
        base = self._s(BASE_FONT_BASE)
        for name in ("TkDefaultFont", "TkTextFont", "TkHeadingFont", "TkMenuFont"):
            tkfont.nametofont(name).configure(family=self.font_family, size=base)

    def _setup_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")

        fam = self.font_family
        base_size = self._s(BASE_FONT_BASE)
        small_size = self._s(BASE_FONT_SMALL)
        algo_pad_y = self._s(BASE_ALGO_PADDING_Y)

        style.configure(
            ".",
            background=SURFACE, foreground=TEXT,
            font=(fam, base_size), fieldbackground=SURFACE, bordercolor=BORDER,
        )
        style.configure(
            "Algo.TButton",
            background=SURFACE_ALT, foreground=TEXT, bordercolor=BORDER,
            focuscolor=SURFACE_ALT, font=(fam, base_size),
            padding=(self._s(10), algo_pad_y), relief="flat",
        )
        style.map(
            "Algo.TButton",
            background=[("active", ACCENT_LIGHT), ("pressed", ACCENT_LIGHT)],
            foreground=[("active", ACCENT), ("pressed", ACCENT)],
            bordercolor=[("active", ACCENT), ("pressed", ACCENT)],
        )
        style.configure(
            "AlgoSelected.TButton",
            background=ACCENT, foreground="white", bordercolor=ACCENT,
            focuscolor=ACCENT, font=(fam, base_size, "bold"),
            padding=(self._s(10), algo_pad_y), relief="flat",
        )
        style.map(
            "AlgoSelected.TButton",
            background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)],
        )
        style.configure(
            "Accent.TButton",
            background=ACCENT, foreground="white", bordercolor=ACCENT,
            focuscolor=ACCENT, font=(fam, base_size + 1, "bold"),
            padding=(0, self._s(10)), relief="flat",
        )
        style.map(
            "Accent.TButton",
            background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)],
        )
        style.configure(
            "Ghost.TButton",
            background=SURFACE, foreground=TEXT_MUTED, bordercolor=BORDER,
            focuscolor=SURFACE, font=(fam, small_size),
            padding=(self._s(12), self._s(6)), relief="flat",
        )
        style.map(
            "Ghost.TButton",
            background=[("active", SURFACE_ALT)],
            foreground=[("active", TEXT)],
        )
        style.configure(
            "Size.TButton",
            background=SURFACE_ALT, foreground=TEXT_MUTED, bordercolor=BORDER,
            focuscolor=SURFACE_ALT, font=(fam, small_size),
            padding=(self._s(8), self._s(4)), relief="flat",
        )
        style.map(
            "Size.TButton",
            background=[("active", ACCENT_LIGHT), ("pressed", ACCENT_LIGHT)],
            foreground=[("active", ACCENT)],
        )
        style.configure(
            "SizeSelected.TButton",
            background=ACCENT, foreground="white", bordercolor=ACCENT,
            focuscolor=ACCENT, font=(fam, small_size, "bold"),
            padding=(self._s(8), self._s(4)), relief="flat",
        )
        style.configure(
            "Modern.TEntry",
            fieldbackground=SURFACE, foreground=TEXT,
            bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
            insertcolor=ACCENT, padding=self._s(6), relief="flat",
        )
        style.map(
            "Modern.TEntry",
            bordercolor=[("focus", ACCENT)],
            lightcolor=[("focus", ACCENT)],
            darkcolor=[("focus", ACCENT)],
        )

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------
    def _init_state(self) -> None:
        self.algorithm_var = tk.StringVar(value="bresenham_line")
        self.scale_var = tk.DoubleVar(value=30.0)

        self.x1_var = tk.StringVar(value="-8")
        self.y1_var = tk.StringVar(value="-4")
        self.x2_var = tk.StringVar(value="8")
        self.y2_var = tk.StringVar(value="5")

        self.cx_var = tk.StringVar(value="0")
        self.cy_var = tk.StringVar(value="0")
        self.r_var = tk.StringVar(value="5")

        self.last_pixels: list[tuple[int, int]] = []
        self.last_shape: tuple | None = None
        self.last_algorithm_key: str = ""
        self.last_time_us: float = 0.0

        self.scale = float(self.scale_var.get())

        self.canvas_w = self._s(BASE_CANVAS_SIZE)
        self.canvas_h = self._s(BASE_CANVAS_SIZE)
        self.canvas_origin_x = self.canvas_w / 2
        self.canvas_origin_y = self.canvas_h / 2

    # ------------------------------------------------------------------
    # Layout (grid everywhere)
    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        self.root.grid_rowconfigure(0, weight=0)   # header
        self.root.grid_rowconfigure(1, weight=1)   # main
        self.root.grid_rowconfigure(2, weight=0)   # footer
        self.root.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_main()
        self._build_footer()

    # ---- Header -------------------------------------------------------
    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=SURFACE)
        header.grid(row=0, column=0, sticky="ew")

        pad = self._s(BASE_PAD)
        inner = tk.Frame(header, bg=SURFACE)
        inner.pack(fill=tk.X, padx=pad, pady=(pad, pad - self._s(4)))

        tk.Label(
            inner, text="Raster Algorithms", bg=SURFACE, fg=TEXT,
            font=(self.font_family, self._s(BASE_FONT_TITLE), "bold"),
        ).pack(anchor=tk.W)
        tk.Label(
            inner, text="Lab 3 · line & circle rasterization · basic algorithms",
            bg=SURFACE, fg=TEXT_MUTED,
            font=(self.font_family, self._s(BASE_FONT_BASE)),
        ).pack(anchor=tk.W, pady=(self._s(2), 0))

        tk.Frame(header, bg=ACCENT, height=self._s(3)).pack(side=tk.TOP, fill=tk.X)

    # ---- Main ---------------------------------------------------------
    def _build_main(self) -> None:
        pad = self._s(BASE_PAD)
        main = tk.Frame(self.root, bg=BG)
        main.grid(row=1, column=0, sticky="nsew", padx=pad, pady=pad)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)  # canvas grows
        main.grid_columnconfigure(1, weight=0, minsize=self._s(BASE_CARD_WIDTH))

        self._build_canvas(main)
        self._build_sidebar(main)

    def _build_canvas(self, parent: tk.Widget) -> None:
        self.canvas = tk.Canvas(
            parent,
            width=self._s(BASE_CANVAS_SIZE),
            height=self._s(BASE_CANVAS_SIZE),
            bg=SURFACE, highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=BORDER, bd=0,
        )
        self.canvas.grid(
            row=0, column=0, sticky="nsew", padx=(0, self._s(BASE_PAD)),
        )
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _build_sidebar(self, parent: tk.Widget) -> None:
        sidebar = tk.Frame(parent, bg=BG)
        sidebar.grid(row=0, column=1, sticky="nsew")
        sidebar.grid_rowconfigure(0, weight=0)   # controls card
        sidebar.grid_rowconfigure(1, weight=1)   # info card (grows)
        sidebar.grid_columnconfigure(0, weight=1)

        self._build_controls_card(sidebar)
        self._build_info_card(sidebar)

    # ---- Controls card ------------------------------------------------
    def _build_controls_card(self, parent: tk.Widget) -> None:
        pad = self._s(BASE_PAD)
        card = tk.Frame(
            parent, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER,
        )
        card.grid(row=0, column=0, sticky="ew", pady=(0, pad))
        card.grid_columnconfigure(0, weight=1)

        inner = tk.Frame(card, bg=SURFACE)
        inner.grid(row=0, column=0, sticky="ew",
                   padx=self._s(14), pady=self._s(14))
        inner.grid_columnconfigure(0, weight=1)

        # Algorithm section
        tk.Label(
            inner, text="Algorithm", bg=SURFACE, fg=TEXT,
            font=(self.font_family, self._s(BASE_FONT_BASE), "bold"),
        ).grid(row=0, column=0, sticky="w")

        algo_grid = tk.Frame(inner, bg=SURFACE)
        algo_grid.grid(row=1, column=0, sticky="ew", pady=(self._s(8), self._s(16)))
        algo_grid.grid_columnconfigure(0, weight=1)
        algo_grid.grid_columnconfigure(1, weight=1)

        self.algo_buttons: dict[str, ttk.Button] = {}
        for i, key in enumerate(_ALGORITHMS):
            btn = ttk.Button(
                algo_grid, text=_SHORT_LABELS[key], style="Algo.TButton",
                command=lambda k=key: self._on_algorithm_selected(k),
            )
            row, col = divmod(i, 2)
            btn.grid(
                row=row, column=col, sticky="ew",
                padx=(0 if col == 0 else self._s(4),
                      self._s(4) if col == 0 else 0),
                pady=self._s(2),
            )
            self.algo_buttons[key] = btn

        # Parameters section
        tk.Label(
            inner, text="Parameters", bg=SURFACE, fg=TEXT,
            font=(self.font_family, self._s(BASE_FONT_BASE), "bold"),
        ).grid(row=2, column=0, sticky="w")

        self.params_container = tk.Frame(inner, bg=SURFACE)
        self.params_container.grid(row=3, column=0, sticky="ew",
                                   pady=(self._s(8), self._s(12)))
        self.params_container.grid_columnconfigure(0, weight=1)

        # Line params
        self.line_params = tk.Frame(self.params_container, bg=SURFACE)
        self.line_params.grid(row=0, column=0, sticky="ew")
        self.line_params.grid_columnconfigure(0, weight=1)
        self._build_param_row(self.line_params, 0, "x1", self.x1_var, "y1", self.y1_var)
        self._build_param_row(self.line_params, 1, "x2", self.x2_var, "y2", self.y2_var)

        # Circle params (hidden initially)
        self.circle_params = tk.Frame(self.params_container, bg=SURFACE)
        self.circle_params.grid(row=0, column=0, sticky="ew")
        self.circle_params.grid_columnconfigure(0, weight=1)
        self._build_param_row(self.circle_params, 0, "cx", self.cx_var, "cy", self.cy_var)
        self._build_param_row(self.circle_params, 1, "r",  self.r_var, None, None)
        self.circle_params.grid_remove()  # hidden by default

        # Draw button
        ttk.Button(
            inner, text="Draw", style="Accent.TButton", command=self._on_draw,
        ).grid(row=4, column=0, sticky="ew", pady=(self._s(4), 0))

    def _build_param_row(
        self,
        parent: tk.Widget,
        row: int,
        label1: str, var1: tk.StringVar,
        label2: str | None, var2: tk.StringVar | None,
    ) -> None:
        frame = tk.Frame(parent, bg=SURFACE)
        frame.grid(row=row, column=0, sticky="ew", pady=self._s(2))

        # Label–Entry–Label–Entry. Entries get weight so they stretch.
        frame.grid_columnconfigure(0, weight=0)   # label1
        frame.grid_columnconfigure(1, weight=1)   # entry1
        frame.grid_columnconfigure(2, weight=0)   # label2
        frame.grid_columnconfigure(3, weight=1)   # entry2

        tk.Label(
            frame, text=label1, bg=SURFACE, fg=TEXT_MUTED,
            font=(self.font_family, self._s(BASE_FONT_SMALL)),
        ).grid(row=0, column=0, sticky="w", padx=(0, self._s(4)))
        ttk.Entry(
            frame, textvariable=var1, style="Modern.TEntry",
            width=self._s(BASE_ENTRY_WIDTH) // 2 + 4,  # min; stretches above
        ).grid(row=0, column=1, sticky="ew",
               padx=(0, self._s(10) if label2 else 0))

        if label2 is not None and var2 is not None:
            tk.Label(
                frame, text=label2, bg=SURFACE, fg=TEXT_MUTED,
                font=(self.font_family, self._s(BASE_FONT_SMALL)),
            ).grid(row=0, column=2, sticky="w", padx=(0, self._s(4)))
            ttk.Entry(
                frame, textvariable=var2, style="Modern.TEntry",
                width=self._s(BASE_ENTRY_WIDTH) // 2 + 4,
            ).grid(row=0, column=3, sticky="ew")

    # ---- Info card ----------------------------------------------------
    def _build_info_card(self, parent: tk.Widget) -> None:
        card = tk.Frame(
            parent, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER,
        )
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)

        inner = tk.Frame(card, bg=SURFACE)
        inner.grid(row=0, column=0, sticky="nsew",
                   padx=self._s(14), pady=self._s(14))
        inner.grid_columnconfigure(0, weight=1)

        tk.Label(
            inner, text="Results", bg=SURFACE, fg=TEXT,
            font=(self.font_family, self._s(BASE_FONT_BASE), "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.timing_label = self._value_row(inner, 1, "Time / call", "—")
        self.pixels_label = self._value_row(inner, 2, "Pixels", "—")
        self.last_algo_label = self._value_row(inner, 3, "Algorithm", "—")

        ttk.Separator(inner, orient=tk.HORIZONTAL).grid(
            row=4, column=0, sticky="ew", pady=(self._s(12), self._s(10)),
        )

        tk.Label(
            inner, text="Integer coords ↔ grid", bg=SURFACE, fg=TEXT,
            font=(self.font_family, self._s(BASE_FONT_BASE), "bold"),
        ).grid(row=5, column=0, sticky="w")

        explanation = (
            "Each pixel (x, y) is drawn as the cell\n"
            "[x, x+1] × [y, y+1] on the math grid.\n\n"
            "Integer (x, y) = cell corner. The filled\n"
            "square occupies the cell to its upper-right.\n\n"
            "Red dashed = ideal shape through the\n"
            "centres of the endpoint cells.\n\n"
            "Wu AA (bonus) draws each pixel with\n"
            "opacity = fractional coverage of the\n"
            "cell by the ideal line. Compare with a\n"
            "Bresenham line of the same endpoints:\n"
            "hard edges vs. smooth edges."
        )


        tk.Label(
            inner, text=explanation, bg=SURFACE, fg=TEXT_MUTED,
            font=(self.font_family, self._s(BASE_FONT_SMALL)),
            justify=tk.LEFT,
        ).grid(row=6, column=0, sticky="w", pady=(self._s(6), 0))

    def _value_row(
        self, parent: tk.Widget, row: int, label: str, value: str,
    ) -> tk.Label:
        frame = tk.Frame(parent, bg=SURFACE)
        frame.grid(row=row, column=0, sticky="ew", pady=(self._s(8), 0))
        frame.grid_columnconfigure(1, weight=1)

        tk.Label(
            frame, text=label, bg=SURFACE, fg=TEXT_MUTED,
            font=(self.font_family, self._s(BASE_FONT_SMALL)),
        ).grid(row=0, column=0, sticky="w")

        value_label = tk.Label(
            frame, text=value, bg=SURFACE, fg=TEXT,
            font=(self.mono_family, self._s(BASE_FONT_VALUE), "bold"),
        )
        value_label.grid(row=0, column=1, sticky="e")
        return value_label

    # ---- Footer -------------------------------------------------------
    def _build_footer(self) -> None:
        footer = tk.Frame(self.root, bg=SURFACE)
        footer.grid(row=2, column=0, sticky="ew")
        tk.Frame(footer, bg=BORDER, height=1).pack(side=tk.TOP, fill=tk.X)

        pad = self._s(BASE_PAD)
        inner = tk.Frame(footer, bg=SURFACE)
        inner.pack(fill=tk.X, padx=pad, pady=self._s(10))

        # Grid so the slider column stretches on wide windows.
        inner.grid_columnconfigure(0, weight=0)   # "Scale"
        inner.grid_columnconfigure(1, weight=1)   # slider
        inner.grid_columnconfigure(2, weight=0)   # value label
        inner.grid_columnconfigure(3, weight=0)   # S/M/L
        inner.grid_columnconfigure(4, weight=0)   # Clear

        tk.Label(
            inner, text="Scale", bg=SURFACE, fg=TEXT_MUTED,
            font=(self.font_family, self._s(BASE_FONT_SMALL)),
        ).grid(row=0, column=0, sticky="w", padx=(0, self._s(12)))

        self.scale_slider = ttk.Scale(
            inner, from_=5, to=100, orient=tk.HORIZONTAL,
            variable=self.scale_var, command=self._on_scale_change,
            length=self._s(220),
        )
        self.scale_slider.grid(row=0, column=1, sticky="ew")

        self.scale_value_label = tk.Label(
            inner, text="30 px / unit", bg=SURFACE, fg=TEXT,
            font=(self.font_family, self._s(BASE_FONT_SMALL)),
        )
        self.scale_value_label.grid(row=0, column=2, sticky="w", padx=self._s(12))

        # S / M / L buttons
        size_frame = tk.Frame(inner, bg=SURFACE)
        size_frame.grid(row=0, column=3, sticky="e", padx=(self._s(12), self._s(6)))

        self.size_buttons: dict[str, ttk.Button] = {}
        for i, (label, factor) in enumerate(
            [("S", 0.85), ("M", 1.0), ("L", 1.25), ("Auto", None)]
        ):
            key = label
            if factor is None:
                cmd = lambda: self._on_size_selected(None)
            else:
                cmd = lambda f=factor: self._on_size_selected(f)
            btn = ttk.Button(
                size_frame, text=label, style="Size.TButton", command=cmd,
            )
            btn.grid(row=0, column=i, padx=(0, self._s(2)))
            self.size_buttons[key] = btn
        self._update_size_buttons()

        ttk.Button(
            inner, text="Clear", style="Ghost.TButton", command=self._on_clear,
        ).grid(row=0, column=4, sticky="e")

    def _update_size_buttons(self) -> None:
        # Highlight the button that matches the current override.
        override = self.user_scale_override
        for key, btn in self.size_buttons.items():
            if key == "Auto":
                selected = override is None
            elif key == "S":
                selected = override == 0.85
            elif key == "M":
                selected = override == 1.0
            else:  # L
                selected = override == 1.25
            btn.configure(
                style="SizeSelected.TButton" if selected else "Size.TButton",
            )

    # ------------------------------------------------------------------
    # Window resize → re-scale
    # ------------------------------------------------------------------
    def _on_root_configure(self, event: tk.Event) -> None:
        if event.widget is not self.root:
            return
        if self._resize_after_id is not None:
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(300, self._maybe_rescale)

    def _maybe_rescale(self) -> None:
        self._resize_after_id = None
        if self.user_scale_override is not None:
            return  # user pinned a manual size; do not auto-rescale

        w = self.root.winfo_width()
        h = self.root.winfo_height()
        raw = min(w / REF_WINDOW_W, h / REF_WINDOW_H)
        target = max(1.0, min(MAX_AUTO_SCALE, raw))
        if abs(target - self.auto_window_scale) > 0.1:
            self.auto_window_scale = target
            self.ui_scale = self._effective_scale()
            self._rebuild()

    def _on_size_selected(self, factor: float | None) -> None:
        if factor is None:
            self.user_scale_override = None
        else:
            self.user_scale_override = factor
        self.ui_scale = self._effective_scale()
        self._update_size_buttons()
        self._rebuild()

    # ------------------------------------------------------------------
    # Rebuild (preserves state)
    # ------------------------------------------------------------------
    def _rebuild(self) -> None:
        """Destroy the current widget tree and rebuild it at ui_scale."""
        saved = {
            "algo": self.algorithm_var.get(),
            "x1": self.x1_var.get(), "y1": self.y1_var.get(),
            "x2": self.x2_var.get(), "y2": self.y2_var.get(),
            "cx": self.cx_var.get(), "cy": self.cy_var.get(),
            "r":  self.r_var.get(),
            "scale": self.scale_var.get(),
            "last_shape": self.last_shape,
        }

        for child in self.root.winfo_children():
            child.destroy()

        self._setup_fonts()
        self._setup_style()
        self._init_state()
        self._build_layout()

        # Restore state.
        self.algorithm_var.set(saved["algo"])
        self.x1_var.set(saved["x1"])
        self.y1_var.set(saved["y1"])
        self.x2_var.set(saved["x2"])
        self.y2_var.set(saved["y2"])
        self.cx_var.set(saved["cx"])
        self.cy_var.set(saved["cy"])
        self.r_var.set(saved["r"])
        self.scale_var.set(saved["scale"])
        self.scale = float(self.scale_var.get())

        self._update_algo_buttons()
        self._update_param_visibility()
        self._on_draw()

    # ------------------------------------------------------------------
    # Coordinate transform
    # ------------------------------------------------------------------
    def _math_to_canvas(self, mx: float, my: float) -> tuple[float, float]:
        return (
            self.canvas_origin_x + mx * self.scale,
            self.canvas_origin_y - my * self.scale,
        )

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.canvas_w = event.width
        self.canvas_h = event.height
        self.canvas_origin_x = event.width / 2
        self.canvas_origin_y = event.height / 2
        self._redraw()

    # ------------------------------------------------------------------
    # Rendering (unchanged from previous version, just scaled label sizes)
    # ------------------------------------------------------------------
    def _grid_step(self) -> int:
        for step in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000):
            if step * self.scale >= self._s(40):
                return step
        return 1000

    def _redraw(self) -> None:
        self._render_grid()
        self._render_axes()
        self._render_ideal()
        self._render_pixels()

    def _render_grid(self) -> None:
        self.canvas.delete("grid")
        w, h = self.canvas_w, self.canvas_h
        step = self._grid_step()
        half = max(w, h) / self.scale
        for x in range(int(-half // step) * step,
                       int(half // step) * step + step, step):
            cx, _ = self._math_to_canvas(x, 0)
            if 0 <= cx <= w:
                self.canvas.create_line(cx, 0, cx, h, fill=GRID_COLOR, tags="grid")
        for y in range(int(-half // step) * step,
                       int(half // step) * step + step, step):
            _, cy = self._math_to_canvas(0, y)
            if 0 <= cy <= h:
                self.canvas.create_line(0, cy, w, cy, fill=GRID_COLOR, tags="grid")

    def _render_axes(self) -> None:
        self.canvas.delete("axis")
        w, h = self.canvas_w, self.canvas_h
        ox, oy = self.canvas_origin_x, self.canvas_origin_y
        tick_font = (self.font_family, self._s(8))
        label_font = (self.font_family, self._s(10), "bold")

        self.canvas.create_line(0, oy, w, oy, fill=AXES_COLOR, width=1, tags="axis")
        self.canvas.create_line(ox, 0, ox, h, fill=AXES_COLOR, width=1, tags="axis")

        arrow = self._s(4)
        self.canvas.create_polygon(
            w - arrow * 2, oy - arrow, w - 1, oy, w - arrow * 2, oy + arrow,
            fill=AXES_COLOR, outline="", tags="axis",
        )
        self.canvas.create_polygon(
            ox - arrow, arrow * 2, ox, 1, ox + arrow, arrow * 2,
            fill=AXES_COLOR, outline="", tags="axis",
        )

        self.canvas.create_text(
            w - self._s(20), oy - self._s(14), text="X",
            fill=AXIS_LABEL, font=label_font, tags="axis",
        )
        self.canvas.create_text(
            ox + self._s(14), self._s(16), text="Y",
            fill=AXIS_LABEL, font=label_font, tags="axis",
        )

        step = self._grid_step()
        half = max(w, h) / self.scale
        for x in range(int(-half // step) * step,
                       int(half // step) * step + step, step):
            if x == 0:
                continue
            cx, _ = self._math_to_canvas(x, 0)
            if 0 <= cx <= w:
                self.canvas.create_text(
                    cx, oy + self._s(12), text=str(x),
                    fill=AXIS_LABEL, font=tick_font, tags="axis",
                )
        for y in range(int(-half // step) * step,
                       int(half // step) * step + step, step):
            if y == 0:
                continue
            _, cy = self._math_to_canvas(0, y)
            if 0 <= cy <= h:
                self.canvas.create_text(
                    ox - self._s(14), cy, text=str(y),
                    fill=AXIS_LABEL, font=tick_font, tags="axis",
                )
        self.canvas.create_text(
            ox - self._s(8), oy + self._s(12), text="0",
            fill=AXIS_LABEL, font=tick_font, tags="axis",
        )

    def _render_ideal(self) -> None:
        self.canvas.delete("ideal")
        if self.last_shape is None:
            return
        kind = self.last_shape[0]
        if kind == "line":
            _, x1, y1, x2, y2 = self.last_shape
            ax, ay = self._math_to_canvas(x1 + 0.5, y1 + 0.5)
            bx, by = self._math_to_canvas(x2 + 0.5, y2 + 0.5)
            self.canvas.create_line(
                ax, ay, bx, by, fill=IDEAL, width=1, dash=(4, 4), tags="ideal",
            )
        elif kind == "circle":
            _, cx, cy, r = self.last_shape
            ox, oy = self._math_to_canvas(cx + 0.5, cy + 0.5)
            rad = r * self.scale
            self.canvas.create_oval(
                ox - rad, oy - rad, ox + rad, oy + rad,
                outline=IDEAL, width=1, dash=(4, 4), tags="ideal",
            )

    def _render_pixels(self) -> None:
        self.canvas.delete("pixel")
        for pixel in self.last_pixels:
            # Anti-aliased algorithms return (x, y, alpha);
            # the others return (x, y).
            if len(pixel) == 3:
                x, y, alpha = pixel
                fill = self._blend_color(PIXEL, SURFACE, alpha)
                outline = ""  # no hard border on partial-coverage pixels
            else:
                x, y = pixel
                fill = PIXEL
                outline = PIXEL_OUTLINE

            cx1, cy1 = self._math_to_canvas(x, y + 1)
            cx2, cy2 = self._math_to_canvas(x + 1, y)
            self.canvas.create_rectangle(
                cx1, cy1, cx2, cy2,
                fill=fill, outline=outline, width=1, tags="pixel",
            )

    @staticmethod
    def _blend_color(fg_hex: str, bg_hex: str, alpha: float) -> str:
        """Blend a foreground colour with a background colour at a given
        opacity. Used to render anti-aliased pixels on the Tk canvas,
        which has no native alpha channel."""
        fr = int(fg_hex[1:3], 16); fg = int(fg_hex[3:5], 16); fb = int(fg_hex[5:7], 16)
        br = int(bg_hex[1:3], 16); bg = int(bg_hex[3:5], 16); bb = int(bg_hex[5:7], 16)
        r = int(round(fr * alpha + br * (1 - alpha)))
        g = int(round(fg * alpha + bg * (1 - alpha)))
        b = int(round(fb * alpha + bb * (1 - alpha)))
        return f"#{r:02x}{g:02x}{b:02x}"

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------
    def _clear_state(self) -> None:
        self.last_pixels = []
        self.last_shape = None
        self.last_algorithm_key = ""
        self.last_time_us = 0.0

    def _update_algo_buttons(self) -> None:
        current = self.algorithm_var.get()
        for key, btn in self.algo_buttons.items():
            btn.configure(
                style="AlgoSelected.TButton" if key == current else "Algo.TButton",
            )

    def _update_param_visibility(self) -> None:
        if self.algorithm_var.get() == "bresenham_circle":
            self.line_params.grid_remove()
            self.circle_params.grid()
        else:
            self.circle_params.grid_remove()
            self.line_params.grid()

    def _on_algorithm_selected(self, key: str) -> None:
        if key == self.algorithm_var.get():
            return
        self.algorithm_var.set(key)
        self._update_algo_buttons()
        self._update_param_visibility()
        self._clear_state()
        self._on_draw()

    def _on_scale_change(self, _value: str = "") -> None:
        try:
            self.scale = float(self.scale_var.get())
        except (ValueError, tk.TclError):
            return
        self.scale_value_label.config(text=f"{round(self.scale)} px / unit")
        self._redraw()

    def _on_clear(self) -> None:
        self._clear_state()
        self._redraw()
        self._update_info()

    def _on_draw(self) -> None:
        key = self.algorithm_var.get()
        try:
            args = self._read_inputs(key)
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        fn = _ALGORITHMS[key]
        try:
            pixels = fn(*args)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Algorithm error", str(exc))
            return

        if key == "bresenham_circle":
            cx, cy, r = args
            self.last_shape = (
                "circle", int(round(cx)), int(round(cy)), int(round(r)),
            )
        else:
            x1, y1, x2, y2 = args
            self.last_shape = (
                "line", int(round(x1)), int(round(y1)),
                int(round(x2)), int(round(y2)),
            )

        self.last_pixels = pixels
        self.last_algorithm_key = key
        self.last_time_us = self._benchmark(fn, args)
        self._redraw()
        self._update_info()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _read_inputs(self, key: str) -> tuple[float, ...]:
        try:
            if key == "bresenham_circle":
                return (
                    float(self.cx_var.get()),
                    float(self.cy_var.get()),
                    float(self.r_var.get()),
                )
            return (
                float(self.x1_var.get()), float(self.y1_var.get()),
                float(self.x2_var.get()), float(self.y2_var.get()),
            )
        except ValueError as exc:
            raise ValueError(
                "Please enter numeric values in all parameter fields."
            ) from exc

    def _benchmark(self, fn, args: tuple[float, ...]) -> float:
        estimate = self._estimate_pixel_count(args)
        iterations = max(100, min(5000, 1_000_000 // max(1, estimate)))
        fn(*args)  # warm-up
        start = time.perf_counter()
        for _ in range(iterations):
            fn(*args)
        elapsed = time.perf_counter() - start
        return elapsed / iterations * 1e6

    @staticmethod
    def _estimate_pixel_count(args: tuple[float, ...]) -> int:
        if len(args) == 3:
            return max(1, int(8 * max(1, round(abs(args[2])))))
        x1, y1, x2, y2 = args
        return max(
            1,
            int(max(abs(round(x2) - round(x1)),
                    abs(round(y2) - round(y1)))) + 1,
        )

    @staticmethod
    def _format_time(us: float) -> str:
        if us < 1:
            return f"{us * 1000:.0f} ns"
        if us < 1000:
            return f"{us:.2f} µs"
        return f"{us / 1000:.2f} ms"

    def _update_info(self) -> None:
        self.timing_label.config(
            text=self._format_time(self.last_time_us)
            if self.last_time_us > 0 else "—",
        )
        self.pixels_label.config(
            text=str(len(self.last_pixels)) if self.last_pixels else "—",
        )
        self.last_algo_label.config(
            text=_FULL_LABELS[self.last_algorithm_key]
            if self.last_algorithm_key else "—",
        )