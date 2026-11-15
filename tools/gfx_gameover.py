"""gfx_gameover.py: big ゲームオーバー / クリアもくひょう / クリア sheet (gfx/gameover.tsv: 174AB9D, 800x3 tiles16 =
128x96, OBJ pal 1, loaded at OBJ tile 0 of scene 37).
Rows 0-31: four 32x32 cells ゲ ム オ バ (screen x 32, 74, 104, 152, each bouncing on its own; the x positions are
animated, no table in ROM) plus the 32x8 dash ー at rows 32-39 (shown 3 times). English: GAME in cell 1 (right
aligned) and OVER in cell 2 (left aligned), 2x tall / 1x wide so each word sits in one cell; cells 0, 3 and the dash
are blanked. Rows 40-67: small クリアもくひょう strip -> CLEAR GOAL. Rows 72-95: big クリア in three 32 px cells ->
CL / EA / R! (one pair per cell, so no letter straddles a cell if the cells move apart).
Ink: fill 15 (bottom rows 14), ring 13 then 11, shadow 8 (+1, +1), as the original lettering.
    python -X utf8 tools/gfx_gameover.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_winlose import ring  # noqa: E402


def mask(word, sx, sy, gap=1, bold=True):
    """Ink of `word` in the dialogue font, scaled sx by sy, top-left at 0 -> (set of (x, y), w, h)."""
    small = [[0] * 128 for _ in range(16)]
    gfx.typeset(small, [word], (0, 0, 128, 16), fill=1, outline=[], bold=bold, gap=gap)
    pts = {(x, y) for y in range(16) for x in range(128) if small[y][x]}
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    w, h = max(p[0] for p in pts) - x0 + 1, max(p[1] for p in pts) - y0 + 1
    ink = {(sx * (x - x0) + dx, sy * (y - y0) + dy) for x, y in pts for dx in range(sx) for dy in range(sy)}
    return ink, sx * w, sy * h


def letter(img, word, box, sx, sy, align="c", gap=1, rings=2):
    """Draw word in box (x0, y0, x1, y1) with 1 or 2 rings and a shadow, all inside the box."""
    ink, w, h = mask(word, sx, sy, gap)
    x0, y0, x1, y1 = box
    room = x1 - x0 - 2 * rings - 1  # rings left, rings + shadow right
    if w > room or h > y1 - y0 - 2 * rings - 1:
        raise SystemExit(f"{word!r} {w}x{h} does not fit {box}")
    ox = x0 + rings + {"l": 0, "r": room - w, "c": (room - w) // 2}[align]
    oy = y0 + rings + (y1 - y0 - 2 * rings - 1 - h) // 2
    ink = {(x + ox, y + oy) for x, y in ink}
    r1 = ring(ink)
    r2 = ring(ink | r1) if rings == 2 else set()
    for x, y in ink | r1 | r2:
        img[y + 1][x + 1] = 8
    for x, y in r2:
        img[y][x] = 8
    for x, y in r1:
        img[y][x] = 10 if rings == 2 else 8
    for x, y in ink:
        img[y][x] = 15 if (y - oy) * 3 < h else 14 if (y - oy) * 3 < 2 * h else 13


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("gameover")
    (_, off, size, layout, png), = gfx.rows("gameover")
    img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
    for row in img:
        row[:] = [0] * 128
    # cells 1 and 2 overlap by 2 px on screen: tight letters, OVER pushed right for a word gap
    letter(img, "GAME", (32, 0, 64, 32), 1, 2, "r", rings=1, gap=0)
    letter(img, "OVER", (68, 0, 96, 32), 1, 2, "l", rings=1, gap=0)
    letter(img, "CLEAR GOAL", (0, 40, 128, 68), 1, 2)
    for i, pair in enumerate(("CL", "EA", "R!")):
        letter(img, pair, (32 * i, 68, 32 * i + 32, 96), 2, 2, rings=1, gap=0)
    gfx.save_png(img, pal, gfx.ROOT / png)
    print(png)


if __name__ == "__main__":
    main()
