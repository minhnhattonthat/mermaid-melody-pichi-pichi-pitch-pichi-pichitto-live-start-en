import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]
import build  # noqa: E402
import writelog  # noqa: E402


def test_english_build_writes_only_its_zones():
    orig = build.ROM.read_bytes()
    log = []
    new = build.build(orig, "en", None, log)
    assert {w[3] for w in log} == {"text", "boxes", "vwf", "gfx", "names"}
    assert writelog.check(orig, new, log) == []
    # a stage writing outside its zones, or a byte changed with no write, fails
    bad = bytearray(new)
    bad[0x100] ^= 0xFF
    assert writelog.check(orig, bytes(bad), log)
    stray = [(0x100, orig[0x100:0x101], bytes(bad[0x100:0x101]), "boxes")]
    assert any("outside its zones" in e for e in writelog.check(orig, bytes(bad), log + stray))
