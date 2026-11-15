import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import enfont  # noqa: E402
import marker  # noqa: E402
import msgcodec  # noqa: E402
import msgtable  # noqa: E402
import vwf  # noqa: E402
from tbl import Table  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="no ROM dump in rom/")
GLYPHS = enfont.load()


def test_font_glyphs_sit_on_the_baseline_and_fit_the_shifted_cell():
    for ch, rows in GLYPHS:
        assert len(rows[0]) + 1 <= enfont.MAX_INK, ch
        if ch.isascii() and ch.isalnum():
            assert "#" in rows[7] and "#" not in rows[0], ch
    have = {ch for ch, _ in GLYPHS}
    assert set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,!?'\"-:;()&~…") <= have


def test_slots_unique_digits_kept_and_reserved_free():
    slots = enfont.slots(GLYPHS)
    assert len(set(slots.values())) == len(slots)
    assert [slots[str(d)] for d in range(10)] == enfont.DIGIT_SLOTS
    assert not ({0x00, 0xAC} & set(slots.values()))
    assert max(slots.values()) < 0xF0


def test_en_tbl_is_in_sync_with_the_font():
    assert (ROOT / "tbl" / "en.tbl").read_text(encoding="utf-8").splitlines() == enfont.tbl_lines()


def test_cell_shading():
    px = enfont.pixels([".#."] + ["..."] * 9)
    assert px[1][1] == 3 and px[1][2] == 2 and px[1][0] == 0


def test_marker_keeps_codes_and_stays_within_the_japanese_width():
    widths = {ch: enfont.width(rows) for ch, rows in GLYPHS}
    out = marker.marker_text("1A2B", "{call:@2B8C}あいう\nかきくけこ{wait}", widths)
    assert out.startswith("{call:@2B8C}[1A2B]") and out.endswith("{wait}") and "\n" in out
    first, second = out[len("{call:@2B8C}"):-len("{wait}")].split("\n")
    assert sum(widths[c] for c in first) <= 36 and sum(widths[c] for c in second) <= 60


def test_pack_spills_into_the_next_region_keeping_fallthrough_runs_together():
    jp = Table.load(ROOT / "tbl" / "jp.tbl")
    base = msgtable.BASE
    rom = bytearray(base + 64)
    entries = [{"id": "0000", "ids": [0], "jp": "あい{end}"},
               {"id": "0003", "ids": [1], "jp": "あいう"},  # no terminator: falls through to 0007
               {"id": "0007", "ids": list(range(2, msgtable.N)), "jp": "あ{end}"}]
    rom += bytes(3 * msgtable.N)
    msgcodec.TAB, tab = base + 64, msgcodec.TAB
    try:
        msgcodec.pack(rom, entries, jp, "jp", regions=((base, base + 6), (base + 32, base + 64)))
    finally:
        msgcodec.TAB = tab
    offs = [int.from_bytes(rom[base + 64 + 3 * i:base + 67 + 3 * i], "little") for i in range(3)]
    assert offs == [0, 32, 35]  # 0003 did not fit after 0000, so 0003+0007 moved together


@needs_rom
def test_english_build_patches_vwf_and_draws_marker_text():
    orig = build.ROM.read_bytes()
    entries = marker.marked(msgcodec.load_script())
    rom = build.build(orig, "en", entries)
    assert rom[0x56CC:0x56D0] == bytes.fromhex("004a1047")
    entry = struct.unpack_from("<I", rom, 0x56D0)[0]
    assert entry == (0x08000000 + vwf.CODE) | 1
    slots = enfont.slots(GLYPHS)
    assert rom[vwf.WIDTHS + slots["m"]] == 7 and rom[vwf.WIDTHS + 0] == 0
    assert struct.unpack_from("<H", rom, vwf.ATTR + 2 * slots["!"])[0] & 0xC000 == 0
    assert len(rom) == len(orig)
