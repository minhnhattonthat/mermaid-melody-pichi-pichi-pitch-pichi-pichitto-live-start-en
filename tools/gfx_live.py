"""gfx_live.py: live-data error screen (warp `live_broken`): bubble ライブのデータがこわれているよ! on BG3.
gfx/live.tsv 1747BC1 (800x10 chain, the whole BG3 picture). The bubble's text cells use BG pals 4/5 (dark blue 1,
white 15); the cells between letters use pal 3 (no dark colour), and the map is not raw in ROM, so the English stays in
the two bands that are pal 4/5 all across: map rows 5-6 and 9-10, cells 2-15.
    python -X utf8 tools/gfx_live.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_bg import Layer  # noqa: E402

RECT = (2, 4, 14, 9)  # bubble inside, map cells 2-15 x 4-12
LINES = [("Your live data", 8), ("is broken!", 40)]  # (text, top y in RECT: map rows 5 and 9)


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    _, off, size, layout, png = next(gfx.rows("live"))
    data = gfx.decode(rom, off, size)[0]
    img = gfx.to_image(data, layout)
    L = Layer("live_broken", 3)
    x0, y0, w, h = RECT
    px = L.compose(RECT)
    for j in range(h):
        for i in range(w):
            if L.entry(x0 + i, y0 + j)[3] in (4, 5):  # text cells: blank to white
                for y in range(8):
                    px[8 * j + y][8 * i:8 * i + 8] = [15] * 8
    for text, top in LINES:
        gfx.typeset(px, [text], (0, top, 8 * w, top + 16), 1, [], bold=True)
    print(L.write(img, data, RECT, px), "tiles changed")
    gfx.save_png(img, gfx.load_pal("live"), gfx.ROOT / png)
    print(png)


if __name__ == "__main__":
    main()
