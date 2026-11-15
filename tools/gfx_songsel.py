"""gfx_songsel.py: song-select high-score panel labels and difficulty pills.
gfx/songsel.tsv 173F4E9 (800x1 tiles16 128x32, OBJ pal 3 of song_select): かんたん (96,0)-(128,8), ふつう (96,8)-(128,16),
  むずかしい (88,24)-(128,32), each one row of 8 px OBJs at screen x 4 -> Easy / Normal / Hard (D14), dark ink 6 on the
  panel green, plain (not bold) font, cap top on the row's first line ('y' tail clipped to one row).
gfx/pills.tsv 173FE48 (800x2 tiles16 128x64, OBJ pal 8 of live_list): six 16x8 pills at y 32/40, x 0/16/32, one
  kana each (か ふ む / い き き = かんたん ふつう むずかしい / いつもの きぶん きまぐれ) -> E N H / U M R in white.
    python -X utf8 tools/gfx_songsel.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_gameover import mask  # noqa: E402

LABELS = [("Easy", (96, 0, 128, 8)), ("Normal", (96, 8, 128, 16)), ("Hard", (88, 24, 128, 32))]
PILLS = [("E", 0, 32, 2), ("N", 16, 32, 6), ("H", 32, 32, 10), ("U", 0, 40, 2), ("M", 16, 40, 6), ("R", 32, 40, 10)]


def labels(img):
    for word, (x0, y0, x1, y1) in LABELS:
        for y in range(y0 + 1, y1 - 1):  # kana rows; the first column is the panel's left edge
            for x in range(x0 + 1, x1 - 1):
                if img[y][x] in (6, 7, 8):
                    img[y][x] = 9
        ink, w, h = mask(word, 1, 1, 1, bold=False)
        if w > x1 - x0 - 3:
            raise SystemExit(f"{word!r} {w} px does not fit {x1 - x0 - 3}")
        ox = x0 + 2 + (x1 - x0 - 3 - w) // 2
        for x, y in ink:
            if y0 + y < y1:
                img[y0 + y][ox + x] = 6


def pills(img):
    for ch, x0, y0, fill in PILLS:
        for y in range(y0, y0 + 8):
            for x in range(x0, x0 + 16):
                if img[y][x] in (13, 14, 15):
                    img[y][x] = fill
        ink, w, h = mask(ch, 1, 1, 1, bold=False)
        ox, oy = x0 + (16 - w) // 2, y0 + (8 - h + 1) // 2
        for x, y in ink:
            img[oy + y][ox + x] = 15


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    for group, fn in (("songsel", labels), ("pills", pills)):
        (_, off, size, layout, png), = gfx.rows(group)
        img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
        fn(img)
        gfx.save_png(img, gfx.load_pal(group), gfx.ROOT / png)
        print(png)


if __name__ == "__main__":
    main()
