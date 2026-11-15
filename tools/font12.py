"""font12.py: render the game's 12x12 2bpp font (ROM 0x18745E0, 36 bytes per glyph, 3 bytes per row, 4 px per byte)
into a labelled sheet, glyph index in hex every 16.

    python -X utf8 tools/font12.py ROM OUT.png [--base 18745E0] [--count 1116] [--msb]

Pixel order inside a byte is a guess until the sheet reads right: default low bits = leftmost pixel; --msb flips it.
"""
import argparse
import struct

from PIL import Image, ImageDraw

BASE = 0x18745E0
CODEMAP = 0x187EA84  # u16 per text code -> glyph index (verified: code 22..26 = あいうえお)


def glyph(rom, base, i, msb=False):
    g = rom[base + 36 * i: base + 36 * i + 36]
    px = []
    for y in range(12):
        row = []
        for b in g[3 * y:3 * y + 3]:
            vals = [(b >> (2 * k)) & 3 for k in range(4)]
            row += vals[::-1] if msb else vals
        px.append(row)
    return px


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("out")
    ap.add_argument("--base", default=f"{BASE:X}")
    ap.add_argument("--count", type=int, default=1116)
    ap.add_argument("--msb", action="store_true")
    ap.add_argument("--zoom", type=int, default=2)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--codes", action="store_true", help="index = text code, drawn through the code->glyph table")
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    base = int(a.base, 16)
    cols, cw = 16, 14
    rows = (a.count + cols - 1) // cols
    img = Image.new("L", (40 + cols * cw, rows * cw), 255)
    d = ImageDraw.Draw(img)
    for i in range(a.start, a.start + a.count):
        k = i - a.start
        gx, gy = 40 + (k % cols) * cw, (k // cols) * cw
        if k % cols == 0:
            d.text((0, gy), f"{i:03X}", fill=0)
        g = struct.unpack_from("<H", rom, CODEMAP + 2 * i)[0] if a.codes else i
        for y, row in enumerate(glyph(rom, base, g, a.msb)):
            for x, v in enumerate(row):
                if v:
                    img.putpixel((gx + x, gy + y), 255 - 85 * v)
    img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST).save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
