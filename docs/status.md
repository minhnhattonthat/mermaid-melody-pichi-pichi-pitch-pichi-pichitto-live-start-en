# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git (sessions 1-19 of
phase 8: graphics redraws and the first visual-QA fixes, see `git log` and `docs/re/graphics.md` §Redraws).

- **Phase:** 8. QA in the emulator (phase 7 done 2026-11-15). Last build: `build.py` -> build/mermaid_en.gba
  (2026-11-16 session 20, sha1 in `work/qa/tour4.build`; smoke ok, write log clean, check 43 passed); marker build
  `build.py --marker --out build/marker.gba`.
- **Session 20 (2026-11-16):**
  - Minigame logos redrawn (D18, `tools/gfx_logos.py`): Compare / Line Up / Match / Catch Pitch, checked in game
    (`work/qa/p8logos`, warp row `minititles`); `tools/gfx_left.py`: 0 rows left.
  - Text coverage 1591/1591 (`tools/cover.py work/qa/tour3/runs work/qa/cover --waive docs/text_unshown.tsv`): msgview
    sweep `ROM=build/mermaid_en.gba FRAMES=1500 EVERY=1500 sh tools/debug/warp_many.sh msgview MSG work/qa/cover
    <ids>` (warp_many now logs TEXT); the 46 units with no message id are {call} targets (names, codes), waived.
  - Visual QA of tour3 (codex, `work/qa/verdicts/`) found: the engine char-wraps a line past the box ("lov/e"), so
    `tools/msgboxes.py` records boxes seen in game (`docs/re/msgboxes.tsv`, budget kind "seen" in `boxes.py`),
    profiles 128-141 got a budget, guessed boxes wrap to their own width (not the Japanese line's); in-song dialogue
    names (tag 2B99, no newline) count on their line and read "Lucia: ..." (was "LuciaYou're"); one-word last lines
    before trailing codes unwidowed (44); "Amazing!" centred (`gfx_clear.py`). `batches.py rewrap` keeps blank-line
    runs, `[Name]` headers, {FD} lines and speaker changes.
  - `inkbox.py`: card game Yes/No (15/15, 18/18) and Retry (10/10) centred; Quit/Continue buttons match the
    original's placement (stars on the right edge).
- **Session 21 (2026-11-16):** tour3 verdict issues fixed: `FA FF 04` (scene callback 4) takes 9 param bytes
  (`msgparse.py`; EP 28 streaks / EP 11 swallowed end); live-data error bubble in English (`tools/gfx_live.py`,
  chain 1747BC1 found with `kcomplog.lua`); solo cards get a plate over the old lettering (`gfx_solo.py`), Nonstop
  centred; "Nothing here!" centred (`gfx_songs.py` NUDGE). Polish pass done (`docs/polish.md` 0 unticked, 12 waived):
  dot runs -> "..." and no space before {FA:06}/{wait} in all English, ~85 reviewer Minors applied
  (`work/tl/polish_subs.tsv`, merged with `batches.py merge polish`).
- **Interrupted (session 21):** the system killed the polish-pass commit (pre-commit check unfinished) and tour5
  (61 runs) for low memory. Polish changes are staged, not committed; `README.md`, `docs/release-readme.txt` and
  `tools/release.py` are new and unchecked. Resume: `git commit` (hook runs check.py), then tour5 from scratch.
- **Next (phase 8):**
  1. Tour5 of the session-21 build (`python -X utf8 tools/tour.py --out work/qa/tour5`), then `qa_gate.py init
     work/qa/manifest.tsv work/qa/tour5/sheets --build build/mermaid_en.gba --glob "sheet*.png"`, `qa_gate.py todo
     ... --out-dir work/qa/chunks`, delete old `work/qa/vqa_log/*.out`, `sh tools/codex_vqa.sh work/qa/chunks 5`, fix,
     re-tour, until `qa_gate.py check` exits 0. Text coverage: `tools/cover.py work/qa/tour5/runs work/qa/cover
     --waive docs/text_unshown.tsv`.
  2. Then phase 9 (release): `tools/release.py` (not written yet; gates per the skill's pipeline.md §Release),
     README filled from the template, zip verified. Never publish.
- **Later:**
  - F6 name width in the lint is a 60 px guess: measure with the Latin keyboard (max name length?).
  - Katakana-page ー may be code 0xC2 (glyph 0x16F, not in jp.tbl), not 0x67: type it on page 2, check it prints "-".
  - Debug tool gaps: GOD mode (life gauge address unknown), scenes 17/30/31 blank when warped, 止め絵チェック item,
    results after a real song.
- **Done:**
  - Step 0, phases 1-7 (2026-11-15): see `docs/re/*` (encoding, pointers, free space, scenes, VWF, width gate),
    `tools/debug/` (51 warps), `build.py` (identity test), `tools/msgcodec.py` (1617 units), 16 translated and
    reviewed batches (`docs/review-log.md`), build green (control codes, fit lint, write log zones).
  - Phase 8 graphics (sessions 1-20): every graphics-sweep row redrawn (`gfx/*.tsv`) or waived (`docs/gfx_waived.tsv`).
- **Open bugs:** none known in the session-20 build (tour3 issues fixed; tour4 unreviewed).
- **Known limits:** Japanese fallback text in an English build draws as junk (its glyph slots hold English letters):
  every used unit needs English.
- **Waiting on the user:** (non-blocking) story background 1B6AFB2 tiles the series logo ぴちぴちピッチ as a faded
  64x16 wallpaper; kept Japanese (a 64x16 repeat can't hold "Pichi Pichi Pitch" legibly); say if it should be
  redrawn. (non-blocking) song lyrics shipped as romaji (D10); English meaning is the alternative. (non-blocking)
  "Love Love Shower Pitch" for ラブ②シャワーピッチ (D11). (non-blocking) staff name readings unverified: 佐藤和朗
  Kazuaki Sato, 堀田健志 Takeshi Hotta, ポリン Porin. (non-blocking) GUI keyboard input in tools/mesen not checked by
  hand; emu.py wrote default key mappings. (non-blocking) minigame names Compare / Line Up / Match / Catch Pitch
  (D18).
