# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool next (phase 1 recon done 2026-11-15). Last build: none.
- **Done:**
  - Step 0 (2026-11-15): template, rom.sha1, MesenCE 2.2.1 + GBA BIOS in tools/mesen, guard hook proven, pre-commit (tools/check.py) rejects a failing test, original ROM smoke-boots, scripted input and Lua probe ok.
  - Phase 1 (2026-11-15): no prior English patch; no SJIS. Graphics: kcomp decoder (`tools/kcomp.py`), resource tables (`tools/restables.py`), static sweep of every block (`tools/sweep.py`, 104 sheets) reviewed read-only by codex (`tools/codex_review.sh`) -> 170 text blocks in `docs/re/graphics_sweep.tsv`; tour list in `docs/re/graphics.md`. Script: message table 0x1860CE0 (2474 x 24-bit offsets from 0x18629DE), 1 byte per char = glyph index, FF end, 47.7k bytes; 12x12 2bpp frequency-ordered font at 0x18745E0 (`tools/font12.py`, `tools/fontstr.py`); name-entry buffer and charset (`docs/re/text.md`). Free space: 0x1FDF760-0x1FFFFFF trap-filled with FF, see compression.md.
- **Next:**
  1. Phase 2 debug tool (`references/emulator-qa.md` §Debug tool): scene list `tools/debug/scenes.tsv` + `tools/debug/warp.lua`. Reach: name entry (blank save), title, main menu, each menu item (ひとりでピッチ / あなたのピッチ / いっしょにピッチ / あつめて / 5th item), song start, results, game over, collection screens, options/save prompts, ending/credits. Find the game-state variable driving scene changes (watch the main-loop state byte when the menu changes) and the story/unlock flags in SRAM (`SRAM_V112`).
  2. Use `tools/lua/textobj.lua` on each warp to see which screens draw font text and which message ids; ひとりでピッチ draws ~320 glyphs at song start (`work/qa/tour0`, frame ~451): find what.
  3. Phase 4 prerequisites (not yet done): read the text interpreter (setup 0x08007440, char loop calling drawchar 0x080056CC from 0x0800775B) and list control codes / 2-byte glyph prefixes (suspects E7 F0 F1 F6 F7 F8 FA FD FE) with argument counts; build `tbl/jp.tbl` glyph index -> character by reading the font sheet (template-match first, then eyes; check look-alikes).
  4. English name entry needs Latin letters in the name charset (0x187EA84 has 0-9 A-F only) and a redrawn keyboard: engine work for phase 5.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) GUI keyboard input in tools/mesen not checked by hand; emu.py wrote default key mappings.
