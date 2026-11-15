# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4. Extract next (phase 3 identity build done 2026-11-15). Last build: identity, sha1 d6bd3140... = dump, smoke ok.
- **Done:**
  - Step 0 (2026-11-15): template, rom.sha1, MesenCE 2.2.1 + GBA BIOS in tools/mesen, guard hook proven, pre-commit (tools/check.py) rejects a failing test, original ROM smoke-boots, scripted input and Lua probe ok.
  - Phase 1 (2026-11-15): no prior English patch; no SJIS. Graphics: kcomp decoder (`tools/kcomp.py`), resource tables (`tools/restables.py`), static sweep of every block (`tools/sweep.py`, 104 sheets) reviewed read-only by codex (`tools/codex_review.sh`) -> 170 text blocks in `docs/re/graphics_sweep.tsv`; tour list in `docs/re/graphics.md`. Script: message table 0x1860CE0 (2474 x 24-bit offsets from 0x18629DE), 1 byte per char = glyph index, FF end, 47.7k bytes; 12x12 2bpp frequency-ordered font at 0x18745E0 (`tools/font12.py`, `tools/fontstr.py`); name-entry buffer and charset (`docs/re/text.md`). Free space: 0x1FDF760-0x1FFFFFF trap-filled with FF, see compression.md.
  - Phase 2 (2026-11-15): scene dispatcher found (u8 0x0300287C, table 0x09D37060, 43 ids); `tools/debug/warp.lua` + `scenes.tsv` (50 entries: every scene id with a screen, menu items, modes, minigames, story episodes via `--var EP=1..39`, any message via `--var MSG=0..2473` in the leftover debug menu's message viewer). Save fixture made by the game (`tools/debug/make_save.py`). `tools/debug/regen.py` reached 50/50 from cold boot; shots `work/qa/warp/sheet/`, states `work/states/<name>.mss`. Notes: `docs/re/scenes.md`.
  - Phase 3 (2026-11-15): `build.py` -> `tools/msgtable.py` unpacks the message table into segments (one per distinct offset, bounds from the table since FF also appears as an argument) and repacks them with a rebuilt table; `tests/test_identity.py` asserts the output equals the dump, that later offsets follow a grown segment, and that overflow is refused. Build smoke-boots. Only the table/base literals in code point into the text region (`docs/re/text.md` §Layout).
- **Next:**
  1. Phase 4 extract: replace table segments with real string bounds once codes are known (msgtable.unpack docstring); text format + roundtrip + coverage tests over 0x18629DE..0x1872DD4.
  2. Phase 4 prerequisites: read the text interpreter (setup 0x08007454, char loop calling drawchar 0x080056CC from 0x0800775B) and list control codes / 2-byte glyph prefixes (suspects E7 F0 F1 F6 F7 F8 FA FD FE) with argument counts; build `tbl/jp.tbl` glyph index -> character from the font sheet. The debug message viewer (`SCENE='msgview' --var MSG=N`) shows any message for checking codes.
  3. English name entry needs Latin letters in the name charset (0x187EA84 has 0-9 A-F only) and a redrawn keyboard: engine work for phase 5.
  4. Debug tool gaps (add when needed): GOD mode for gameplay (life gauge address unknown), scenes 17/30/31 blank when warped, 止め絵チェック item, results after a real song (only empty results warp).
  5. Text coverage (phase 8): `tools/lua/msglog.lua` logs `TEXT <hex id>`; a msgview sweep over all ids plus story EP 1-39 covers the script.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) GUI keyboard input in tools/mesen not checked by hand; emu.py wrote default key mappings.
