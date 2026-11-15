import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402

ROM = ROOT / "rom" / "Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


@needs_rom
def test_rom_hash_matches():
    check_rom.check()  # sys.exit on mismatch fails the test
