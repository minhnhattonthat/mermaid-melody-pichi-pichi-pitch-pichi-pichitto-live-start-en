"""gfx_roomsel.py: room pickers (mascot / poster): banner and slot buttons.
gfx/roomsel.tsv 1CFC7D6 (mascot): BG2 banner, map cells 8-21 x 1-3 = block tiles 1-40 in map order (read from the
  mascot dump: VRAM tile = block tile + 128). White (13) anti-aliased text on fill 5, x 5-106 y 13-25 of the 112x24
  banner; corner cells are shared flipped tiles, so the text stays in x 8-103.
gfx/roombtn.tsv 1D0ADC0: three OBJ buttons 64x24 at (0,0) (64,0) (0,24): ひみつ★ / おかない / はらない, text (15) on
  fill 2 inside x 5-58 y 5-18.
    python -X utf8 tools/gfx_roomsel.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_bg import Layer  # noqa: E402
from gfx_cards import fit  # noqa: E402

# offset: (text, dump scene, bg, map rect (cells), VRAM tile of block tile 0, fill, ink, fill box, text box);
# poster / card collection: dumps work/qa/ppu/poster|card_coll (warps `poster`, `card_coll`), BG1, white (15) text
# on fill 7 / 2; their corner tiles and one mid tile are shared (flipped) top/bottom, so text stays in x 8.. y 6-17.
BANNERS = {0x1CFC7D6: ("Place which mascot?", "mascot", 2, (8, 1, 14, 3), 128, 5, 13, None, (8, 4, 104, 18)),
           0x1CE3D71: ("Which poster?", "poster", 1, (6, 1, 13, 3), 0, 7, 15, (5, 5, 104, 19), (8, 5, 101, 19)),
           0x1CFDD65: ("★Card Collection★", "card_coll", 1, (8, 1, 14, 3), 256, 2, 15, (5, 5, 107, 19),
                       (8, 5, 104, 19))}
BUTTONS = [("Secret", 0, 0), ("No mascot", 64, 0), ("No poster", 0, 24)]


def banner_map(scene, bg, rect, base):
    """cell (i, j) of rect -> (block tile, hflip, vflip), from the scene's dump."""
    L = Layer(scene, bg)
    x0, y0, w, h = rect
    return {(i, j): (L.entry(x0 + i, y0 + j)[0] - base,) + L.entry(x0 + i, y0 + j)[1:3]
            for i in range(w) for j in range(h)}


def cell(img, k, hf, vf):
    px = [row[k % 16 * 8:k % 16 * 8 + 8] for row in img[k // 16 * 8:k // 16 * 8 + 8]]
    px = [r[::-1] for r in px] if hf else px
    return px[::-1] if vf else px


def banner(img, spec):
    text, scene, bg, rect, base, fill, ink, fbox, tbox = spec
    m = banner_map(scene, bg, rect, base)
    _, _, w, h = rect
    im = [[0] * (8 * w) for _ in range(8 * h)]
    for (i, j), (k, hf, vf) in m.items():
        for y, row in enumerate(cell(img, k, hf, vf)):
            im[8 * j + y][8 * i:8 * i + 8] = row
    if fbox is None:  # mascot: banner rows 13-25 = rect rows 5-17
        for y in range(5, 18):
            im[y][8:104 if y > 15 else 107] = [5] * (96 if y > 15 else 99)  # ? tail in x 104-106: cell 13 unique above row 16
    else:
        x0, y0, x1, y1 = fbox
        for y in range(y0, y1):
            im[y][x0:x1] = [fill] * (x1 - x0)
    fit(im, text, tbox, ink, [])  # corner tiles shared (flipped) with the bottom row: checked below
    done = {}
    for (i, j), (k, hf, vf) in m.items():
        px = [r[8 * i:8 * i + 8] for r in im[8 * j:8 * j + 8]]
        px = px[::-1] if vf else px
        px = [r[::-1] for r in px] if hf else px
        if done.setdefault(k, px) != px:
            raise SystemExit(f"banner cell {i},{j}: block tile {k} is shared with other pixels")
        for y in range(8):
            img[k // 16 * 8 + y][k % 16 * 8:k % 16 * 8 + 8] = px[y]


def buttons(img):
    for word, x0, y0 in BUTTONS:
        for y in range(y0 + 5, y0 + 19):
            img[y][x0 + 5:x0 + 59] = [2] * 54
        fit(img, word, (x0 + 5, y0 + 4, x0 + 59, y0 + 20), 15, [])


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    for group in ("roomsel", "roombtn", "poster", "cardcoll"):
        for _, off, size, layout, png in gfx.rows(group):
            img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
            banner(img, BANNERS[off]) if group != "roombtn" else buttons(img)
            gfx.save_png(img, gfx.load_pal(group), gfx.ROOT / png)
            print(png)


if __name__ == "__main__":
    main()
