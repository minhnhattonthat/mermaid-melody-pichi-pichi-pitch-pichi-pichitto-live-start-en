"""Write log for the build: every byte run each build stage changes, and the zones each stage may touch.

build.py diffs the ROM around each stage (text, boxes, vwf) and writes `<out>.writes.log` in romdiff.py's format
(`OFFSET ORIG_HEX NEW_HEX stage`). check() then runs romdiff's checks (orig bytes match the dump, no write overwritten
by a later stage, no overlap, nothing changed outside a write) plus: each stage writes only inside its own zones.

    python -X utf8 tools/writelog.py [BUILT]   (default build/mermaid_en.gba and its .writes.log; exit 1 on errors)
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import boxes  # noqa: E402
import gfx  # noqa: E402
import msgtable  # noqa: E402
import names  # noqa: E402
import romdiff  # noqa: E402
import vwf  # noqa: E402

# (lo, hi) half-open file offsets each stage may write
ZONES = {
    "text": [(msgtable.TAB, msgtable.END), (vwf.FREE_END, 0x2000000)],  # pointer table + old region, free space
    "boxes": [boxes.EVENTS],  # bubble geometry in the event scripts
    "vwf": [(vwf.BLIT_SITE, vwf.BLIT_SITE + 10), (vwf.BLIT_POOL, vwf.BLIT_POOL + 4),
            (vwf.DRAWCHAR - 0x08000000, vwf.DRAWCHAR - 0x08000000 + 8),
            (vwf.FONT - 0x08000000, vwf.ATTR), (vwf.ATTR, vwf.ATTR + 2 * vwf.NWIDTH), (vwf.CODE, vwf.FREE_END)],
    "names": [(names.CHARSET, names.CHARSET + 2 * names.NCODES)],  # name charset: kana key codes -> Latin
}


def runs(before, after, name):
    """Changed byte runs as romdiff writes (offset, orig, new, name). Bytes past the end of before count as FF."""
    a = np.frombuffer(bytes(before).ljust(len(after), b"\xff"), np.uint8)
    b = np.frombuffer(bytes(after), np.uint8)
    diff = np.flatnonzero(a != b)
    if not len(diff):
        return []
    cut = np.flatnonzero(np.diff(diff) > 1)
    starts = np.r_[diff[0], diff[cut + 1]]
    ends = np.r_[diff[cut], diff[-1]] + 1
    return [(int(s), bytes(a[s:e]), bytes(b[s:e]), name) for s, e in zip(starts, ends)]


def save(path, writes):
    Path(path).write_text("".join(f"{o:07X} {x.hex()} {y.hex()} {n}\n" for o, x, y, n in writes), encoding="utf-8")


def check(orig, new, writes):
    errs, _ = romdiff.check(orig, new, set(), writes)
    zones = dict(ZONES, gfx=gfx.slots(orig))
    for off, x, _, name in writes:
        if not any(lo <= off and off + len(x) <= hi for lo, hi in zones.get(name, [])):
            errs.append(f"0x{off:07X}: {name} writes {len(x)} bytes outside its zones")
    return errs


def main(argv):
    built = Path(argv[0]) if argv else ROOT / "build" / "mermaid_en.gba"
    import build  # noqa: E402  (repo root is on sys.path when run from there)
    errs = check(build.ROM.read_bytes(), built.read_bytes(), romdiff.load_writes(f"{built}.writes.log"))
    print("\n".join(errs[:60]) or f"{built.name}: every write in its zone, orig bytes match, no overlap")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    sys.exit(main(sys.argv[1:]))
