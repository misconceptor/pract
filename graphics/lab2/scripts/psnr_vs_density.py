"""Generate PSNR-vs-noise-density plot for the report.

Shows:
- Median filter dramatically improves PSNR on salt-and-pepper noise
- Median filter barely helps on Gaussian noise

Saves the plot to docs/screenshots/psnr_vs_density.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.io_utils import load_image, to_gray
from src.metrics import psnr
from src.noise import add_gaussian, add_salt_pepper
from src.order_stats import median_filter

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "assets" / "order_statistics" / "portrait" / "6167110844_da1b453b0e_c.jpg"
OUT = ROOT / "docs" / "screenshots" / "psnr_vs_density.png"


def main() -> None:
    clean = to_gray(load_image(CLEAN))

    sp_densities = np.array([0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30])
    sp_noisy_psnr, sp_median_psnr = [], []
    for d in sp_densities:
        rng = np.random.default_rng(0)
        noisy = add_salt_pepper(clean, density=float(d), rng=rng)
        filtered = median_filter(noisy, k=3)
        sp_noisy_psnr.append(psnr(clean, noisy))
        sp_median_psnr.append(psnr(clean, filtered))

    g_sigmas = np.array([5, 10, 20, 30, 40, 50, 60])
    g_noisy_psnr, g_median_psnr = [], []
    for s in g_sigmas:
        rng = np.random.default_rng(0)
        noisy = add_gaussian(clean, sigma=float(s), rng=rng)
        filtered = median_filter(noisy, k=3)
        g_noisy_psnr.append(psnr(clean, noisy))
        g_median_psnr.append(psnr(clean, filtered))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    axes[0].plot(sp_densities * 100, sp_noisy_psnr, "o--", label="Noisy")
    axes[0].plot(sp_densities * 100, sp_median_psnr, "o-", label="Median k=3")
    axes[0].set_xlabel("Salt & pepper density (%)")
    axes[0].set_ylabel("PSNR vs clean (dB)")
    axes[0].set_title("Salt-and-pepper noise")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(g_sigmas, g_noisy_psnr, "o--", label="Noisy")
    axes[1].plot(g_sigmas, g_median_psnr, "o-", label="Median k=3")
    axes[1].set_xlabel("Gaussian sigma (intensity units)")
    axes[1].set_ylabel("PSNR vs clean (dB)")
    axes[1].set_title("Gaussian noise")
    axes[1].grid(alpha=0.3)
    axes[1].legend()

    plt.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()