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
  follows, *and* the text pointers inside the bytecode (below). **verified**: `build.py` packs `script/` through
  `tools/msgcodec.py` and the output equals the dump (`tests/test_identity.py`); a ROM with an early unit grown by 4
  glyphs shows msg 1407 and 1612 (`{call:}` speaker names) identically to the original in `msgview`.
- **Interpreter** (phase 4, read from the code): per-character step 0x08007454; getchar 0x08004978 reads one byte
  through a pointer stack (text object +0, depth at +0x2F; read16/24/32 at 0x4990/0x49B0/0x49D4). Byte < 0xF0 is a
  glyph; 0xF0-0xFF dispatch through the table at 0x09D36F50. Handlers set [0x03002A20+0x222]: 0 next byte, 1 draw
  glyph [+0x14], 2 stop for this frame.

## Control codes (tools/msgparse.py; argument counts read from each handler)
| Code | Handler | Bytes after | Meaning / text form |
|---|---|---|---|
| 00-EF | drawchar 0x080056CC | 0 | glyph = code (`tbl/jp.tbl`) |
| F0-F5 xx | 0x080058CC | 1 | glyph (code-F0)<<8 \| xx (codes 0x0F0-0x1F1 used) |
| F6 b | 0x08005D58 | 1 + by sub b&1F: 2: +1 if b&80; 4: 2 (+1 if b&80, +1 more if b&C0=C0); 5: 2; 7: 1; 12: 3; else 0 | push a generated string (number, name, message 0x0A-0x0E) `{F6:..}` |
| F7 | 0x080061B8 | 0 | wait for a button `{wait}` |
| F8 o24 | 0x08005B3C | 3 | call text at BASE+o (push), returns at its FF `{call:@id}`: speaker names, character names |
| F9 o24 | 0x08005BFC | 3 | goto `{goto:@id}` |
| FA s | 0x080063A8 | 1 + sub | s >= 0x80: colour (s&7F); s = FF: scene callback n + 1 byte (RAM table 0x030063EC); s < 0x1C: table 0x09D36EA8, extra bytes 0 1 4 0 0 * 0 1 * 0 0 1 2 * 3 1 1 1 0 0 0 6 * 0 0 5 0 0 for s = 0..27; `{FA:..}` |
| FA 05 | 0x08006010 | b; +1 if b&80; b=FE: one o24 per choice (jump); b=FF: end choice | choice menu |
| FA 08 / FA 16 | 0x08005BC8 / 0x08005BE4 | o24 table indexed by RAM 0x03002C5B / 0x03002C5C (jump) | branch |
| FA 0D n | 0x080062BC | n x o24 (random jump) | |
| FA 0E o24, FA 19 w16 o24, FA 15 o24 o24 | | pointers relocated | conditional jumps |
| FB a32 f | 0x08005CA4 | 5 | print number at RAM a (format f) `{FB:..}` |
| FC b [c] | 0x080058F4 | 1, or 2 when b&C0 = 0 | cursor position `{FC:..}` |
| FD b | 0x080059F0 | 1 | glyph spacing: bit0 8 px, bit7 16 px, else 12 `{FD:..}` |
| FE | 0x08005AD8 | 0 | newline `\n` |
| FF | 0x08005A4C | 0 | end (or return from a call) `{end}` |
- Jump tables with a runtime index (FA 05 FE, FA 08, FA 16) have no stored length: msgparse reads entries until it
  reaches the lowest target, which in this ROM always follows the table. **verified** by coverage: parsing from every
  table offset and every pointer target gives 0 errors and no byte that is both an opcode and an argument; the only
  bytes nothing reaches (773, 26 runs: unused strings, a blank 9-line fill, 0x00..0x24) parse cleanly as strings too.
- Used: FA 06 x526 (page break), FA colour x612, FA 0B/0C/11, F6 x18, FB x13 (RAM 0x030037B0.., 0x030064BC..).
  No FA 02 / 0D / 0E / 19 in the script.
- Text form and units: `tools/msgcodec.py` docstring. 1617 units (2474 ids): table offsets + pointer targets +
  unreached runs (`used: false`, keep as is).

## Font
- 12x12, 2 bpp, 36 bytes per glyph (3 bytes per row, 4 px per byte, low bits = left pixel), ROM 0x18745E0
  (literal 0x098745E0 at 0x08004F94). Glyph order = frequency in the script: 00 blank, 01 `…`, 02 `い`, 03 `、`,
  04 `た` ... (`python -X utf8 tools/font12.py work/orig.gba out.png [--start N --count M]`). **verified** (render reads
  as kana/kanji; `あ` glyph 0x0F read by drawchar at 0x098747FC).
- `tbl/jp.tbl`: the 498 glyphs the script uses (0x000-0x1F1, all of them). Kana, digits, ー/－ from the name charset
  table; the other 300 read off `tools/font_sheet.py` sheets, then checked on kanji/katakana/Latin word lists from the
  decoded script (fixed look-alikes: 質 土 貴 連 鷲 邉 暮 蒼, `l` not `1`). **verified** for kana (charset) and by
  reading; 0x167 (circled glyph after 編曲： in the song credits) is a **guess** `Ⓒ`. Glyphs above 0x1F1 (to ~0x45B)
  are unused by the script; check them only if a menu or graphic draws them.
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
