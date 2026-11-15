"""gfx_diff.py: difficulty bubbles + button-hint pieces (gfx/diff.tsv, block 17264E2: 128x128 OBJ sheet, placed at
OBJ tile row 8 col 16, 2D map) -> gfx/out/diff/17264E2.png.
Six 64x32 bubbles (rows 0-95) with thick light kana (13-15, shading 3/7) on a flat fill: the text's bounding box is
painted back to the bubble's fill, then the English goes on in 15 with a 15 ring (chunky like the original).
Rows 112-127: four 32x16 header pieces (ボタン, スタート, もどる, けってい; outline 10, fill 15, AA 11-12).
    python -X utf8 tools/gfx_diff.py
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

BUBBLES = ["Easy", "Normal", "Hard", "Usual", "Mood", "Random"]  # かんたん ふつう むずかしい いつもの きぶん きまぐれ
PIECES = ["Button", "Start", "Back", "OK"]  # ボタン スタート もどる けってい (32x16 each at y 112)
TEXT = {13, 14, 15}


def bubble(img, cx, cy, word):
    pts = [(x, y) for y in range(cy + 4, cy + 28) for x in range(cx + 6, cx + 58) if img[y][x] in TEXT]
    x0, y0 = min(p[0] for p in pts) - 1, min(p[1] for p in pts) - 1
    x1, y1 = max(p[0] for p in pts) + 1, max(p[1] for p in pts) + 1
    fill = Counter(img[y][x] for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
                   if img[y][x] not in TEXT | {3, 7}).most_common(1)[0][0]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if img[y][x] in TEXT | {3, 7}:
                img[y][x] = fill
    gfx.typeset(img, [word], (cx + 5, cy + 6, cx + 59, cy + 25), fill=15, outline=[], gap=2)


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("diff")
    (_, off, size, layout, png), = gfx.rows("diff")
    img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
    for i, word in enumerate(BUBBLES):
        bubble(img, i % 2 * 64, i // 2 * 32, word)
    for i, word in enumerate(PIECES):
        for y in range(112, 128):
            img[y][i * 32:i * 32 + 32] = [0] * 32
        gfx.typeset(img, [word], (i * 32, 112, i * 32 + 32, 124), fill=15, outline=10, bold=False)
    gfx.save_png(img, pal, gfx.ROOT / png)
    print(png)


if __name__ == "__main__":
    main()
