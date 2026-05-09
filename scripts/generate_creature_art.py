#!/usr/bin/env python3
"""
Generate creature-themed 1-bit artwork for nice!view gem.

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
    """Create a white background image."""
    img = Image.new("1", (w, h), 1)  # 1 = white in Pillow 1-bit mode
    return img


def draw_creature_face(draw: ImageDraw.Draw, expression: str, size: int = 68):
    """Draw a creature face with the given expression."""
    cx, cy = size // 2, size // 2

    # Head outline - round/oval shape
    head_top = cy - 22
    head_bottom = cy + 18
    head_left = cx - 24
    head_right = cx + 24
    draw.ellipse([head_left, head_top, head_right, head_bottom], outline=0, width=2)

    # Small ears/antennae
    draw.line([(cx - 18, head_top + 4), (cx - 26, head_top - 10)], fill=0, width=2)
    draw.line([(cx + 18, head_top + 4), (cx + 26, head_top - 10)], fill=0, width=2)
    # Ear tips (little balls)
    draw.ellipse([cx - 28, head_top - 14, cx - 24, head_top - 10], fill=0)
    draw.ellipse([cx + 24, head_top - 14, cx + 28, head_top - 10], fill=0)

    # Eyes based on expression
    eye_y = cy - 6
    eye_x_left = cx - 12
    eye_x_right = cx + 12
    eye_w, eye_h = 10, 10

    if expression == "neutral":
        # Round calm eyes
        draw.ellipse([eye_x_left - eye_w // 2, eye_y - eye_h // 2,
                      eye_x_left + eye_w // 2, eye_y + eye_h // 2], outline=0, width=2)
        draw.ellipse([eye_x_right - eye_w // 2, eye_y - eye_h // 2,
                      eye_x_right + eye_w // 2, eye_y + eye_h // 2], outline=0, width=2)
        # Small pupils
        draw.point((eye_x_left, eye_y), fill=0)
        draw.point((eye_x_right, eye_y), fill=0)
        # Small calm mouth
        draw.arc([cx - 8, cy + 4, cx + 8, cy + 12], start=0, end=180, fill=0, width=2)

    elif expression == "alert":
        # Focused/slit eyes
        draw.ellipse([eye_x_left - eye_w // 2, eye_y - eye_h // 2,
                      eye_x_left + eye_w // 2, eye_y + eye_h // 2], outline=0, width=2)
        draw.ellipse([eye_x_right - eye_w // 2, eye_y - eye_h // 2,
                      eye_x_right + eye_w // 2, eye_y + eye_h // 2], outline=0, width=2)
        # Horizontal slit pupils
        draw.line([(eye_x_left - 4, eye_y), (eye_x_left + 4, eye_y)], fill=0, width=2)
        draw.line([(eye_x_right - 4, eye_y), (eye_x_right + 4, eye_y)], fill=0, width=2)
        # Firm mouth
        draw.line([(cx - 6, cy + 10), (cx + 6, cy + 10)], fill=0, width=2)

    elif expression == "surprised":
        # Wide round eyes
        draw.ellipse([eye_x_left - eye_w // 2 - 2, eye_y - eye_h // 2 - 2,
                      eye_x_left + eye_w // 2 + 2, eye_y + eye_h // 2 + 2], outline=0, width=2)
        draw.ellipse([eye_x_right - eye_w // 2 - 2, eye_y - eye_h // 2 - 2,
                      eye_x_right + eye_w // 2 + 2, eye_y + eye_h // 2 + 2], outline=0, width=2)
        # Small pupils
        draw.point((eye_x_left, eye_y), fill=0)
        draw.point((eye_x_right, eye_y), fill=0)
        # Open mouth (small O)
        draw.ellipse([cx - 4, cy + 6, cx + 4, cy + 14], outline=0, width=2)

    elif expression == "fierce":
        # Angled angry eyes
        draw.polygon([(eye_x_left - 6, eye_y + 4), (eye_x_left + 6, eye_y - 2),
                      (eye_x_left + 4, eye_y + 4)], outline=0, fill=0)
        draw.polygon([(eye_x_right - 6, eye_y - 2), (eye_x_right + 6, eye_y + 4),
                      (eye_x_right - 4, eye_y + 4)], outline=0, fill=0)
        # Fangs / sharp mouth
        draw.line([(cx - 8, cy + 10), (cx - 4, cy + 14), (cx, cy + 10),
                   (cx + 4, cy + 14), (cx + 8, cy + 10)], fill=0, width=2)

    elif expression == "sleepy":
        # Closed eyes (curved lines)
        draw.arc([eye_x_left - 6, eye_y - 4, eye_x_left + 6, eye_y + 4], start=0, end=180, fill=0, width=2)
        draw.arc([eye_x_right - 6, eye_y - 4, eye_x_right + 6, eye_y + 4], start=0, end=180, fill=0, width=2)
        # Tiny mouth
        draw.arc([cx - 4, cy + 8, cx + 4, cy + 12], start=0, end=180, fill=0, width=1)
        # Little "zzz" above head
        draw.line([(cx + 20, head_top - 6), (cx + 24, head_top - 10)], fill=0, width=1)
        draw.line([(cx + 24, head_top - 10), (cx + 20, head_top - 10)], fill=0, width=1)
        draw.line([(cx + 20, head_top - 10), (cx + 24, head_top - 14)], fill=0, width=1)


def generate_layer_faces():
    """Generate creature face images for each layer."""
    expressions = {
        "layer_art_0": "neutral",      # base layer
        "layer_art_1": "alert",        # nav layer
        "layer_art_2": "surprised",    # sym layer
        "layer_art_3": "fierce",       # game layer
        "layer_art_default": "sleepy", # fallback
    }

    for name, expr in expressions.items():
        img = new_image(68, 68)
        draw = ImageDraw.Draw(img)
        draw_creature_face(draw, expr, size=68)
        png_path = ASSETS_DIR / "layer_art" / f"{name}.png"
        img.save(png_path)
        print(f"Generated {png_path}")


def draw_creature_tail(draw: ImageDraw.Draw, frame: int, width: int = 69, height: int = 68):
    """Draw a creature tail that waves gently."""
    # The tail is a curved line with a fluffy tip
    # It waves left and right across frames

    # Tail base (fixed point at bottom center)
    base_x = width // 2
    base_y = height - 10

    # Tail tip position varies by frame
    # Frame 0: tip left, Frame 3: tip right, Frame 6: back to left
    phases = [-12, -8, -3, 3, 8, 12]
    tip_offset = phases[frame % len(phases)]

    tip_x = base_x + tip_offset
    tip_y = 20

    # Control point for the curve (midpoint, swaying less)
    ctrl_x = base_x + tip_offset // 2
    ctrl_y = (base_y + tip_y) // 2

    # Draw tail as a thick bezier-like curve using line segments
    points = []
    steps = 12
    for t in range(steps + 1):
        t_norm = t / steps
        # Quadratic bezier
        x = int((1 - t_norm) ** 2 * base_x + 2 * (1 - t_norm) * t_norm * ctrl_x + t_norm ** 2 * tip_x)
        y = int((1 - t_norm) ** 2 * base_y + 2 * (1 - t_norm) * t_norm * ctrl_y + t_norm ** 2 * tip_y)
        points.append((x, y))

    # Draw thick tail
    for i in range(len(points) - 1):
        thickness = max(1, 4 - i // 3)
        draw.line([points[i], points[i + 1]], fill=0, width=thickness)

    # Fluffy tip (small cluster of dots/ovals)
    draw.ellipse([tip_x - 5, tip_y - 5, tip_x + 5, tip_y + 5], outline=0, width=2)
    draw.ellipse([tip_x - 3, tip_y - 3, tip_x + 3, tip_y + 3], fill=0)

    # Tiny sparkles around the tail tip
    sparkle_positions = [
        (tip_x + 8, tip_y - 4),
        (tip_x - 6, tip_y + 6),
        (tip_x + 4, tip_y + 8),
    ]
    # Only show some sparkles per frame for subtle twinkle
    for idx, (sx, sy) in enumerate(sparkle_positions):
        if (frame + idx) % 2 == 0:
            draw.point((sx, sy), fill=0)
            draw.point((sx + 1, sy), fill=0)
            draw.point((sx, sy + 1), fill=0)
            draw.point((sx + 1, sy + 1), fill=0)


def generate_peripheral_frames():
    """Generate 6 animation frames of a waving creature tail."""
    for i in range(6):
        img = new_image(69, 68)
        draw = ImageDraw.Draw(img)
        draw_creature_tail(draw, i, width=69, height=68)
        png_path = ASSETS_DIR / "peripheral_art" / f"peripheral_art_{i:02d}.png"
        img.save(png_path)
        print(f"Generated {png_path}")


def convert_all():
    """Convert all generated PNGs to LVGL C arrays."""
    converter = SCRIPT_DIR / "png_to_lvgl.py"

    # Convert peripheral frames
    for i in range(6):
        png = ASSETS_DIR / "peripheral_art" / f"peripheral_art_{i:02d}.png"
        c_out = ASSETS_DIR / f"peripheral_art_{i:02d}.c"
        subprocess.run([sys.executable, str(converter), str(png), str(c_out),
                        f"--name", f"peripheral_art_{i:02d}"], check=True)

    # Convert layer faces
    for name in ["layer_art_0", "layer_art_1", "layer_art_2", "layer_art_3", "layer_art_default"]:
        png = ASSETS_DIR / "layer_art" / f"{name}.png"
        c_out = ASSETS_DIR / f"{name}.c"
        subprocess.run([sys.executable, str(converter), str(png), str(c_out),
                        f"--name", name], check=True)


def main():
    ensure_dirs()
    print("Generating creature artwork...")
    generate_layer_faces()
    generate_peripheral_frames()
    print("\nConverting to LVGL C arrays...")
    convert_all()
    print("\nDone! All assets generated.")


if __name__ == "__main__":
    main()
