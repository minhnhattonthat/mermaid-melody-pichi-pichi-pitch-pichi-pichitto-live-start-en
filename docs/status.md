# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate (not started; phase 5 done 2026-11-15). Last build: `build.py` -> build/mermaid_en.gba sha1 e9d8c53a (no English yet, smoke ok); marker build `build.py --marker --out build/marker.gba`.
- **Done:**
  - Step 0 (2026-11-15): template, rom.sha1, MesenCE 2.2.1 + GBA BIOS in tools/mesen, guard hook proven, pre-commit (tools/check.py) rejects a failing test, original ROM smoke-boots, scripted input and Lua probe ok.
  - Phase 1 (2026-11-15): no prior English patch; no SJIS. Graphics: kcomp decoder (`tools/kcomp.py`), resource tables (`tools/restables.py`), static sweep of every block (`tools/sweep.py`, 104 sheets) reviewed read-only by codex (`tools/codex_review.sh`) -> 170 text blocks in `docs/re/graphics_sweep.tsv`; tour list in `docs/re/graphics.md`. Script: message table 0x1860CE0 (2474 x 24-bit offsets from 0x18629DE), 1 byte per char = glyph index, FF end, 47.7k bytes; 12x12 2bpp frequency-ordered font at 0x18745E0 (`tools/font12.py`, `tools/fontstr.py`); name-entry buffer and charset (`docs/re/text.md`). Free space: 0x1FDF760-0x1FFFFFF trap-filled with FF, see compression.md.
  - Phase 2 (2026-11-15): scene dispatcher found (u8 0x0300287C, table 0x09D37060, 43 ids); `tools/debug/warp.lua` + `scenes.tsv` (50 entries: every scene id with a screen, menu items, modes, minigames, story episodes via `--var EP=1..39`, any message via `--var MSG=0..2473` in the leftover debug menu's message viewer). Save fixture made by the game (`tools/debug/make_save.py`). `tools/debug/regen.py` reached 50/50 from cold boot; shots `work/qa/warp/sheet/`, states `work/states/<name>.mss`. Notes: `docs/re/scenes.md`. Story text advances with `--mash 30` (emu.py A-mash).
  - Phase 3 (2026-11-15): `build.py` -> `tools/msgtable.py` unpacks/repacks the message table; `tests/test_identity.py`.
  - Phase 4 (2026-11-15): control codes (`docs/re/text.md`, `tools/msgparse.py`); `tbl/jp.tbl`; `tools/msgcodec.py` -> `script/msg_00..16.json` (1617 units), roundtrip + relocation tests.
  - Phase 5 (2026-11-15): English font `fonts/en12.txt` + VWF patch `tools/vwf.py`; text packs into two regions; `build.py --marker` / `--qa ID=text`; box probes `tools/lua/boxlog.lua`, `tilelog.lua`. Width gate: `tools/boxes.py` (bubble geometry from the event scripts, range budgets, fit lint, bubble auto-grow in the English build), `tests/test_fit.py` (Japanese calibration 0 errors; English script must have 0 errors: this gates every commit). `python -X utf8 tools/boxes.py [--warn]` prints the report. All facts: `docs/re/vwf.md` §Boxes, §Width gate.
- **Next (phase 6):**
  1. Read `$SKILL/references/translation.md`; write the style guide / translator brief, glossary (names per D1/D2: official English names where they exist), batches under `work/tl/`. Give every row its budget from `boxes.budget()` (kind, px limit, lines) so translators wrap to it; the batch check = `tools/boxes.py` lint on the batch.
  2. Speaker names and character names are call-target units with no message id (`2A5B` るちあ, `2AE7` 海斗, `2B32` マーメイド, ...): translate them once, as glossary names; `2B8C`/`2B92` are the name-tag brackets `【`/`】` (keep the `{FA:0C0008}`/`{FA:0C0088}` codes).
  3. `{FD:01}..{FD:00}` = furigana/half-width runs (e.g. 堂本{FD:01}（どうもと）{FD:00}): the VWF only works at spacing 12, so English text should drop the furigana and these codes.
  4. Lyrics (256-305, 512-1023): default romaji (see Waiting on the user); lint limit 180 px, 1 line.
  5. Units with a guess budget (unobserved ids) warn only: confirm their boxes in the phase-8 tour.
- **Later:**
  - English name entry needs Latin letters in the name charset (0x187EA84 has 0-9 A-F only) and a redrawn keyboard; F6 name width in the lint is a 60 px guess until then.
  - Debug tool gaps (add when needed): GOD mode for gameplay (life gauge address unknown), scenes 17/30/31 blank when warped, 止め絵チェック item, results after a real song (only empty results warp).
  - Text coverage (phase 8): `tools/lua/msglog.lua` logs `TEXT <hex id>`; msgview sweep over all ids plus story EP 1-39 (with `--mash`).
  - Glyph 0x167 (circled, song credits) read as `Ⓒ`, a guess: zoom it in game when the credits are QA'd.
- **Open bugs:** none.
- **Known limits:** msgview's debug box garbles rows when a message runs past 7 lines with no page break (real pages are <= 4 lines; story boxes clean). Japanese fallback text in an English build draws as junk (its glyph slots hold English letters): every used unit needs English.
- **Waiting on the user:** (non-blocking) song lyrics (msgs 256-305, 512-1023, karaoke strip): default plan = romaji so they match the sung audio and the colour sweep; English meaning is the alternative. (non-blocking) GUI keyboard input in tools/mesen not checked by hand; emu.py wrote default key mappings.
