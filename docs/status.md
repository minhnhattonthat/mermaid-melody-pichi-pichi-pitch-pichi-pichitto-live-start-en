# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git (sessions 1-18 of
phase 8: graphics redraws, see `git log` and `docs/re/graphics.md` §Redraws).

- **Phase:** 8. QA in the emulator (phase 7 done 2026-11-15). Last build: `build.py` -> build/mermaid_en.gba
  (2026-11-16 session 19, sha1 e27acfa6; smoke ok, write log clean, check 43 passed); marker build
  `build.py --marker --out build/marker.gba`.
- **Session 19 (2026-11-16):** a codex visual-QA pass over the session-18 tour (`work/qa/tour`, verdicts
  `work/qa/verdicts/chunk_000..022`, 37 issues; list `work/qa/issues_so_far.tsv`) found, now fixed:
  - in-song dialogue and credits/profile `{FD:01}` runs drew English codes through the 8 px kana font (mode 1,
    flags bit 0): `tools/vwf.py` sends mode 1 to the VWF path (not message ids < 7: debug menu keeps kana, D13);
  - lyric strip lost letters / showed stale tiles on long lines: lyric predraw copies only pool slots 0..103 and the
    allocator cursor never went back to freed slots; VWF free_col now rewinds the cursor (`docs/re/vwf.md`);
  - in-song dialogue boxes are event op 0x7006 records (`boxes.song_boxes`, 121 messages): budgeted at W 22
    (cols 4..26, 8 px wrap), grown by the `boxes` build stage, 57 units rewrapped, 7 shortened (94AD 9EA8 A054
    A475 AEE4 B634 B913);
  - tail-less boxes off col 1 (15, e.g. EP 13 Aqua Regina over a drawn frame) no longer grow (`boxes.fixed`);
  - one-word last lines: `batches.py unwidow` (141 units) and `wrap()` now avoids them; `batches.py rewrap` joins and
    rewraps units a box rule change broke;
  - bold `gfx.typeset` filled the 1 px gaps of m/w (solid block): wider bold m/w (`gfx.BOLD_WIDE`), all groups
    regenerated.
  New probes: `tools/lua/objlog.lua` (text object fields), `pathlog.lua` (VWF/orig/8 px path per glyph),
  `tilepool.lua` (pool use); `msglog.lua` lines now carry flags/sp/W/H.
- **Next (phase 8):**
  1. Full tour of build e27acfa6 done: `work/qa/tour3` (53/53 scenes, 39/39 episodes, 393 sheets; text coverage
     872/1591 units from its logs). The old run's 49 verdict files in `work/qa/verdicts/` are for the old tour. Then:
     `python -X utf8 $SKILL/scripts/qa_gate.py init work/qa/manifest.tsv work/qa/tour3/sheets --build
     build/mermaid_en.gba --glob "sheet*.png"`, clear `work/qa/verdicts/` (old tour), `qa_gate.py todo
     work/qa/manifest.tsv work/qa/verdicts --size 8 --out-dir work/qa/chunks`, `sh tools/codex_vqa.sh work/qa/chunks 4`
     (independent read-only codex verdicts, ~3 min a chunk), fix every issue, re-tour changed scenes, until
     `qa_gate.py check` exits 0. (A session-18 codex_vqa run on the old tour may still be running when this starts:
     let it end before clearing verdicts.)
  2. Text coverage: `python -X utf8 tools/cover.py work/qa/tour3/runs` (per unit), then msgview sweeps for unshown ids
     (warp `msgview --var MSG=N`; its debug box is mode 1, so since session 19 it draws English through the VWF:
     check once) and waivers in `docs/text_unshown.tsv`; `textcover.py` must exit 0 for phase 9.
  3. `inkbox.py` on choice / centred menu boxes (Yes/No prompts, main menu, song select).
  4. Graphics left (`python -X utf8 tools/gfx_left.py`, release gate): minigame logos 1BF039E 1BF198F 1BF2D7E 1BF416C
     (くらべてピッチ, そろえてピッチ, あわせてピッチ, キャッチでピッチ; the game names appear nowhere else in English).
     Default under D5: redraw (notes `docs/re/graphics.md` §Minigame logos: tile slots nearly full, design needed);
     if that proves impossible, waive in `docs/gfx_waived.tsv` with a D18 entry. Character banners 1BFA943 1BFC919
     1BFE551 and 1721BEB/1722E8B/170633B are waived/unreached in `docs/gfx_waived.tsv`.
  5. Check in game: A44E/FC29/459A "Love Love Shower Pitch" with FD codes; credits pages (0859 0962 0A62 0B06 0C0F,
     `{FA:06}` between songs; credits use `{FD:01}` runs, now VWF: re-check their layout) and glyph 0x167 `Ⓒ`;
     profiles' "[Name]" header line; units with a guess budget (69 warnings, `tools/boxes.py --warn`).
- **Later:**
  - F6 name width in the lint is a 60 px guess: measure with the Latin keyboard (max name length?).
  - Katakana-page ー may be code 0xC2 (glyph 0x16F, not in jp.tbl), not 0x67: type it on page 2, check it prints "-".
  - Debug tool gaps: GOD mode (life gauge address unknown), scenes 17/30/31 blank when warped, 止め絵チェック item,
    results after a real song.
- **Done:**
  - Step 0, phases 1-7 (2026-11-15): see `docs/re/*` (encoding, pointers, free space, scenes, VWF, width gate),
    `tools/debug/` (50 warps), `build.py` (identity test), `tools/msgcodec.py` (1617 units), 16 translated and
    reviewed batches (`docs/review-log.md`), build green (control codes, fit lint, write log zones).
  - Phase 8 graphics (sessions 1-18): every graphics-sweep row redrawn (`gfx/*.tsv`) or waived
    (`docs/gfx_waived.tsv`) except the 4 minigame logos; checked in cold-boot warps (`work/qa/p8*`).
- **Open bugs:** none known in build e27acfa6 (issues from the old tour fixed; the new tour is unreviewed).
- **Known limits:** Japanese fallback text in an English build draws as junk (its glyph slots hold English letters):
  every used unit needs English.
- **Waiting on the user:** (non-blocking) story background 1B6AFB2 tiles the series logo ぴちぴちピッチ as a faded
  64x16 wallpaper; kept Japanese (a 64x16 repeat can't hold "Pichi Pichi Pitch" legibly); say if it should be
  redrawn. (non-blocking) song lyrics shipped as romaji (D10); English meaning is the alternative. (non-blocking)
  "Love Love Shower Pitch" for ラブ②シャワーピッチ (D11). (non-blocking) staff name readings unverified: 佐藤和朗
  Kazuaki Sato, 堀田健志 Takeshi Hotta, ポリン Porin. (non-blocking) GUI keyboard input in tools/mesen not checked by
  hand; emu.py wrote default key mappings.
