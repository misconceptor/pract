"""
Nonlinear order-statistic filters + linear contrast stretching + histogram
equalization (with RGB-per-channel vs HSV-V-only comparison).

Run with:
    streamlit run app.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.noise import add_gaussian, add_salt_pepper
from src.contrast import linear_contrast_stretch
from src.histogram_eq import (
    equalize_gray,
    equalize_hsv_v_only,
    equalize_rgb_per_channel,
)
from src.io_utils import load_image, to_gray
from src.metrics import entropy, psnr, std_dev
from src.order_stats import (
    max_filter,
    median_filter,
    min_filter,
    percentile_filter,
)

st.set_page_config(
    page_title="Variant 5 — Image Processing Lab",
    page_icon="🖼️",
    layout="wide",
)

ROOT = Path(__file__).parent
ORDER_DIR = ROOT / "assets" / "order_statistics"
CONTRAST_DIR = ROOT / "assets" / "contrast"
COLOR_DIR = ROOT / "assets" / "color_eq"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

@st.cache_data
def list_order_pairs() -> dict[str, list[tuple[str, str]]]:
    """Return {category: [(clean_path, noisy_path), ...]} for order_stats."""
    result: dict[str, list[tuple[str, str]]] = {}
    if not ORDER_DIR.exists():
        return result
    for sub in sorted(ORDER_DIR.iterdir()):
        if not sub.is_dir():
            continue
        pairs: list[tuple[str, str]] = []
        for clean in sorted(sub.iterdir()):
            if not clean.is_file() or clean.name.startswith("noisy_"):
                continue
            noisy = sub / f"noisy_{clean.name}"
            if noisy.exists():
                pairs.append((str(clean), str(noisy)))
        if pairs:
            result[sub.name] = pairs
    return result


@st.cache_data
def list_images(folder: Path) -> list[str]:
    if not folder.exists():
        return []
    return [
        str(p) for p in sorted(folder.iterdir())
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ]


@st.cache_data
def cached_load(path: str) -> np.ndarray:
    return load_image(path)

def _gray_hist(ax, img: np.ndarray, title: str):
    g = to_gray(img)
    ax.hist(g.ravel(), bins=256, range=(0, 256), color="black", alpha=0.8)
    ax.set_title(title, fontsize=10)
    ax.set_xlim(0, 255)
    ax.set_yticks([])


def _rgb_hist(ax, img: np.ndarray, title: str):
    if img.ndim == 2:
        return _gray_hist(ax, img, title)
    for ch, color, label in zip(range(3), ["r", "g", "b"], ["R", "G", "B"]):
        ax.hist(
            img[..., ch].ravel(), bins=256, range=(0, 256),
            color=color, alpha=0.4, label=label,
        )
    ax.set_title(title, fontsize=10)
    ax.set_xlim(0, 255)
    ax.set_yticks([])
    ax.legend(loc="upper right", fontsize=8)


def histogram_row(items: list[tuple[str, np.ndarray]], rgb: bool = False):
    fig, axes = plt.subplots(1, len(items), figsize=(4.5 * len(items), 2.4))
    if len(items) == 1:
        axes = [axes]
    for ax, (title, img) in zip(axes, items):
        (_rgb_hist if rgb else _gray_hist)(ax, img, title)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def show_triplet(images: list[tuple[str, np.ndarray]]):
    cols = st.columns(3)
    for col, (title, img) in zip(cols, images):
        with col:
            st.image(img, caption=title, use_container_width=True, clamp=True)

st.sidebar.title("Variant 5")
st.sidebar.markdown(
    "**Order-statistic filters**  \n"
    "**Histogram equalization + linear contrast**  \n"
    "**RGB vs HSV color equalization**"
)
st.sidebar.markdown("---")
st.sidebar.caption(
    "Streamlit UI · OpenCV + NumPy backend · "
    "Image Processing Lab"
)

tab_ord, tab_contrast, tab_color, tab_about = st.tabs([
    "Order-statistic filters",
    "Linear contrast vs histogram equalization",
    "RGB vs HSV equalization",
    "About",
])


with tab_ord:
    st.header("Nonlinear filters based on order statistics")
    st.caption(
        "Each output pixel is a **rank** of the sorted neighbourhood — median, "
        "min, max, or an arbitrary percentile. Perfect for salt-and-pepper noise."
    )

    mode = st.radio(
        "Input source",
        ["Real noisy pair", "Synthetic noise"],
        horizontal=True,
        key="ord_mode",
    )

    if mode == "Real noisy pair":
        pairs = list_order_pairs()
        if not pairs:
            st.error(f"No paired images found under `{ORDER_DIR}`.")
            st.stop()

        col_a, col_b = st.columns(2)
        with col_a:
            category = st.selectbox("Category", list(pairs.keys()), key="ord_cat")
        with col_b:
            idx = st.selectbox(
                "Image",
                range(len(pairs[category])),
                format_func=lambda i: Path(pairs[category][i][0]).name,
                key="ord_img",
            )
        clean_path, noisy_path = pairs[category][idx]
        clean = cached_load(clean_path)
        noisy = cached_load(noisy_path)
        noisy_label = "Noisy (input, real)"

    else:  # synthetic noise
        # use the clean images from any category as ground truth
        pairs = list_order_pairs()
        if not pairs:
            st.error(f"No images found under `{ORDER_DIR}`.")
            st.stop()

        col_a, col_b = st.columns(2)
        with col_a:
            category = st.selectbox(
                "Category", list(pairs.keys()), key="ord_syn_cat"
            )
        with col_b:
            idx = st.selectbox(
                "Clean image",
                range(len(pairs[category])),
                format_func=lambda i: Path(pairs[category][i][0]).name,
                key="ord_syn_img",
            )
        clean_path = pairs[category][idx][0]
        clean = cached_load(clean_path)
        clean_gray_only = to_gray(clean)

        col_c, col_d = st.columns(2)
        with col_c:
            noise_type = st.selectbox(
                "Noise type", ["Salt & pepper", "Gaussian"], key="ord_noise_type"
            )
        with col_d:
            if noise_type == "Salt & pepper":
                density = st.slider(
                    "Density (%)", 1, 40, 10, key="ord_sp_density"
                ) / 100.0
            else:
                sigma = st.slider(
                    "Sigma (intensity units)", 2, 80, 20, key="ord_g_sigma"
                )

        rng = np.random.default_rng(0)  # reproducible
        if noise_type == "Salt & pepper":
            noisy = add_salt_pepper(clean_gray_only, density=density, rng=rng)
            noisy_label = f"Noisy (S&P {int(density * 100)} %)"
        else:
            noisy = add_gaussian(clean_gray_only, sigma=float(sigma), rng=rng)
            noisy_label = f"Noisy (Gaussian σ={sigma})"

    col_e, col_f, col_g = st.columns(3)
    with col_e:
        filter_name = st.selectbox(
            "Filter", ["Median", "Min", "Max", "Percentile"], key="ord_filter"
        )
    with col_f:
        k = st.slider("Kernel size (px)", 3, 11, 3, step=2, key="ord_k")
    with col_g:
        pct = 50
        if filter_name == "Percentile":
            pct = st.slider(
                "Percentile (0=min, 50=median, 100=max)",
                0, 100, 50, key="ord_pct",
            )

    clean_gray = to_gray(clean)

    if filter_name == "Median":
        filtered = median_filter(noisy, k=k)
    elif filter_name == "Min":
        filtered = min_filter(noisy, k=k)
    elif filter_name == "Max":
        filtered = max_filter(noisy, k=k)
    else:
        filtered = percentile_filter(noisy, k=k, percentile=pct)

    show_triplet([
        ("Clean (ground truth, grayscale)", clean_gray),
        (noisy_label, noisy),
        (f"{filter_name} result (k={k}"
         f"{', p=' + str(pct) if filter_name == 'Percentile' else ''})",
         filtered),
    ])

    st.subheader("Quality metrics")
    before = psnr(clean_gray, noisy)
    after = psnr(clean_gray, filtered)
    m1, m2, m3 = st.columns(3)
    m1.metric("PSNR — noisy vs clean", f"{before:.2f} dB")
    m2.metric(
        "PSNR — filtered vs clean",
        f"{after:.2f} dB",
        delta=f"{after - before:+.2f} dB",
    )
    m3.metric("Filtered std-dev", f"{std_dev(filtered):.1f}")

    st.subheader("Histograms")
    histogram_row([
        ("Clean", clean_gray),
        ("Noisy", noisy),
        (filter_name, filtered),
    ])

    with st.expander("Why this filter?"):
        if filter_name == "Median":
            st.markdown(
                "Median = 50th percentile. Removes impulse (salt-and-pepper) "
                "noise by replacing outliers with the middle value, while "
                "preserving edges better than a Gaussian blur."
            )
        elif filter_name == "Min":
            st.markdown(
                "Min filter replaces each pixel with the darkest in its window. "
                "Removes white (salt) noise but **expands dark regions** — "
                "shrinks bright objects, destroys thin lines."
            )
        elif filter_name == "Max":
            st.markdown(
                "Max filter replaces each pixel with the brightest in its window. "
                "Removes black (pepper) noise but **expands bright regions** — "
                "blooms highlights, closes gaps."
            )
        else:
            st.markdown(
                "Percentile filter is the general case: `p=0` → min, `p=50` → "
                "median, `p=100` → max. Useful when noise is asymmetric "
                "(e.g. only salt or only pepper)."
            )

    if mode == "Synthetic noise":
        st.info(
            "**Try this:** switch to **Gaussian** noise and watch PSNR collapse — "
            "the median filter barely improves it. Switch back to **Salt & pepper** "
            "and PSNR jumps. That's the whole reason median filters exist."
        )

with tab_contrast:
    st.header("Linear contrast stretching vs histogram equalization")
    st.caption(
        "Two approaches to boosting contrast. **Stretching** is linear and "
        "predictable. **Equalization** is non-linear and driven by the histogram."
    )

    images = list_images(CONTRAST_DIR)
    if not images:
        st.error(f"No images found in `{CONTRAST_DIR}`.")
    else:
        idx = st.selectbox(
            "Image",
            range(len(images)),
            format_func=lambda i: Path(images[i]).name,
            key="contrast_img",
        )
        path = images[idx]

        c_low, c_high = st.columns(2)
        with c_low:
            low_pct = st.slider("Clip low %", 0, 20, 2, key="contrast_low")
        with c_high:
            high_pct = st.slider("Clip high %", 80, 100, 98, key="contrast_high")

        orig = cached_load(path)
        gray = to_gray(orig)
        stretched = linear_contrast_stretch(gray, low_pct=low_pct, high_pct=high_pct)
        equalized = equalize_gray(gray)

        show_triplet([
            ("Original (grayscale)", gray),
            (f"Linear stretch (clip {low_pct}–{high_pct}%)", stretched),
            ("Histogram equalization", equalized),
        ])

        st.subheader("Metrics")
        std1, std2, std3 = st.columns(3)
        std1.metric("Original std-dev", f"{std_dev(gray):.2f}")
        std2.metric("Stretched std-dev", f"{std_dev(stretched):.2f}")
        std3.metric("Equalized std-dev", f"{std_dev(equalized):.2f}")

        ent1, ent2, ent3 = st.columns(3)
        ent1.metric("Original entropy", f"{entropy(gray):.3f}")
        ent2.metric("Stretched entropy", f"{entropy(stretched):.3f}")
        ent3.metric("Equalized entropy", f"{entropy(equalized):.3f}")

        st.subheader("Histograms")
        histogram_row([
            ("Original", gray),
            ("Linear stretch", stretched),
            ("Equalized", equalized),
        ])

        st.info(
            "**Stretching** is a straight line — it preserves the shape of the "
            "histogram and only widens it. **Equalization** reshapes the histogram "
            "toward uniform, which can over-amplify noise in flat regions (skies, "
            "walls). That's why large-sky or portrait images often look worse after "
            "equalization but fine after percentile-clipped stretching."
        )

with tab_color:
    st.header("Color histogram equalization — RGB vs HSV")
    st.caption(
        "The lab asks you to compare two color approaches: equalize R, G, B "
        "independently, or equalize only V in HSV."
    )

    images = list_images(COLOR_DIR)
    if not images:
        st.error(f"No images found in `{COLOR_DIR}`.")
    else:
        idx = st.selectbox(
            "Image",
            range(len(images)),
            format_func=lambda i: Path(images[i]).name,
            key="color_img",
        )
        path = images[idx]

        orig = cached_load(path)
        rgb_eq = equalize_rgb_per_channel(orig)
        hsv_eq = equalize_hsv_v_only(orig)

        show_triplet([
            ("Original", orig),
            ("RGB per-channel equalization", rgb_eq),
            ("HSV V-only equalization", hsv_eq),
        ])

        st.subheader("Histograms (per channel)")
        histogram_row(
            [("Original", orig), ("RGB eq", rgb_eq), ("HSV V-eq", hsv_eq)],
            rgb=True,
        )

        st.info(
            "**RGB per-channel** equalizes each channel with a different CDF, so "
            "the R/G/B histograms are not aligned — neutral regions (skin, walls, "
            "sky) drift toward blue/magenta/green. **HSV V-only** keeps H and S "
            "fixed and only redistributes brightness, so colors remain close to "
            "the original and the result looks like a natural exposure lift."
        )

        with st.expander("Report tip — how to measure the color shift"):
            st.markdown(
                "Pick a **neutral region** (a wall, a face without makeup, the sky) "
                "and compute the per-channel mean in both outputs. The HSV "
                "equalization should keep the R:G:B ratio closer to the original; "
                "the RGB equalization will skew it. Include a small side-by-side "
                "crop in your report — it is a very convincing figure."
            )


with tab_about:
    st.header("About this lab — Variant 5")
    st.markdown(
        """
Three linked methods are implemented:

1. **Nonlinear filters based on order statistics** — sliding-window filters
   that pick a rank from the sorted neighborhood: **median**, **min**, **max**,
   and a general **percentile/rank** filter.
2. **Histogram equalization** — CDF-based mapping, implemented from scratch,
   in grayscale, RGB per-channel, and HSV V-only forms.
3. **Linear contrast stretching** — robust percentile-clipped linear transform
   (`out = (in − p_low) × 255 / (p_high − p_low)`).

### Where each method lives

| Method | File | Function |
|---|---|---|
| Order statistics | `src/order_stats.py` | `median_filter`, `min_filter`, `max_filter`, `percentile_filter` |
| Linear contrast | `src/contrast.py` | `linear_contrast_stretch` |
| Histogram equalization | `src/histogram_eq.py` | `equalize_gray`, `equalize_rgb_per_channel`, `equalize_hsv_v_only` |
| Metrics | `src/metrics.py` | `psnr`, `entropy`, `std_dev` |
| I/O | `src/io_utils.py` | `load_image`, `to_gray`, `to_hsv` |

### Test image database

- `assets/order_statistics/{flat, texture, contrast_edge, portrait, heavy-noise}/`
  — **paired** clean + salt-and-pepper noisy images. Each pair is
  `X.jpg` (clean) and `noisy_X.jpg` (noisy), so PSNR can be computed against
  the ground truth.
- `assets/contrast/` — lossless low-contrast photos for the linear/equalization
  comparison.
- `assets/color_eq/` — Kodak suite images for the RGB vs HSV comparison.
        """
    )