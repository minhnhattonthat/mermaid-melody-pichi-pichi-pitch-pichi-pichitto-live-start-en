"""build.py: build build/mermaid_en.gba from the pinned dump.

    python -X utf8 build.py [--lang jp] [--marker] [--qa ID=text ...] [--out PATH]

Packs script/msg_*.json (each unit's `lang` text, falling back to jp) into the message regions and rebuilds the
message table and the text pointers inside the bytecode (tools/msgcodec.py). With only jp text the output equals the
dump (tests/test_identity.py). An English build encodes en text with the VWF font (tools/enfont.py, tbl/en.tbl),
jp fallback text with tbl/jp.tbl, widens story bubbles to fit (tools/boxes.py) and patches in the VWF (tools/vwf.py). --marker replaces every used unit with
marker text (tools/marker.py); --qa ID=text overrides one unit's en text (unit id, e.g. 1A2B).
Every build also writes OUT.writes.log; `python -X utf8 tools/writelog.py OUT` checks it (tests/test_writelog.py)."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import boxes  # noqa: E402
import check_rom  # noqa: E402
import enfont  # noqa: E402
import gfx  # noqa: E402
import gfx_eptitle  # noqa: E402
import gfx_songs  # noqa: E402
import marker  # noqa: E402
import msgcodec  # noqa: E402
import msgtable  # noqa: E402
import names  # noqa: E402
import vwf  # noqa: E402
import writelog  # noqa: E402
from tbl import Table  # noqa: E402

ROM = ROOT / "rom" / "Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"
OUT = ROOT / "build" / "mermaid_en.gba"
# old message region first (the identity layout), then the free space after the VWF code
REGIONS = ((msgtable.BASE, msgtable.END), (vwf.FREE_END, 0x2000000))


def build(orig, lang="en", entries=None, log=None):
    """log: a list that receives every write as (offset, orig, new, stage) (tools/writelog.py checks them)."""
    rom = bytearray(orig)
    entries = entries if entries is not None else msgcodec.load_script()
    jp = Table.load(ROOT / "tbl" / "jp.tbl")
    if lang == "jp":
        msgcodec.pack(rom, entries, jp, "jp")
        return bytes(rom)

    def stage(name, f):
        before = bytes(rom) if log is not None else None
        f()
        if log is not None:
            log.extend(writelog.runs(before, rom, name))

    stage("text", lambda: msgcodec.pack(rom, entries, Table(enfont.tbl_lines()), lang, REGIONS, fallback=jp))
    stage("boxes", lambda: boxes.grow(rom, entries, lang))
    stage("vwf", lambda: vwf.apply(rom))
    stage("gfx", lambda: gfx.apply(rom))
    stage("names", lambda: names.apply(rom))
    stage("maps", lambda: gfx_eptitle.apply(rom))
    stage("objs", lambda: gfx_songs.apply(rom))
    stage("raw", lambda: gfx.apply_raw(rom))
    return bytes(rom)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en")
    ap.add_argument("--marker", action="store_true")
    ap.add_argument("--qa", action="append", default=[], help="ID=text: en text for one unit")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    check_rom.check()
    entries = msgcodec.load_script()
    extra = {k: v.replace("\\n", "\n") for k, v in (q.split("=", 1) for q in a.qa)}
    if a.marker:
        entries = marker.marked(entries, extra)
    elif extra:
        entries = [dict(e, en=extra.get(e["id"], e.get("en", ""))) for e in entries]
    log = []
    out = build(ROM.read_bytes(), a.lang, entries, log)
    path = Path(a.out)
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(out)
    writelog.save(f"{path}.writes.log", log)
    print(f"wrote {path} ({len(out)} bytes, {len(log)} writes in {path.name}.writes.log)")


if __name__ == "__main__":
    main()
