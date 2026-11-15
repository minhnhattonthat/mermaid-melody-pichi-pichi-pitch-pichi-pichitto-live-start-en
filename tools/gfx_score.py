"""gfx_score.py: score / goal words of the HUD atlas 1F0F059 (gfx/score.tsv: 800x8 = eight 128x32 panels, 2 across = 256x128) ->
gfx/out/score/1F0F059.png. The game copies tile rectangles of this atlas into OBJ VRAM (gameover 41, tokoton 36/40,
draw 42, results 5; `tools/gfx_where.py SCENE 1F0F059 800x8 tiles16` lists the pieces), so every English word stays
inside the tiles its Japanese used. Word style: pink fill 10-12, white ring 13-15, transparent 0.
    python -X utf8 tools/gfx_score.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

# (x0, y0, x1, y1) piece rect in the atlas -> English (None: erase only)
WORDS = [
    ((48, 56, 80, 80), "pts"),            # てん (big, 32x24, after the score)
    ((80, 64, 96, 80), None),             # あ|と (16x16 + 8x16 below, shown side by side before the song count):
    ((88, 80, 96, 96), None),             #   erased, "100 songs" reads alone
    ((96, 64, 128, 80), "songs"),         # きょく
    ((48, 80, 88, 96), "Left"),           # のこり (before the points left)
    ((96, 80, 128, 96), "Song"),          # うた
    ((0, 96, 88, 112), "Clear goal"),     # クリアもくひょう
    ((96, 96, 128, 112), "pts"),          # てん (small)
    ((0, 112, 48, 128), "High"),          # さいこう|とくてん: the game also shows とくてん alone, as the left
    ((48, 112, 88, 128), "Score"),        #   half of と from (216, 16) + x 48-87 here, so "Score" sits in that half
    ((216, 16, 224, 32), None),           # と left half (8x16)
    ((96, 112, 128, 128), "Rhythm"),      # リズム
]


def word(img, rect, text):
    x0, y0, x1, y1 = rect
    for y in range(y0, y1):
        for x in range(x0, x1):
            if img[y][x] >= 10:
                img[y][x] = 0
    if not text:
        return
    for bold, gap in ((True, 1), (False, 1), (False, 0)):  # tightest that fits
        try:
            gfx.typeset(img, [text], (x0 + 1, y0, x1 - 1, y1), fill=10, outline=[15, 14], bold=bold, gap=gap)
            return
        except ValueError:
            continue
    raise SystemExit(f"{text!r} does not fit {rect}")


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("score")
    (_, off, size, layout, png), = gfx.rows("score")
    img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
    for rect, text in WORDS:
        word(img, rect, text)
    gfx.save_png(img, pal, gfx.ROOT / png)
    print(png)


if __name__ == "__main__":
    main()
