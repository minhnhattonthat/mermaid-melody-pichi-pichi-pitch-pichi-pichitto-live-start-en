"""msgboxes.py: text boxes seen in game -> docs/re/msgboxes.tsv (id, W, H, flags), a budget source for tools/boxes.py
where the event scripts give none (ids it would otherwise guess).

    python -X utf8 tools/msgboxes.py [LOGDIR ...]      default work/qa/tour3/runs

Reads "MSG <frame> <id> obj=.. lr=.. flags=<hex> sp=.. W=<w> H=<h>" lines (tools/lua/msglog.lua) from every log.txt
under the dirs, skipping debug runs (msgview, debug_menu: their debug box is not the game's). Keeps the narrowest W
and lowest H seen per id. Merges into the existing file, so runs from several tours add up.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/re/msgboxes.tsv"
SKIP = {"msgview", "debug_menu"}
LINE = re.compile(r"^MSG \d+ (\d+) .*flags=([0-9A-F]+) .*W=(\d+) H=(\d+)", re.M)


def load():
    """-> {id: (W, H, flags)}"""
    if not OUT.exists():
        return {}
    rows = [ln.split("\t") for ln in OUT.read_text(encoding="utf-8").splitlines() if ln and ln[0] != "#"]
    return {int(i): (int(w), int(h), int(f, 16)) for i, w, h, f in rows}


def main():
    dirs = [Path(d) for d in sys.argv[1:]] or [ROOT / "work/qa/tour3/runs"]
    seen = load()
    for d in dirs:
        for log in d.rglob("log.txt"):
            if SKIP & set(log.parts):
                continue
            for mid, flags, w, h in LINE.findall(log.read_text(encoding="utf-8", errors="replace")):
                mid, w, h = int(mid), int(w), int(h)
                old = seen.get(mid)
                seen[mid] = (min(w, old[0]), min(h, old[1]), int(flags, 16)) if old else (w, h, int(flags, 16))
    OUT.write_text("# message id\tW (cells)\tH (cells)\tflags (hex): narrowest box seen in game, tools/msgboxes.py\n"
                   + "".join(f"{i}\t{w}\t{h}\t{f:X}\n" for i, (w, h, f) in sorted(seen.items())),
                   encoding="utf-8", newline="\n")
    print(f"{len(seen)} ids in {OUT}")


if __name__ == "__main__":
    main()
