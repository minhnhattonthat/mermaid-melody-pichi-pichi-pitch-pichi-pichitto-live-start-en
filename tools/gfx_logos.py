"""gfx_logos.py: the four minigame title logos (room -> minigame title page, BG2; docs/re/graphics.md §Minigame logos).

    python -X utf8 tools/gfx_logos.py show      original logos rendered from ROM (chain + map record + dump palette)
                                                -> work/gfx/logos_jp.png, with per-page stats
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_eptitle import decode_map, encode_map, tile  # noqa: E402
from gfx_gameover import mask  # noqa: E402
from gfx_minigame import orient  # noqa: E402
from gfx_winlose import ring  # noqa: E402

# page: (chain, size, map record, dump with the palette, Japanese)
PAGES = {1: (0x1BF198F, (0x800, 4), 0x1D243B9, "minititle", "くらべてピッチ"),
         2: (0x1BF2D7E, (0x800, 4), 0x1D244D8, "minititle2", "そろえてピッチ"),
         3: (0x1BF039E, (0x800, 6), 0x1D24266, "minititle3", "あわせてピッチ"),
         4: (0x1BF416C, (0x800, 4), 0x1D2461B, "minititle4", "キャッチでピッチ")}


def rom():
    return next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()


# page: words, letter fill, shadow, kana boxes (screen px x0, y0, x1, y1: top word, ピッチ; arrows/marks outside)
SPEC = {1: (("Compare", "Pitch"), (0x00, 0xFF, 0x10), (0xA4, 0x10, 0xC5), [(70, 4, 168, 40), (78, 60, 163, 99)]),
        2: (("Line Up", "Pitch"), (0xFF, 0x00, 0xC5), (0xA4, 0x10, 0xCD), [(52, 9, 186, 45), (65, 61, 170, 99)]),
        3: (("Match", "Pitch"), (0xFF, 0x9C, 0x00), (0xA4, 0x10, 0xCD), [(85, 5, 191, 38), (63, 62, 152, 98)]),
        4: (("Catch", "Pitch"), (0x08, 0xD5, 0xFF), (0xA4, 0x10, 0xCD), [(49, 15, 191, 43), (75, 70, 165, 96)])}
PAD = (8, 2)  # the English letter box = kana box grown by this (x, y)
LETTER_SHARE = float(sys.argv[2]) if len(sys.argv) > 2 else 0.01
LETTER_BOXES = {4: [(100, 15, 191, 43), (75, 70, 165, 96)]}  # Catch right of the crane claw (x 70-98)
PALS = gfx.GFX / "logos.pals"  # per page the 4 BG palettes its record's pals 0-3 use (cut from the dumps), 512 bytes


def bg_pal(page):
    """the page's palettes 0-3 as RGB. The loader adds 2 (pages 1, 3) or 6 (pages 2, 4) to the record's pal bits."""
    if not PALS.exists():
        raw = b""
        for p in PAGES:
            d = next((gfx.ROOT / "work/qa/ppu" / PAGES[p][3]).glob("*.pal.bin")).read_bytes()
            b = 2 + 4 * (1 - p % 2)
            raw += d[32 * b:32 * (b + 4)]
        PALS.write_bytes(raw)
    raw = PALS.read_bytes()[128 * (page - 1):128 * page]
    return [[gfx.rgb(raw[32 * p + 2 * i] | raw[32 * p + 2 * i + 1] << 8) for i in range(16)] for p in range(4)]


def load(r, page):
    off, size, rec, _, _ = PAGES[page]
    img = gfx.to_image(gfx.decode(r, off, size)[0], "tiles16")
    cells, end = decode_map(r, rec)
    return img, cells, end - rec, bg_pal(page)


def render(img, cells, pals, box):
    """cells -> RGB rows (index 0 = None) over box (x0, y0, w, h in cells)."""
    x0, y0, w, h = box
    out = [[None] * (8 * w) for _ in range(8 * h)]
    for j in range(h):
        for i in range(w):
            v = cells[(y0 + j) * 32 + x0 + i]
            k = v & 0x3FF
            if k >= len(img) // 8 * 16:
                continue
            for r, row in enumerate(orient(tile(img, k), v)):
                for c, ix in enumerate(row):
                    out[8 * j + r][8 * i + c] = pals[v >> 12][ix] if ix else None
    return out


def canvas(img, cells, pals):
    """the whole 32x32-cell screen as RGB rows (None = clear)."""
    return render(img, cells, pals, (0, 0, 32, 32))


def components(px, colour):
    """8-connected components of `colour` -> [(size, x0, y0, x1, y1, points)], biggest first."""
    seen, out = set(), []
    for y, row in enumerate(px):
        for x, c in enumerate(row):
            if c == colour and (x, y) not in seen:
                comp, st = {(x, y)}, [(x, y)]
                while st:
                    a, b = st.pop()
                    for q in ((a + i, b + j) for i in (-1, 0, 1) for j in (-1, 0, 1)):
                        if q not in comp and 0 <= q[0] < 256 and 0 <= q[1] < 256 and px[q[1]][q[0]] == colour:
                            comp.add(q)
                            st.append(q)
                seen |= comp
                xs, ys = [p[0] for p in comp], [p[1] for p in comp]
                out.append((len(comp), min(xs), min(ys), max(xs), max(ys), comp))
    return sorted(out, key=lambda c: -c[0])


def erase(px, fill, shadow, boxes, near=(-3, 6)):
    """unknown (False) the letter-coloured pixels within `near` (dx/dy range: the shadow falls down-right) of a fill
    component (8+ px) centred in a box, plus shadow pixels joined to them (within the box + 10); then fill the holes
    from their known neighbours (majority, clear counts as a colour). Letter colours: fill, shadow, and each colour
    that is 3%+ of the ring 1-2 px round the fill (art there keeps its own colours: card frames, stars, the claw)."""
    seeds = set()
    for n, x0, y0, x1, y1, pts in components(px, fill):
        if n >= 8 and any(b[0] <= (x0 + x1) // 2 <= b[2] and b[1] <= (y0 + y1) // 2 <= b[3] for b in boxes):
            seeds |= pts

    def grow(pts, rx, ry):
        return {(x + i, y + j) for x, y in pts for i in range(*rx) for j in range(*ry)
                if 0 <= x + i < 256 and 0 <= y + j < 256}
    zone = Counter(px[y][x] for x, y in grow(seeds, (-2, 3), (-2, 3)) - seeds)
    keep = {fill, shadow} | {c for c, k in zone.items() if c is not None and k >= LETTER_SHARE * sum(zone.values())}
    hole = {(x, y) for x, y in grow(seeds, near, near) if px[y][x] in keep}
    st = list(hole)
    while st:  # shadow left outside `near`
        x, y = st.pop()
        for q in ((x + i, y + j) for i in (-1, 0, 1) for j in (-1, 0, 1)):
            if q not in hole and any(b[0] - 10 <= q[0] <= b[2] + 10 and b[1] - 10 <= q[1] <= b[3] + 10 for b in boxes) \
                    and 0 <= q[0] < 256 and 0 <= q[1] < 256 and px[q[1]][q[0]] == shadow:
                hole.add(q)
                st.append(q)
    for x, y in hole:
        px[y][x] = False
    need = 3
    while hole:
        done = {}
        for x, y in hole:
            nb = [px[y + j][x + i] for i in (-1, 0, 1) for j in (-1, 0, 1)
                  if (i or j) and 0 <= x + i < 256 and 0 <= y + j < 256 and px[y + j][x + i] is not False]
            if len(nb) >= need:
                votes = Counter(nb)
                votes[None] *= 1.5  # letters stood out of the art: lean to clear
                done[x, y] = votes.most_common(1)[0][0]
        if not done:
            need -= 1
            continue
        need = 3
        for (x, y), c in done.items():
            px[y][x] = c
        hole -= set(done)


def letter(px, word, box, fill, shadow, white=(255, 255, 255)):
    """word centred in box (x0, y0, x1, y1): fill, two white rings, a shadow (+2, +2) round all of it."""
    x0, y0, x1, y1 = box
    for sx, sy in ((3, 3), (2, 3), (2, 2)):
        ink, w, h = mask(word, sx, sy)
        if w + 7 <= x1 - x0 and h + 7 <= y1 - y0:
            break
    else:
        raise SystemExit(f"{word!r} does not fit {box}")
    ox, oy = x0 + 2 + (x1 - x0 - 7 - w) // 2, y0 + 2 + (y1 - y0 - 7 - h) // 2
    ink = {(x + ox, y + oy) for x, y in ink}
    r1 = ring(ink)
    r2 = ring(ink | r1)
    body = ink | r1 | r2
    for x, y in {(x + i, y + j) for x, y in body for i, j in ((1, 1), (2, 2), (1, 2), (2, 1))} - body:
        px[y][x] = shadow
    for x, y in r1 | r2:
        px[y][x] = white
    for x, y in ink:
        px[y][x] = fill


def quantize(px, cells, pals):
    """RGB screen -> (cells' pal per cell, index rows): each 8x8 cell takes the palette nearest its colours (the
    original pal when equal), index 0 = clear."""
    def d(a, b):
        return sum((p - q) ** 2 for p, q in zip(a, b))
    idx = [[0] * 256 for _ in range(256)]
    pal_of = [0] * 1024
    for n in range(1024):
        cx, cy = n % 32 * 8, n // 32 * 8
        cols = Counter(px[cy + r][cx + c] for r in range(8) for c in range(8))
        cols.pop(None, None)
        if not cols:
            continue
        best = min(range(4), key=lambda p: (sum(k * min(d(c, q) for q in pals[p][1:]) for c, k in cols.items()),
                                            p != cells[n] >> 12))
        pal_of[n] = best
        near = {c: 1 + min(range(15), key=lambda i: d(c, pals[best][1 + i])) for c in cols}
        for r in range(8):
            for c in range(8):
                v = px[cy + r][cx + c]
                idx[cy + r][cx + c] = near[v] if v is not None else 0
    return pal_of, idx


def retile(idx, pal_of, ntiles):
    """index rows + pals -> (new cells, tile image of ntiles tiles): tiles deduped with flips, tile 0 blank."""
    tiles, keys, cells = [[[0] * 8 for _ in range(8)]], {}, [0] * 1024
    keys[tuple(map(tuple, tiles[0]))] = (0, 0)
    for n in range(1024):
        cx, cy = n % 32 * 8, n // 32 * 8
        t = [idx[cy + r][cx:cx + 8] for r in range(8)]
        if not any(map(any, t)):
            continue
        for flip in (0, 0x400, 0x800, 0xC00):
            k = keys.get(tuple(map(tuple, orient(t, flip))))
            if k is not None:
                cells[n] = pal_of[n] << 12 | flip | k[0]
                break
        else:
            keys[tuple(map(tuple, t))] = (len(tiles), 0)
            cells[n] = pal_of[n] << 12 | len(tiles)
            tiles.append(t)
    if len(tiles) > ntiles:
        raise SystemExit(f"logo needs {len(tiles)} tiles, the block holds {ntiles}")
    img = [[0] * 128 for _ in range(ntiles // 16 * 8)]
    for k, t in enumerate(tiles):
        for r in range(8):
            img[k // 16 * 8 + r][k % 16 * 8:k % 16 * 8 + 8] = t[r]
    return cells, img


def bbox(cells):
    used = [n for n, v in enumerate(cells) if v & 0x3FF]
    xs, ys = [n % 32 for n in used], [n // 32 for n in used]
    return min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1


def vram(dump, screen):
    """the dump's BG2 (char 0x4000, map 0x600D000 + 0x800 * screen) -> (tile image, cells)."""
    v = next((gfx.ROOT / "work/qa/ppu" / dump).glob("*.vram.bin")).read_bytes()
    img = gfx.to_image(v[0x4000:0xC000], "tiles16")
    m = v[0xD000 + 0x800 * screen:0xD800 + 0x800 * screen]
    return img, [m[2 * i] | m[2 * i + 1] << 8 for i in range(1024)]


def show():
    from PIL import Image
    r = rom()
    ims = []
    for page in PAGES:
        img, cells, nbytes, pals = load(r, page)
        if "vram" in sys.argv:
            img, cells = vram(PAGES[page][3], 1 - page % 2)
        box = bbox(cells)
        ks = [v & 0x3FF for v in cells if v & 0x3FF]
        ntiles = len(img) // 8 * 16
        print(f"page {page}: box {box}, tiles {ntiles}, max used {max(ks)}, distinct {len(set(ks))}, "
              f"beyond block {sorted({k for k in ks if k >= ntiles})[:8]}, pals {sorted({v >> 12 for v in cells})}, "
              f"record {nbytes} bytes")
        px = render(img, cells, pals, box)
        im = Image.new("RGB", (len(px[0]), len(px)), (40, 40, 40))
        im.putdata([c or (40, 40, 40) for row in px for c in row])
        ims.append(im.resize((im.width * 3, im.height * 3), Image.NEAREST))
    sheet = Image.new("RGB", (max(i.width for i in ims), sum(i.height + 8 for i in ims)), (0, 0, 0))
    y = 0
    for i in ims:
        sheet.paste(i, (0, y))
        y += i.height + 8
    out = gfx.ROOT / "work/gfx/logos_jp.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(out)


def image(px, scale=3):
    from PIL import Image
    im = Image.new("RGB", (256, 128), (40, 40, 40))
    im.putdata([c or (40, 40, 40) for row in px[:128] for c in row])
    return im.resize((256 * scale, 128 * scale), Image.NEAREST)


def main():
    """English logos -> gfx/out/logos/<chain>.png (index carrier: gfx/logos.pal), gfx/logos.maps,
    preview work/gfx/logos_en.png (Japanese above English)."""
    from PIL import Image
    r = rom()
    raw = b"".join((2 * i * 0x421).to_bytes(2, "little") for i in range(16))  # 16 distinct greys
    (gfx.GFX / "logos.pal").write_bytes(raw)
    gpal = gfx.load_pal("logos")
    rows = ["# minigame title logos (room minigame pages 1-4, BG2, 4 pals per tile map; tools/gfx_logos.py writes the",
            "# pngs (tile indices shown as greys) and the new map records gfx/logos.maps)",
            "# offset\tsize\tlayout\tpng\tEnglish\tJapanese"]
    maps = ["# map record (file offset)\tnew run stream (hex): written by gfx_eptitle.apply (stage maps), moved if longer"]
    shots = []
    for page, (words, fill, shadow, boxes) in SPEC.items():
        off, size, rec, _, jp = PAGES[page]
        img, cells, nbytes, pals = load(r, page)
        px = canvas(img, cells, pals)
        shots.append(image(px))
        erase(px, fill, shadow, boxes)
        for word, (x0, y0, x1, y1) in zip(words, LETTER_BOXES.get(page, boxes)):
            letter(px, word, (x0 - PAD[0], y0 - PAD[1], x1 + PAD[0], y1 + PAD[1]), fill, shadow)
        pal_of, idx = quantize(px, cells, pals)
        new, timg = retile(idx, pal_of, size[1] * 0x800 // 32)
        q = canvas(timg, new, pals)
        assert all(q[y][x] == (pals[pal_of[y // 8 * 32 + x // 8]][idx[y][x]] if idx[y][x] else None)
                   for y in range(256) for x in range(256))
        shots.append(image(q))
        png = f"gfx/out/logos/{off:07X}.png"
        gfx.save_png(timg, gpal, gfx.ROOT / png)
        stream = encode_map(new)
        maps.append(f"{rec:07X}\t{stream.hex()}")
        rows.append(f"{off:07X}\t800x{size[1]}\ttiles16\t{png}\t{' '.join(words)}\t{jp}")
        print(f"page {page}: {max(v & 0x3FF for v in new) + 1} tiles of {size[1] * 0x800 // 32}, "
              f"map {len(stream)}/{nbytes} bytes")
    (gfx.GFX / "logos.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (gfx.GFX / "logos.maps").write_text("\n".join(maps) + "\n", encoding="utf-8")
    sheet = Image.new("RGB", (768 * 2 + 8, 4 * 392), (0, 0, 0))
    for i, s in enumerate(shots):
        sheet.paste(s, (i % 2 * 776, i // 2 * 392))
    out = gfx.ROOT / "work/gfx/logos_en.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    {"show": show}.get(sys.argv[1] if len(sys.argv) > 1 else "", main)()
