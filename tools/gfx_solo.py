"""gfx_solo.py: Solo Pitch mode-carousel banners (scene 28, BG2: char base 0x4000, 64x32 map, banner in BG pal 5)
とことんピッチ / つづけてピッチ / アニメでピッチ -> Marathon Pitch / Nonstop Pitch / Anime Pitch (D15).
Each card's tiles come from one block (gfx/solo.tsv); the banner is the run of pal-5 cells under the portrait.
Erase: pink fill (index 8) strokes grown by 3 px (white ring F + red outer 3/5/9), only inside pal-5 cells, so the art
around stays. Draw: the dialogue font 1x wide / 2x tall (as GAME OVER), fill 8, two white rings F, outer ring 3.
    python -X utf8 tools/gfx_solo.py        (needs work/qa/ppu/<scene> dumps of the original ROM)
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_bg import Layer  # noqa: E402
from gfx_gameover import mask  # noqa: E402
from gfx_winlose import ring  # noqa: E402

CARDS = {  # scene -> English, map column of the card, cell rows of the lettering, Style
    "solo_modes": ("Marathon Pitch", 0, (13, 15), (5, 8, 15, None, (5, 3), 5, 1, 0)),  # rows 14-15 only
    "solo_tsuzukete": ("Nonstop Pitch", 32, (13, 16), (6, 8, 15, 4, (6,), 4, 1, 0)),
    "solo_anime": ("Anime Pitch", 0, (13, 17), (5, 9, 15, 5, (5,), 6, 1, 0, 14)),  # erase to the white cloud (14)
}
# Style = (banner palette, fill, white ring, outer ring or None, palettes whose cells may be erased, dy and dx from
# the old centre, white rings, [index erased pixels of banner cells get, default 0 = transparent]); text must stay off
# art palettes and shared tiles (raises otherwise)


def edit(L, word, x0, rows, style):
    """Card at map columns x0..x0+31, lettering in cell rows `rows` (lo, hi)."""
    PAL, fill, white, outer, _, dy, whites, dx, *_ = style
    rect = (x0, rows[0] - 1, 32, rows[1] - rows[0] + 3)
    cx0, cy0, w, h = rect
    img = L.compose(rect)
    palof = {(x, y): L.entry(cx0 + x // 8, cy0 + y // 8)[3] for y in range(8 * h) for x in range(8 * w)}
    band = range(8, 8 * h - 8)
    strokes = {(x, y) for y in band for x in range(8 * w) if palof[(x, y)] == PAL and img[y][x] == fill}
    uses = Counter(L.entry(x, y)[0] for x in range(L.w) for y in range(L.h))
    want = L.colours(PAL)

    def nearest(x, y, rgb):
        cols = L.colours(palof[(x, y)])
        return min((sum(abs(a - b) for a, b in zip(cols[i], rgb)), i) for i in range(1, 16))

    # plate: the old lettering grown 3 px (it and its outline), closed by 4 px into one smooth blob, painted white with
    # a 1 px edge in the old outline colour over every cell it covers (art cells too: outline bits there were the old
    # lettering's), so nothing of the old lettering is left loose; shared tiles (blank tile 0 etc.) stay as they are
    grown = strokes
    for _ in range(3):
        grown = grown | ring(grown)
    edge = Counter(img[y][x] for x, y in grown - strokes if 0 <= x < 8 * w and 0 <= y < 8 * h
                   and palof[(x, y)] == PAL and img[y][x] not in (0, fill, white)).most_common(1)[0][0]
    blob = grown
    for _ in range(4):
        blob = blob | ring(blob)
    for _ in range(4):
        blob = blob - ring({(x + i, y + j) for x, y in blob for i in (-1, 0, 1) for j in (-1, 0, 1)} - blob)
    border = blob & ring({(x + i, y + j) for x, y in blob for i in (-1, 0, 1) for j in (-1, 0, 1)} - blob)
    for x, y in blob:
        if 0 <= x < 8 * w and 0 <= y < 8 * h and uses[L.entry(cx0 + x // 8, cy0 + y // 8)[0]] == 1:
            err, k = nearest(x, y, want[edge if (x, y) in border else white])
            if err <= 80:
                img[y][x] = k
    ink, iw, ih = mask(word, 1, 2)
    xs, ys = [p[0] for p in strokes], [p[1] for p in strokes]
    cx, cy = (min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2  # centre of the old lettering
    ink = {(x + cx - iw // 2 + dx, y + cy - ih // 2 + dy) for x, y in ink}
    wr = set()
    for _ in range(whites):
        wr |= ring(ink | wr)
    r3 = ring(ink | wr) if outer is not None else set()
    skipped = 0
    for layer, v in ((r3, outer), (wr, white), (ink, fill)):
        for x, y in layer:
            if uses[L.entry(cx0 + x // 8, cy0 + y // 8)[0]] > 1:
                if layer is not ink:  # a ring pixel over a shared blank tile is left out
                    continue
                raise SystemExit(f"{word!r}: px {x},{y} lands on a shared tile (cell {cx0 + x // 8},{cy0 + y // 8})")
            err, k = nearest(x, y, want[v])
            if err > 80 and layer is not ink:  # an art palette with no such colour: that ring pixel is left out
                skipped += 1
                continue
            if err > 80:  # 75 = pal 3's light pink standing in for the pink fill
                raise SystemExit(f"{word!r}: px {x},{y} in a pal-{palof[(x, y)]} cell, nearest colour off by {err}")
            img[y][x] = k
    print(f"{word!r}: {skipped} ring pixels left out (no near colour)")
    return rect, img


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("solo")
    rows = {off: (size, layout, png) for _, off, size, layout, png in gfx.rows("solo")}
    images = {off: gfx.to_image(gfx.decode(rom, off, s)[0], lay) for off, (s, lay, _) in rows.items()}
    for scene, (word, x0, band, style) in CARDS.items():
        L = Layer(scene, 2)
        rect, img = edit(L, word, x0, band, style)
        if "--show" in sys.argv:
            from PIL import Image
            im = Image.new("RGB", (8 * rect[2], 8 * rect[3]))
            for y, row in enumerate(img):
                for x, v in enumerate(row):
                    im.putpixel((x, y), L.colours(L.entry(rect[0] + x // 8, rect[1] + y // 8)[3])[v])
            im.resize((im.width * 3, im.height * 3)).save(gfx.ROOT / f"work/gfx/solo_{scene}.png")
        # the card's block: the one whose tiles match the banner cells
        ts = {L.entry(rect[0] + i, rect[1] + j)[0] for i in range(rect[2]) for j in range(rect[3])} - {0}
        for off, (size, layout, png) in rows.items():
            data = gfx.decode(rom, off, size)[0]
            src = L.block_tiles(data)
            if all(src(t) is not None and data[32 * src(t):32 * src(t) + 32] == L.vram[L.cb + 32 * t:L.cb + 32 * t + 32]
                   for t in ts):
                n = L.write(images[off], data, rect, img, layout)
                print(f"{scene}: {word!r} -> {off:X}, banner cells {rect}, {n} tiles")
                break
        else:
            raise SystemExit(f"{scene}: no block in gfx/solo.tsv holds the banner tiles")
    for off, (_, _, png) in rows.items():
        gfx.save_png(images[off], pal, gfx.ROOT / png)
        print(png)


if __name__ == "__main__":
    main()
