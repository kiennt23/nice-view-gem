#!/usr/bin/env python3
"""
Generate dragon pixel art from user-provided hand-drawn sprites.

User provides:
- neutral.jpg       -> layer_art_0
- glasses.jpg       -> layer_art_1
- raised-brows.jpg  -> layer_art_2
- angry.jpg         -> layer_art_3
- sleepy.jpg        -> layer_art_default
- flying3.jpg       -> peripheral_art_00..05 (6 frames, 3x2 grid with borders)

Outputs:
- assets/peripheral_art/  (6 animation frames, 69x68)
- assets/layer_art/       (5 face images, 68x68)
"""

import shutil
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
BOARD_ASSETS_DIR = PROJECT_DIR / "boards" / "shields" / "nice_view_gem" / "assets"


def ensure_dirs():
    (ASSETS_DIR / "peripheral_art").mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "layer_art").mkdir(parents=True, exist_ok=True)
    BOARD_ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def new_image(w, h):
    return Image.new("1", (w, h), 1)


def process_sprite(path, size=68):
    """Load a user-provided sprite, downscale to size×size, clean up."""
    img = Image.open(path).convert("L")
    small = img.resize((size, size), Image.NEAREST)
    return small.point(lambda x: 0 if x < 128 else 1, "1")


def detect_bordered_frames(sheet_path):
    """Auto-detect inner regions of bordered frames in a sprite sheet."""
    img = Image.open(sheet_path).convert("L")
    arr = np.array(img)
    mask = arr < 128

    def find_h_borders():
        borders = []
        for y in range(mask.shape[0]):
            row = mask[y]
            start = None
            for x, v in enumerate(row):
                if v and start is None:
                    start = x
                elif not v and start is not None:
                    if x - start > 200:
                        borders.append((y, start, x))
                    start = None
            if start is not None and mask.shape[1] - start > 200:
                borders.append((y, start, mask.shape[1]))
        return borders

    def find_v_borders():
        borders = []
        for x in range(mask.shape[1]):
            col = mask[:, x]
            start = None
            for y, v in enumerate(col):
                if v and start is None:
                    start = y
                elif not v and start is not None:
                    if y - start > 200:
                        borders.append((x, start, y))
                    start = None
            if start is not None and mask.shape[0] - start > 200:
                borders.append((x, start, mask.shape[0]))
        return borders

    h = find_h_borders()
    v = find_v_borders()

    h_y = sorted(set(y for y, _, _ in h))
    v_x = sorted(set(x for x, _, _ in v))

    def group_consecutive(vals):
        if not vals:
            return []
        groups = []
        cur = [vals[0]]
        for v in vals[1:]:
            if v == cur[-1] + 1:
                cur.append(v)
            else:
                groups.append(cur)
                cur = [v]
        groups.append(cur)
        return groups

    h_groups = group_consecutive(h_y)
    v_groups = group_consecutive(v_x)

    if len(h_groups) != 4 or len(v_groups) != 6:
        raise ValueError(
            f"Expected 4 horizontal and 6 vertical border groups, "
            f"got {len(h_groups)} and {len(v_groups)}"
        )

    frames = []
    for ri in range(2):
        for ci in range(3):
            top = h_groups[ri * 2][-1] + 1
            bottom = h_groups[ri * 2 + 1][0] - 1
            left = v_groups[ci * 2][-1] + 1
            right = v_groups[ci * 2 + 1][0] - 1
            frames.append((left, top, right, bottom))

    return img, frames


def generate_layer_faces():
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
    """Extract 6 frames from flying3.jpg, auto-detecting bordered regions."""
    sheet, frames = detect_bordered_frames(PROJECT_DIR / "flying3.jpg")
    arr = np.array(sheet.convert("L"))

    for idx, (left, top, right, bottom) in enumerate(frames):
        # Crop inside border
        cropped = arr[top:bottom + 1, left:right + 1]
        pil_crop = Image.fromarray(cropped)

        # Remove "+" anchor marker at top-left corner (paint ~14x14 white)
        draw = ImageDraw.Draw(pil_crop)
        draw.rectangle([0, 0, 13, 13], fill=255)

        # Convert to 1-bit with threshold
        bw = pil_crop.point(lambda x: 0 if x < 128 else 255, "1")

        # Resize to fit in 69x68 maintaining aspect ratio
        bw.thumbnail((69, 68), Image.NEAREST)

        # Center in 69x68 canvas (white background)
        canvas = new_image(69, 68)
        ox = (69 - bw.size[0]) // 2
        oy = (68 - bw.size[1]) // 2
        canvas.paste(bw, (ox, oy))

        png_path = ASSETS_DIR / "peripheral_art" / f"peripheral_art_{idx:02d}.png"
        canvas.save(png_path)
        print(f"Generated {png_path} ({canvas.size})")


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


def sync_to_board_assets():
    """Copy generated C arrays to the board assets dir where CMakeLists.txt reads them."""
    for i in range(6):
        src = ASSETS_DIR / f"peripheral_art_{i:02d}.c"
        dst = BOARD_ASSETS_DIR / f"peripheral_art_{i:02d}.c"
        shutil.copy2(src, dst)
    for name in ["layer_art_0", "layer_art_1", "layer_art_2", "layer_art_3", "layer_art_default"]:
        src = ASSETS_DIR / f"{name}.c"
        dst = BOARD_ASSETS_DIR / f"{name}.c"
        shutil.copy2(src, dst)
    print(f"Synced C arrays to {BOARD_ASSETS_DIR}")


def main():
    ensure_dirs()
    print("Processing user-provided sprites...")
    generate_layer_faces()
    print("\nGenerating peripheral frames from flying3.jpg...")
    generate_peripheral_frames()
    print("\nConverting to LVGL C arrays...")
    convert_all()
    print("\nSyncing to board assets...")
    sync_to_board_assets()
    print("\nDone! All assets generated.")


if __name__ == "__main__":
    main()
