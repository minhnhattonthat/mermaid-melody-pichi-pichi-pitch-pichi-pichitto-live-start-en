"""gfx_draw.py: big ひきわけ of the draw screen (scene 42; gfx/draw.tsv: 1F1345A, 800x2 tiles16 = 128x64) -> DRAW.
Rows 0-31: four 32x32 cells, one kana each, shown as separate bouncing sprites, so one letter per cell: the dialogue
font at 3x, violet fill 7 (top rows 9), white ring 15 (2 px), drop shadow 11 (+2,+2). Rows 32-63 (stars) are kept.
    python -X utf8 tools/gfx_draw.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_winlose import mask, ring  # noqa: E402

WORD = "DRAW"  # ひきわけ


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("draw")
    (_, off, size, layout, png), = gfx.rows("draw")
    img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
    for y in range(32):
        img[y][:] = [0] * 128
    for i, ch in enumerate(WORD):
        ink = {(x + 32 * i, y) for x, y in mask(ch, 30, 30, 3)}
        r1 = ring(ink)
        r2 = ring(ink | r1)
        y0 = min(p[1] for p in ink)
        for x, y in ink | r1 | r2:
            if (x + 2 - 32 * i) < 32 and y + 2 < 32:
                img[y + 2][x + 2] = 11
        for x, y in r1 | r2:
            img[y][x] = 15
        for x, y in ink:
            img[y][x] = 9 if y - y0 < 3 else 7
        gfx.save_png(img, pal, gfx.ROOT / png)
    print(png)


if __name__ == "__main__":
    main()
