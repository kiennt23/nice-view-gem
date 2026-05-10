#!/usr/bin/env python3
"""
Generate dragon pixel art based on user-provided inspiration image.

Uses the 68x68 pixel art dragon as a base, with minimal expression overlays.
Neutral uses the inspiration as-is. Other expressions add small overlays.

Outputs:
- assets/peripheral_art/  (6 animation frames, 69x68)
- assets/layer_art/       (5 face images, 68x68)
"""

import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"
INSPIRATION = PROJECT_DIR / "bOqi27WXAid9iP1f6iJw--0--1kZfg.jpg"


def ensure_dirs():
    (ASSETS_DIR / "peripheral_art").mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "layer_art").mkdir(parents=True, exist_ok=True)


def new_image(w, h):
    return Image.new("1", (w, h), 1)


def load_base_dragon():
    """Load and clean the inspiration dragon to 68x68 line art."""
    import numpy as np

    img = Image.open(INSPIRATION).convert("L")
    arr = np.array(img)

    # Crop to center
    h, w = arr.shape
    crop_top = int(h * 0.08)
    crop_bottom = int(h * 0.92)
    crop_left = int(w * 0.05)
    crop_right = int(w * 0.95)
    cropped = arr[crop_top:crop_bottom, crop_left:crop_right]

    # Find tight bbox of dark pixels
    mask = cropped < 180
    ys, xs = np.where(mask)
    left, top = xs.min(), ys.min()
    right, bottom = xs.max(), ys.max()
    dragon = cropped[top:bottom, left:right]

    # Downscale to 68x68
    pil_dragon = Image.fromarray(dragon)
    scaled = pil_dragon.resize((68, 68), Image.NEAREST)
    sarr = np.array(scaled)

    # Threshold: keep only dark pixels (black outlines)
    bw = (sarr < 80).astype(np.uint8)

    # Remove isolated noise pixels
    for y in range(1, 67):
        for x in range(1, 67):
            if bw[y, x] == 1:
                neighbors = bw[y - 1 : y + 2, x - 1 : x + 2].sum() - 1
                if neighbors < 2:
                    bw[y, x] = 0

    return Image.fromarray((1 - bw) * 255).convert("1")


def fill_circle(draw, cx, cy, r, fill):
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                draw.point((x, y), fill=fill)


def draw_line(draw, x1, y1, x2, y2, width, fill):
    dx, dy = x2 - x1, y2 - y1
    steps = int(max(abs(dx), abs(dy)) * 2) + 1
    for i in range(steps):
        t = i / steps
        px, py = x1 + dx * t, y1 + dy * t
        for wy in range(-width // 2, width // 2 + 1):
            for wx in range(-width // 2, width // 2 + 1):
                draw.point((int(px + wx), int(py + wy)), fill=fill)


def create_expression(base, expression):
    """Create an expression variant from the base dragon."""
    img = base.copy()
    draw = ImageDraw.Draw(img)

    if expression == "neutral":
        # Use inspiration as-is
        pass

    elif expression == "alert":
        # Glasses — thin outline circles at exact eye centers
        # Left eye center ~ (23, 26)
        for y in range(20, 33):
            for x in range(17, 30):
                dx, dy = x - 23, y - 26
                d = dx * dx + dy * dy
                if 12 <= d <= 20:
                    draw.point((x, y), fill=0)
        # Right eye center ~ (41, 27)
        for y in range(21, 34):
            for x in range(35, 48):
                dx, dy = x - 41, y - 27
                d = dx * dx + dy * dy
                if 12 <= d <= 20:
                    draw.point((x, y), fill=0)
        # Bridge
        draw_line(draw, 28, 26, 36, 27, 1, fill=0)
        # Serious mouth — small flat line over the smile center only
        for x in range(34, 46):
            for y in range(38, 42):
                draw.point((x, y), fill=1)
        draw_line(draw, 34, 40, 46, 40, 2, fill=0)

    elif expression == "surprised":
        # Raised eyebrows
        draw_line(draw, 14, 18, 26, 14, 2, fill=0)
        draw_line(draw, 34, 14, 46, 18, 2, fill=0)
        # Open mouth (small O, draw over smile)
        for x in range(34, 44):
            for y in range(36, 46):
                draw.point((x, y), fill=1)
        fill_circle(draw, 39, 41, 3, fill=0)
        fill_circle(draw, 39, 41, 1, fill=1)

    elif expression == "fierce":
        # Angry eyebrows (angled down, thick)
        for dx in range(-10, 3):
            y_base = 20 + abs(dx + 4) // 2
            draw.point((16 + dx, y_base), fill=0)
            draw.point((16 + dx, y_base + 1), fill=0)
        for dx in range(-2, 11):
            y_base = 20 + abs(dx - 4) // 2
            draw.point((38 + dx, y_base), fill=0)
            draw.point((38 + dx, y_base + 1), fill=0)
        # Fangs mouth (draw over smile)
        for x in range(30, 48):
            for y in range(36, 46):
                draw.point((x, y), fill=1)
        pts = [(32, 38), (35, 44), (38, 38), (41, 44), (44, 38)]
        for i in range(len(pts) - 1):
            draw_line(draw, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 2, fill=0)

    elif expression == "sleepy":
        # Closed eyes (curved white lines drawn over original eyes)
        # Left eye
        for t in range(-6, 7):
            y_off = abs(t) // 3
            draw.point((22 + t, 29 + y_off), fill=1)
            draw.point((22 + t, 28 + y_off), fill=1)
        # Right eye
        for t in range(-6, 7):
            y_off = abs(t) // 3
            draw.point((40 + t, 29 + y_off), fill=1)
            draw.point((40 + t, 28 + y_off), fill=1)
        # Zzz
        zx, zy = 48, 12
        draw_line(draw, zx, zy, zx + 4, zy, 1, fill=0)
        draw_line(draw, zx + 4, zy, zx, zy - 4, 1, fill=0)
        draw_line(draw, zx, zy - 4, zx + 4, zy - 4, 1, fill=0)
        # Smaller Z
        draw_line(draw, zx + 6, zy - 6, zx + 9, zy - 6, 1, fill=0)
        draw_line(draw, zx + 9, zy - 6, zx + 6, zy - 9, 1, fill=0)
        draw_line(draw, zx + 6, zy - 9, zx + 9, zy - 9, 1, fill=0)

    return img


def draw_peripheral_dragon(draw, frame, width=69, height=68):
    """Small simplified flying dragon for peripheral animation."""
    bob = [0, -2, -3, -2, 0, 1][frame]
    cx, cy = width // 2, height // 2 + 6 + bob

    # Head
    fill_circle(draw, cx, cy - 6, 10, fill=0)
    # Snout
    fill_circle(draw, cx + 8, cy - 4, 5, fill=0)
    # Horns
    draw_line(draw, cx - 6, cy - 14, cx - 10, cy - 20, 2, fill=0)
    draw_line(draw, cx + 4, cy - 14, cx + 8, cy - 20, 2, fill=0)
    # Frills
    frills = [(cx - 10, cy - 8), (cx - 12, cy - 4), (cx - 10, cy)]
    for i in range(len(frills) - 1):
        draw_line(draw, frills[i][0], frills[i][1], frills[i + 1][0], frills[i + 1][1], 2, fill=0)

    # Body
    fill_circle(draw, cx + 1, cy + 6, 9, fill=0)

    # Belly scales
    for bx in range(cx - 4, cx + 6, 4):
        for by in range(cy + 4, cy + 12, 4):
            draw.point((bx, by), fill=1)

    # Wings (animated)
    wing_y = [-6, -3, 0, -2, -5, -3][frame]
    wing_l = [(cx - 6, cy), (cx - 16, cy + wing_y - 2), (cx - 14, cy + wing_y + 5), (cx - 6, cy + 3)]
    for i in range(len(wing_l) - 1):
        draw_line(draw, wing_l[i][0], wing_l[i][1], wing_l[i + 1][0], wing_l[i + 1][1], 2, fill=0)
    wing_r = [(cx + 6, cy), (cx + 16, cy + wing_y - 2), (cx + 14, cy + wing_y + 5), (cx + 6, cy + 3)]
    for i in range(len(wing_r) - 1):
        draw_line(draw, wing_r[i][0], wing_r[i][1], wing_r[i + 1][0], wing_r[i + 1][1], 2, fill=0)

    # Tail
    tail_wave = [0, 1, 2, 1, 0, -1][frame]
    tail_pts = [(cx + 7, cy + 10), (cx + 14, cy + 14 + tail_wave), (cx + 12, cy + 20)]
    for i in range(len(tail_pts) - 1):
        draw_line(draw, tail_pts[i][0], tail_pts[i][1], tail_pts[i + 1][0], tail_pts[i + 1][1], 2, fill=0)

    # Legs
    fill_circle(draw, cx - 3, cy + 12, 3, fill=0)
    fill_circle(draw, cx + 5, cy + 12, 3, fill=0)

    # Eye
    fill_circle(draw, cx - 1, cy - 7, 4, fill=1)
    fill_circle(draw, cx, cy - 7, 1, fill=0)
    fill_circle(draw, cx - 3, cy - 9, 1, fill=1)

    # Smile
    for t in range(-2, 3):
        y_off = (t * t) // 4
        draw.point((cx + 7 + t, cy - 2 + y_off), fill=1)

    # Fire puffs
    if frame in (1, 2, 4):
        fx, fy = cx + 12, cy - 2 + frame
        fill_circle(draw, fx, fy, 2, fill=0)
        draw.point((fx + 2, fy + 1), fill=0)

    # Sparkles
    sparkles = [
        [(12, 10), (56, 16), (32, 6)],
        [(14, 8), (54, 18), (30, 4)],
        [(10, 12), (58, 14), (34, 8)],
        [(12, 10), (56, 16), (32, 6)],
        [(16, 8), (52, 20), (28, 10)],
        [(12, 12), (56, 14), (32, 6)],
    ]
    for sx, sy in sparkles[frame]:
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw.point((sx + dx, sy + dy), fill=0)


def generate_layer_faces(base):
    expressions = {
        "layer_art_0": "neutral",
        "layer_art_1": "alert",
        "layer_art_2": "surprised",
        "layer_art_3": "fierce",
        "layer_art_default": "sleepy",
    }
    for name, expr in expressions.items():
        img = create_expression(base, expr)
        png_path = ASSETS_DIR / "layer_art" / f"{name}.png"
        img.save(png_path)
        print(f"Generated {png_path}")


def generate_peripheral_frames():
    for i in range(6):
        img = new_image(69, 68)
        draw = ImageDraw.Draw(img)
        draw_peripheral_dragon(draw, i, width=69, height=68)
        png_path = ASSETS_DIR / "peripheral_art" / f"peripheral_art_{i:02d}.png"
        img.save(png_path)
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
    print("Loading base dragon from inspiration...")
    base = load_base_dragon()
    base.save(ASSETS_DIR / "layer_art" / "base_dragon.png")
    print(f"Base dragon saved to {ASSETS_DIR / 'layer_art' / 'base_dragon.png'}")

    print("\nGenerating expression variants...")
    generate_layer_faces(base)

    print("\nGenerating peripheral frames...")
    generate_peripheral_frames()

    print("\nConverting to LVGL C arrays...")
    convert_all()
    print("\nDone! All assets generated.")


if __name__ == "__main__":
    main()
