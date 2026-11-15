"""gfx_names.py: name-entry keyboard keys in Latin (gfx/names.tsv, 171EAB9 chain, a gfx.FORKS fork).
Keys are 8 px apart in four groups at screen x 16/64/112/160, rows at y 110/124/138 (OAM 18-44 on both pages;
page 1 = hiragana dump `name_entry`, page 2 = katakana dump `name_kata`: warp name_entry, SELECT, ppudump).
Each key gets the letter tools/names.py prints for its code (page 1 upper, page 2 lower), white 15 with a 13
shadow like the kana; the small-kana keys (group 4, rows 2-3) keep their lower band; ゛゜ and っゃゅょ go blank.
gfx/nehead.tsv 179B69F: header ボタン / けってい / きりかえ -> Button / OK / A/a (START, SELECT already Latin).
    python -X utf8 tools/gfx_names.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enfont  # noqa: E402
import gfx  # noqa: E402
import names  # noqa: E402
from gfx_cards import fit  # noqa: E402
from gfx_obj import Sprites  # noqa: E402

PAGES = [("name_entry", 1), ("name_kata", 2)]
OAM = range(18, 45)
CAP_TOP = [6, 20, 34]  # cap-height top row of each key row
SMALL_TOP = 22  # row 2 group 4 (small kana sat lower): digits keep that band
FILL, SHADOW = 15, 13


def draw(img, ch, x, top, font):
    rows = font[ch]
    bold = len(rows[0]) <= 5  # bold like the kana, except M W ♥ (7 px) that would fill the 8 px key
    x += (8 - len(rows[0]) - bold) // 2
    ink = {(x + i + d, top - 1 + r) for r, row in enumerate(rows) for i, c in enumerate(row) if c == "#"
           for d in range(1 + bold)}
    for px, py in ink:
        if (px + 1, py + 1) not in ink:
            img[py + 1][px + 1] = SHADOW
    for px, py in ink:
        img[py][px] = FILL


def edit(img, page, font):
    """img = composed keyboard, origin at screen (16, 110)."""
    for y in range(len(img)):  # the bands overlap: clear all before drawing (descenders reach the next band)
        img[y] = [0] * len(img[y])
    for k, (_, upper, lower) in enumerate(names.KEYS):
        row, grp = divmod(k, 4)
        text = upper if page == 1 else lower
        top = SMALL_TOP if (row, grp) == (1, 3) else CAP_TOP[row]
        for i, ch in enumerate(text):
            if ch != " ":
                draw(img, ch, 48 * grp + 8 * i, top, font)


def keys(img, data, layout):
    font = {c: rows for c, rows in enfont.load()}
    for scene, page in PAGES:
        s = Sprites(scene, OAM)
        assert (s.x0, s.y0) == (16, 110), (scene, s.x0, s.y0)
        im = s.compose()
        edit(im, page, font)
        gfx.save_png(im, gfx.load_pal("names"), gfx.ROOT / f"work/gfx/names_{scene}.png")  # screen-space preview
        print(scene, s.write(img, data, im, layout), "tiles")


# header pieces: (OAM ids, word, fill, box in the pieces' own space); outline 5 like START/SELECT. OBJ 2 (the second
# ボタン) shares OBJ 7's tiles. OBJ 6 overlaps OBJ 7's last 2 columns: both stay blank there.
HEADER = [([7], "Button", 15, (0, 0, 30, 12)), ([6, 5], "OK", 8, (2, 0, 24, 12)), ([1], "A/a", 15, (0, 0, 32, 12))]


def header(img, data, layout):
    for ids, word, fill, box in HEADER:
        s = Sprites("name_entry", ids)
        im = [[0] * s.w for _ in range(s.h)]
        fit(im, word, box, fill, [5])
        s.write(img, data, im, layout)


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    for group, fn in (("names", keys), ("nehead", header)):
        (_, off, size, layout, png), = gfx.rows(group)
        data = gfx.decode(rom, off, size)[0]
        img = gfx.to_image(data, layout)
        fn(img, data, layout)
        gfx.save_png(img, gfx.load_pal(group), gfx.ROOT / png)
        print(png)


if __name__ == "__main__":
    main()
