"""marker.py: marker text for the phase-5 marker build (build.py --marker).

Every used unit keeps its control codes and newlines; each run of Japanese glyphs becomes ASCII of the same pixel
width (12 px per Japanese glyph): the unit's first run starts with its id `[1A2B]`, the rest is a digit ruler
`1234567890...` (6 px a digit), so a box shows which unit it is and how far a line of that width reaches.
`--qa ID=text` style overrides: pass {unit id: en text} as `extra`."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enfont  # noqa: E402
from msgcodec import TOKEN  # noqa: E402

JP_PX = 12


def fill(prefix, px, widths):
    out, w = prefix, sum(widths[c] for c in prefix)
    k = 0
    while True:
        d = "1234567890"[k % 10]
        if w + widths[d] > px:
            return out
        out, w, k = out + d, w + widths[d], k + 1


def marker_text(uid, jp, widths):
    out, run, first = [], 0, True

    def flush():
        nonlocal run, first
        if run:
            out.append(fill(f"[{uid}]" if first else "", run * JP_PX, widths))
            first, run = False, 0

    for m in TOKEN.finditer(jp):
        if m[1] or m[3] or m[0] == "\n":
            flush()
            out.append(m[0])
        else:
            run += 1
    flush()
    return "".join(out)


def marked(entries, extra=None):
    widths = {ch: enfont.width(rows) for ch, rows in enfont.load()}
    out = []
    for e in entries:
        en = (extra or {}).get(e["id"]) or (marker_text(e["id"], e["jp"], widths) if e["used"] else "")
        out.append(dict(e, en=en))
    return out


if __name__ == "__main__":
    import msgcodec
    for e in marked(msgcodec.load_script())[:int(sys.argv[1]) if sys.argv[1:] else 5]:
        print(e["id"], repr(e["jp"][:60]), "->", repr(e["en"][:80]))
