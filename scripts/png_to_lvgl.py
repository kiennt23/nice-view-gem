#!/usr/bin/env python3
"""
Convert monochrome PNG images to LVGL I1 format C arrays.

Usage:
    python png_to_lvgl.py <input_png> <output_c> [--name VAR_NAME]

The input PNG must be pure black & white (1-bit).
Output is a C file with an lv_img_dsc_t struct compatible with LV_COLOR_FORMAT_I1.
"""

import argparse
import pathlib
import sys

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


def png_to_lvgl(input_path: pathlib.Path, output_path: pathlib.Path, var_name: str):
    img = Image.open(input_path)

    if img.mode != "1":
        img = img.convert("1")

    width, height = img.size
    pixels = img.load()

    # LVGL I1: MSB first, each row padded to byte boundary
    row_bytes = (width + 7) // 8
    data = bytearray()

    for y in range(height):
        row_bits = 0
        bit_count = 0
        for x in range(width):
            # Pillow "1" mode: 0 = black, 255 = white
            # LVGL I1 with normal palette: 0 = white, 1 = black
            # So black pixel -> bit 1, white pixel -> bit 0
            bit = 0 if pixels[x, y] == 255 else 1
            row_bits = (row_bits << 1) | bit
            bit_count += 1
            if bit_count == 8:
                data.append(row_bits)
                row_bits = 0
                bit_count = 0
        # Pad remaining bits in the row
        if bit_count > 0:
            row_bits <<= (8 - bit_count)
            data.append(row_bits)

    data_size = len(data)

    c_code = f'''#include <lvgl.h>

#ifndef LV_ATTRIBUTE_MEM_ALIGN
#define LV_ATTRIBUTE_MEM_ALIGN
#endif

#ifndef LV_ATTRIBUTE_IMG_{var_name.upper()}
#define LV_ATTRIBUTE_IMG_{var_name.upper()}
#endif

const LV_ATTRIBUTE_MEM_ALIGN LV_ATTRIBUTE_LARGE_CONST LV_ATTRIBUTE_IMG_{var_name.upper()} uint8_t
    {var_name}_map[] = {{
#if CONFIG_NICE_VIEW_WIDGET_INVERTED
        0x00, 0x00, 0x00, 0xff, /*Color of index 0*/
        0xff, 0xff, 0xff, 0xff, /*Color of index 1*/
#else
        0xff, 0xff, 0xff, 0xff, /*Color of index 0*/
        0x00, 0x00, 0x00, 0xff, /*Color of index 1*/
#endif

'''

    # Format data as hex bytes, 12 per line
    hex_lines = []
    for i in range(0, len(data), 12):
        chunk = data[i:i+12]
        hex_vals = ", ".join(f"0x{b:02x}" for b in chunk)
        hex_lines.append(f"        {hex_vals},")
    c_code += "\n".join(hex_lines)
    c_code = c_code.rstrip(",") + "\n"

    c_code += f'''}};

const lv_img_dsc_t {var_name} = {{
    .header.cf = LV_COLOR_FORMAT_I1,
    .header.w = {width},
    .header.h = {height},
    .data_size = {data_size},
    .data = {var_name}_map,
}};
'''

    output_path.write_text(c_code)
    print(f"Generated {output_path} ({width}x{height}, {data_size} bytes)")


def main():
    parser = argparse.ArgumentParser(description="Convert PNG to LVGL I1 C array")
    parser.add_argument("input", type=pathlib.Path, help="Input PNG file")
    parser.add_argument("output", type=pathlib.Path, help="Output C file")
    parser.add_argument("--name", default=None, help="Variable name prefix (default: stem of input)")
    args = parser.parse_args()

    var_name = args.name or args.input.stem
    png_to_lvgl(args.input, args.output, var_name)


if __name__ == "__main__":
    main()
