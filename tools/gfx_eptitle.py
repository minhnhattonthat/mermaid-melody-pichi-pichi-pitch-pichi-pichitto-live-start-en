"""gfx_eptitle.py: episode-title strips of the episode grid (scene 25), 40 chains 18AF223..18BFC9C (800x2 each).
Each block = blank tile 0 + the title's tiles (BG1, pal 12, VRAM tile = block tile + 0x100). The BG1 map of title N
is a record found by the u16 table at 0x1881720 (entry N, offset from the table; entry 0 is another screen): a 5-byte
header, then a stream that fills the 32x32 map, by cell count (1024):
    byte < 0x80: big-endian u16 literal (flip bits in the high byte, tile in the low bits), one cell
    0x80 | n:    n + 1 cells, each the last value + 1        0xC0 | n:  n + 1 cells repeating the last value
The originals pack only the kanji cells; the English build gives every title the same RECT (block tiles 1.. in
reading order), rewritten in place (every new record is shorter; the rest of the old one is never read).
    python -X utf8 tools/gfx_eptitle.py sheet     Japanese titles from their maps -> work/gfx/eptitle_jp.png
    python -X utf8 tools/gfx_eptitle.py           English pngs for gfx/eptitle.tsv
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

TABLE = 0x1881720
RECT = (3, 8, 24, 5)  # cells x, y, w, h: centred on the originals (x 7-22 in title 1), 120 tiles of 127
FILL, RINGS = 1, [7, 4]  # original roles: 1 = letter body, 6-A inner edge, 3-5 outer edge, 0 = clear


def record(rom, n):
    """file offset of title n's map stream (n = 1..40)."""
    return TABLE + int.from_bytes(rom[TABLE + 2 * n:TABLE + 2 * n + 2], "little") + 5


def decode_map(rom, p):
    """-> (1024 u16 cells, end offset)"""
    cells, last = [], 0
    while len(cells) < 1024:
        b = rom[p]
        if b < 0x80:
            last = b << 8 | rom[p + 1]
            cells.append(last)
            p += 2
        elif b & 0x40:
            cells += [last] * ((b & 0x3F) + 1)
            p += 1
        else:
            for _ in range((b & 0x3F) + 1):
                last += 1
                cells.append(last)
            p += 1
    assert len(cells) == 1024, f"map stream at {p:X} overruns the map"
    return cells, p


def encode_map(cells):
    """inverse of decode_map (greedy: increment runs, then repeats, else a literal)."""
    out, i, last = bytearray(), 0, None
    while i < len(cells):
        v = cells[i]
        n = 0
        while last is not None and i + n < len(cells) and n < 64 and cells[i + n] == last + n + 1:
            n += 1
        if n:
            out.append(0x80 | n - 1)
            last += n
            i += n
            continue
        while last is not None and i + n < len(cells) and n < 64 and cells[i + n] == last:
            n += 1
        if n:
            out.append(0xC0 | n - 1)
            i += n
            continue
        out += v.to_bytes(2, "big")
        last = v
        i += 1
    return bytes(out)


def rect_map():
    x0, y0, w, h = RECT
    cells = [0] * 1024
    for j in range(h):
        for i in range(w):
            cells[(y0 + j) * 32 + x0 + i] = 1 + j * w + i
    return cells


def other_maps():
    """gfx/*.maps (written by generators such as gfx_minigame.py): [(record offset, new stream)]."""
    lines = [ln for f in sorted(gfx.GFX.glob("*.maps")) for ln in f.read_text(encoding="utf-8").splitlines()]
    return [(int(a, 16), bytes.fromhex(b)) for a, b in (ln.split("\t") for ln in lines if ln and ln[0] != "#")]


def records(rom):
    """-> [(record offset, new stream)]: every title's map -> RECT, plus gfx/*.maps."""
    new = encode_map(rect_map())
    return [(record(rom, n), new) for n in range(1, 41)] + other_maps()


# shortcut: fixed spot in the free gap between the packed text (ends ~0x1FEA100) and the relocated gfx (~0x1FFD500),
# growing up; apply fails loudly if either side ever reaches it.
MAP_RELOC = 0x1FF0000


def placed(rom):
    """-> [(record, new stream, written at, pointer or None)]. A stream longer than its record moves to MAP_RELOC
    behind a copy of its `00 c4` header, and the 32-bit pointer at record - 6 (-> the header) is repointed; only the
    minigame records (gfx/*.maps) have that pointer, so an episode title that grows is an error."""
    out, top = [], MAP_RELOC
    for p, new in records(rom):
        if len(new) <= decode_map(rom, p)[1] - p:
            out.append((p, new, p, None))
            continue
        if rom[p - 2:p] != b"\x00\xc4" or int.from_bytes(rom[p - 6:p - 2], "little") != 0x08000000 | p - 2:
            raise SystemExit(f"map {p:X}: new {len(new)} bytes > old, and no record pointer to move it")
        out.append((p, rom[p - 2:p] + new, top, p - 6))
        top += len(new) + 2
    return out


def apply(rom):
    """Rewrite every map record in place (build stage "maps"; the old tail is never read: 1024 cells), or move it."""
    for p, new, at, ptr in placed(bytes(rom)):
        if ptr is not None:
            if any(rom[at:at + len(new)]):
                raise SystemExit(f"map {p:X}: relocation spot {at:X} is not free (move MAP_RELOC)")
            rom[ptr:ptr + 4] = (0x08000000 | at).to_bytes(4, "little")
        rom[at:at + len(new)] = new


def zones(rom):
    return [z for p, new, at, ptr in placed(rom) for z in [(at, at + len(new))] + ([(ptr, ptr + 4)] if ptr else [])]


def tile(img, k):
    return [row[k % 16 * 8:k % 16 * 8 + 8] for row in img[k // 16 * 8:k // 16 * 8 + 8]]


def compose(img, cells):
    """block image (tiles16) + map cells -> indices of the used cells' bounding box"""
    used = [(i % 32, i // 32, v) for i, v in enumerate(cells) if v & 0x3FF]
    x0, y0 = min(x for x, _, _ in used), min(y for _, y, _ in used)
    w, h = max(x for x, _, _ in used) - x0 + 1, max(y for _, y, _ in used) - y0 + 1
    im = [[0] * (8 * w) for _ in range(8 * h)]
    for x, y, v in used:
        px = tile(img, v & 0x3FF)
        px = [r[::-1] for r in px] if v & 0x400 else px
        px = px[::-1] if v & 0x800 else px
        for r, row in enumerate(px):
            im[8 * (y - y0) + r][8 * (x - x0):8 * (x - x0) + 8] = row
    return im


def ink(lines, tall):
    """0/1 mask of lines in en12 (bold), each row repeated `tall` times, cropped to the ink."""
    W, H = 400, 14 * len(lines) + 4
    c = [[0] * W for _ in range(H)]
    gfx.typeset(c, lines, (0, 0, W, H), 1, [], lead=13)
    used = [i for i, r in enumerate(c) if any(r)]
    rows = c[used[0]:used[-1] + 1]
    x0 = min(r.index(1) for r in rows if any(r))
    x1 = max(len(r) - r[::-1].index(1) for r in rows if any(r))
    return [r[x0:x1] for r in rows for _ in range(tall)]


def layouts(text):
    words = text.split()
    yield [text], 2
    for i in range(1, len(words)):
        yield [" ".join(words[:i]), " ".join(words[i:])], 1
    yield [text], 1


def draw(im, text):
    """typeset text centred in im: one line 2x tall if it fits, else the most even two lines, else one line."""
    h, w = len(im), len(im[0])
    pad = len(RINGS)
    fits = []
    for lines, tall in layouts(text):
        m = ink(lines, tall)
        if len(m[0]) + 2 * pad <= w and len(m) + 2 * pad <= h:
            fits.append((tall, -len(lines), -abs(len(lines[0]) - len(lines[-1])), m))
    if not fits:
        raise SystemExit(f"{text!r}: no layout fits {w}x{h}")
    m = max(fits, key=lambda f: f[:3])[3]
    ox, oy = (w - len(m[0])) // 2, (h - len(m)) // 2
    px = {(ox + i, oy + j): FILL for j, r in enumerate(m) for i, v in enumerate(r) if v}
    for ring in RINGS:
        for (a, b) in list(px):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    px.setdefault((a + dx, b + dy), ring)
    for (a, b), v in px.items():
        im[b][a] = v


def edit(img, text):
    """block image -> English title laid out for RECT (tile 1 + j * w + i = cell (i, j)); other tiles cleared."""
    _, _, w, h = RECT
    im = [[0] * (8 * w) for _ in range(8 * h)]
    draw(im, text)
    for row in img:
        row[:] = [0] * len(row)
    for j in range(h):
        for i in range(w):
            k = 1 + j * w + i
            for r in range(8):
                img[k // 16 * 8 + r][k % 16 * 8:k % 16 * 8 + 8] = im[8 * j + r][8 * i:8 * i + 8]
    return im


def entries():
    for line in (gfx.GFX / "eptitle.tsv").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            f = line.split("\t")
            yield int(f[0], 16), f[3], f[4]


def sheet():
    from PIL import Image, ImageDraw
    rom = (gfx.ROOT / "work/orig.gba").read_bytes()
    big = Image.new("RGB", (2 * 8 * 26 * 2, 2 * 56 * 20), (40, 0, 40))
    d = ImageDraw.Draw(big)
    for n, (off, _, _) in enumerate(entries()):
        img = gfx.to_image(gfx.decode(rom, off, (0x800, 2))[0], "tiles16")
        im = compose(img, decode_map(rom, record(rom, n + 1))[0])
        X, Y = (n % 2) * 8 * 26 * 2, (n // 2) * 112
        for y, row in enumerate(im):
            for x, v in enumerate(row):
                big.paste((v * 17,) * 3, (X + 2 * x, Y + 14 + 2 * y, X + 2 * x + 2, Y + 16 + 2 * y))
        d.text((X + 2, Y + 1), f"{n + 1} {off:07X}", fill=(255, 255, 0))
    out = gfx.ROOT / "work/gfx/eptitle_jp.png"
    big.save(out)
    print(out)


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("eptitle")
    for off, png, text in entries():
        img = gfx.to_image(gfx.decode(rom, off, (0x800, 2))[0], "tiles16")
        edit(img, text)
        gfx.save_png(img, pal, gfx.ROOT / png)
    print("40 titles -> gfx/out/eptitle/")


if __name__ == "__main__":
    sheet() if sys.argv[1:] == ["sheet"] else main()
