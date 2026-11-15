import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx  # noqa: E402
import gfx_songs as g  # noqa: E402

ROM = ROOT / "rom" / "Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


def test_pieces_tile_the_line_left_to_right():
    for n in range(1, 9):
        body = g.pieces(n)
        xs = []
        for k in range(n):
            a, b, c = struct.unpack_from("<HHH", body, 6 * k)
            assert (a >> 2 & 3, b & 3) == (1, 2)  # 32x16
            assert ((a >> 6) ^ 0x200) - 0x200 == g.Y
            xs.append(((b >> 6) ^ 0x200) - 0x200)
            assert c == k // 4 * 64 + k % 4 * 4
        assert xs == [-16 * n + 32 * k for k in range(n)]


@needs_rom
def test_titles_are_chunks_of_the_chain_and_lists_only_shrink():
    rom = ROM.read_bytes()
    (_, off, size, _, _), = gfx.rows("songs")
    assert set(g.TITLES) <= set(gfx.chunk_starts(rom, off, size))
    for p, new in g.rows():
        assert len(new) <= 2 + 6 * rom[p] and new[1] == rom[p + 1]
