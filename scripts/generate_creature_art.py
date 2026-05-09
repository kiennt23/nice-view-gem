#!/usr/bin/env python3
"""
Generate side-view retro Game Boy style dragon for nice!view gem.

A compact baby dragon facing right, with strong silhouette,
big eye, horns, wing, tail, and clawed feet.

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


def fill_circle(draw, cx, cy, r, fill):
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                draw.point((x, y), fill=fill)


def fill_ellipse(draw, cx, cy, rx, ry, fill):
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            dx, dy = x - cx, y - cy
            if (dx * dx) / max(rx * rx, 1) + (dy * dy) / max(ry * ry, 1) <= 1.0:
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
    """Side-view baby dragon facing right."""

    # === BODY ===
    # Vertical egg shape
    fill_ellipse(draw, cx + 2, cy + 6, 12, 14, fill=0)

    # === HEAD ===
    # Big circle on upper-left of body
    fill_circle(draw, cx - 6, cy - 10, 13, fill=0)

    # === SNOOT ===
    # Small ellipse poking right from head
    fill_ellipse(draw, cx + 8, cy - 9, 7, 4, fill=0)

    # === HORNS ===
    # Main horn
    horn_pts = [(cx - 10, cy - 20), (cx - 6, cy - 28), (cx - 2, cy - 20)]
    for i in range(len(horn_pts) - 1):
        draw_line(draw, horn_pts[i][0], horn_pts[i][1],
                  horn_pts[i + 1][0], horn_pts[i + 1][1], 2, fill=0)
    # Horn tip fill
    for y in range(cy - 28, cy - 24):
        for x in range(cx - 8, cx - 4):
            draw.point((x, y), fill=0)
    # Horn ridge (white notch)
    draw_line(draw, cx - 7, cy - 24, cx - 5, cy - 24, 1, fill=1)

    # Second smaller horn
    horn_pts2 = [(cx - 4, cy - 20), (cx - 1, cy - 25), (cx + 2, cy - 19)]
    for i in range(len(horn_pts2) - 1):
        draw_line(draw, horn_pts2[i][0], horn_pts2[i][1],
                  horn_pts2[i + 1][0], horn_pts2[i + 1][1], 2, fill=0)

    # === NECK CONNECTION ===
    # Smooth blend from head to body
    for y in range(cy - 2, cy + 6):
        for x in range(cx - 6, cx + 6):
            if (x - cx) ** 2 + (y - (cy + 2)) ** 2 <= 8 * 8:
                draw.point((x, y), fill=0)

    # === WING ===
    # Triangle on back (left side)
    wing_pts = [(cx - 8, cy - 2), (cx - 20, cy - 10),
                (cx - 18, cy + 4), (cx - 8, cy + 4)]
    draw_polygon(draw, wing_pts, fill=0)
    # Wing bone line (white)
    draw_line(draw, cx - 14, cy - 6, cx - 12, cy + 2, 1, fill=1)
    draw_line(draw, cx - 16, cy - 4, cx - 14, cy + 2, 1, fill=1)

    # === TAIL ===
    # Curving up and left from body
    for t in range(22):
        tx = cx - 10 - t
        ty = cy + 12 - int((t / 3.5) ** 1.6)
        draw.point((tx, ty), fill=0)
        draw.point((tx, ty + 1), fill=0)
    # Tail spike
    for y in range(cy - 4, cy + 4):
        for x in range(cx - 34, cx - 28):
            dx, dy = x - (cx - 31), y - cy
            if dx * dx + dy * dy <= 3 * 3:
                draw.point((x, y), fill=0)
    # Spike highlight
    draw.point((cx - 32, cy - 1), fill=1)

    # === LEGS ===
    # Front leg
    fill_ellipse(draw, cx + 5, cy + 18, 3, 5, fill=0)
    # Back leg
    fill_ellipse(draw, cx - 5, cy + 18, 3, 5, fill=0)
    # Claws (white tips)
    for lx in [cx + 2, cx + 5, cx + 8]:
        draw.point((lx, cy + 23), fill=1)
    for lx in [cx - 8, cx - 5, cx - 2]:
        draw.point((lx, cy + 23), fill=1)

    # === NOSTRIL ===
    draw.point((cx + 14, cy - 10), fill=1)


def draw_dragon_face(draw, expression, cx, cy):
    """Expression details layered on the side-view dragon."""
    eye_cx, eye_cy = cx + 1, cy - 11

    if expression == "neutral":
        # Big calm eye (white sclera)
        fill_circle(draw, eye_cx, eye_cy, 6, fill=1)
        # Round pupil
        fill_circle(draw, eye_cx + 2, eye_cy, 3, fill=0)
        # Highlight
        fill_circle(draw, eye_cx, eye_cy - 3, 2, fill=1)
        # Small smile
        for t in range(4):
            draw.point((cx + 8 + t, cy - 5 + t // 2), fill=1)

    elif expression == "alert":
        # Eye with glasses
        fill_circle(draw, eye_cx, eye_cy, 5, fill=1)
        # Slit pupil
        draw_line(draw, eye_cx - 2, eye_cy, eye_cx + 4, eye_cy, 2, fill=0)
        # Highlight
        draw.point((eye_cx - 1, eye_cy - 3), fill=1)
        # Glasses frame
        fill_circle(draw, eye_cx, eye_cy, 7, fill=0)
        fill_circle(draw, eye_cx, eye_cy, 5, fill=1)
        # Temple arm
        draw_line(draw, eye_cx - 8, eye_cy, eye_cx - 6, eye_cy, 1, fill=0)
        # Serious mouth
        draw_line(draw, cx + 6, cy - 5, cx + 12, cy - 5, 2, fill=1)

    elif expression == "surprised":
        # Wide eye
        fill_circle(draw, eye_cx, eye_cy - 1, 7, fill=1)
        # Tiny pupil
        fill_circle(draw, eye_cx + 2, eye_cy, 2, fill=0)
        # Big highlight
        fill_circle(draw, eye_cx - 2, eye_cy - 4, 2, fill=1)
        # Raised eyebrow (black line above eye)
        draw_line(draw, cx - 4, cy - 20, cx + 6, cy - 22, 2, fill=0)
        # Open mouth (small O)
        fill_circle(draw, cx + 10, cy - 4, 3, fill=1)
        fill_circle(draw, cx + 10, cy - 4, 1, fill=0)

    elif expression == "fierce":
        # Angry eye (angled top)
        for y in range(eye_cy - 6, eye_cy + 3):
            for x in range(eye_cx - 5, eye_cx + 6):
                dx, dy = x - eye_cx, y - eye_cy
                top_limit = -4 + abs(dx) // 2
                if dy >= top_limit and dx * dx + dy * dy <= 20:
                    draw.point((x, y), fill=1)
        # Small angry pupil
        fill_circle(draw, eye_cx + 2, eye_cy + 1, 2, fill=0)
        # Fangs / open mouth
        pts = [(cx + 8, cy - 3), (cx + 10, cy + 1), (cx + 12, cy - 3)]
        for i in range(len(pts) - 1):
            draw_line(draw, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 2, fill=1)
        # Smoke from nostril
        draw_line(draw, cx + 14, cy - 10, cx + 18, cy - 14, 1, fill=0)
        draw_line(draw, cx + 17, cy - 13, cx + 20, cy - 16, 1, fill=0)

    elif expression == "sleepy":
        # Closed eye (white curved line)
        for t in range(-6, 7):
            y_off = abs(t) // 4
            draw.point((eye_cx + t, eye_cy + y_off), fill=1)
            draw.point((eye_cx + t, eye_cy + y_off - 1), fill=1)
        # Peaceful mouth
        for t in range(-2, 3):
            y_off = (t * t) // 4
            draw.point((cx + 9 + t, cy - 5 + y_off), fill=1)
        # Little "Z" above head
        zx, zy = cx + 12, cy - 24
        draw_line(draw, zx, zy, zx + 4, zy, 1, fill=0)
        draw_line(draw, zx + 4, zy, zx, zy - 4, 1, fill=0)
        draw_line(draw, zx, zy - 4, zx + 4, zy - 4, 1, fill=0)


def draw_creature_face(draw, expression, size=68):
    """Draw side-view dragon centered on canvas."""
    cx, cy = size // 2 - 4, size // 2 + 2
    draw_dragon_body(draw, cx, cy)
    draw_dragon_face(draw, expression, cx, cy)


def draw_peripheral_dragon(draw, frame, width=69, height=68):
    """Small flying dragon for peripheral animation."""
    bob = [0, -2, -4, -2, 0, 1][frame]
    cx, cy = width // 2 - 4, height // 2 + 6 + bob

    # Body
    fill_ellipse(draw, cx + 2, cy + 4, 10, 10, fill=0)
    # Head
    fill_circle(draw, cx - 4, cy - 6, 9, fill=0)
    # Snout
    fill_ellipse(draw, cx + 6, cy - 5, 5, 3, fill=0)
    # Horn
    horn_pts = [(cx - 8, cy - 14), (cx - 5, cy - 20), (cx - 2, cy - 14)]
    for i in range(len(horn_pts) - 1):
        draw_line(draw, horn_pts[i][0], horn_pts[i][1],
                  horn_pts[i + 1][0], horn_pts[i + 1][1], 2, fill=0)

    # Animated wing (flapping)
    wing_y_offsets = [-8, -4, 0, -2, -6, -4]
    wy = wing_y_offsets[frame]
    wing_pts = [(cx - 6, cy), (cx - 18, cy + wy - 4),
                (cx - 16, cy + wy + 6), (cx - 6, cy + 4)]
    draw_polygon(draw, wing_pts, fill=0)
    # Wing bone
    draw_line(draw, cx - 12, cy + wy, cx - 10, cy + 2, 1, fill=1)

    # Tail (wagging)
    tail_wave = [0, 1, 2, 1, 0, -1][frame]
    for t in range(14):
        tx = cx - 8 - t
        ty = cy + 10 - int((t / 3) ** 1.5) + tail_wave
        draw.point((tx, ty), fill=0)
        draw.point((tx, ty + 1), fill=0)

    # Eye
    fill_circle(draw, cx + 1, cy - 7, 4, fill=1)
    fill_circle(draw, cx + 2, cy - 7, 2, fill=0)
    fill_circle(draw, cx, cy - 9, 1, fill=1)

    # Smile
    for t in range(3):
        draw.point((cx + 6 + t, cy - 2), fill=1)

    # Fire puff (frames 1, 2, 4)
    if frame in (1, 2, 4):
        fx, fy = cx + 10, cy - 2 + frame
        fill_circle(draw, fx, fy, 2, fill=0)
        draw.point((fx + 2, fy + 1), fill=0)

    # Sparkles
    sparkle_sets = [
        [(14, 12), (54, 16), (32, 8)],
        [(16, 10), (52, 18), (30, 6)],
        [(12, 14), (56, 14), (34, 10)],
        [(14, 12), (54, 16), (32, 8)],
        [(18, 10), (50, 20), (28, 12)],
        [(14, 14), (54, 14), (32, 8)],
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
    print("Generating side-view dragon artwork...")
    generate_layer_faces()
    generate_peripheral_frames()
    print("\nConverting to LVGL C arrays...")
    convert_all()
    print("\nDone! All assets generated.")


if __name__ == "__main__":
    main()
