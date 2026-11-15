"""gfx.py: graphics text redraws (kcomp blocks of 4bpp tiles) -> the build's "gfx" stage.

gfx/<group>.tsv rows: offset<TAB>size<TAB>layout<TAB>png<TAB>note   (offset/size hex: the block and its decoded size;
  size 800x2 = a chain of 2 streams of 0x800 bytes each, back to back)
  layout  objWxH*N : N OBJ sprites of WxH tiles, 1D mapping, side by side (64x32 sprite = obj8x4)
          tilesC   : plain tile sheet C tiles wide (row-major)
  png     gfx/out/<group>/<offset>.png, an RGB image in the block's palette (index image via the palette below);
          pixels must use colours of that palette; where two indices share a colour the original index is kept.
Palette per group: gfx/<group>.pal (16 BGR555 colours, 32 bytes), cut from an emulator palette dump.

    python -X utf8 tools/gfx.py export GROUP          # write the original block of every row as gfx/orig/<group>/<off>.png
    python -X utf8 tools/gfx.py check                 # every row's png decodes, fits the palette, and re-encodes
The build compresses each edited block (tools/kcomp.py) and writes it over the original stream when it fits, else into
free space with the resource-table records that point at it repointed (docs/re/graphics.md §Redraws).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import kcomp  # noqa: E402

GFX = ROOT / "gfx"


def rgb(c):
    return ((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31)


def load_pal(group):
    raw = (GFX / f"{group}.pal").read_bytes()
    return [rgb(raw[i] | raw[i + 1] << 8) for i in range(0, 32, 2)]


def parse_layout(layout):
    """-> (tile columns per unit, tile rows, units). A tile sheet is one unit."""
    if layout.startswith("obj"):
        wh, n = layout[3:].split("*")
        w, h = wh.split("x")
        return int(w), int(h), int(n)
    return int(layout[5:]), None, 1


def to_image(data, layout):
    """4bpp tiles -> rows of palette indices."""
    tw, th, units = parse_layout(layout)
    ntiles = len(data) // 32
    if th is None:
        th = -(-ntiles // tw)
    img = [[0] * (tw * 8 * units) for _ in range(th * 8)]
    for t in range(min(ntiles, tw * th * units)):
        u, r = divmod(t, tw * th)
        ty, tx = divmod(r, tw)
        for y in range(8):
            for x in range(8):
                b = data[t * 32 + y * 4 + x // 2]
                img[ty * 8 + y][(u * tw + tx) * 8 + x] = b >> 4 if x & 1 else b & 15
    return img


def from_image(img, layout, orig):
    """Inverse of to_image; bytes beyond the laid-out tiles keep `orig`."""
    tw, th, units = parse_layout(layout)
    ntiles = len(orig) // 32
    if th is None:
        th = -(-ntiles // tw)
    out = bytearray(orig)
    for t in range(min(ntiles, tw * th * units)):
        u, r = divmod(t, tw * th)
        ty, tx = divmod(r, tw)
        for y in range(8):
            for x in range(0, 8, 2):
                row = img[ty * 8 + y]
                X = (u * tw + tx) * 8 + x
                out[t * 32 + y * 4 + x // 2] = row[X] | row[X + 1] << 4
    return bytes(out)


def save_png(img, pal, path):
    from PIL import Image
    h, w = len(img), len(img[0])
    im = Image.new("RGB", (w, h))
    im.putdata([pal[i] for row in img for i in row])
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def load_png(path, pal, orig_img):
    """RGB png -> indices; a colour shared by several indices keeps the original pixel's index."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    w, h = im.size
    assert (w, h) == (len(orig_img[0]), len(orig_img)), f"{path}: {w}x{h}, expected {len(orig_img[0])}x{len(orig_img)}"
    px = list(im.getdata())
    img = []
    for y in range(h):
        row = []
        for x in range(w):
            c = px[y * w + x]
            idx = [i for i, p in enumerate(pal) if p == c]
            if not idx:
                raise ValueError(f"{path}: colour {c} at {x},{y} not in the palette")
            o = orig_img[y][x]
            row.append(o if o in idx else idx[0])
        img.append(row)
    return img


def rows(group=None):
    for tsv in sorted(GFX.glob("*.tsv")) if group is None else [GFX / f"{group}.tsv"]:
        for line in tsv.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                f = line.split("\t")
                size, _, n = f[1].partition("x")
                yield tsv.stem, int(f[0], 16), (int(size, 16), int(n or 1)), f[2], f[3]


def decode(rom, off, size):
    """size = (chunk size, chunks): a chain of streams back to back (caller 0x08000EA0 decodes 0x800 at a time).
    -> (data, end of the last stream)."""
    data = b""
    for _ in range(size[1]):
        d, off = kcomp.decompress(rom, off, size[0])
        data += d
    return data, off


def encode(data, size):
    return b"".join(kcomp.compress(data[i:i + size[0]]) for i in range(0, len(data), size[0]))


def edited_blocks(rom):
    """-> [(offset, old stream end, new compressed stream)] for every row whose png exists."""
    out = []
    for group, off, size, layout, png in rows():
        if not (ROOT / png).exists():
            continue
        data, end = decode(rom, off, size)
        oimg = to_image(data, layout)
        new = from_image(load_png(ROOT / png, load_pal(group), oimg), layout, data)
        if new != data:
            out.append((off, end, encode(new, size)))
    return out


def typeset(img, lines, box, fill, outline, top=None, top_rows=4, bold=True, lead=12, shadow=None, gap=1):
    """Draw lines centred in box = (x0, y0, x1, y1) with the dialogue font (fonts/en12.txt): core pixels plus a bold
    column, ink `fill` (`top` for the first `top_rows` core rows), and a 1 px `outline` ring (8-neighbour); a list
    of indices draws one ring per entry, innermost first. shadow = (index, dx, dy): the inked shape again, offset,
    under the text. gap = px between letters. lead = px from one line's core top to the next. Raises if a line is
    wider than the box (rings included)."""
    rings = outline if isinstance(outline, list) else [outline]
    pad = max(len(rings) - 1, 0)  # rings past the first need room inside the box
    import enfont
    font = {c: rows for c, rows in enfont.load()}
    x0, y0, x1, y1 = box
    desc = any("#" in font[c][8] + font[c][9] for c in lines[-1])
    total = lead * (len(lines) - 1) + (9 if desc else 7)  # cap top (core row 1) to the last inked row
    y = y0 + (y1 - y0 - total + 1) // 2 - 1
    ink = {}
    for ln in lines:
        widths = [len(font[c][0]) + bold + gap for c in ln]
        w = sum(widths) - gap
        if w + 2 * pad > x1 - x0:
            raise ValueError(f"{ln!r}: {w + 2 * pad} px > box {x1 - x0}")
        x = x0 + (x1 - x0 - w + 1) // 2
        for c, cw in zip(ln, widths):
            for r, row in enumerate(font[c]):
                for i, ch in enumerate(row):
                    if ch == "#":
                        for dx in range(1 + bold):
                            ink[(x + i + dx, y + r)] = top if top is not None and r < top_rows else fill
            x += cw
        y += lead
    for ring in rings:
        for (px, py) in list(ink):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    ink.setdefault((px + dx, py + dy), ring)
    if shadow:
        s, sx, sy = shadow
        for (px, py) in list(ink):
            if (px + sx, py + sy) not in ink and 0 <= py + sy < len(img) and 0 <= px + sx < len(img[0]):
                img[py + sy][px + sx] = s
    for (px, py), v in ink.items():
        img[py][px] = v
    return img


def slots(rom):
    """(start, end) of every row's original stream chain: the gfx stage's write zones."""
    return [(off, decode(rom, off, size)[1]) for _, off, size, _, _ in rows()]


def apply(rom):
    """Write edited blocks over their original streams; a block that outgrows its slot stops the build (no
    relocation yet: the encoder beat the original on all 258 unscrambled blocks it was tried on)."""
    for off, end, comp in edited_blocks(rom):
        if len(comp) > end - off:
            raise SystemExit(f"gfx block {off:X}: {len(comp)} bytes > slot {end - off}: add relocation")
        rom[off:off + len(comp)] = comp


def main():
    cmd = sys.argv[1]
    rom = next((ROOT / "rom").glob("*.gba")).read_bytes()
    if cmd == "export":
        group = sys.argv[2]
        pal = load_pal(group)
        for _, off, size, layout, _png in rows(group):
            data, _ = decode(rom, off, size)
            save_png(to_image(data, layout), pal, GFX / "orig" / group / f"{off:07X}.png")
        print("exported", group)
    elif cmd == "check":
        for off, end, comp in edited_blocks(rom):
            print(f"{off:07X} slot {end - off} new {len(comp)}{'  TOO BIG' if len(comp) > end - off else ''}")


if __name__ == "__main__":
    main()
