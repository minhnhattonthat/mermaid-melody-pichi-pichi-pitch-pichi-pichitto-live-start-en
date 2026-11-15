"""font_sheet.py: labelled sheet of chosen glyph indices (hex label over each cell), to read glyphs by eye.

    python -X utf8 tools/font_sheet.py ROM OUT.png CODES... [--cols 12] [--zoom 4]
    python -X utf8 tools/font_sheet.py ROM OUT.png --unmapped tbl/jp.tbl --upto 1F1

CODES are hex glyph indices or ranges (10-1F). --unmapped takes every index up to --upto that the table lacks."""
import argparse

from PIL import Image, ImageDraw

from font12 import BASE, glyph


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("out")
    ap.add_argument("codes", nargs="*")
    ap.add_argument("--unmapped")
    ap.add_argument("--upto", default="1F1")
    ap.add_argument("--cols", type=int, default=12)
    ap.add_argument("--zoom", type=int, default=4)
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    codes = []
    for c in a.codes:
        lo, _, hi = c.partition("-")
        codes += range(int(lo, 16), int(hi or lo, 16) + 1)
    if a.unmapped:
        have = {int(line.split("=")[0], 16) for line in open(a.unmapped, encoding="utf-8") if "=" in line}
        codes += [i for i in range(int(a.upto, 16) + 1) if i not in have]
    z, cw, ch = a.zoom, 16, 22
    rows = (len(codes) + a.cols - 1) // a.cols
    img = Image.new("L", (a.cols * cw * z, rows * ch * z), 255)
    d = ImageDraw.Draw(img)
    for k, i in enumerate(codes):
        x0, y0 = (k % a.cols) * cw * z, (k // a.cols) * ch * z
        d.text((x0 + 2, y0), f"{i:03X}", fill=0, font_size=7 * z // 2 + 2)
        for y, row in enumerate(glyph(rom, BASE, i)):
            for x, v in enumerate(row):
                if v:
                    d.rectangle([x0 + (2 + x) * z, y0 + (9 + y) * z, x0 + (3 + x) * z - 1, y0 + (10 + y) * z - 1],
                                fill=255 - 85 * v)
    img.save(a.out)
    print(a.out, len(codes), "glyphs")


if __name__ == "__main__":
    main()
