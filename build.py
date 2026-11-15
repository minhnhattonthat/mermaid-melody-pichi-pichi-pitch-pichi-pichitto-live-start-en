"""build.py: build build/mermaid_en.gba from the pinned dump.

    python -X utf8 build.py [--lang jp] [--marker] [--qa ID=text ...] [--out PATH]

Packs script/msg_*.json (each unit's `lang` text, falling back to jp) into the message regions and rebuilds the
message table and the text pointers inside the bytecode (tools/msgcodec.py). With only jp text the output equals the
dump (tests/test_identity.py). An English build encodes en text with the VWF font (tools/enfont.py, tbl/en.tbl),
jp fallback text with tbl/jp.tbl, widens story bubbles to fit (tools/boxes.py) and patches in the VWF (tools/vwf.py). --marker replaces every used unit with
marker text (tools/marker.py); --qa ID=text overrides one unit's en text (unit id, e.g. 1A2B)."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import boxes  # noqa: E402
import check_rom  # noqa: E402
import enfont  # noqa: E402
import marker  # noqa: E402
import msgcodec  # noqa: E402
import msgtable  # noqa: E402
import vwf  # noqa: E402
from tbl import Table  # noqa: E402

ROM = ROOT / "rom" / "Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"
OUT = ROOT / "build" / "mermaid_en.gba"
# old message region first (the identity layout), then the free space after the VWF code
REGIONS = ((msgtable.BASE, msgtable.END), (vwf.FREE_END, 0x2000000))


def build(orig, lang="en", entries=None):
    rom = bytearray(orig)
    entries = entries if entries is not None else msgcodec.load_script()
    jp = Table.load(ROOT / "tbl" / "jp.tbl")
    if lang == "jp":
        msgcodec.pack(rom, entries, jp, "jp")
        return bytes(rom)
    msgcodec.pack(rom, entries, Table(enfont.tbl_lines()), lang, REGIONS, fallback=jp)
    boxes.grow(rom, entries, lang)
    vwf.apply(rom)
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
    out = build(ROM.read_bytes(), a.lang, entries)
    path = Path(a.out)
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(out)
    print(f"wrote {path} ({len(out)} bytes)")


if __name__ == "__main__":
    main()
