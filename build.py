"""build.py: build build/mermaid_en.gba from the pinned dump.

    python -X utf8 build.py

Phase 3 (identity): the message table and strings go through unpack -> pack unchanged; the output must equal the dump
(tests/test_identity.py)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402
import msgtable  # noqa: E402

ROM = ROOT / "rom" / "Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"
OUT = ROOT / "build" / "mermaid_en.gba"


def build(orig):
    rom = bytearray(orig)
    msgtable.pack(rom, msgtable.unpack(orig))
    return bytes(rom)


def main():
    check_rom.check()
    out = build(ROM.read_bytes())
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(out)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(out)} bytes)")


if __name__ == "__main__":
    main()
