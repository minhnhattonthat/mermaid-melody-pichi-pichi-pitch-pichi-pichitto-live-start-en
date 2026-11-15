"""sweep.py: static graphics sweep. Decode every block in work/restables.tsv with kcomp (until the stream reaches the
next pointer), save it, and render labelled gba4 contact sheets for a read-only Japanese-cell review.

    python -X utf8 tools/sweep.py work/orig.gba [--tsv work/restables.tsv] [--out work/sweep] [--per 24]

Writes OUT/blocks/<off>.bin, OUT/index.tsv (offset, status, decoded size, stream end, sheet) and OUT/sheet_NNN.png.
Every pointer gets a status; skipped ones are printed with the reason (none dropped silently):
  exact  stream ended exactly at the next pointer   over  ended past it (block size unknown, kept)
  short  stopped at the next pointer mid-stream     err   invalid back-reference (not a kcomp stream)
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from kcomp import TABLE_OFF  # noqa: E402

MAXOUT = 0x40000
RAW_EXTRA = {0x1856272, 0x1F20B60, 0x1F68308}


def decode_to(rom, off, limit):
    """Decode a kcomp stream at off until the source reaches limit. Returns (data, end, status)."""
    flags = rom[off]
    p, out = off + 1, bytearray()
    try:
        while p < limit and len(out) < MAXOUT:
            c = rom[p]
            p += 1
            n = (c & 0x3F) + 1
            t = c >> 6
            if t == 0:
                out += rom[p:p + n]
                p += n
            elif t == 1:
                d = rom[p] + 1
                p += 1
                if d > len(out):
                    return bytes(out), p, "err"
                for _ in range(n + 1):
                    out.append(out[-d])
            else:
                if n > len(out):
                    return bytes(out), p, "err"
                for _ in range(2 if t == 2 else 1):
                    out.append(out[-n])
    except IndexError:
        return bytes(out), p, "err"
    status = "exact" if p == limit else ("over" if p > limit else "short")
    if flags & 1:
        if (flags >> 1) + 62 > 127:  # swap table would run past the 127-byte IWRAM image: not a real stream
            return bytes(out), p, "err"
        tab = rom[TABLE_OFF + (flags >> 1):TABLE_OFF + (flags >> 1) + 62]
        size = len(out)
        for b in range(0, size - size % 64, 64):
            for k in range(1, 63):
                j = b + tab[k - 1]
                out[b + k], out[j] = out[j], out[b + k]
    return bytes(out), p, status


def gba4(data, cols=32):
    """Grey 4bpp tile render, index 0 = black."""
    ntiles = len(data) // 32
    if not ntiles:
        return None
    rows = (ntiles + cols - 1) // cols
    w = min(ntiles, cols) * 8
    img = Image.new("L", (w, rows * 8))
    px = img.load()
    for t in range(ntiles):
        tx, ty = (t % cols) * 8, (t // cols) * 8
        for y in range(8):
            for x in range(8):
                b = data[t * 32 + y * 4 + x // 2]
                v = (b >> 4) if x & 1 else (b & 15)
                px[tx + x, ty + y] = v * 17
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("--tsv", default="work/restables.tsv")
    ap.add_argument("--out", default="work/sweep")
    ap.add_argument("--maxh", type=int, default=1400, help="sheet height in px before a new sheet starts")
    ap.add_argument("--zoom", type=int, default=2)
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    ptrs = sorted({int(line.split("\t")[0], 16) for line in open(a.tsv, encoding="utf-8") if line.strip()})
    os.makedirs(f"{a.out}/blocks", exist_ok=True)
    # pass 1: pointers that are not kcomp streams (false-positive records) must not cut the real block before them
    bad = set()
    for i, off in enumerate(ptrs):
        if decode_to(rom, off, ptrs[i + 1] if i + 1 < len(ptrs) else 0x1FDF760)[2] == "err":
            bad.add(off)
    good = [p for p in ptrs if p not in bad] + [0x1FDF760]
    nxt = {p: good[k + 1] for k, p in enumerate(good[:-1])}
    rows, counts = [], {}
    for off in ptrs:
        limit = nxt.get(off) or min(p for p in good if p > off)
        data, end, st = decode_to(rom, off, limit)
        counts[st] = counts.get(st, 0) + 1
        if st == "err" or len(data) < 32:
            print(f"skip {off:07X}: {st}, {len(data)} bytes decoded")
            rows.append([off, st, len(data), end, "-"])
            continue
        open(f"{a.out}/blocks/{off:07X}.bin", "wb").write(data)
        rows.append([off, st, len(data), end, None])
    # sheets: blocks stacked with a label strip, 256 px wide (32 tiles), each block capped at 64 tile rows
    sheet, y, n, items = None, 0, 0, []

    def flush():
        nonlocal sheet, y, n, items
        if not items:
            return
        img = Image.new("RGB", (256 + 70, y), (40, 0, 40))
        d = ImageDraw.Draw(img)
        for yy, label, im in items:
            img.paste(im.convert("RGB"), (70, yy))
            d.text((2, yy), label, fill=(255, 255, 0))
        img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST).save(f"{a.out}/sheet_{n:03d}.png")
        n += 1
        y, items = 0, []

    for r in rows:
        if r[4] == "-":
            continue
        im = gba4(open(f"{a.out}/blocks/{r[0]:07X}.bin", "rb").read()[:32 * 32 * 64])
        if im is None:
            r[4] = "-"
            continue
        if y + im.height + 4 > a.maxh:
            flush()
        items.append((y, f"{r[0]:07X}", im))
        r[4] = f"sheet_{n:03d}"
        y += im.height + 4
    flush()
    with open(f"{a.out}/index.tsv", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(f"{r[0]:07X}\t{r[1]}\t{r[2]:X}\t{r[3]:07X}\t{r[4]}\n")
    print(f"{len(ptrs)} pointers: {counts}; {n} sheets in {a.out}")
    # ROM regions no decoded block covers (code, sound, raw data, or graphics this table scan missed)
    spans = sorted((r[0], r[3]) for r in rows if r[1] != "err")
    pos, gaps = 0x10000, []
    for s, e in spans:
        if s - pos >= 0x4000:
            gaps.append((pos, s))
        pos = max(pos, e)
    if 0x1FDF760 - pos >= 0x4000:
        gaps.append((pos, 0x1FDF760))
    with open(f"{a.out}/gaps.tsv", "w", encoding="utf-8") as f:
        for s, e in gaps:
            f.write(f"{s:07X}\t{e:07X}\t{e - s:X}\n")
    print(f"{len(gaps)} uncovered regions >= 16 KiB, {sum(e - s for s, e in gaps):,} bytes -> {a.out}/gaps.tsv")
    # raw sheets of the uncovered regions, except the big ones that look like PCM audio in work/gapview.png
    # (guess by eye, 2026-11-15); 0x1856272 (raw digit font), 0x1F20B60 and 0x1F68308 are rendered anyway
    n0 = n
    for s, e in gaps:
        if e - s >= 0x30000 and s not in RAW_EXTRA:
            print(f"raw skip {s:07X}-{e:07X}: looks like audio")
            continue
        for o in range(s & ~0x1F, e, 0x8000):
            im = gba4(rom[o:min(o + 0x8000, e)])
            if im is None:
                continue
            if y + im.height + 4 > a.maxh:
                flush()
            items.append((y, f"raw {o:07X}", im))
            y += im.height + 4
    flush()
    print(f"raw sheets sheet_{n0:03d}..sheet_{n - 1:03d}")


if __name__ == "__main__":
    main()
