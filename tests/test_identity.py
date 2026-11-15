import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import msgtable  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="no ROM dump in rom/")


@needs_rom
def test_identity_build_is_byte_identical():
    orig = build.ROM.read_bytes()
    assert build.build(orig) == orig


@needs_rom
def test_repack_moves_strings_and_table_follows():
    # Growing one segment must shift every later offset by the same amount and keep each id's bytes.
    orig = build.ROM.read_bytes()
    segs = msgtable.unpack(orig)
    k = len(segs) // 2
    segs[k] = (segs[k][0], b"\x00" + segs[k][1])
    rom = bytearray(orig)
    msgtable.pack(rom, segs)
    a, b = msgtable.offsets(orig), msgtable.offsets(rom)
    split = msgtable.offsets(orig)[segs[k][0][0]] if segs[k][0] else None
    assert all(nb - na == (1 if split is not None and na > split else 0) for na, nb in zip(a, b))
    assert msgtable.unpack(bytes(rom))[k + 1][1] == segs[k + 1][1]


def test_pack_rejects_overflow():
    rom = bytearray(msgtable.END + 16)
    with pytest.raises(ValueError):
        msgtable.pack(rom, [(list(range(msgtable.N)), bytes(msgtable.END - msgtable.BASE + 1))])
