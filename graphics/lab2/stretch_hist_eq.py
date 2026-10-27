from src.histogram_eq import equalize_gray, equalize_rgb_per_channel, equalize_hsv_v_only
from src.io_utils import load_image, save_image, to_gray

print("\nHistogram Equalization")

color_img = load_image("assets/color_eq/kodim03.png")

eq_rgb = equalize_rgb_per_channel(color_img)
save_image(eq_rgb, "docs/screenshots/test_eq_rgb.jpg")

eq_hsv = equalize_hsv_v_only(color_img)
save_image(eq_hsv, "docs/screenshots/test_eq_hsv.jpg")

print("Saved test_eq_rgb.jpg and test_eq_hsv.jpg to docs/screenshots/")
print("Open them to see the difference: RGB eq will likely have weird color shifts, HSV eq will look natural but brighter.")
