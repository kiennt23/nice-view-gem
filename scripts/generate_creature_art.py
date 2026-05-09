#!/usr/bin/env python3
"""
Generate retro Game Boy style dragon pixel art for nice!view gem.

A compact, detailed dragon with scales, wings, horns, and claws.
Clean 1-bit style inspired by classic GB sprites (Pokemon, Kirby).

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


def stroke_circle(draw, cx, cy, r, fill):
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d = dist_sq(x, y, cx, cy)
            if r * r - r <= d <= r * r + r:
                draw.point((x, y), fill=fill)


def fill_ellipse(draw, cx, cy, rx, ry, fill):
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            dx, dy = x - cx, y - cy
            if (dx * dx) / max(rx * rx, 1) + (dy * dy) / max(ry * ry, 1) <= 1.0:
                draw.point((x, y), fill=fill)


def stroke_ellipse(draw, cx, cy, rx, ry, width, fill):
    for y in range(cy - ry - width - 1, cy + ry + width + 2):
        for x in range(cx - rx - width - 1, cx + rx + width + 2):
            dx, dy = x - cx, y - cy
            d = (dx * dx) / max(rx * rx, 1) + (dy * dy) / max(ry * ry, 1)
            if 0.88 <= d <= 1.12:
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


def draw_polygon(draw, points, fill):
    """Fill a polygon using scanline."""
    import math
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    for y in range(min_y, max_y + 1):
        intersections = []
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                if y2 != y1:
                    x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    intersections.append(x)
        intersections.sort()
        for i in range(0, len(intersections) - 1, 2):
            for x in range(int(intersections[i]), int(intersections[i + 1]) + 1):
                draw.point((x, y), fill=fill)


def draw_dragon_body(draw, cx, cy):
    """Draw the main dragon body shape — compact with wings, tail, horns."""
    # === HEAD ===
    # Main head shape: rounded with a slight snout
    head_points = [
        (cx - 16, cy - 18),  # left cheek
        (cx - 18, cy - 8),   # left jaw
        (cx - 14, cy + 2),   # chin left
        (cx, cy + 6),        # chin center
        (cx + 14, cy + 2),   # chin right
        (cx + 18, cy - 8),   # right jaw
        (cx + 16, cy - 18),  # right cheek
        (cx + 8, cy - 24),   # forehead right
        (cx, cy - 26),       # forehead top
        (cx - 8, cy - 24),   # forehead left
    ]
    draw_polygon(draw, head_points, fill=0)

    # Snout bump
    fill_ellipse(draw, cx, cy - 2, 10, 8, fill=0)

    # === HORNS ===
    # Left horn (curved back)
    draw_line(draw, cx - 12, cy - 22, cx - 20, cy - 30, 3, fill=0)
    draw_line(draw, cx - 20, cy - 30, cx - 18, cy - 36, 2, fill=0)
    # Right horn
    draw_line(draw, cx + 12, cy - 22, cx + 20, cy - 30, 3, fill=0)
    draw_line(draw, cx + 20, cy - 30, cx + 18, cy - 36, 2, fill=0)
    # Horn ridges (white notches)
    draw_line(draw, cx - 18, cy - 28, cx - 16, cy - 28, 1, fill=1)
    draw_line(draw, cx - 17, cy - 32, cx - 15, cy - 32, 1, fill=1)
    draw_line(draw, cx + 16, cy - 28, cx + 18, cy - 28, 1, fill=1)
    draw_line(draw, cx + 15, cy - 32, cx + 17, cy - 32, 1, fill=1)

    # === EARS ===
    # Small pointed ears behind horns
    ear_left = [(cx - 14, cy - 18), (cx - 22, cy - 22), (cx - 16, cy - 14)]
    ear_right = [(cx + 14, cy - 18), (cx + 22, cy - 22), (cx + 16, cy - 14)]
    draw_polygon(draw, ear_left, fill=0)
    draw_polygon(draw, ear_right, fill=0)
    # Ear inner (white)
    draw_line(draw, cx - 18, cy - 19, cx - 17, cy - 17, 1, fill=1)
    draw_line(draw, cx + 17, cy - 17, cx + 18, cy - 19, 1, fill=1)

    # === BODY ===
    # Compact body below head
    body_points = [
        (cx - 14, cy + 4),
        (cx - 18, cy + 14),
        (cx - 12, cy + 26),
        (cx, cy + 30),
        (cx + 12, cy + 26),
        (cx + 18, cy + 14),
        (cx + 14, cy + 4),
    ]
    draw_polygon(draw, body_points, fill=0)

    # Belly plates (white scales on chest)
    for i, bx in enumerate(range(cx - 8, cx + 9, 4)):
        by = cy + 12 + i * 3
        for dx in range(-2, 3):
            for dy in range(-1, 2):
                if abs(dx) + abs(dy) <= 2:
                    draw.point((bx + dx, by + dy), fill=1)

    # === WINGS (folded on back) ===
    # Left wing
    wing_l = [
        (cx - 10, cy + 2),
        (cx - 26, cy - 6),
        (cx - 28, cy + 4),
        (cx - 24, cy + 14),
        (cx - 16, cy + 16),
        (cx - 12, cy + 10),
    ]
    draw_polygon(draw, wing_l, fill=0)
    # Wing membrane lines (white)
    draw_line(draw, cx - 18, cy + 2, cx - 22, cy + 2, 1, fill=1)
    draw_line(draw, cx - 16, cy + 8, cx - 20, cy + 8, 1, fill=1)

    # Right wing
    wing_r = [
        (cx + 10, cy + 2),
        (cx + 26, cy - 6),
        (cx + 28, cy + 4),
        (cx + 24, cy + 14),
        (cx + 16, cy + 16),
        (cx + 12, cy + 10),
    ]
    draw_polygon(draw, wing_r, fill=0)
    draw_line(draw, cx + 18, cy + 2, cx + 22, cy + 2, 1, fill=1)
    draw_line(draw, cx + 16, cy + 8, cx + 20, cy + 8, 1, fill=1)

    # === TAIL ===
    # Curling tail behind body
    tail_points = [
        (cx - 8, cy + 24),
        (cx - 18, cy + 28),
        (cx - 22, cy + 22),
        (cx - 18, cy + 16),
        (cx - 12, cy + 18),
    ]
    for i in range(len(tail_points) - 1):
        draw_line(draw, tail_points[i][0], tail_points[i][1],
                  tail_points[i + 1][0], tail_points[i + 1][1], 3, fill=0)
    # Tail spike (white tip)
    fill_circle(draw, cx - 20, cy + 22, 2, fill=1)

    # === LEGS / CLAWS ===
    # Left leg
    draw_line(draw, cx - 10, cy + 26, cx - 14, cy + 32, 3, fill=0)
    draw_line(draw, cx - 14, cy + 32, cx - 18, cy + 30, 2, fill=0)
    draw_line(draw, cx - 14, cy + 32, cx - 16, cy + 34, 2, fill=0)
    draw_line(draw, cx - 14, cy + 32, cx - 12, cy + 34, 2, fill=0)
    # Right leg
    draw_line(draw, cx + 10, cy + 26, cx + 14, cy + 32, 3, fill=0)
    draw_line(draw, cx + 14, cy + 32, cx + 18, cy + 30, 2, fill=0)
    draw_line(draw, cx + 14, cy + 32, cx + 16, cy + 34, 2, fill=0)
    draw_line(draw, cx + 14, cy + 32, cx + 12, cy + 34, 2, fill=0)

    # === BACK LEGS (smaller, behind) ===
    draw_line(draw, cx - 6, cy + 24, cx - 10, cy + 30, 2, fill=0)
    draw_line(draw, cx + 6, cy + 24, cx + 10, cy + 30, 2, fill=0)

    # === SCALE TEXTURE (body detail) ===
    # Small white dots forming scale rows on the black body
    scale_positions = [
        (cx - 6, cy + 6), (cx + 2, cy + 8), (cx + 8, cy + 6),
        (cx - 8, cy + 10), (cx, cy + 12), (cx + 6, cy + 10),
        (cx - 4, cy + 16), (cx + 4, cy + 16),
        (cx - 10, cy + 18), (cx + 10, cy + 18),
    ]
    for sx, sy in scale_positions:
        draw.point((sx, sy), fill=1)

    # Nostrils
    draw.point((cx - 3, cy - 1), fill=1)
    draw.point((cx + 3, cy - 1), fill=1)


def draw_dragon_face(draw, expression, cx, cy):
    """Draw expression-specific face details on top of the dragon body."""
    eye_y = cy - 8

    if expression == "neutral":
        # Relaxed eyes (white ovals with black pupils)
        fill_ellipse(draw, cx - 10, eye_y, 7, 8, fill=1)
        fill_ellipse(draw, cx + 10, eye_y, 7, 8, fill=1)
        # Pupils
        fill_circle(draw, cx - 10, eye_y, 3, fill=0)
        fill_circle(draw, cx + 10, eye_y, 3, fill=0)
        # Highlights
        fill_circle(draw, cx - 12, eye_y - 3, 2, fill=1)
        fill_circle(draw, cx + 8, eye_y - 3, 2, fill=1)
        # Calm smile
        for t in range(-5, 6):
            y_off = (t * t) // 10
            draw.point((cx + t, cy + 4 + y_off), fill=1)
            draw.point((cx + t, cy + 3 + y_off), fill=1)

    elif expression == "alert":
        # Focused eyes (slightly narrowed)
        fill_ellipse(draw, cx - 10, eye_y, 6, 7, fill=1)
        fill_ellipse(draw, cx + 10, eye_y, 6, 7, fill=1)
        # Horizontal slit pupils
        draw_line(draw, cx - 13, eye_y, cx - 7, eye_y, 2, fill=0)
        draw_line(draw, cx + 7, eye_y, cx + 13, eye_y, 2, fill=0)
        # Tiny highlights
        draw.point((cx - 12, eye_y - 2), fill=1)
        draw.point((cx + 8, eye_y - 2), fill=1)
        # Serious mouth
        draw_line(draw, cx - 4, cy + 4, cx + 4, cy + 4, 2, fill=1)
        # Glasses frames
        stroke_ellipse(draw, cx - 10, eye_y, 9, 9, 1, fill=1)
        stroke_ellipse(draw, cx + 10, eye_y, 9, 9, 1, fill=1)
        draw_line(draw, cx - 1, eye_y, cx + 1, eye_y, 1, fill=1)

    elif expression == "surprised":
        # Wide round eyes
        fill_ellipse(draw, cx - 10, eye_y - 1, 8, 9, fill=1)
        fill_ellipse(draw, cx + 10, eye_y - 1, 8, 9, fill=1)
        # Tiny pupils
        fill_circle(draw, cx - 10, eye_y, 2, fill=0)
        fill_circle(draw, cx + 10, eye_y, 2, fill=0)
        # Big highlights
        fill_circle(draw, cx - 13, eye_y - 4, 2, fill=1)
        fill_circle(draw, cx + 7, eye_y - 4, 2, fill=1)
        # Raised eyebrows (black lines on forehead)
        draw_line(draw, cx - 16, cy - 18, cx - 8, cy - 22, 2, fill=0)
        draw_line(draw, cx + 8, cy - 22, cx + 16, cy - 18, 2, fill=0)
        # Open mouth (small O)
        fill_circle(draw, cx, cy + 6, 4, fill=1)
        fill_circle(draw, cx, cy + 6, 1, fill=0)

    elif expression == "fierce":
        # Angry angled eyes
        # Eyebrow ridges (black, angled down)
        for dx in range(-12, 2):
            y_base = cy - 16 + abs(dx + 6) // 3
            draw.point((cx - 12 + dx, y_base), fill=0)
            draw.point((cx - 12 + dx, y_base + 1), fill=0)
        for dx in range(-1, 13):
            y_base = cy - 16 + abs(dx - 6) // 3
            draw.point((cx + dx, y_base), fill=0)
            draw.point((cx + dx, y_base + 1), fill=0)

        # Eye whites (smaller, angled)
        for y in range(eye_y - 6, eye_y + 4):
            for x in range(cx - 18, cx - 2):
                dx, dy = x - (cx - 10), y - eye_y
                top_limit = -4 + abs(dx) // 2
                if dy >= top_limit and dx * dx + dy * dy <= 30:
                    draw.point((x, y), fill=1)
            for x in range(cx + 2, cx + 18):
                dx, dy = x - (cx + 10), y - eye_y
                top_limit = -4 + abs(dx) // 2
                if dy >= top_limit and dx * dx + dy * dy <= 30:
                    draw.point((x, y), fill=1)

        # Small angry pupils
        fill_circle(draw, cx - 10, eye_y + 1, 2, fill=0)
        fill_circle(draw, cx + 10, eye_y + 1, 2, fill=0)
        # Fangs / sharp mouth
        pts = [(cx - 6, cy + 2), (cx - 3, cy + 8), (cx, cy + 2),
               (cx + 3, cy + 8), (cx + 6, cy + 2)]
        for i in range(len(pts) - 1):
            draw_line(draw, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 2, fill=1)
        # Smoke puff from nostrils
        draw_line(draw, cx - 6, cy - 4, cx - 10, cy - 8, 1, fill=0)
        draw_line(draw, cx + 6, cy - 4, cx + 10, cy - 8, 1, fill=0)

    elif expression == "sleepy":
        # Closed eyes (white curved lines on black head)
        for t in range(-8, 9):
            y_off = abs(t) // 4
            draw.point((cx - 10 + t, eye_y + y_off), fill=1)
            draw.point((cx - 10 + t, eye_y + y_off - 1), fill=1)
            draw.point((cx + 10 + t, eye_y + y_off), fill=1)
            draw.point((cx + 10 + t, eye_y + y_off - 1), fill=1)
        # Little breath marks
        draw_line(draw, cx - 18, cy - 14, cx - 14, cy - 18, 1, fill=0)
        draw_line(draw, cx - 16, cy - 16, cx - 12, cy - 20, 1, fill=0)
        # Tiny mouth
        for t in range(-2, 3):
            y_off = (t * t) // 4
            draw.point((cx + t, cy + 4 + y_off), fill=1)


def draw_creature_face(draw, expression, size=68):
    """Draw a retro Game Boy style dragon."""
    cx, cy = size // 2, size // 2 - 2
    draw_dragon_body(draw, cx, cy)
    draw_dragon_face(draw, expression, cx, cy)


def draw_peripheral_dragon(draw, frame, width=69, height=68):
    """Small flying dragon for peripheral animation."""
    bob = [0, -2, -3, -2, 0, 1][frame]
    cx, cy = width // 2, height // 2 + 6 + bob

    # === BODY ===
    fill_ellipse(draw, cx, cy, 14, 12, fill=0)

    # === HEAD ===
    fill_ellipse(draw, cx, cy - 10, 10, 9, fill=0)
    # Snout
    fill_ellipse(draw, cx, cy - 6, 7, 5, fill=0)

    # === HORNS ===
    draw_line(draw, cx - 6, cy - 16, cx - 12, cy - 22, 2, fill=0)
    draw_line(draw, cx + 6, cy - 16, cx + 12, cy - 22, 2, fill=0)

    # === WINGS (animated flapping) ===
    wing_phases = [
        # (wing tip x offset, wing tip y offset)
        (-18, -8), (-20, -4), (-18, 0), (-16, -2), (-18, -8), (-19, -6)
    ]
    wx, wy = wing_phases[frame]
    # Left wing
    wing_l_pts = [
        (cx - 8, cy - 4),
        (cx + wx, cy + wy),
        (cx - 6, cy + 4),
    ]
    draw_polygon(draw, wing_l_pts, fill=0)
    # Wing bone line
    draw_line(draw, cx - 8, cy - 4, cx + wx + 2, cy + wy, 1, fill=1)

    # Right wing
    wing_r_pts = [
        (cx + 8, cy - 4),
        (cx - wx, cy + wy),
        (cx + 6, cy + 4),
    ]
    draw_polygon(draw, wing_r_pts, fill=0)
    draw_line(draw, cx + 8, cy - 4, cx - wx - 2, cy + wy, 1, fill=1)

    # === TAIL ===
    tail_wave = [0, 2, 4, 2, 0, -1][frame]
    tail_pts = [
        (cx - 6, cy + 8),
        (cx - 14 + tail_wave, cy + 12),
        (cx - 10 + tail_wave, cy + 16),
    ]
    for i in range(len(tail_pts) - 1):
        draw_line(draw, tail_pts[i][0], tail_pts[i][1],
                  tail_pts[i + 1][0], tail_pts[i + 1][1], 2, fill=0)

    # === EYES ===
    eye_y = cy - 12
    fill_circle(draw, cx - 4, eye_y, 3, fill=1)
    fill_circle(draw, cx + 4, eye_y, 3, fill=1)
    fill_circle(draw, cx - 4, eye_y + 1, 1, fill=0)
    fill_circle(draw, cx + 4, eye_y + 1, 1, fill=0)
    fill_circle(draw, cx - 5, eye_y - 1, 1, fill=1)
    fill_circle(draw, cx + 3, eye_y - 1, 1, fill=1)

    # === SMILE ===
    for t in range(-3, 4):
        y_off = (t * t) // 5
        draw.point((cx + t, cy - 4 + y_off), fill=1)
        draw.point((cx + t, cy - 5 + y_off), fill=1)

    # === FIRE BREATH (every few frames) ===
    if frame in (1, 2, 4):
        # Small fire puffs below
        puff_x = cx + (4 if frame % 2 == 0 else -4)
        fill_circle(draw, puff_x, cy + 18, 2, fill=0)
        draw.point((puff_x, cy + 20), fill=0)
        draw.point((puff_x + 2, cy + 19), fill=0)

    # === SPARKLES ===
    sparkle_sets = [
        [(12, 10), (56, 14), (30, 6)],
        [(14, 8), (54, 16), (28, 4)],
        [(10, 12), (58, 12), (32, 8)],
        [(12, 10), (56, 14), (30, 6)],
        [(16, 8), (52, 18), (26, 10)],
        [(12, 12), (56, 12), (30, 6)],
    ]
    for sx, sy in sparkle_sets[frame]:
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw.point((sx + dx, sy + dy), fill=0)


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
    print("Generating Game Boy style dragon artwork...")
    generate_layer_faces()
    generate_peripheral_frames()
    print("\nConverting to LVGL C arrays...")
    convert_all()
    print("\nDone! All assets generated.")


if __name__ == "__main__":
    main()
