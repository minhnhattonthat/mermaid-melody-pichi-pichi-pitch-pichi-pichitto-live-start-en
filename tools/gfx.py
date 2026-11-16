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
    pal = [rgb(raw[i] | raw[i + 1] << 8) for i in range(0, 32, 2)]
    # a shared colour makes load_png keep the original index there, so text erased to a same-coloured index survives
    # and shows under another palette: a block drawn under several palettes needs a .pal with 16 distinct colours
    # (menu.pal repeats 7-9, harmless: those captions only ever use OBJ pal 15)
    assert len(set(pal)) == 16 or group == "menu", f"gfx/{group}.pal repeats a colour"
    return pal


def parse_layout(layout):
    """-> (tile columns per unit, tile rows, units, units per image row). A tile sheet is one unit.
    objWxH*N/R: N units of WxH tiles, R to an image row (default all N side by side)."""
    if layout.startswith("obj"):
        wh, n = layout[3:].split("*")
        n, _, r = n.partition("/")
        w, h = wh.split("x")
        return int(w), int(h), int(n), int(r or n)
    return int(layout[5:]), None, 1, 1


def _place(t, tw, th, per_row):
    """tile index -> (tile x, tile y) in the image."""
    u, r = divmod(t, tw * th)
    ty, tx = divmod(r, tw)
    return (u % per_row) * tw + tx, (u // per_row) * th + ty


def to_image(data, layout):
    """4bpp tiles -> rows of palette indices."""
    tw, th, units, per_row = parse_layout(layout)
    ntiles = len(data) // 32
    if th is None:
        th = -(-ntiles // tw)
    img = [[0] * (tw * 8 * per_row) for _ in range(th * 8 * -(-units // per_row))]
    for t in range(min(ntiles, tw * th * units)):
        X, Y = _place(t, tw, th, per_row)
        for y in range(8):
            for x in range(8):
                b = data[t * 32 + y * 4 + x // 2]
                img[Y * 8 + y][X * 8 + x] = b >> 4 if x & 1 else b & 15
    return img


def from_image(img, layout, orig):
    """Inverse of to_image; bytes beyond the laid-out tiles keep `orig`."""
    tw, th, units, per_row = parse_layout(layout)
    ntiles = len(orig) // 32
    if th is None:
        th = -(-ntiles // tw)
    out = bytearray(orig)
    for t in range(min(ntiles, tw * th * units)):
        tX, tY = _place(t, tw, th, per_row)
        for y in range(8):
            for x in range(0, 8, 2):
                row = img[tY * 8 + y]
                X = tX * 8 + x
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


def chunk_starts(rom, off, size):
    """File offset of each stream in a chain."""
    starts = []
    for _ in range(size[1]):
        starts.append(off)
        off = kcomp.decompress(rom, off, size[0])[1]
    return starts


def edited_blocks(rom, forks=False):
    """-> [(offset, old stream end, new compressed chain, [(old chunk start, new chunk offset in the chain)])] for
    every row whose png exists (forks=True: only FORKS rows, else only the others). A chunk may have its own pointer
    (179BC34: the episode grid reads the whole chain, the cursor each chunk), so plan() repoints every chunk that
    moves."""
    out = []
    for group, off, size, layout, png in rows():
        if not (ROOT / png).exists() or (group in FORKS) != forks:
            continue
        data, end = decode(rom, off, size)
        oimg = to_image(data, layout)
        new = from_image(load_png(ROOT / png, load_pal(group), oimg), layout, data)
        if new != data:
            parts = [kcomp.compress(new[i:i + size[0]]) for i in range(0, len(new), size[0])]
            rel = [sum(map(len, parts[:k])) for k in range(len(parts))]
            out.append((off, end, b"".join(parts), list(zip(chunk_starts(rom, off, size), rel))))
    return out


# en12's m and w have 1 px gaps between stems that the bold column fills (a solid block): wider cores for bold typeset.
_B = "......."
BOLD_WIDE = {
    "m": [_B, _B, _B, "######.", "#..#..#", "#..#..#", "#..#..#", "#..#..#", _B, _B],
    "w": [_B, _B, _B, "#.....#", "#.....#", "#..#..#", "#..#..#", ".#...#.", _B, _B],
}


def typeset(img, lines, box, fill, outline, top=None, top_rows=4, bold=True, lead=12, shadow=None, gap=1, heavy=False):
    """Draw lines centred in box = (x0, y0, x1, y1) with the dialogue font (fonts/en12.txt): core pixels plus a bold
    column, ink `fill` (`top` for the first `top_rows` core rows), and a 1 px `outline` ring (8-neighbour); a list
    of indices draws one ring per entry, innermost first. shadow = (index, dx, dy): the inked shape again, offset,
    under the text. gap = px between letters. lead = px from one line's core top to the next. heavy: every core
    pixel also inks the one below (2 px horizontal strokes, for art the game scales down). Raises if a line is
    wider than the box (rings included)."""
    rings = outline if isinstance(outline, list) else [outline]
    pad = max(len(rings) - 1, 0)  # rings past the first need room inside the box
    import enfont
    font = {c: rows for c, rows in enfont.load()}
    if bold:
        font.update(BOLD_WIDE)
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
                            for dy in range(1 + heavy):
                                ink[(x + i + dx, y + r + dy)] = top if top is not None and r < top_rows else fill
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


RELOC_TOP = 0x2000000  # blocks that outgrow their slot go here, downward (0x00 padding; text fills upward from 0x1FE0200)
# A block shared by two scenes, redrawn for one: group -> (resource table, records, record, literal). The new chain
# and a copy of the table (that record -> the new chain) go below the relocated blocks; only the literal (the one
# scene's table pointer) moves to the copy, so the other scene keeps the original (which another, non-fork group may
# still edit in place: `cohead`).
FORKS = {"names": (0x16F6CC8, 197, 39, 0x10E10)}  # name keyboard; compose keeps kana (docs/re/graphics.md)


def pointers(rom, off):
    """File offsets of every 32-bit pointer 0x08000000|off (resource tables hold them unaligned)."""
    pat, hits, i = (0x08000000 | off).to_bytes(4, "little"), [], rom.find((0x08000000 | off).to_bytes(4, "little"))
    while 0 <= i < 0x1FDF760:  # original data only: past it is the patch's own text and code
        hits.append(i)
        i = rom.find(pat, i + 1)
    return hits


def plan(rom):
    """-> [(offset, old stream end, new chain, target, [(pointer offset, new value)])]; target = offset when the
    chain fits in place, else a spot below RELOC_TOP. Every chunk that lands elsewhere gets its pointers moved."""
    out, top = [], RELOC_TOP
    for off, end, comp, chunks in edited_blocks(rom):
        at = off
        if len(comp) > end - off:
            top -= len(comp)
            at = top
            if not pointers(rom, off):
                raise SystemExit(f"gfx block {off:X}: {len(comp)} bytes > slot {end - off} and no pointer to move it")
        moves = [(p, 0x08000000 | (at + rel)) for start, rel in chunks if at + rel != start for p in pointers(rom, start)]
        out.append((off, end, comp, at, moves))
    return out


def fork_plan(rom, top):
    """-> [(new chain at, chain, table copy at, table, records, record, literal)] for FORKS rows, below `top`."""
    out, of = [], {off: FORKS[g] for g, off, *_ in rows() if g in FORKS}
    for off, _, comp, _ in edited_blocks(rom, forks=True):
        table, n, rec, lit = of[off]
        at = top = top - len(comp)
        copy = top = top - 5 * n
        out.append((at, comp, copy, table, n, rec, lit))
    return out


def low(p):
    """Lowest relocated offset of a plan (RELOC_TOP when nothing moved)."""
    return min([at for off, _, _, at, _ in p if at != off], default=RELOC_TOP)


def slots(rom):
    """The gfx stage's write zones: every row's original stream chain, relocated streams and moved pointers, forks."""
    zones = [(off, decode(rom, off, size)[1]) for _, off, size, _, _ in rows()]
    p = plan(rom)
    for off, _, comp, at, moves in p:
        if at != off:
            zones.append((at, at + len(comp)))
        zones += [(ptr, ptr + 4) for ptr, _ in moves]
    for at, comp, copy, _, n, _, lit in fork_plan(rom, low(p)):
        zones += [(at, at + len(comp)), (copy, copy + 5 * n), (lit, lit + 4)]
    return zones


def apply(rom):
    """Write edited chains over their original streams, or below RELOC_TOP when they outgrow the slot (the old
    stream stays, unused), and repoint every chunk that moved. Then the forks: their chain and table copy (taken
    after the moves, so it carries them) below that, and the scene's literal -> the copy."""
    p = plan(rom)
    forks = fork_plan(rom, low(p))
    for off, end, comp, at, moves in p:
        if at != off and any(rom[at:at + len(comp)]):
            raise SystemExit(f"gfx block {off:X}: relocation spot {at:X} is not free (text grew into it?)")
        rom[at:at + len(comp)] = comp
        for ptr, v in moves:
            rom[ptr:ptr + 4] = v.to_bytes(4, "little")
    for at, comp, copy, table, n, rec, lit in forks:
        if any(rom[copy:at + len(comp)]):
            raise SystemExit(f"gfx fork at {copy:X}: not free (text grew into it?)")
        t = bytearray(rom[table:table + 5 * n])
        t[5 * rec:5 * rec + 4] = (0x08000000 | at).to_bytes(4, "little")
        rom[at:at + len(comp)] = comp
        rom[copy:copy + 5 * n] = t
        rom[lit:lit + 4] = (0x08000000 | copy).to_bytes(4, "little")


def raw_rows():
    """gfx/*.raw (written by generators such as gfx_clear.py, which check each row fits its old bytes):
    [(file offset, new bytes)] written in place."""
    lines = [ln for f in sorted(GFX.glob("*.raw")) for ln in f.read_text(encoding="utf-8").splitlines()]
    return [(int(a, 16), bytes.fromhex(b)) for a, b in (ln.split("\t")[:2] for ln in lines if ln and ln[0] != "#")]


def apply_raw(rom):
    """Build stage raw: palette words, map records and other small in-place patches."""
    for at, new in raw_rows():
        rom[at:at + len(new)] = new


def raw_zones():
    return [(at, at + len(new)) for at, new in raw_rows()]


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
        p = plan(rom)
        for off, end, comp, at, moves in p:
            print(f"{off:07X} slot {end - off} new {len(comp)}{f'  moved to {at:07X}' if at != off else ''}"
                  f"{f', {len(moves)} pointers' if moves else ''}")
        for at, comp, copy, table, _, rec, lit in fork_plan(rom, low(p)):
            print(f"fork {len(comp)} bytes at {at:07X}, table {table:X} copy at {copy:07X} (record {rec}), literal {lit:X}")


if __name__ == "__main__":
    main()
