"""gfx_options.py: Your Pitch options screen labels (scene 14; gfx/options.tsv: 1723EBE, 800x8 panelled atlas
obj16x4*8/2 = 256x128, OBJ pal 2, pal 1 when selected). Each label is a row of OBJ sprites 24 px tall:
ヘッドホン / マーメイド 80 px, はいけい / やじるし 64, なまえ 48, あり / なし 40 -> Headphones, Mermaid, Background, Arrows,
Name, On, Off. The right half (background thumbnails) and the name frame stay.
Ink as the original: fill a/b/c (dark to light blue, bottom to top), white ring(s) f, shadow 6 at (+1, +1).
    python -X utf8 tools/gfx_options.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_gameover import mask  # noqa: E402
from gfx_winlose import ring  # noqa: E402

LABELS = [  # English, sprite rect (x0, y0, x1, y1) in the block render, align
    ("Name", (80, 0, 128, 24), "l"),
    ("Background", (0, 32, 64, 56), "l"),
    ("Arrows", (64, 32, 128, 56), "l"),
    ("Headphones", (0, 56, 80, 80), "l"),
    ("On", (80, 56, 120, 80), "l"),
    ("Mermaid", (0, 80, 80, 104), "l"),
    ("Off", (80, 80, 120, 104), "l"),
]  # rects from the OAM tile numbers (2D OBJ map: row = tile // 32), not the 32 px panels
RINGS = {"Background": 1}  # 60 px of ink: 2 white rings + shadow need 65 of its 64 px; the rest get 2 like the original


def draw(img, word, box, align):
    rings = RINGS.get(word, 2)
    ink, w, h = mask(word, 1, 2)
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        img[y][x0:x1] = [0] * (x1 - x0)
    room = x1 - x0 - 2 * rings - 1
    if w > room or h > y1 - y0 - 2 * rings - 1:
        raise SystemExit(f"{word!r} {w}x{h} does not fit {box}")
    ox = x0 + rings + {"l": 0, "c": (room - w) // 2}[align]
    oy = y0 + rings + (y1 - y0 - 2 * rings - 1 - h) // 2
    ink = {(x + ox, y + oy) for x, y in ink}
    rim = set()
    for _ in range(rings):
        rim |= ring(ink | rim)
    for x, y in ink | rim:
        img[y + 1][x + 1] = 6
    for x, y in rim:
        img[y][x] = 15
    for x, y in ink:
        img[y][x] = 12 if (y - oy) * 3 < h else 11 if (y - oy) * 3 < 2 * h else 10


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("options")
    (_, off, size, layout, png), = gfx.rows("options")
    img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
    for word, box, align in LABELS:
        draw(img, word, box, align)
    gfx.save_png(img, pal, gfx.ROOT / png)
    print(png)


if __name__ == "__main__":
    main()
