"""Latin name entry (tools/names.py): every key code prints an English glyph, the two pages differ only in case."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import enfont  # noqa: E402
import names  # noqa: E402

ROM = next((Path(__file__).resolve().parents[1] / "rom").glob("*.gba")).read_bytes()


def test_every_key_has_a_glyph():
    slots = enfont.slots(enfont.load())
    m = names.keymap(ROM)
    assert len(m) == 2 * (0x67 - 0x16) + 1  # hiragana 16-66 + ー 67 + katakana 71-C1
    assert all(ch in slots for ch in m.values())


def test_pages_are_cases():
    m = names.keymap(ROM)
    for c in range(0x16, 0x67):
        assert m[c + names.KATA] == m[c].lower()
    assert "".join(sorted(ch for ch in m.values() if ch.isalpha())) .count("A") == 1
