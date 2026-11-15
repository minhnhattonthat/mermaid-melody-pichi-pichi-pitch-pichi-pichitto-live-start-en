"""Graphics-sweep rows still Japanese: jp-text/mixed rows of docs/re/graphics_sweep.tsv with neither a gfx/*.tsv row
nor a docs/gfx_waived.tsv line. Exit 1 if any (release gate).

    python -X utf8 tools/gfx_left.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def offsets(path, col=0):
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            out.add(line.split("\t")[col].strip().upper())
    return out


def left():
    done = set().union(*(offsets(f) for f in (ROOT / "gfx").glob("*.tsv"))) | offsets(ROOT / "docs/gfx_waived.tsv")
    rows = [l.split("\t") for l in (ROOT / "docs/re/graphics_sweep.tsv").read_text(encoding="utf-8").splitlines()]
    return [r for r in rows if len(r) > 3 and r[1] in ("jp-text", "mixed") and r[0].split()[-1].upper() not in done]


if __name__ == "__main__":
    rows = left()
    for r in rows:
        print(r[0], r[1], r[3][:80])
    print(f"{len(rows)} graphics rows still Japanese")
    sys.exit(1 if rows else 0)
