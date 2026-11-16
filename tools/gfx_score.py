"""gfx_score.py: score / goal words of the HUD atlas 1F0F059 (gfx/score.tsv: 800x8 = eight 128x32 panels, 2 across = 256x128) ->
gfx/out/score/1F0F059.png. The game copies tile rectangles of this atlas into OBJ VRAM (gameover 41, tokoton 36/40,
draw 42, results 5; `tools/gfx_where.py SCENE 1F0F059 800x8 tiles16` lists the pieces), so every English word stays
inside the tiles its Japanese used. Word style: pink fill 10-12, white ring 13-15, transparent 0.
    python -X utf8 tools/gfx_score.py
"""
import sys
from collections import Counter
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


# Results-screen sprites (warp state work/states/results_real.mss, user's save after a real song): each is a 48x24
# canvas of atlas pieces (src x, y, w, h, canvas x, y), mapped from the OAM dump (OBJ tile -> block tile).
def _pill(x, y, yb, xb=176):  # 48x16 top + 48x8 bottom strip in the x 176-223 column
    return [(x, y, 48, 16, 0, 0), (xb, yb, 48, 8, 0, 16)]


def _btn(t32, t16, b32, b16):  # framed button: 32+16 wide, 16+8 tall
    return [(*t32, 32, 16, 0, 0), (*t16, 16, 16, 32, 0), (*b32, 32, 8, 0, 16), (*b16, 16, 8, 32, 16)]


# pills: white kana 14-15 on fill 2/6/10; buttons: pink kana 10-14 on white 15 inside a yellow frame
SPRITES = [
    (_pill(128, 32, 32), "Easy", "pill"),     # かんたん
    (_pill(128, 48, 40), "Normal", "pill"),   # ふつう
    (_pill(128, 64, 48), "Hard", "pill"),     # むずかしい
    (_pill(128, 80, 104), "Usual", "pill"),   # いつもの
    (_pill(128, 96, 112), "Mood", "pill"),    # きぶん
    (_pill(128, 112, 120), "Random", "pill"),  # きまぐれ
    (_pill(176, 64, 56), "Part", "pill"),     # パート
    (_pill(176, 80, 96), "Mix", "pill"),      # ミックス
    (_btn((224, 32), (224, 48), (224, 72), (240, 80)), "Next", "btn"),  # すすむ
    (_btn((224, 16), (240, 48), (224, 64), (224, 80)), "Save", "btn"),  # セーブ
]


def sprite(img, pieces, text, kind):
    cv = [[0] * 48 for _ in range(24)]
    for sx, sy, w, h, dx, dy in pieces:
        for y in range(h):
            cv[dy + y][dx:dx + w] = img[sy + y][sx:sx + w]
    ink = {14, 15} if kind == "pill" else {10, 11, 12, 13, 14}
    x0, y0, x1, y1 = (4, 2, 44, 22) if kind == "pill" else (5, 3, 42, 21)
    bg = Counter(cv[y][x] for y in range(y0, y1) for x in range(x0, x1) if cv[y][x] not in ink | {0})
    bg = bg.most_common(1)[0][0] if kind == "pill" else 15
    for y in range(y0, y1):
        for x in range(x0, x1):
            if cv[y][x] in ink:
                cv[y][x] = bg
    for bold, gap in ((True, 1), (False, 1), (False, 0)):
        try:
            if kind == "pill":
                gfx.typeset(cv, [text], (x0, y0 + 3, x1, y1), fill=15, outline=[bg + 2], bold=bold, gap=gap)  # ring = pill edge 4/8/12
            else:
                gfx.typeset(cv, [text], (x0, y0 + 2, x1, y1), fill=10, outline=[], bold=bold, gap=gap)  # 13 is grey in pal 11/12
            break
        except ValueError:
            continue
    else:
        raise SystemExit(f"{text!r} does not fit")
    for sx, sy, w, h, dx, dy in pieces:
        for y in range(h):
            img[sy + y][sx:sx + w] = cv[dy + y][dx:dx + w]


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
    for pieces, text, kind in SPRITES:
        sprite(img, pieces, text, kind)
    gfx.save_png(img, pal, gfx.ROOT / png)
    print(png)


if __name__ == "__main__":
    main()
