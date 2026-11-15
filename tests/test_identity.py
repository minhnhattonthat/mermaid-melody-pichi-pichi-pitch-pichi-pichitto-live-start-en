import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import msgcodec  # noqa: E402
import msgtable  # noqa: E402
from tbl import Table  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="no ROM dump in rom/")
JP = Table.load(ROOT / "tbl" / "jp.tbl")


@needs_rom
def test_identity_build_is_byte_identical():
    orig = build.ROM.read_bytes()
    assert build.build(orig, "jp") == orig


@needs_rom
def test_repack_relocates_table_and_text_pointers():
    # Grow one unit by a glyph: every later unit must move by one byte, and the table and every embedded
    # call/goto/jump pointer must follow, so the repacked ROM decodes to the same text everywhere else.
    orig = build.ROM.read_bytes()
    entries = msgcodec.load_script()
    k = next(i for i, e in enumerate(entries) if e["used"] and e["ids"] and i > len(entries) // 4)
    entries[k] = dict(entries[k], jp="あ" + entries[k]["jp"])
    rom = bytearray(orig)
    msgcodec.pack(rom, entries, JP)
    split = int(entries[k]["id"], 16)
    assert [o + (o > split) for o in msgtable.offsets(orig)] == msgtable.offsets(rom)
    old, new = msgcodec.units(orig), msgcodec.units(bytes(rom))
    assert len(old) == len(new)
    moved = {a["id"]: b["id"] for a, b in zip(old, new)}
    assert all(int(moved[i], 16) == int(i, 16) + (int(i, 16) > split) for i in moved)
    for i, (a, b) in enumerate(zip(old, new)):
        want = re.sub(r"@([0-9A-F]{4})", lambda m: "@" + moved[m[1]], msgcodec.decode_unit(a, JP))
        assert msgcodec.decode_unit(b, JP) == ("あ" + want if i == k else want)


def test_pack_rejects_overflow():
    rom = bytearray(msgtable.END + 16)
    big = [{"id": "0000", "ids": list(range(msgtable.N)), "jp": "あ" * (msgtable.END - msgtable.BASE + 1)}]
    with pytest.raises(ValueError):
        msgcodec.pack(rom, big, JP)
