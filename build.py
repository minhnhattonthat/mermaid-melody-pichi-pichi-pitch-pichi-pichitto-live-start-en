"""build.py: build build/mermaid_en.gba from the pinned dump.

    python -X utf8 build.py [--lang jp]

Packs script/msg_*.json (each unit's `lang` text, falling back to jp) into the message region and rebuilds the
message table and the text pointers inside the bytecode (tools/msgcodec.py). With only jp text the output equals the
dump (tests/test_identity.py)."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402
import msgcodec  # noqa: E402
from tbl import Table  # noqa: E402

ROM = ROOT / "rom" / "Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"
OUT = ROOT / "build" / "mermaid_en.gba"


def build(orig, lang="en", entries=None):
    rom = bytearray(orig)
    # shortcut: en text still encodes through jp.tbl until the English font exists (phase 5)
    msgcodec.pack(rom, entries if entries is not None else msgcodec.load_script(), Table.load(ROOT / "tbl" / "jp.tbl"),
                  lang)
    return bytes(rom)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en")
    a = ap.parse_args()
    check_rom.check()
    out = build(ROM.read_bytes(), a.lang)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(out)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(out)} bytes)")


if __name__ == "__main__":
    main()
