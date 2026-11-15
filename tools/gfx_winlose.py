"""gfx_winlose.py: big かち / まけ lettering (gfx/winlose.tsv: 1F12431, 1F12CBD, 800x2 tiles16 = 128x64) -> WIN / LOSE.
Rows 0-31: the coloured word (64x32: two 32x32 glyph cells; rainbow fill 4-9 by row, white ring 14-15 + D, transparent
0) and its silhouette (x 64-127, all index 1). Rows 32-63 (hearts / notes) are kept. The English is the dialogue
font at 2x, centred across both cells.
    python -X utf8 tools/gfx_winlose.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

WORDS = {0x1F12431: "WIN", 0x1F12CBD: "LOSE"}  # かち まけ
GRAD = [9, 9, 8, 8, 7, 7, 6, 6, 5, 5, 4, 4]  # fill by band of the inked height, top to bottom


def mask(word, W=64, H=32, s=2):
    """s-times scaled ink of the word, centred in W x H (3 px left for rings) -> set of (x, y)."""
    for bold, gap in ((True, 1), (False, 1)):
        small = [[0] * 64 for _ in range(16)]
        try:
            gfx.typeset(small, [word], (0, 0, (W - 6) // s, 16), fill=1, outline=[], bold=bold, gap=gap)
        except ValueError:
            continue
        pts = {(x, y) for y in range(16) for x in range(64) if small[y][x]}
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        ox = (W - s * (max(xs) - min(xs) + 1)) // 2 - s * min(xs)
        oy = (H - s * (max(ys) - min(ys) + 1)) // 2 - s * min(ys)
        return {(s * x + dx + ox, s * y + dy + oy) for x, y in pts for dx in range(s) for dy in range(s)}
    raise SystemExit(f"{word!r} does not fit {W} px at {s}x")


def ring(pts):
    return {(x + dx, y + dy) for x, y in pts for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - pts


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("winlose")
    for _, off, size, layout, png in gfx.rows("winlose"):
        img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
        for y in range(32):
            img[y][:] = [0] * 128
        ink = mask(WORDS[off])
        r1 = ring(ink)
        r2 = ring(ink | r1)
        r3 = ring(ink | r1 | r2)
        y0, y1 = min(p[1] for p in ink), max(p[1] for p in ink)
        for x, y in r3:
            img[y][x] = 13
        for x, y in r1 | r2:
            img[y][x] = 15
        for x, y in ink:
            img[y][x] = GRAD[(y - y0) * len(GRAD) // (y1 - y0 + 1)]
        for x, y in ink | r1 | r2 | r3:
            img[y][x + 64] = 1
        gfx.save_png(img, pal, gfx.ROOT / png)
        print(png)


if __name__ == "__main__":
    main()
