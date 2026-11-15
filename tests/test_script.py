"""Extraction tests (phase 4): roundtrip, coverage of the text region, script files in sync with the ROM."""
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import msgcodec  # noqa: E402
import msgtable  # noqa: E402
from msgparse import u24  # noqa: E402
from tbl import Table  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="no ROM dump in rom/")
JP = Table.load(ROOT / "tbl" / "jp.tbl")


@pytest.fixture(scope="module")
def orig():
    return build.ROM.read_bytes()


@pytest.fixture(scope="module")
def units(orig):
    return msgcodec.units(orig)


def test_table_has_no_duplicate_characters():
    dup = [v for v, n in Counter(JP.dec.values()).items() if n > 1]
    assert not dup, f"two codes read as the same character: {dup}"


@needs_rom
def test_every_unit_roundtrips(units):
    pos = {u["id"]: int(u["id"], 16) for u in units}
    for u in units:
        b, fix = msgcodec.encode(msgcodec.decode_unit(u, JP), JP)
        b = bytearray(b)
        for q, t in fix:
            b[q:q + 3] = pos[t].to_bytes(3, "little")
        assert bytes(b) == u["bytes"], u["id"]


@needs_rom
def test_units_cover_the_text_region(orig, units):
    d = msgcodec.text_data(orig)
    assert b"".join(u["bytes"] for u in units) == d
    assert orig[msgtable.BASE + len(d):msgtable.END] == bytes(msgtable.END - msgtable.BASE - len(d))
    starts = {int(u["id"], 16) for u in units}
    assert set(msgtable.offsets(orig)) <= starts
    assert sorted(i for u in units for i in u["ids"]) == list(range(msgtable.N))
    for u in units:  # every text pointer inside the bytecode lands on a unit start
        for raw, ptrs in u["tokens"]:
            assert all(u24(raw, q) in starts for q in ptrs), u["id"]


@needs_rom
def test_no_unmapped_glyph_in_used_text(units):
    bad = [u["id"] for u in units if u["used"] and "[" in msgcodec.decode_unit(u, JP)]
    assert not bad


@needs_rom
def test_script_files_match_the_rom(units):
    entries = msgcodec.load_script()
    assert [e["id"] for e in entries] == [u["id"] for u in units]
    for e, u in zip(entries, units):
        assert e["ids"] == u["ids"] and e["used"] == u["used"], e["id"]
        assert e["jp"] == msgcodec.decode_unit(u, JP), f"{e['id']}: jp out of date, re-run msgcodec.py dump --force"
