import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx  # noqa: E402
import kcomp  # noqa: E402

ROM = ROOT / "rom" / "Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


@needs_rom
def test_compress_roundtrip_real_blocks():
    rom = ROM.read_bytes()
    for off in (0x1712CF7, 0x1708763):
        data, end = kcomp.decompress(rom, off, 0x800)
        comp = kcomp.compress(data)
        assert kcomp.decompress(comp, 0, 0x800)[0] == data
        assert len(comp) <= end - off


def test_layout_roundtrip():
    data = bytes(range(256)) * 16  # 128 tiles
    for layout in ("obj16x4*2", "tiles32", "tiles8"):
        assert gfx.from_image(gfx.to_image(data, layout), layout, data) == data


@needs_rom
def test_no_pointerless_stream_after_a_row():
    """A stream right after a row's chain with no pointer of its own is read as the chain's tail (179E33F behind the
    episode numbers): a shorter in-place write would shift it, so the row must take it in (gfx/epnum.tsv)."""
    import kcomp
    rom = ROM.read_bytes()
    for _, off, size, _, _ in gfx.rows():
        end = gfx.decode(rom, off, size)[1]
        if gfx.pointers(rom, end):
            continue
        try:
            kcomp.decompress(rom, end, size[0])
        except Exception:
            continue
        raise AssertionError(f"{off:X}: pointerless stream at {end:X} after the chain")


@needs_rom
def test_every_row_fits_its_slot_or_moves():
    rom = ROM.read_bytes()
    low = gfx.RELOC_TOP
    for off, end, comp, at, moves in gfx.plan(rom):
        assert len(comp) <= end - off if at == off else moves and at < gfx.RELOC_TOP, f"{off:X}"
        if at != off:
            low = min(low, at)
    assert not any(rom[low:gfx.RELOC_TOP])  # relocations land in the 0x00 padding
