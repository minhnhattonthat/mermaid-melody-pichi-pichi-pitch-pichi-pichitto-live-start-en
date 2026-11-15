# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator (phase 7 done 2026-11-15). Last build: `build.py` -> build/mermaid_en.gba (2026-11-15 session 11, sha1 ad9c2669; smoke ok, write log clean, check 39 passed); marker build `build.py --marker --out build/marker.gba`.
- **Phase 8 progress (2026-11-15, session 11):** all 40 episode titles English (group `eptitle`, build stage `maps`:
  the per-episode BG1 map records at 0x1881720 decoded and rewritten to one 24x5 rect; `docs/re/graphics.md`
  §eptitle). `nomosaic.lua` fixed (shadow 0x030000B0). New `tools/lua/execlog.lua`. Digits-only sweep rows
  (1F0857E 1F0B17B 1F11200..1F11FD4 1D0CA42) and 179BEF6..179DE22 (inside the `epnum` chain) need no redraw.
  **Lead for the parked maps** (minigame panels 1C00CFF.., prompt 1C0657A, poster banner 1CE3D71): their BG maps
  are "not in ROM": likely the same run-stream format (`gfx_eptitle.decode_map`, writer 0x08001FFC): run
  `tools/lua/execlog.lua --var PC_LO=0x03000BF0` while the screen loads; r12 = the record. Then give the text cells
  unique tiles by rewriting the record (as `maps` does) instead of fighting shared checker tiles.
- **Phase 8 progress (2026-11-15, session 10):** room sub-screens reached (routes + dumps in `docs/re/graphics.md`
  §Room sub-screens). Groups `roomsel` (mascot banner -> Place which mascot?, checked) and `roombtn` (Secret / No
  mascot / No poster, unseen) English, `tools/gfx_roomsel.py`. Minigame title panels drawn by `tools/gfx_minigame.py`
  but PARKED (`gfx/minipanel.tsv` rows commented): their BG map shares checker tiles; find the map's source first.
  Fixed `gfx_bg.Layer.write` missing tiles shared with unchanged cells. Remaining sweep rows (~40 after session 11,
  list with `docs/re/graphics_sweep.tsv` minus `gfx/*.tsv`): song
  titles (OBJ list table unknown), minigame logos/panels, title logo 1703236 (D5: official romanized logo exists ->
  redraw), poster/card-collection banners (unreached), sheet_055 banners, 1813332/18170D4, 1C0657A.
- **Phase 8 progress (2026-11-15, session 9):** name entry fully English: groups `names` (keyboard, a gfx.FORKS fork
  of the whole 16-stream chain 171EAB9 `800x16`; page 1 A-Z, page 2 a-z, digits/punct per `tools/names.py`),
  `nehead` (header Button / OK / A/a), `nametag` (opening-movie name tag なまえ -> Name), `tools/gfx_names.py`;
  checked: both pages, header, compose still kana (`work/qa/p8names`), tag (`work/qa/p8tag`). Katakana-page dump:
  `work/qa/ppu/name_kata`. Compose header ボタン メニューへ -> Button Menu (`cohead`: the original 171EAB9 chain
  rewritten in place; `gfx.FORKS` is now keyed by group so one offset can have a fork and an in-place edit).
- **Phase 8 progress (2026-11-15, session 8):** build stage `names` (`tools/names.py`, `tests/test_names.py`): name
  charset 0x187EA84 maps every keyboard code to the English letter on that key; `gfx.FORKS` (new chain + resource
  table copy, one literal moved); `tools/lua/reslog.lua` logs resource-record loads with the asking code.
- **Phase 8 progress (2026-11-15, session 7):** `gfx.apply` relocates chains that outgrow their slot (below
  0x2000000) and repoints every moved chunk's pointers; new test: no pointerless stream may follow a row. Groups
  `epnum` (179BC34 800x16: episode numbers 話 -> EP, grid + cursor checked in scene 25, `work/qa/p8ep`) and `bonus`
  (1D095BE Bonus Movie!, unseen) English. 1C0657A つづけてあそぶ? needs its BG map (end of a minigame; notes in
  `docs/re/graphics.md`).
- **Phase 8 progress (2026-11-15, session 6):** room + card-game graphics English (`tools/gfx_cards.py`: buttons
  Play/Yes/Quit/No 1D031F4, room bubbles 1D09C87, top-right hints A OK / B Quit 1D01FD9, prompt Play a game? 1C07510),
  checked in warps room / card_game (`work/qa/p8cards`). New helpers: `tools/gfx_obj.py` (sprite compose/write-back,
  the OBJ twin of gfx_bg), `tools/oamlist.py`, `tools/objsrc.py`, `tools/lua/kcomplog.lua` (logs every kcomp call's
  src: finds blocks the sweep missed). Read but not drawn: 179BC34 episode cursor 話 plate, 1B6AFB2 story logo
  wallpaper, 170633B (see `docs/re/graphics.md`).
- **Phase 8 progress (2026-11-15, session 5):** groups `options` (scene 14 labels Name/Background/Arrows/Headphones/
  On/Off/Mermaid, `work/qa/p8opt`), `songsel` (score panel Easy/Normal/Hard) + `pills` (E N H / U M R, unseen),
  `clear` (Kaito cut-in Amazing! / Well done!, `work/qa/p8clear`) English. Open, with what was tried, in
  `docs/re/graphics.md`: song titles (per-title OBJ list is data; find its table before redrawing), clear siblings
  1813332 / 18170D4 (per-cell palettes not found). Helper `tools/findmap.py`.
- **Phase 8 progress (2026-11-15, session 1):** graphics pipeline built and piloted: `kcomp.compress` (optimal parse, roundtrip-tested), `tools/gfx.py` (tsv rows, chained 0x800 streams, OBJ/tile layouts, png <-> indices, `typeset`, build stage `gfx` writing in place, write zones), `tools/gfx_menu.py`; group `menu` (6 main-menu captions) English in cold-boot warps (`work/qa/p8menu/sheet/`). Notes: `docs/re/graphics.md` §Redraws. Order chosen: graphics first, then the full QA tour + visual-QA verdicts (a tour before the redraws would lose its verdicts when sheets change).
- **Phase 8 progress (2026-11-15, session 2):** groups `modes` (6 mode labels), `icons` (6 menu icons), `diff` (difficulty bubbles Easy/Normal/Hard/Usual/Mood/Random + header pieces Button/Start/Back/OK) English, checked in cold-boot warps (`work/qa/p8modes`, `work/qa/p8diff`). Main menu and difficulty screens fully English. Screen map: `work/gfx/scenes.tsv` from `tools/gfx_scenes.py` (needs `work/qa/ppu` dumps + `tools/gfx_chain.py`, both regenerate in ~5 min). `gfx.typeset` gained ring lists, shadow, gap.
- **Phase 8 progress (2026-11-15, session 3):** groups `btn` (pause / game over / continue cloud buttons, Yes/No
  prompt) and `score` (HUD atlas 1F0F059 words) English, checked in warps (`work/qa/p8btn`, `work/qa/p8score`);
  1F59B31 = copy of the diff sheet, done by the same png; 1F5ABD8 Part/Mix/Sync; `draw` (DRAW, checked in scene 42);
  `winlose` (WIN/LOSE, unwarped). Last build sha1 a0ca757e (smoke ok, write log clean). Helpers `tools/gfx_where.py` (sprite -> block rect, palette)
  and `tools/gfx_grid.py`; layout `objWxH*N/R` for panelled atlases. Notes in `docs/re/graphics.md` §Redraws.
- **Phase 8 progress (2026-11-15, session 4):** groups `gameover` (174AB9D GAME OVER / CLEAR GOAL / CLEAR!, checked
  in scene 37, `work/qa/p8go`) and `solo` (carousel cards Marathon / Nonstop / Anime Pitch, D15, checked in
  `work/qa/p8solo`). New `tools/gfx_bg.py` for text on BG maps (show a layer with a grid; compose/write map cells
  back into a block's tiles), `tools/palfix.py` (dumped palettes with repeated colours). Full warp tour of the
  English build: 50/50 (`work/qa/en/sheet`, overview `work/qa/en/all1.png`/`all2.png`). Japanese graphics still
  visible there: options menu labels (1723EBE), room/card game prompt ゲームする？ する/しない (1D0xxxx/1C0xxxx),
  name entry / compose keyboards, song select & song list labels (173F4E9 173FE48 1743F0B..), hippo_talk banner,
  story 1B6AFB2, clear 180F0F8, results 170633B, episode numbers 179BC34.. (00話 -> needs a design), link_check なまえ
  1F0CEC0. 1EFF70B looked like digits/hex font only (no Japanese seen): confirm and drop from the list.
- **Done:**
  - Step 0 (2026-11-15): template, rom.sha1, MesenCE 2.2.1 + GBA BIOS in tools/mesen, guard hook proven, pre-commit (tools/check.py) rejects a failing test, original ROM smoke-boots, scripted input and Lua probe ok.
  - Phase 1 (2026-11-15): no prior English patch; no SJIS. Graphics: kcomp decoder (`tools/kcomp.py`), resource tables (`tools/restables.py`), static sweep of every block (`tools/sweep.py`, 104 sheets) reviewed read-only by codex (`tools/codex_review.sh`) -> 170 text blocks in `docs/re/graphics_sweep.tsv`; tour list in `docs/re/graphics.md`. Script: message table 0x1860CE0 (2474 x 24-bit offsets from 0x18629DE), 1 byte per char = glyph index, FF end, 47.7k bytes; 12x12 2bpp frequency-ordered font at 0x18745E0 (`tools/font12.py`, `tools/fontstr.py`); name-entry buffer and charset (`docs/re/text.md`). Free space: 0x1FDF760-0x1FFFFFF trap-filled with FF, see compression.md.
  - Phase 2 (2026-11-15): scene dispatcher found (u8 0x0300287C, table 0x09D37060, 43 ids); `tools/debug/warp.lua` + `scenes.tsv` (50 entries: every scene id with a screen, menu items, modes, minigames, story episodes via `--var EP=1..39`, any message via `--var MSG=0..2473` in the leftover debug menu's message viewer). Save fixture made by the game (`tools/debug/make_save.py`). `tools/debug/regen.py` reached 50/50 from cold boot; shots `work/qa/warp/sheet/`, states `work/states/<name>.mss`. Notes: `docs/re/scenes.md`. Story text advances with `--mash 30` (emu.py A-mash).
  - Phase 3 (2026-11-15): `build.py` -> `tools/msgtable.py` unpacks/repacks the message table; `tests/test_identity.py`.
  - Phase 4 (2026-11-15): control codes (`docs/re/text.md`, `tools/msgparse.py`); `tbl/jp.tbl`; `tools/msgcodec.py` -> `script/msg_00..16.json` (1617 units), roundtrip + relocation tests.
  - Phase 5 (2026-11-15): English font `fonts/en12.txt` + VWF patch `tools/vwf.py`; text packs into two regions; `build.py --marker` / `--qa ID=text`; box probes `tools/lua/boxlog.lua`, `tilelog.lua`. Width gate: `tools/boxes.py` (bubble geometry from the event scripts, range budgets, fit lint, bubble auto-grow in the English build), `tests/test_fit.py` (Japanese calibration 0 errors; English script must have 0 errors: this gates every commit). `python -X utf8 tools/boxes.py [--warn]` prints the report. All facts: `docs/re/vwf.md` §Boxes, §Width gate.
  - Phase 6 (2026-11-15): 16 batches (1519 units, `work/tl/bNNN.tsv` -> `.out.tsv`) by 4 translator agents, every batch reviewed (`tools/pairs.py` -> `work/qa/review/`, reviewer agents), all Critical/Important fixed, merged into `script/`; every used unit has English. Glossary + rulings D10-D12 added; Minors deferred in `docs/polish.md`. `batches.py`: wrap now measures the line before a page code, glossary match ignores line breaks, `{call}s` plural lint, a call may be written out as its text.
  - Phase 6 review fixes (2026-11-15): 32 flattened-voice lines reworked; style-reference rows for every recurring speaker; every batch re-reviewed by an independent codex pass (`tools/codex_tl_review.sh`, reports `work/qa/review/*.report.md`, outcomes `docs/review-log.md`), 1 Critical + 40 Important fixed and re-checked (approved); new Minors appended to `docs/polish.md`. Honorific lint after calls; glossary rows Pichi Pichi, Eek/Eee; lyric long-vowel exception.
  - Phase 7 (2026-11-15): build green: `batches.py check` 0 problems (control codes matched), fit lint 0 errors / 78 guess warnings, `tools/check.py` 31 passed. Every build writes `<out>.writes.log` (per stage: text, boxes, vwf); `tools/writelog.py` = romdiff (orig bytes, overlap, no unlogged change) + each stage only in its zones (`tests/test_writelog.py`). Debug menu units 0040/0110 keep Japanese (D13, status keep-jp): that menu draws with the original font, verified in a shot.
- **Next (phase 8):**
  1. QA tour per `references/emulator-qa.md`: warp to every scene (`tools/debug/regen.py build/mermaid_en.gba`), story EP 1-39 with `--mash`, contact sheets, visual-QA verdicts (do them as an independent read-only pass: codex via `tools/codex_review.sh`), `qa_gate.py check` exit 0; `inkbox.py` on choice/centred menus; `textcover.py` from `tools/lua/msglog.lua`.
  2. Graphics text (session 6 adds `cardbtn` `roombub` `hint` `prompt`, session 7 `epnum` `bonus`; drop 1D031F4
     1D09C87 1C07510 1D0B2A4 179BC34..179DE22 1D095BE from the list; 1C0657A waits for a minigame-end warp; session 9
     did 1F0CEC0 and name entry 171EAB9 171F78F 17212DD 179B69F: drop them too (and compose's header); next: the list
     below):
     `menu`, `modes`, `icons`, `diff`, `btn`, `score` done (docs/re/graphics.md §Redraws). `btn`, `score`, `draw`, `winlose`, `gameover`, `solo`, 1F5ABD8, `options`, `songsel`, `pills`, `clear` done too (so drop 1723EBE, 173F4E9, 173FE48, 180F0F8 from the list below). BG-mapped screens (options, story, results, episode grid): use `tools/gfx_bg.py` like `tools/gfx_solo.py`. Next by screen from `work/gfx/scenes.tsv` (session-4 list above first): 1F0CEC0 なまえ; find the screens of 1F0DA41/1F0E3F7 (resource table 1EFF434), 1F12431/1F12CBD and 1F5ABD8 (1F56AB0 entry 58) and add warps; 1F0F059 pills + framed labels (see graphics.md) once a scene showing them is found; 1EFF70B (mixed, loaded by most scenes); song select labels 173F4E9 173FE48 1BF7155; mode carousel 1BF5582 1BF8856; song titles 17403F7..1743F0B (song_list); result banner 170633B; options 1723EBE; name entry 171EAB9 171F78F 17212DD 179B69F; room/card game 1D0xxxx 1C0657A 1C07510; clear 180F0F8; game over 174AB9D; story 1B6AFB2; episode grid numbers 179BC34..179DE22; then the 83 rows no warp loaded (episode titles, banners sheet_055). Then the remaining rows of `docs/re/graphics_sweep.tsv` (~145 jp/mixed blocks) by screen. Large static sets fit parallel `translate-retro-game:graphics` agents (`docs/graphics-brief.md` from the skill's assets, `work/gfx/<group>.txt`): episode-title strips 0x18AF223-0x18BFC9C (~45 rows), character banners sheet_055. Many sweep sizes 0x1018/0x103E are 0x800 chains (`800x2`): re-check each row's chain before drawing. Then zoomed cold-boot shots.
  3. Check in game: A44E/FC29/459A "Love Love Shower Pitch" with FD codes; 9D2D poem furigana codes kept with empty readings; credits pages (0859 0962 0A62 0B06 0C0F) got `{FA:06}` between songs: does the credits screen page?; 0B06 arranger glyph Ⓒ guess written "(C)"; profiles' "[Name]" header line.
  4. Units with a guess budget (78 warnings) warn only: confirm their boxes in the tour.
  5. The msgview debug box (warp `MSG=N`) draws through the non-VWF debug font, so English shows as junk there: use story warps for visual QA, msgview only for text logging. Phase 9: pass 0040/0110 to `jp_left.py --known` (intended Japanese).
- **Later:**
  - F6 name width in the lint is a 60 px guess: measure once the Latin keyboard is in (max name length?).
  - Katakana-page ー may be code 0xC2 (glyph 0x16F, not in jp.tbl), not 0x67: type it on page 2 and check it prints "-".
  - Debug tool gaps (add when needed): GOD mode for gameplay (life gauge address unknown), scenes 17/30/31 blank when warped, 止め絵チェック item, results after a real song (only empty results warp).
  - Text coverage (phase 8): `tools/lua/msglog.lua` logs `TEXT <hex id>`; msgview sweep over all ids plus story EP 1-39 (with `--mash`).
  - Glyph 0x167 (circled, song credits) read as `Ⓒ`, a guess: zoom it in game when the credits are QA'd.
- **Open bugs:** none.
- **Known limits:** msgview's debug box garbles rows when a message runs past 7 lines with no page break (real pages are <= 4 lines; story boxes clean). Japanese fallback text in an English build draws as junk (its glyph slots hold English letters): every used unit needs English.
- **Waiting on the user:** (non-blocking) story background 1B6AFB2 tiles the series logo ぴちぴちピッチ as a faded
  64x16 wallpaper; kept Japanese (a 64x16 repeat can't hold "Pichi Pichi Pitch" legibly); say if it should be redrawn. (non-blocking) song lyrics shipped as romaji (D10); English meaning is the alternative. (non-blocking) "Love Love Shower Pitch" for ラブ②シャワーピッチ (D11). (non-blocking) staff name readings unverified: 佐藤和朗 Kazuaki Sato, 堀田健志 Takeshi Hotta, ポリン Porin. (non-blocking) GUI keyboard input in tools/mesen not checked by hand; emu.py wrote default key mappings.
