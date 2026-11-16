# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git (sessions 1-19 of
phase 8: graphics redraws and the first visual-QA fixes, see `git log` and `docs/re/graphics.md` §Redraws).

- **Phase:** 9. Release done 2026-11-17: v1.0 zip built and verified by `tools/release.py` (not published). Gates:
  visual QA 397/397 ok, story pass 40/40 ok, text coverage 1591/1591, `jp_left` 0, `gfx_left` 0, polish 0 unticked.
  Last build: `build.py` -> build/mermaid_en.gba (session 26, sha1 1d0f02a984597e2c3f3c12c596010cfbfb6a11d4,
  CRC32 7A0E5172; smoke ok, write log clean); marker
  build `build.py --marker --out build/marker.gba`.
- **Session 27 (2026-11-17):** user found Japanese on the results screen (pills かんたん/いつもの.., buttons
  すすむ/セーブ). Atlas 1F0F059 pieces had been left as "not seen in a warp yet": the tour's results shot (frame 960)
  came before the panels slide in, and VQA passed the blank sheet. Fixed: `SPRITES` in `tools/gfx_score.py`
  (Easy Normal Hard Usual Mood Random Part Mix, Next, Save); results rows in `scenes.tsv` wait 300 frames. Build
  sha1 5706775acf45426c0aeb9adb8517c808cf42367f, check 43 passed, smoke ok, 6 atlas scenes re-toured + VQA ok, gate
  waived for this build. **v1.0 zip is stale: re-run `tools/release.py`.** Open: stray comma after "Rhythm" on
  results (pre-existing); pills Normal/Hard/Mood/Random/Part/Mix unseen in game (fixture save = Easy/Usual).
- **Session 26 (2026-11-17), phase 9:**
  - Story pass: `tools/story.py` writes one chapter per episode (`work/qa/story/chapters/epNN.txt`, tour5 log order;
    lines the tour never reaches, after the song, placed by message-id block, marked `(+)`) + `extras` (late
    inserts 936-93D, 977+). `sh tools/codex_story.sh 4 CH..` (brief `docs/story-reviewer-brief.md`) ->
    `work/qa/story/reports/`, `tools/story_verdicts.py [--minors]` -> `verdicts/`. Round 1: 39 ok, ep12 issue (8202
    Eriru blamed the princesses: "That's what they get for mocking me!"); 21 Minors -> 18 fixed, 4 waived
    (`docs/polish.md` §Story pass). Round 2 re-review of the 11 changed chapters: all ok; FE17 fixed, 11 waived.
    `qa_gate.py check work/qa/story/manifest.tsv work/qa/story/verdicts`: 40/40.
  - Eps 1 6 9 12 18 24 26 27 34 re-toured into tour5, 79 sheets codex-reviewed ok (`verdicts/round_5.tsv`); FE17
    (not on any sheet) waived for the final build (`work/qa/manifest.tsv.waive`, msgview shot `work/qa/p9msg/2429`).
  - `tools/release.py` now runs skill `jp_left.py` on the message region (`--orig`, `docs/jp_known.txt`: the 9
    debug-menu runs, D13): 0 runs. README: base ROM CRC32/MD5.
- **Session 25 (2026-11-17):** codex reviewed the session-24 re-tour (392 ok, 1 issue): EP 36 msg 582C left "Hey,"
  alone before the {FA:06} prompt; moved to the next page ("we'll" -> "we" so the cursor line fits 186 px). EP 36
  re-toured alone (`tour.py --eps 36 --no-scenes`, single ep now accepted) and reviewed ok. Verdicts folded into
  `verdicts/round_3.tsv` + `round_4.tsv` (chunks in `verdicts_old/tour5_r3`, `_r4`).
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
- **Session 22 (2026-11-16):** polish pass, README, `tools/release.py`, `docs/release-readme.txt` committed (check 43
  passed; build sha1 44cb0bbd... in `work/qa/tour5.build`). Tour5 (`--jobs 4`) killed again by the harness for low
  system memory; a later run finished it and codex reviewed 387/395 sheets (4 issues).
- **Session 23 (2026-11-16):** tour5 issues fixed: song-dialogue boxes capped at cols 4-24 like the Japanese
  (`boxes.SONG_COLS`; at W 22 the text tiles reached the right gauge, EP 9 msg 1674), 52 song lines rewrapped, 12
  shortened by hand; GAME OVER stacked GAME/OVER in sprite cell 2 (screen x 104-136, centred; `gfx_gameover.py`);
  EP 27 lone "..." line joined. Re-tour into the same `work/qa/tour5` (so manifest paths stay valid), `--jobs 3`.
- **Session 24 (2026-11-16):** re-tour of session 23 reviewed by codex (385 ok, 4 issue + ep08 sheet_4 waived: the
  line-scroll ghost frame is the original's, JP f3306; brief updated). Fixed: the wait cursor (2 cells in from the
  right edge on a page's last line) covered "Lucia-sama!" (EP 36): `boxes.CURSOR` lint rule + grow room, `batches.py
  uncursor` broke 77 such lines (docs/re/vwf.md §Boxes); difficulty bubbles drawn with 2 px strokes (`typeset(...,
  heavy=True)`: the unselected ones are scaled down) and the yellow bubble's shade 4 cleared ("Usual" specks).
  Verdicts of that round folded into `work/qa/verdicts/round_2.tsv` (old chunks in `verdicts_old/tour5_r2`); re-tour
  into `work/qa/tour5` again.
- **Next:** nothing left in the pipeline. `tools/release.py --version 1.0` passed every gate (2026-11-17 session 26)
  and wrote `release/v1.0/` (zip = BPS + README.txt; patched CRC32 7A0E5172, sha1 1d0f02a9...). Publishing
  (`gh release create`, upload) is the owner's call only. A text change after this needs a re-tour of the touched
  episodes (or `qa_gate.py waive` for an untoured line) and a re-run of the story pass on changed chapters.
  - Re-tour recipe if text changes: fold `verdicts/chunk_*.tsv` into `verdicts/round_N.tsv` and move the chunks out
    before `qa_gate.py init work/qa/manifest.tsv work/qa/tour5/sheets --build build/mermaid_en.gba --glob
    "sheet*.png"`, then `qa_gate.py todo ... --size 8 --out-dir work/qa/chunks`, `sh tools/codex_vqa.sh
    work/qa/chunks 4`; refresh `work/qa/tour5.build` (`sha1sum build/mermaid_en.gba`).
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
- **Open bugs:** none known in the session-25 build (tour5 fully reviewed ok).
- **Known limits:** Japanese fallback text in an English build draws as junk (its glyph slots hold English letters):
  every used unit needs English.
- **Waiting on the user:** (non-blocking) story background 1B6AFB2 tiles the series logo ぴちぴちピッチ as a faded
  64x16 wallpaper; kept Japanese (a 64x16 repeat can't hold "Pichi Pichi Pitch" legibly); say if it should be
  redrawn. (non-blocking) song lyrics shipped as romaji (D10); English meaning is the alternative. (non-blocking)
  "Love Love Shower Pitch" for ラブ②シャワーピッチ (D11). (non-blocking) staff name readings unverified: 佐藤和朗
  Kazuaki Sato, 堀田健志 Takeshi Hotta, ポリン Porin. (non-blocking) GUI keyboard input in tools/mesen not checked by
  hand; emu.py wrote default key mappings. (non-blocking) minigame names Compare / Line Up / Match / Catch Pitch
  (D18).
