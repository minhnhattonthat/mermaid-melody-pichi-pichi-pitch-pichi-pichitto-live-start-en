"""Reviewer pairs file for translation batches (docs/reviewer-brief.md).

    python -X utf8 tools/pairs.py b001 [b002 ...]   -> work/qa/review/<batch>.txt

Each entry: `>> id | speaker | limit | JP` then `EN` (the batch is in story order, so neighbours are the context).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TL = ROOT / "work" / "tl"
OUT = ROOT / "work" / "qa" / "review"


def rows(path):
    return [l.split("\t") for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def pairs(batch):
    en = {r[0]: r[1] if len(r) > 1 else "" for r in rows(TL / f"{batch}.out.tsv")}
    lines = []
    for r in rows(TL / f"{batch}.tsv"):
        uid, spk, _form, limit, jp = (r + [""] * 5)[:5]
        lines += [f">> {uid} | {spk} | {limit} | {jp}", en.get(uid, "(MISSING)"), ""]
    return "\n".join(lines)


def main(argv):
    if not argv:
        sys.exit(__doc__)
    OUT.mkdir(parents=True, exist_ok=True)
    for b in argv:
        (OUT / f"{b}.txt").write_text(pairs(b), encoding="utf-8")
        print(OUT / f"{b}.txt")


if __name__ == "__main__":
    main(sys.argv[1:])
