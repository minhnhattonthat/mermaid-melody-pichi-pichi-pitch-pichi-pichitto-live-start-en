"""Text coverage per script unit (textcover.py works per address; here a unit has several message ids).

    python -X utf8 tools/cover.py [LOGDIR ...] [--waive docs/text_unshown.tsv] [--list]

A used unit counts as shown when any of its message ids appears as "TEXT <hex id>" in a log.txt under a LOGDIR
(tools/lua/msglog.lua; default dirs: work/qa/tour/runs, work/qa/cover). Prints unshown, unwaived units grouped by
file; exit 1 if any. Waiver lines: "unit<TAB>reason" (no reason = not waived).
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def shown_ids(dirs):
    ids = set()
    for d in dirs:
        for log in Path(d).rglob("log.txt"):
            ids |= {int(m, 16) for m in re.findall(r"^TEXT ([0-9A-Fa-f]+)", log.read_text(errors="replace"), re.M)}
    return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="*", default=[str(ROOT / "work/qa/tour/runs"), str(ROOT / "work/qa/cover")])
    ap.add_argument("--waive", default=str(ROOT / "docs/text_unshown.tsv"))
    ap.add_argument("--list", action="store_true", help="print every unshown unit, not only counts per file")
    a = ap.parse_args()
    seen = shown_ids([d for d in a.dirs if Path(d).exists()])
    waived = {}
    if Path(a.waive).exists():
        for line in Path(a.waive).read_text(encoding="utf-8").splitlines():
            f = line.split("\t")
            if len(f) > 1 and f[1].strip() and not line.startswith("#"):
                waived[f[0]] = f[1]
    total = left = 0
    for fn in sorted((ROOT / "script").glob("msg_*.json")):
        miss = []
        for u in json.loads(fn.read_text(encoding="utf-8")):
            if not u["used"]:
                continue
            total += 1
            if not seen & set(u["ids"]) and u["id"] not in waived:
                miss.append(u)
        left += len(miss)
        if miss:
            print(f"{fn.name}: {len(miss)} unshown, ids {miss[0]['ids'][:1]}..{miss[-1]['ids'][-1:]}")
            if a.list:
                for u in miss:
                    print(f"  {u['id']} ids {u['ids']} {u['en'][:60]!r}")
    print(f"{total - left}/{total} used units shown or waived")
    sys.exit(1 if left else 0)


if __name__ == "__main__":
    main()
