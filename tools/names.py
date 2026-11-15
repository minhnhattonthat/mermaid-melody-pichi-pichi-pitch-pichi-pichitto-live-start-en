"""names.py: Latin name entry. The name keyboard keys keep their kana codes; the name charset (code -> glyph slot,
0x187EA84, docs/re/text.md) maps each key's code to the English letter drawn on it (gfx group `names`), so a name
prints in English wherever it shows (name screen, F6 in dialogue). Hiragana page = capitals, katakana page = small
letters; voiced codes (after the blanked ゛゜ keys) print their base key's letter.
    build stage `names` (build.py); python -X utf8 tools/names.py prints the key map.
"""
import struct
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enfont  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CHARSET, NCODES = 0x187EA84, 199
KATA = 0x5B  # katakana code = hiragana code + 0x5B (ア 71 = あ 16 + 5B; ヌ ヲ ゥ match too)
# (hiragana keys, page-1 letters, page-2 letters), in screen order: row 1, row 2, row 3, four groups a row.
# ー (code 67) is one key on both pages, so it has the same character on both.
KEYS = [("あいうえお", "ABCDE", "abcde"), ("たちつてと", "FGHIJ", "fghij"), ("まみむめも", "KLMNO", "klmno"),
        ("わをん", "PQR", "pqr"),
        ("かきくけこ", "STUVW", "stuvw"), ("なにぬねの", "XYZ.&", "xyz.&"), ("やゆよー", "!?'-", "!?'-"),
        ("ぁぃぅぇぉ", "01234", "01234"),
        ("さしすせそ", "56789", "56789"), ("はひふへほ", "♪♥★()", "♪♥★()"), ("らりるれろ", ",:/~+", ",:/~+"),
        ("っゃゅょ", "    ", "    ")]


def kana_codes(rom):
    """hiragana -> code, read through the charset and tbl/jp.tbl."""
    out = {}
    for c in range(NCODES):
        ch = GLYPHS.get(struct.unpack_from("<H", rom, CHARSET + 2 * c)[0])
        if ch and ("ぁ" <= ch <= "ゔ" or ch == "ー"):
            out.setdefault(ch, c)
    return out


def _glyphs():
    out = {}
    for line in (ROOT / "tbl/jp.tbl").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            out[int(k, 16)] = v
    return out


GLYPHS = _glyphs()


def keymap(rom):
    """-> {code: character} for every key code on both pages, voiced codes included."""
    codes = kana_codes(rom)
    m = {}
    for kana, upper, lower in KEYS:
        for k, u, lo in zip(kana, upper, lower):
            m[codes[k]] = u
            if k != "ー":
                m[codes[k] + KATA] = lo
    for ch, c in codes.items():  # が -> か's letter, ぱ -> は's
        base = unicodedata.normalize("NFD", ch)[0]
        if base != ch and c not in m:
            m[c] = m[codes[base]]
            m[c + KATA] = m[codes[base] + KATA]
    return m


def apply(rom):
    slots = enfont.slots(enfont.load())
    for c, ch in keymap(rom).items():
        struct.pack_into("<H", rom, CHARSET + 2 * c, slots[ch])


if __name__ == "__main__":
    rom = next((ROOT / "rom").glob("*.gba")).read_bytes()
    print(" ".join(f"{c:02X}={ch}" for c, ch in sorted(keymap(rom).items())))
