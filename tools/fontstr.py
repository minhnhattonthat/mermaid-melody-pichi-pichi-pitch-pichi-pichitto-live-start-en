"""fontstr.py: draw a run of glyph indices with the 12x12 font, to read candidate text by eye.

    python -X utf8 tools/fontstr.py ROM OUT.png OFFSET COUNT [--u8 | --u16] [--per 32]
"""
import argparse
import struct

from PIL import Image, ImageDraw

from font12 import BASE, glyph


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("out")
    ap.add_argument("off")
    ap.add_argument("count", type=int)
    ap.add_argument("--u8", action="store_true")
    ap.add_argument("--per", type=int, default=32)
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    off = int(a.off, 16)
    step = 1 if a.u8 else 2
    vals = [rom[off + k] if a.u8 else struct.unpack_from("<H", rom, off + 2 * k)[0] for k in range(a.count)]
    rows = (len(vals) + a.per - 1) // a.per
    img = Image.new("L", (60 + a.per * 13, rows * 14), 255)
    d = ImageDraw.Draw(img)
    for k, v in enumerate(vals):
        x, y = 60 + (k % a.per) * 13, (k // a.per) * 14
        if k % a.per == 0:
            d.text((0, y), f"{off + k * step:07X}", fill=0)
        if v < 1116:
            for yy, row in enumerate(glyph(rom, BASE, v)):
                for xx, p in enumerate(row):
                    if p:
                        img.putpixel((x + xx, y + yy), 255 - 85 * p)
        else:
            d.rectangle((x, y, x + 11, y + 11), outline=128)
    img.resize((img.width * 2, img.height * 2), Image.NEAREST).save(a.out)


if __name__ == "__main__":
    main()
