"""Width gate: box budgets, fit lint and bubble auto-grow (tools/boxes.py, docs/re/vwf.md §Boxes)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import boxes  # noqa: E402
import build  # noqa: E402
import msgcodec  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="no ROM dump in rom/")
LONG = "{FA:FF0201}Hee hee... so you came after all, did you?\n{FA:FF0200}{end}"  # 202 px: needs W 27


@pytest.fixture(scope="module")
def rom():
    return build.ROM.read_bytes()


@pytest.fixture(scope="module")
def entries():
    return msgcodec.load_script()


def with_en(entries, uid, text):
    return [dict(e, en=text) if e["id"] == uid else e for e in entries]


@needs_rom
def test_bubbles_parse_the_story_boxes(rom):
    bub = boxes.bubbles(rom)
    assert len(bub) == 799 and 1480 <= min(bub) and max(bub) <= 2473
    assert all(6 <= w <= 28 and col >= 1 and col + w <= 29 and 2 <= h <= 14 for _, col, _, w, h, _ in bub.values())
    assert bub[1531][1:5] == (4, 11, 20, 4)  # EP 1 villain bubble, as boxlog.lua saw it
    assert bub[1760][1:] == (5, 11, 20, 6, 0) and boxes.fixed(bub[1760])  # EP 13 Aqua Regina, no tail: never grows


@needs_rom
def test_japanese_script_fits_its_budgets(rom, entries):
    # calibration: the measured budgets must hold the original text
    jp = boxes.lint(entries, "jp", boxes.bubbles(rom), boxes.song_boxes(rom))
    assert [r for r in jp if r[0] == "error"] == []


@needs_rom
def test_english_script_fits_its_budgets(rom, entries):
    errors = [r for r in boxes.lint(entries, "en", boxes.bubbles(rom), boxes.song_boxes(rom)) if r[0] == "error"]
    assert errors == [], "\n".join(map(str, errors[:20]))


@needs_rom
def test_song_boxes_parse_and_grow(rom, entries):
    song = boxes.song_boxes(rom)  # in-song dialogue (op 6), 121 messages; EP 1 1544 as msglog.lua saw it
    assert len(song) == 121 and song[1544][0][1:] == (5, 11, 18, 6)
    assert all(boxes.SONG_COLS[0] <= c and c + w <= boxes.SONG_COLS[1] for v in song.values() for _, c, _, w, _ in v)
    out = bytearray(rom)
    bare = [dict(e, en="") for e in entries]
    unit = next(e["id"] for e in entries if 1544 in e["ids"])
    assert boxes.grow(out, with_en(bare, unit, "This song... I used to sing it all the time{end}")) == 1
    assert struct.unpack_from("<HH", out, song[1544][0][0] + 8) == (4 << 8 | 11, 20 << 8 | 6)  # capped: W 20 at col 4


@needs_rom
def test_lint_flags_overflow_and_extra_lines(rom, entries):
    bub = boxes.bubbles(rom)
    ok = boxes.lint(with_en(entries, "6689", LONG), "en", bub)
    assert [r for r in ok if r[1] == "6689"] == []
    wide = boxes.lint(with_en(entries, "6689", LONG.replace("did you?", "did you, little mermaid?")), "en", bub)
    assert [r[0] for r in wide if r[1] == "6689"] == ["error"]
    tall = boxes.lint(with_en(entries, "6689", "a\nb\nc\nd{end}"), "en", bub)  # H 4 box, Japanese 1 line
    assert [r[0] for r in tall if r[1] == "6689"] == ["error"]


@needs_rom
def test_grow_widens_only_bubbles_that_need_it(rom, entries):
    out = bytearray(rom)
    bare = [dict(e, en="") for e in entries]  # the shipped script has English: test on none, then one long line
    assert boxes.grow(out, bare) == 0 and out == rom  # no English text: nothing moves
    assert boxes.grow(out, with_en(bare, "6689", LONG)) == 1
    off = boxes.bubbles(rom)[1531][0]
    assert struct.unpack_from("<HH", out, off + 2) == (2 << 8 | 11, 27 << 8 | 4)  # W 27, col 4 -> 2
    assert sum(a != b for a, b in zip(out, rom)) <= 2
