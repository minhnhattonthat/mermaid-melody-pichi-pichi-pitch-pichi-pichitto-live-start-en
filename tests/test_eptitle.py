import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx_eptitle as g  # noqa: E402

ROM = ROOT / "rom" / "Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


@needs_rom
def test_title_maps_roundtrip_and_new_map_fits():
    rom = ROM.read_bytes()
    new = g.encode_map(g.rect_map())
    for n in range(1, 41):
        p = g.record(rom, n)
        cells, end = g.decode_map(rom, p)
        assert g.encode_map(cells) == rom[p:end]  # the game's own encoder: byte-exact
        assert len(new) <= end - p
        if n < 40:  # records are back to back: next header right after this stream
            assert g.record(rom, n + 1) == end + 5


def test_rect_map_decodes():
    cells = g.rect_map()
    assert g.decode_map(g.encode_map(cells), 0)[0] == cells
    x, y, w, h = g.RECT
    assert w * h < 128  # block = 128 tiles, tile 0 blank
