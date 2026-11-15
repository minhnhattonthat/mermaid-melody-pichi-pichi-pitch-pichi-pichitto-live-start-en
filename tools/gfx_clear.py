"""gfx_clear.py: song-clear cut-in (scene 'clear': Kaito, BG3 char base 0x4000, many palettes; gfx/clear.tsv
180F0F8 800x10). すごいぞ! / よくやったな -> "Amazing!" / "Well done!".
The lettering sits on the art, so there is no clean background to restore: its footprint (pink / orange letters,
white rim, grey shadow) becomes a white sticker, and the English goes on it in the old pink and orange, 2x size,
with its own white rings and grey shadow. Each pixel takes the nearest colour of its own cell's palette.
    python -X utf8 tools/gfx_clear.py [--show]
"""
import struct
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
    rows = Counter(y for _, y in letters)  # bands split at the emptiest row of the middle third (the lines overlap
    third = (ys[-1] - ys[0]) // 3  # in y: a plain half put the lower line's tall kana in the upper band)
    mid = min(range(ys[0] + third, ys[-1] - third + 1), key=lambda y: rows[y])
    sticker, inks = {p for p in foot if kind[p] != "G"}, set()
    for word, line in LINES:
        band = [p for p in letters if (p[1] < mid) == (line == 0)]
        bx = [p[0] for p in band]
        by = [p[1] for p in band]
        if line == 0:  # the hair right of すごいぞ! has pink specks that pulled Amazing! right (visual QA)
            bx = sorted(bx)[:len(bx) - len(bx) // 50]
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


RAINBOW_RECT = (1, 13, 29, 6)  # siblings: one line よくがんばりましたね at map y 112-147, x 20-230


def rainbow(L, text="You worked hard!", sx=2, sy=3):
    """Siblings 1813332 / 18170D4 (Elisa? / Sara?, picked by 0xBA + s8 0x0202FA0D): rainbow letters with a white
    rim and a blue shadow. Same sticker idea as `edit`; the English takes the old letters' colour at its x (the
    gradient runs left to right), the sticker's shadow the old shadow blue."""
    x0, y0, w, h = RAINBOW_RECT
    img = L.compose(RAINBOW_RECT)
    W, H = 8 * w, 8 * h
    palof = {(x, y): L.entry(x0 + x // 8, y0 + y // 8)[3] for y in range(H) for x in range(W)}
    rgb = {(x, y): L.colours(palof[(x, y)])[img[y][x]] for y in range(H) for x in range(W)}
    sat = {p for p, (r, g, b) in rgb.items() if max(r, g, b) - min(r, g, b) > 110 and 8 <= p[1] < 44}
    shadow = Counter(rgb[p] for p in sat if sum(rgb[p]) < 300).most_common(1)[0][0]
    letters = {p for p in sat if sum(rgb[p]) >= 300}
    foot = set(sat)
    for _ in range(4):
        foot |= {p for p in ring(foot) if p in rgb and min(rgb[p]) > 200}
    white = (255, 255, 255)
    col = {}  # x -> most common old letter colour within 3 px
    for x in range(W):
        near = Counter(rgb[p] for p in letters if abs(p[0] - x) <= 3)
        col[x] = near.most_common(1)[0][0] if near else None
    for x in range(W):  # ends past the old letters take the nearest known colour
        if col[x] is None:
            col[x] = col[min((k for k in col if col[k]), key=lambda k: abs(k - x))]
    ink, iw, ih = mask(text, sx, sy)
    lx, ly = [p[0] for p in letters], [p[1] for p in letters]
    cx, cy = (min(lx) + max(lx)) // 2, (min(ly) + max(ly)) // 2
    ink = {(x + cx - iw // 2, y + cy - ih // 2) for x, y in ink}
    rim = ring(ink)
    sticker = (foot - sat) | {p for p in sat if p in foot} | ink | rim | ring(ink | rim)
    sticker = {p for p in sticker if p in rgb}
    for _ in range(2):
        sticker |= {(x, y) for x, y in ring(sticker) if (x, y) in rgb
                    and sum((x + dx, y + dy) in sticker for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 3}
    paint = {(x + 2, y + 2): shadow for x, y in sticker if (x + 2, y + 2) not in sticker}
    paint.update({p: white for p in sticker})
    # one letter colour: the old letter colour (or the shadow blue) that most ink cells' palettes hold; an x gradient
    # came out blotchy, as each 8x8 cell has its own palette with only a few of the hues
    cells = {(p[0] // 8, p[1] // 8) for p in ink if p in palof}
    def held(c):
        return sum(any(sum(abs(a - b) for a, b in zip(q, c)) <= 60 for q in L.colours(palof[(8 * cx, 8 * cy)]))
                   for cx, cy in cells)
    tone = max(set(col.values()) | {shadow}, key=lambda c: (held(c), -sum(c)))
    paint.update({p: tone for p in ink})
    # cells whose palette lacks the tone or white (light ones over hair and sky; every slot of those is in use) move
    # to a palette holding both, their unpainted pixels remapped to its nearest colours: L.newcells {(cx, cy): pal}
    def dist(a, b):
        return sum(abs(u - v) for u, v in zip(a, b))

    def has(p, c):
        return min(dist(q, c) for q in L.colours(p)[1:]) <= 60

    good = [p for p in range(14) if has(p, tone) and has(p, white)]
    L.newcells = {}
    for cx, cy in sorted({(x // 8, y // 8) for (x, y), c in paint.items() if (x, y) in palof and c != shadow}):
        p = palof[(8 * cx, 8 * cy)]
        if has(p, tone) and has(p, white):
            continue
        keep = [(x, y) for y in range(8 * cy, 8 * cy + 8) for x in range(8 * cx, 8 * cx + 8)
                if (x, y) not in paint and img[y][x]]
        q = min(good, key=lambda q: sum(min(dist(c, rgb[k]) for c in L.colours(q)[1:]) for k in keep))
        for x, y in keep:
            img[y][x] = min(range(1, 16), key=lambda i: dist(L.colours(q)[i], rgb[(x, y)]))
        for y in range(8 * cy, 8 * cy + 8):
            for x in range(8 * cx, 8 * cx + 8):
                palof[(x, y)] = q
        L.newcells[(x0 + cx, y0 + cy)] = q
    for (x, y), c in paint.items():
        if not (0 <= x < W and 0 <= y < H):
            if c == shadow:
                continue
            raise SystemExit(f"px {x},{y} falls outside {RAINBOW_RECT}")
        cols = L.colours(palof[(x, y)])
        err, k = min((sum(abs(a - b) for a, b in zip(cols[i], c)), i) for i in range(1, 16))
        if err > 120 and c == shadow:  # a cell palette without the blue: no shadow there
            continue
        if err > 120 and c != white:  # letter colour missing in this cell: its darkest (reads on the white)
            err, k = 0, min(range(1, 16), key=lambda i: sum(cols[i]))
        if err > 120 and c == white:  # white missing in this cell: its brightest colour
            k = max(range(1, 16), key=lambda i: sum(cols[i]))
            err = sum(abs(a - b) for a, b in zip(cols[k], c))
        if err > 400 and c == white:
            raise SystemExit(f"px {x},{y}: pal {palof[(x, y)]} has no colour near {c}")
        img[y][x] = k
    return img


# block -> (PPU dump scene, rect, editor, r4); dumps: warp SCENE_ID=39 WRITES 0x0202FA0D:<r4> + ppudump.lua.
# 0x08013E3C loads block 0xBA + r4 of table 16F6CC8, BG palettes 0-13 from 0x183AC40 + 32 * (14 * r4 + 0x5E9)
# and the map, table 0x184ECF4 entry 0x43 + r4 (writer 0x08002378, not the eptitle stream format)
VARIANTS = {0x180F0F8: ("clear", RECT, edit, 0), 0x1813332: ("clear1", RAINBOW_RECT, rainbow, 1),
            0x18170D4: ("clear2", RAINBOW_RECT, rainbow, 2)}
MAPS = 0x184ECF4


def record(rom, r4):
    """file offset of variant r4's map stream: entry -> 3 bytes (?, u16 data offset from MAPS) -> u16 header 0x8400
    (compressed, 1024 cells), then the stream."""
    o = MAPS + struct.unpack_from("<H", rom, MAPS + 2 * (0x43 + r4))[0]
    p = MAPS + struct.unpack_from("<H", rom, o + 1)[0]
    assert struct.unpack_from("<H", rom, p)[0] == 0x8400, f"map header at {p:X}"
    return p + 2


def decode_rec(rom, p):
    """IWRAM decoder 0x080091A0: op n = (b & 0x3F) + 1; b < 0x80: n LE u16 literals, 0x80|: n x last+1, 0xC0|: n x
    last. -> (1024 cells, end)."""
    cells, last = [], 0
    while len(cells) < 1024:
        b, n = rom[p], (rom[p] & 0x3F) + 1
        p += 1
        for _ in range(n):
            if b < 0x80:
                last = struct.unpack_from("<H", rom, p)[0]
                p += 2
            elif not b & 0x40:
                last += 1
            cells.append(last)
    assert len(cells) == 1024, f"map stream ends at {p:X} past 1024 cells"
    return cells, p


def encode_rec(cells):
    out, i, last = bytearray(), 0, None
    while i < len(cells):
        for step, op in ((1, 0x80), (0, 0xC0)):
            n = 0
            while last is not None and i + n < len(cells) and n < 64 and cells[i + n] == last + step * (n + 1):
                n += 1
            if n:
                out.append(op | n - 1)
                last += step * n
                i += n
                break
        else:  # literals until the next cell continues or repeats the one before it
            n = 1
            while i + n < len(cells) and n < 64 and cells[i + n] not in (cells[i + n - 1], cells[i + n - 1] + 1):
                n += 1
            out.append(n - 1)
            for v in cells[i:i + n]:
                out += struct.pack("<H", v)
            last = cells[i + n - 1]
            i += n
    return bytes(out)


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    raws = []
    for _, off, size, layout, png in gfx.rows("clear"):
        scene, rect, fn, r4 = VARIANTS[off]
        data = gfx.decode(rom, off, size)[0]
        block = gfx.to_image(data, layout)
        L = Layer(scene, 3)
        p = record(rom, r4)
        cells, end = decode_rec(rom, p)
        assert encode_rec(cells) == rom[p:end] or len(encode_rec(cells)) <= end - p
        assert cells == [struct.unpack_from("<H", L.vram, L.sb + 2 * i)[0] for i in range(1024)], f"{scene} map"
        img = fn(L)
        newcells = getattr(L, "newcells", {})

        def pal(cx, cy):
            return newcells.get((cx, cy), L.entry(cx, cy)[3])
        if "--show" in sys.argv:
            from PIL import Image
            im = Image.new("RGB", (8 * rect[2], 8 * rect[3]))
            for y, row in enumerate(img):
                for x, v in enumerate(row):
                    im.putpixel((x, y), L.colours(pal(rect[0] + x // 8, rect[1] + y // 8))[v])
            im.resize((im.width * 3, im.height * 3)).save(gfx.ROOT / f"work/gfx/{scene}_new.png")
        print(L.write(block, data, rect, img, layout), "tiles")
        gfx.save_png(block, gfx.load_pal("clear"), gfx.ROOT / png)
        print(png)
        if newcells:
            for (cx, cy), q in newcells.items():
                cells[32 * cy + cx] = cells[32 * cy + cx] & 0x0FFF | q << 12
            new = encode_rec(cells)
            assert decode_rec(new + b"\0\0", 0)[0] == cells
            if len(new) > end - p:
                raise SystemExit(f"{scene} map record {p:X}: {len(new)} bytes > old {end - p}")
            raws.append(f"{p:X}\t{new.hex()}\t{scene}: {len(newcells)} cells re-paletted")
    (gfx.GFX / "clear.raw").write_text("# cut-in BG3 map records rewritten in place (tools/gfx_clear.py)\n"
                                       + "".join(r + "\n" for r in raws), encoding="utf-8")


if __name__ == "__main__":
    main()
