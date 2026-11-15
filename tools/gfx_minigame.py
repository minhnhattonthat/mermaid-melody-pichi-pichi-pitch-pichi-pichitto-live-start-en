"""gfx_minigame.py: minigame title panels (room -> a game object -> title page; left/right cycles four games).
gfx/minipanel.tsv 1C00CFF (pages 1 and 2) / 1C00403 (page 3) / 1C01554 (page 4): BG1 pal 10 panel, map per page
  (dumps work/qa/ppu/minititle, minititle3, minititle4). Line 1 (two rows of white 1 ringed E on a checker) says
  what you win; line 2 (white 1 ringed purple A, after the coin icon) says it costs 100 coins. The checker under the
  erased text is rebuilt per row by majority vote over each x mod 8 phase (background indices only).
    python -X utf8 tools/gfx_minigame.py
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_bg import Layer  # noqa: E402

PANELS = {0x1C00CFF: ("minititle", ["You can win", "Pitch Coins!"]),
          0x1C00403: ("minititle3", ["You can win", "posters and cards!"]),
          0x1C01554: ("minititle4", ["You can win", "mascots!"])}
COST = "Uses 100 coins!"
RECT = (2, 1, 19, 6)
BG = {2, 3, 4, 5, 9}  # checker colours
COIN_END = 30  # line 2 keeps the coin icon left of this column
SPLIT = 26  # first row of line 2


def checker(im, rows, cols):
    """rebuild the 4+4 px checker of each row from the background pixels the text left."""
    for y in rows:
        votes = [Counter() for _ in range(8)]
        for x in cols:
            if im[y][x] in BG:
                votes[x % 8][im[y][x]] += 1
        yield y, [v.most_common(1)[0][0] for v in votes]


def panel(img, data, layout, scene, lines):
    L = Layer(scene, 1)
    im = L.compose(RECT)
    rows = [y for y in range(len(im)) if im[y][6] == 9 and im[y][8] in BG]
    x1 = 8
    while im[rows[0]][x1] in BG - {9}:  # 9 is also the border's middle line
        x1 += 1
    y0, y1, x0 = rows[0], rows[-1] + 1, 8
    pat = dict(checker(im, range(y0, y1), [x for x in range(x0, x1) if x >= COIN_END]))
    for y in range(y0, y1):
        for x in range(x0 if y < SPLIT else COIN_END, x1):
            im[y][x] = pat[y][x % 8]
    gfx.typeset(im, lines, (x0, y0, x1, SPLIT), 1, [14])
    gfx.typeset(im, [COST], (COIN_END, SPLIT, x1, y1), 1, [10], bold=False)
    L.write(img, data, RECT, im, layout)


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    for _, off, size, layout, png in gfx.rows("minipanel"):
        data = gfx.decode(rom, off, size)[0]
        img = gfx.to_image(data, layout)
        panel(img, data, layout, *PANELS[off])
        gfx.save_png(img, gfx.load_pal("minipanel"), gfx.ROOT / png)
        print(png)


if __name__ == "__main__":
    main()
