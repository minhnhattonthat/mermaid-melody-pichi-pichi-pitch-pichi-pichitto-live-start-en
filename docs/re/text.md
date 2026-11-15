# Font-drawn text (script, font, name entry)

## Script (messages)
- **Message table** at ROM 0x1860CE0: 2474 entries x 3 bytes, each a 24-bit little-endian offset from the string base
  0x18629DE (code literals 0x09860CE0 / 0x098629DE at 0x08007440's pool). Message id = u16 at text object +0x18
  (second id at +0x1A, same table). Pointer = 0x098629DE + offset, written to text object +0 (IWRAM 0x03002C60 for the
  link-check box). **verified**: watch.lua on 0x03002C60 -> setter pc 0x080074B0; id 1028 = 0x1865252 =
  `つうしんせつぞくをしらべています` (link-check screen, `work/qa/tobj`).
- **Strings**: one byte per character = glyph index in the frequency-ordered font below; `FF` ends a string.
  Range 0x18629DE..0x1872DD3 (last string end), 47,702 bytes of codes, then zeros. 2413 of 2473 offsets ascending.
  **verified** (decoded the link-check string glyph by glyph against the screen).
- **Layout** (phase 3 scan): 1545 distinct offsets for 2474 ids (929 ids share an offset); text data ends
  0x1872DD4, zero pad to 0x1872DE0. Scanning to the next FF from each sorted offset misses the next offset 310 times
  (FF as a control argument, e.g. `07 FF FA FF`; bytes no id reaches, e.g. 0x00..0x24): FF alone does not bound a
  string. The only 32-bit ROM literals into 0x1860CE0..0x1872DE0 sitting in code are the table and base (7 + 13 uses
  in 0x5B58..0x7A88); other hits are in graphics data. So strings can be repacked or moved anywhere if the table
  follows. **verified**: `build.py` repacks by table segments (`tools/msgtable.py`) and the output equals the dump
  (`tests/test_identity.py`).
- **Control codes / escapes**: all byte values 00-FE occur. Byte frequency falls with the code (font is frequency
  sorted) except E7 (166), F0 (53), F1 (307), F6 (18), F7 (249), F8 (1980), FA (720), FD (65), FE (1438): these are
  control codes and/or 2-byte prefixes for glyphs above 0xFF (font has ~1100 glyphs). **guess**; phase 4 must read
  the interpreter (`0x08007440` sets up a message; per-char loop calls drawchar from 0x0800775B / 0x08006B0C) and
  list each code with its argument count before the roundtrip test.
- 00 starts many strings (3376 uses): blank glyph 0 or a control. **guess**.

## Font
- 12x12, 2 bpp, 36 bytes per glyph (3 bytes per row, 4 px per byte, low bits = left pixel), ROM 0x18745E0
  (literal 0x098745E0 at 0x08004F94). Glyph order = frequency in the script: 00 blank, 01 `…`, 02 `い`, 03 `、`,
  04 `た` ... (`python -X utf8 tools/font12.py work/orig.gba out.png [--start N --count M]`). **verified** (render reads
  as kana/kanji; `あ` glyph 0x0F read by drawchar at 0x098747FC).
- Per-code attribute table at 0x187E2B8 (u16, read by drawchar 0x080056CC; bit 15 takes another path at 0x0800587E;
  low bits look like width/offset steps of 0x200). 0x187E2B8..0x187EA84 = 998 entries. **guess** (meaning of bits).
- Byte -> 4bpp pixel expansion tables at 0x1872DE0 (literal 0x09872DE0) and 0x1873FE0. **verified** (read by the
  blitter at 0x08005088).
- drawchar(textobj r0, code r1) at 0x080056CC calls the glyph blitter 0x08004E68, which builds 4bpp rows on the stack
  and stores them into BG tiles (0x080051B2.., VRAM 0x06000800+ on the name screen). Proportional advance per glyph.

## Name entry
- Name buffer: u16 codes at IWRAM 0x03003BDE (`あいき` = 1, 2, 7: gojuon order from 1). **verified** (RAM diff,
  `work/qa/ne2`, route `1100 -;6 a;30 -;6 right;20 -;6 a;30 -;6 down;20 -;6 a`).
- Name charset table at 0x187EA84: 199 u16 entries, code -> glyph index: 00-0F `0-9A-F`, 10 space, 11 `ー`, 12 `+`,
  13 `!`, 14 `?`, 15 `⇔`, 16.. hiragana `あいうえお..` (with voiced and small kana), 6A.. katakana, circled digits.
  (`tools/font12.py --codes`). Name glyphs are drawn on BG0 (charblock 0, map 0xF000). **verified** (render).
- The name keyboard itself (kana grid) and header `STARTボタン けってい / SELECTボタン きりかえ` are graphics.
- Reaching it: boot with a blank save (`--sav work/states/blank.sav`, 32 KiB of FF); state `work/states/nameentry.mss`
  is *not* a name-entry state (it was made with the old save): rebuild it in phase 2.

## Where font text shows (tour so far)
- Link-check box `つうしんせつぞくをしらべています` (main menu, one Down then A: あなたのピッチ, link mode).
- Something at song start in ひとりでピッチ (320 drawchar calls at frame ~451 of `work/qa/tour0`): not yet seen on a
  shot; phase 2 tour.
