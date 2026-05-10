#!/usr/bin/env python3
"""
Generate dragon pixel art from user-provided hand-drawn sprites.

User provides:
- neutral.jpg       -> layer_art_0
- glasses.jpg       -> layer_art_1
- raised-brows.jpg  -> layer_art_2
- angry.jpg         -> layer_art_3
- sleepy.jpg        -> layer_art_default
- flying.jpg        -> peripheral_art_00..05 (6 frames, 3x2 grid)

Outputs:
- assets/peripheral_art/  (6 animation frames, 69x68)
- assets/layer_art/       (5 face images, 68x68)
"""

import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
    import numpy as np
except ImportError:
    print("Error: Pillow and numpy are required. Install with: pip install Pillow numpy")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"


def ensure_dirs():
    (ASSETS_DIR / "peripheral_art").mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "layer_art").mkdir(parents=True, exist_ok=True)


def new_image(w, h):
    return Image.new("1", (w, h), 1)


def process_sprite(path, size=68):
    """Load a user-provided sprite, downscale to size×size, clean up."""
    img = Image.open(path).convert("L")
    # Downscale with nearest neighbor to preserve hard pixel edges
    small = img.resize((size, size), Image.NEAREST)
    # Threshold: dark pixels become black (0), light become white (1)
    return small.point(lambda x: 0 if x < 128 else 1, "1")


def generate_layer_faces():
    # Process user-provided sprites
    neutral = process_sprite(PROJECT_DIR / "neutral.jpg")
    glasses = process_sprite(PROJECT_DIR / "glasses.jpg")
    raised = process_sprite(PROJECT_DIR / "raised-brows.jpg")
    fierce = process_sprite(PROJECT_DIR / "angry.jpg")
    sleepy = process_sprite(PROJECT_DIR / "sleepy.jpg")

    sprites = {
        "layer_art_0": neutral,
        "layer_art_1": glasses,
        "layer_art_2": raised,
        "layer_art_3": fierce,
        "layer_art_default": sleepy,
    }

    for name, img in sprites.items():
        png_path = ASSETS_DIR / "layer_art" / f"{name}.png"
        img.save(png_path)
        print(f"Generated {png_path}")


def generate_peripheral_frames():
    """Slice flying.jpg (6 frames, 3x2 grid, 816x816) into individual 69x68 frames."""
    sheet = Image.open(PROJECT_DIR / "flying2.jpg").convert("L")
    arr = np.array(sheet)
    rows, cols = 2, 3
    cell_h = arr.shape[0] // rows
    cell_w = arr.shape[1] // cols

    for idx in range(6):
        row = idx // cols
        col = idx % cols
        y1 = row * cell_h
        y2 = (row + 1) * cell_h
        x1 = col * cell_w
        x2 = (col + 1) * cell_w
        cell = arr[y1:y2, x1:x2]

        # Find bounding box of dark pixels
        mask = cell < 128
        if mask.any():
            ys, xs = np.where(mask)
            by1, by2 = ys.min(), ys.max() + 1
            bx1, bx2 = xs.min(), xs.max() + 1
            cropped = cell[by1:by2, bx1:bx2]
        else:
            cropped = cell

        # Convert to PIL and resize to fit in 69x68 maintaining aspect ratio
        pil_crop = Image.fromarray(cropped)
        pil_crop.thumbnail((69, 68), Image.NEAREST)

        # Center in 69x68 canvas (white background)
        canvas = new_image(69, 68)
        ox = (69 - pil_crop.size[0]) // 2
        oy = (68 - pil_crop.size[1]) // 2
        bw = pil_crop.point(lambda x: 0 if x < 128 else 1, "1")
        canvas.paste(bw, (ox, oy))

        png_path = ASSETS_DIR / "peripheral_art" / f"peripheral_art_{idx:02d}.png"
        canvas.save(png_path)
        print(f"Generated {png_path}")


def convert_all():
    converter = SCRIPT_DIR / "png_to_lvgl.py"
    for i in range(6):
        png = ASSETS_DIR / "peripheral_art" / f"peripheral_art_{i:02d}.png"
        c_out = ASSETS_DIR / f"peripheral_art_{i:02d}.c"
        subprocess.run([sys.executable, str(converter), str(png), str(c_out),
                        "--name", f"peripheral_art_{i:02d}"], check=True)
    for name in ["layer_art_0", "layer_art_1", "layer_art_2", "layer_art_3", "layer_art_default"]:
        png = ASSETS_DIR / "layer_art" / f"{name}.png"
        c_out = ASSETS_DIR / f"{name}.c"
        subprocess.run([sys.executable, str(converter), str(png), str(c_out),
                        "--name", name], check=True)


def main():
    ensure_dirs()
    print("Processing user-provided sprites...")
    generate_layer_faces()
    print("\nGenerating peripheral frames from flying2.jpg...")
    generate_peripheral_frames()
    print("\nConverting to LVGL C arrays...")
    convert_all()
    print("\nDone! All assets generated.")


if __name__ == "__main__":
    main()
