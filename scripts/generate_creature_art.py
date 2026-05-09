#!/usr/bin/env python3
"""
Generate clean pixel-art creature for nice!view gem.

A cute round "Mochi" blob monster with solid fills, big shiny eyes,
and expressive faces. Clean 1-bit pixel art style.

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


def ensure_dirs():
    (ASSETS_DIR / "peripheral_art").mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "layer_art").mkdir(parents=True, exist_ok=True)


def new_image(w, h):
    return Image.new("1", (w, h), 1)


def dist_sq(x1, y1, x2, y2):
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


def fill_circle(draw, cx, cy, r, fill):
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            if dist_sq(x, y, cx, cy) <= r * r:
                draw.point((x, y), fill=fill)


def fill_ellipse(draw, cx, cy, rx, ry, fill):
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            dx, dy = x - cx, y - cy
            if (dx * dx) / max(rx * rx, 1) + (dy * dy) / max(ry * ry, 1) <= 1.0:
                draw.point((x, y), fill=fill)


def stroke_ellipse(draw, cx, cy, rx, ry, width, fill):
    """Draw just the outline of an ellipse."""
    for y in range(cy - ry - width - 1, cy + ry + width + 2):
        for x in range(cx - rx - width - 1, cx + rx + width + 2):
            dx, dy = x - cx, y - cy
            d = (dx * dx) / max(rx * rx, 1) + (dy * dy) / max(ry * ry, 1)
            if 0.85 <= d <= 1.15:
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


def draw_creature_face(draw, expression, size=68):
    """Draw Mochi — a cute pear-shaped blob with big eyes."""
    cx, cy = size // 2, size // 2 + 2

    # === BODY ===
    # Pear shape: wider at bottom, rounder at top
    # Upper head circle
    fill_circle(draw, cx, cy - 8, 22, fill=0)
    # Lower body (slightly wider, shorter)
    fill_ellipse(draw, cx, cy + 10, 24, 16, fill=0)
    # Smooth the connection by filling the gap
    for y in range(cy - 8, cy + 2):
        for x in range(cx - 22, cx + 23):
            if dist_sq(x, y, cx, cy - 8) <= 22 * 22 or \
               ((x - cx) ** 2) / (24 * 24) + ((y - (cy + 10)) ** 2) / (16 * 16) <= 1.0:
                draw.point((x, y), fill=0)

    # Little feet (black ovals poking out below)
    fill_ellipse(draw, cx - 14, cy + 24, 6, 4, fill=0)
    fill_ellipse(draw, cx + 14, cy + 24, 6, 4, fill=0)

    # === EYES (white sclera on black body) ===
    if expression in ("neutral", "alert", "surprised", "fierce"):
        eye_y = cy - 6
        if expression == "surprised":
            eye_y -= 2
            eye_r = 11
        elif expression == "fierce":
            eye_r = 9
        else:
            eye_r = 10

        # Left eye white (cutout in black body)
        fill_circle(draw, cx - 13, eye_y, eye_r, fill=1)
        # Right eye white
        fill_circle(draw, cx + 13, eye_y, eye_r, fill=1)

        # Eyelids for fierce/angry
        if expression == "fierce":
            # Angled eyelids (black triangles covering top of eyes)
            for y in range(eye_y - eye_r - 2, eye_y - 2):
                for x in range(cx - 22, cx - 4):
                    dx = x - (cx - 13)
                    if y < eye_y - 4 + abs(dx) // 3:
                        draw.point((x, y), fill=0)
                for x in range(cx + 4, cx + 22):
                    dx = x - (cx + 13)
                    if y < eye_y - 4 + abs(dx) // 3:
                        draw.point((x, y), fill=0)

        # Pupils
        if expression == "surprised":
            pr = 3
        elif expression == "alert":
            pr = 2
        else:
            pr = 4

        fill_circle(draw, cx - 13, eye_y + 1, pr, fill=0)
        fill_circle(draw, cx + 13, eye_y + 1, pr, fill=0)

        # Highlights (white dots in pupils)
        if expression != "alert":
            fill_circle(draw, cx - 15, eye_y - 3, 2, fill=1)
            fill_circle(draw, cx + 11, eye_y - 3, 2, fill=1)
            # Tiny secondary highlight
            draw.point((cx - 11, eye_y + 3), fill=1)
            draw.point((cx + 15, eye_y + 3), fill=1)
        else:
            # Alert: smaller highlights
            draw.point((cx - 16, eye_y - 4), fill=1)
            draw.point((cx + 10, eye_y - 4), fill=1)

    elif expression == "sleepy":
        eye_y = cy - 6
        # Closed eyes (curved black lines on white... but body is black)
        # Instead draw white arcs (sleepy eyelids)
        for t in range(-10, 11):
            y_off = abs(t) // 5
            draw.point((cx - 13 + t, eye_y + y_off), fill=1)
            draw.point((cx - 13 + t, eye_y + y_off - 1), fill=1)
            draw.point((cx + 13 + t, eye_y + y_off), fill=1)
            draw.point((cx + 13 + t, eye_y + y_off - 1), fill=1)
        # Little lashes
        draw_line(draw, cx - 20, eye_y + 2, cx - 18, eye_y + 4, 1, fill=1)
        draw_line(draw, cx + 18, eye_y + 4, cx + 20, eye_y + 2, 1, fill=1)

    # === MOUTH ===
    if expression == "neutral":
        # Small smile
        for t in range(-6, 7):
            y_off = (t * t) // 10
            draw.point((cx + t, cy + 10 + y_off), fill=1)
            draw.point((cx + t, cy + 9 + y_off), fill=1)

    elif expression == "alert":
        # Firm line
        draw_line(draw, cx - 5, cy + 10, cx + 5, cy + 10, 2, fill=1)

    elif expression == "surprised":
        # Open O
        fill_circle(draw, cx, cy + 12, 4, fill=1)
        fill_circle(draw, cx, cy + 12, 1, fill=0)

    elif expression == "fierce":
        # Fangs (W shape in white)
        pts = [(cx - 7, cy + 8), (cx - 3, cy + 14), (cx, cy + 8),
               (cx + 3, cy + 14), (cx + 7, cy + 8)]
        for i in range(len(pts) - 1):
            draw_line(draw, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 2, fill=1)

    elif expression == "sleepy":
        # Tiny mouth
        for t in range(-2, 3):
            y_off = (t * t) // 4
            draw.point((cx + t, cy + 10 + y_off), fill=1)
        # Snot bubble
        stroke_ellipse(draw, cx + 8, cy + 8, 5, 5, 1, fill=1)
        fill_circle(draw, cx + 8, cy + 8, 1, fill=1)

    # === CHEEKS ===
    if expression in ("neutral", "sleepy"):
        for bx, by in [(cx - 20, cy + 4), (cx - 19, cy + 5), (cx - 18, cy + 4),
                        (cx + 18, cy + 4), (cx + 19, cy + 5), (cx + 20, cy + 4)]:
            draw.point((bx, by), fill=1)

    # === EXTRA DETAILS ===
    if expression == "alert":
        # Glasses frames (white outlines around eyes)
        stroke_ellipse(draw, cx - 13, cy - 6, 12, 12, 1, fill=1)
        stroke_ellipse(draw, cx + 13, cy - 6, 12, 12, 1, fill=1)
        draw_line(draw, cx - 1, cy - 6, cx + 1, cy - 6, 1, fill=1)

    elif expression == "surprised":
        # Raised eyebrows (black lines above eyes)
        draw_line(draw, cx - 20, cy - 18, cx - 10, cy - 22, 2, fill=0)
        draw_line(draw, cx + 10, cy - 22, cx + 20, cy - 18, 2, fill=0)

    elif expression == "fierce":
        # Sweat drop
        fill_ellipse(draw, cx + 22, cy - 12, 3, 4, fill=0)
        draw.point((cx + 22, cy - 10), fill=1)

    elif expression == "sleepy":
        # "Zzz"
        zx, zy = cx + 22, cy - 22
        # Big Z
        draw_line(draw, zx, zy, zx + 5, zy, 1, fill=0)
        draw_line(draw, zx + 5, zy, zx, zy - 5, 1, fill=0)
        draw_line(draw, zx, zy - 5, zx + 5, zy - 5, 1, fill=0)
        # Small Z
        draw_line(draw, zx + 7, zy - 7, zx + 10, zy - 7, 1, fill=0)
        draw_line(draw, zx + 10, zy - 7, zx + 7, zy - 10, 1, fill=0)
        draw_line(draw, zx + 7, zy - 10, zx + 10, zy - 10, 1, fill=0)


def draw_peripheral_creature(draw, frame, width=69, height=68):
    """Small floating full-body creature."""
    bob = [0, -2, -4, -2, 0, 1][frame]
    cx, cy = width // 2, height // 2 + 8 + bob

    # Body
    fill_circle(draw, cx, cy, 15, fill=0)

    # Arms waving
    arm_off = [(-2, 0), (-4, -2), (-3, -3), (-2, -2), (-2, 0), (-3, 1)][frame]
    draw_line(draw, cx - 13, cy, cx - 18 + arm_off[0], cy - 5 + arm_off[1], 2, fill=0)
    draw_line(draw, cx + 13, cy, cx + 18 - arm_off[0], cy - 5 + arm_off[1], 2, fill=0)

    # Eyes (white sclera)
    eye_y = cy - 4
    fill_circle(draw, cx - 7, eye_y, 5, fill=1)
    fill_circle(draw, cx + 7, eye_y, 5, fill=1)
    # Pupils
    fill_circle(draw, cx - 7, eye_y + 1, 2, fill=0)
    fill_circle(draw, cx + 7, eye_y + 1, 2, fill=0)
    # Highlights
    fill_circle(draw, cx - 9, eye_y - 2, 1, fill=1)
    fill_circle(draw, cx + 5, eye_y - 2, 1, fill=1)

    # Smile
    for t in range(-4, 5):
        y_off = (t * t) // 6
        draw.point((cx + t, cy + 5 + y_off), fill=1)
        draw.point((cx + t, cy + 4 + y_off), fill=1)

    # Cheeks
    draw.point((cx - 12, cy + 2), fill=1)
    draw.point((cx - 11, cy + 3), fill=1)
    draw.point((cx + 11, cy + 3), fill=1)
    draw.point((cx + 12, cy + 2), fill=1)

    # Sparkles
    sparkles = [
        [(12, 14), (56, 20), (34, 10)],
        [(14, 12), (54, 22), (32, 8)],
        [(10, 16), (58, 18), (36, 12)],
        [(12, 14), (56, 20), (34, 10)],
        [(16, 10), (52, 24), (30, 14)],
        [(12, 16), (56, 18), (34, 10)],
    ]
    for sx, sy in sparkles[frame]:
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw.point((sx + dx, sy + dy), fill=0)

    # Floating dots
    for i, (dx, dy) in enumerate([(10, 28), (58, 32), (22, 48), (48, 46)]):
        if (frame + i * 2) % 3 != 0:
            draw.point((dx, dy), fill=0)


def generate_layer_faces():
    expressions = {
        "layer_art_0": "neutral",
        "layer_art_1": "alert",
        "layer_art_2": "surprised",
        "layer_art_3": "fierce",
        "layer_art_default": "sleepy",
    }
    for name, expr in expressions.items():
        img = new_image(68, 68)
        draw = ImageDraw.Draw(img)
        draw_creature_face(draw, expr, size=68)
        png_path = ASSETS_DIR / "layer_art" / f"{name}.png"
        img.save(png_path)
        print(f"Generated {png_path}")


def generate_peripheral_frames():
    for i in range(6):
        img = new_image(69, 68)
        draw = ImageDraw.Draw(img)
        draw_peripheral_creature(draw, i, width=69, height=68)
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
    print("Generating Mochi creature artwork...")
    generate_layer_faces()
    generate_peripheral_frames()
    print("\nConverting to LVGL C arrays...")
    convert_all()
    print("\nDone! All assets generated.")


if __name__ == "__main__":
    main()
