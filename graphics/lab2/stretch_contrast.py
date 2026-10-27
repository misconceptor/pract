from src.io_utils import load_image, save_image, to_gray
from src.metrics import psnr, histogram_stats
from src.contrast import linear_contrast_stretch

clean = load_image("assets/order_statistics/portrait/6167110844_da1b453b0e_c.jpg")
noisy = load_image("assets/order_statistics/portrait/noisy_6167110844_da1b453b0e_c.jpg")

print("Metrics")
print(f"PSNR (Clean vs Noisy): {psnr(clean, noisy):.2f} dB")
print(f"Stats (Clean): {histogram_stats(clean)}")
print(f"Stats (Noisy): {histogram_stats(noisy)}")

low_contrast_img = load_image("assets/contrast/mc2-lossless.png")
gray = to_gray(low_contrast_img)

stretched = linear_contrast_stretch(gray, low_pct=2.0, high_pct=98.0)

print("\nContrast Stretching")
print(f"Before: min={gray.min()}, max={gray.max()}, std={gray.std():.2f}")
print(f"After : min={stretched.min()}, max={stretched.max()}, std={stretched.std():.2f}")

save_image(stretched, "docs/screenshots/test_stretched.jpg")
print("Saved stretched image to docs/screenshots/")