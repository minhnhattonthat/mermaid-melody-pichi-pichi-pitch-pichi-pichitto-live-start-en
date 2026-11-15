"""gfx_chain.py: for each row of docs/re/graphics_sweep.tsv, find how its block decodes (one stream, or a chain of
0x800-byte streams that ends exactly at the next pointer) and render it as a grey 16-tile-wide sheet for reading.

    python -X utf8 tools/gfx_chain.py [OFFSET..]   -> work/gfx/chain.tsv (offset, size spec, tiles), work/gfx/sheets/<off>.png
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx  # noqa: E402
import kcomp  # noqa: E402

GREY = [(i * 17, i * 17, i * 17) for i in range(16)]


def nexts():
    out = {}
    for line in (ROOT / "work/sweep/index.tsv").read_text().splitlines():
        f = line.split("\t")
        out[f[0]] = (f[1], int(f[2], 16), int(f[3], 16))
    return out


def chain(rom, off, nxt):
    """-> n if n 0x800-byte streams end exactly at nxt, else None."""
    p, n = off, 0
    try:
        while p < nxt and n < 64:
            _, p = kcomp.decompress(rom, p, 0x800)
            n += 1
    except Exception:
        return None
    return n if p == nxt else None


def main():
    rom = (ROOT / "work/orig.gba").read_bytes()
    idx = nexts()
    want = [a.upper() for a in sys.argv[1:]]
    rows = []
    for line in (ROOT / "docs/re/graphics_sweep.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        off = line.split("\t")[0]
        if want and off not in want or off not in idx:
            continue
        st, size, nxt = idx[off]
        n = chain(rom, int(off, 16), nxt)
        spec = f"800x{n}" if n and n > 1 else f"{size:X}x1"
        csize = (0x800, n) if n and n > 1 else (size, 1)
        data, _ = gfx.decode(rom, int(off, 16), csize)
        gfx.save_png(gfx.to_image(data, "tiles16"), GREY, ROOT / f"work/gfx/sheets/{off}.png")
        (ROOT / f"work/gfx/blocks/{off}.bin").parent.mkdir(parents=True, exist_ok=True)
        (ROOT / f"work/gfx/blocks/{off}.bin").write_bytes(data)  # for vramfind.py
        rows.append(f"{off}\t{spec}\t{len(data) // 32}")
    out = ROOT / "work/gfx/chain.tsv"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
