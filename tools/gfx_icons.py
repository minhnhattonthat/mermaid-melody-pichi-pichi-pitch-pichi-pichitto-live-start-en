"""gfx_icons.py: main-menu mode icons (gfx/icons.tsv, block 170C1F2: a 128x192 OBJ sheet, six 64x64 icons) ->
gfx/out/icons/170C1F2.png. Each icon carries a two-line label drawn as light strokes on a flat body (purple body 11,
strokes 12-15; brown body 5, strokes 6-8/15). Inside each text rect the strokes are painted back to the body index,
then the English goes on in white with a 1 px body-dark shadow. Rects: interior light pixels (none of 0-2 within 4 px).
    python -X utf8 tools/gfx_icons.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

# (x0, y0, x1, y1) inclusive text rect, body index, English lines; order = icons in the sheet, row-major
ICONS = [
    ((15, 24, 43, 43), 11, ["Solo", "Pitch"]),      # crab: ひとりで ピッチ
    ((77, 24, 109, 42), 11, ["Link", "Pitch"]),     # apple: いっしょに ピッチ
    ((15, 91, 43, 110), 5, ["Hippo", "Pitch"]),     # pear: ヒッポで ピッチ
    ((75, 82, 109, 101), 5, ["Your", "Pitch"]),     # heart: あなたの ピッチ
    ((15, 149, 47, 176), 5, ["Collect", "Pitch"]),  # bag: あつめて ピッチ
    ((78, 146, 108, 166), 11, ["Live", "Pitch"]),   # book: ライブで ピッチ
]
LIGHT = {11: {12, 13, 14, 15}, 5: {6, 7, 8, 15}}


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("icons")
    (_, off, size, layout, png), = gfx.rows("icons")
    img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
    for (x0, y0, x1, y1), body, lines in ICONS:
        for y in range(y0 - 1, y1 + 2):
            for x in range(x0 - 1, x1 + 2):
                if img[y][x] in LIGHT[body]:
                    img[y][x] = body
        gfx.typeset(img, lines, (x0 - 2, y0, x1 + 3, y1 + 1), fill=15, outline=[], shadow=(body - 1, 1, 1),
                    lead=11)
    gfx.save_png(img, pal, gfx.ROOT / png)
    print(png)


if __name__ == "__main__":
    main()
