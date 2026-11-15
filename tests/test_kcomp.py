import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import kcomp  # noqa: E402

ROM = ROOT / "rom" / "Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"


def test_selftest():
    kcomp.selftest()


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")
def test_menu_portrait_blocks_chain():
    # Main-menu portrait: 9 blocks of 0x800, each stream ends where the next starts (verified against VRAM).
    rom = ROM.read_bytes()
    starts = [0x1712CF7, 0x1713354, 0x1713A34, 0x1714068, 0x171476A, 0x1714DB9, 0x1715411, 0x1715A53, 0x1716023]
    for a, b in zip(starts, starts[1:]):
        data, end = kcomp.decompress(rom, a, 0x800)
        assert len(data) == 0x800 and end == b
