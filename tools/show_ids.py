"""Print batch, speaker, JP and EN for the given unit ids (review and fix-up helper).

python -X utf8 tools/show_ids.py 4823 48E3 [--ctx N]   (--ctx: also N neighbours either side, by batch order)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from batches import TL, index, read_tsv  # noqa: E402


def main(argv):
    ctx = int(argv[argv.index("--ctx") + 1]) if "--ctx" in argv else 0
    ids = [a for a in argv if not a.startswith("--") and not (argv.index(a) > 0 and argv[argv.index(a) - 1] == "--ctx")]
    entries = index()
    rows = [(p.stem, r) for p in sorted(TL.glob("b[0-9][0-9][0-9].tsv")) for r in read_tsv(p)]
    pos = {r[0]: n for n, (_, r) in enumerate(rows)}
    for i in ids:
        if i not in pos:
            print(f"{i}: not in any batch")
            continue
        n = pos[i]
        for k in range(max(0, n - ctx), min(len(rows), n + ctx + 1)):
            batch, r = rows[k]
            e = entries.get(r[0], {})
            mark = ">>" if k == n else "  "
            print(f"{mark} {batch} {r[0]} [{r[1]}] JP: {e.get('jp', '')!r}")
            print(f"   {' ' * len(batch)} EN: {e.get('en', '')!r}")
        print()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1:])
