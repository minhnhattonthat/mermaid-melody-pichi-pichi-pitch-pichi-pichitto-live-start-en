"""gfx_clear.py: song-clear cut-in (scene 'clear': Kaito, BG3 char base 0x4000, many palettes; gfx/clear.tsv
180F0F8 800x10). すごいぞ! / よくやったな -> "Amazing!" / "Well done!".
The lettering sits on the art, so there is no clean background to restore: its footprint (pink / orange letters,
white rim, grey shadow) becomes a white sticker, and the English goes on it in the old pink and orange, 2x size,
with its own white rings and grey shadow. Each pixel takes the nearest colour of its own cell's palette.
    python -X utf8 tools/gfx_clear.py [--show]
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_bg import Layer  # noqa: E402
from gfx_gameover import mask  # noqa: E402
from gfx_winlose import ring  # noqa: E402

RECT = (0, 12, 24, 8)  # cells x, y, w, h holding both lines
LINES = [("Amazing!", 0), ("Well done!", 1)]  # "You did great!" is 142 px at 2x, past the old lettering  # text, line (0 = upper band, 1 = lower)


def cls(c):
    r, g, b = c
    if r > 225 and g > 225 and b > 225:
        return "W"
    if abs(r - g) < 20 and abs(g - b) < 20 and 60 < r < 200:
        return "G"
    if r > 200 and g < 170 and b < 200:
        return "P"
    if r > 200 and g < 220 and b < 150:
        return "O"
    return "."


def edit(L):
    x0, y0, w, h = RECT
    img = L.compose(RECT)
    W, H = 8 * w, 8 * h
    palof = {(x, y): L.entry(x0 + x // 8, y0 + y // 8)[3] for y in range(H) for x in range(W)}
    rgb = {(x, y): L.colours(palof[(x, y)])[img[y][x]] for y in range(H) for x in range(W)}
    kind = {p: cls(c) for p, c in rgb.items()}
    letters = {p for p, k in kind.items() if k in "PO"}
    # footprint = letters plus the white rim / grey shadow touching them (grown 4 px through W/G pixels)
    foot = set(letters)
    for _ in range(4):
        foot |= {p for p in ring(foot) if p in kind and kind[p] in "WG"}
    pink = Counter(rgb[p] for p in letters if kind[p] == "P").most_common(1)[0][0]
    orange = Counter(rgb[p] for p in letters if kind[p] == "O").most_common(1)[0][0]
    white = Counter(rgb[p] for p in foot if kind[p] == "W").most_common(1)[0][0]
    grey = Counter(rgb[p] for p in foot if kind[p] == "G").most_common(1)[0][0]
    ys = sorted({y for _, y in letters})
    mid = (ys[0] + ys[-1]) // 2  # bands: upper line above mid, lower below
    sticker, inks = {p for p in foot if kind[p] != "G"}, set()
    for word, line in LINES:
        band = [p for p in letters if (p[1] < mid) == (line == 0)]
        bx = [p[0] for p in band]
        by = [p[1] for p in band]
        ink, iw, ih = mask(word, 2, 2)
        cx, cy = (min(bx) + max(bx)) // 2, (min(by) + max(by)) // 2
        ink = {(x + cx - iw // 2, y + cy - ih // 2) for x, y in ink}
        rim = ring(ink)
        sticker |= ink | rim | ring(ink | rim)
        inks |= ink
    for _ in range(2):  # close pin holes (old anti-aliased pixels) inside the sticker
        sticker |= {(x, y) for x, y in ring(sticker)
                    if sum((x + dx, y + dy) in sticker for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 3}
    paint = {(x + 2, y + 2): grey for x, y in sticker if (x + 2, y + 2) not in sticker}
    paint.update({p: white for p in sticker})
    for x, y in inks:  # letter edge pink, inside orange (the original's two tones)
        edge = any((x + dx, y + dy) not in inks for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        paint[(x, y)] = pink if edge else orange
    # fallbacks where a cell's palette lacks the colour: orange -> pink; a shadow there is skipped
    falls = {orange: [orange, pink], pink: [pink], white: [white], grey: [grey, None]}
    for (x, y), c in paint.items():
        if not (0 <= x < W and 0 <= y < H) and c == grey:
            continue
        if not (0 <= x < W and 0 <= y < H):
            raise SystemExit(f"px {x},{y} falls outside {RECT}")
        cols = L.colours(palof[(x, y)])
        for want in falls[c]:
            if want is None:
                break
            err, k = min((sum(abs(a - b) for a, b in zip(cols[i], want)), i) for i in range(1, 16))
            if err <= 90:
                img[y][x] = k
                break
        else:
            raise SystemExit(f"px {x},{y}: pal {palof[(x, y)]} has no colour near {c}")
    return img


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    (_, off, size, layout, png), = gfx.rows("clear")
    data = gfx.decode(rom, off, size)[0]
    block = gfx.to_image(data, layout)
    L = Layer("clear", 3)
    img = edit(L)
    if "--show" in sys.argv:
        from PIL import Image
        im = Image.new("RGB", (8 * RECT[2], 8 * RECT[3]))
        for y, row in enumerate(img):
            for x, v in enumerate(row):
                im.putpixel((x, y), L.colours(L.entry(RECT[0] + x // 8, RECT[1] + y // 8)[3])[v])
        im.resize((im.width * 3, im.height * 3)).save(gfx.ROOT / "work/gfx/clear_new.png")
    print(L.write(block, data, RECT, img, layout), "tiles")
    gfx.save_png(block, gfx.load_pal("clear"), gfx.ROOT / png)
    print(png)


if __name__ == "__main__":
    main()
