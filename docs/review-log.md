# Translation review log

One line per review pass: what was reviewed, by whom, the outcome. Full reports (the reviewer's final message) are
saved as `work/qa/review/<name>.report.md` (gitignored; regenerate with `sh tools/codex_tl_review.sh <name>`).
Minors go to `docs/polish.md`; Critical/Important are fixed in the batch out.tsv, `batches.py check`, merged, re-checked.

## Phase 6 (2026-11-15, Claude reviewer agents)
- b005-b016 reviewed; fixes in `work/tl/fixes_wave1.md`, Minors in `docs/polish.md`. The reviewers' messages were not
  saved, and b001-b004 have no recorded outcome (phase-6 review, finding 3), so every batch was reviewed again below.

## Phase 7 (2026-11-15, independent codex read-only pass, `tools/codex_tl_review.sh`)
| Pass | C | I | M | Outcome |
|---|---|---|---|---|
| b001 | 0 | 3 | 3 | 0240 "pts" -> "points", 0D11 "Dept." -> "Department" (+ Minor "Support"); 0040 debug menu now keep-jp (drawn by the original font, D13) |
| b002 | 0 | 4 | 2 | 122C/12B4 "older/younger of the Black Beauty Sisters", 150F Sara "joined Lucia and the others", 19ED "It's Lucia, Hanon and Rina's song"; 12B4 title finding was wrong (already "Kuro no Concerto") |
| b003 | 0 | 0 | 0 | Approved (lyrics) |
| b004 | 0 | 4 | 2 | 36A3 Kyaaa -> Eee, 37DB agency fixed; 27CA haresugata / 27E8 baiorin kept: the game text drops one kana of the sung word (晴れ姿, バイオリン in the children's song "Ongakuka"), the romaji follows the song |
| voice-fix (32 ids, review finding 1) | 0 | 0 | 2 | Approved; both Minors applied |
| b005 | 0 | 1 | 4 | 4BA1 しろ = castle |
| b006 | 0 | 2 | 4 | 4FD6, 540D |
| b007 | 1 | 2 | 7 | 6229 plural (Critical), 6CAA, 6F1F Yuri voice |
| b008 | 0 | 2 | 9 | 7F77, 7FD2 Ring of Wishes |
| b009 | 0 | 5 | 3 | 823F 854A 8E43 92EC 938D |
| b010 | 0 | 5 | 5 | 95EC 9821 9882 A475 A555 |
| b011 | 0 | 4 | 6 | A8AD AE58 B061 B76B |
| b012 | 0 | 2 | 7 | BD1C ("that girl"), C6E5 |
| b013 | 0 | 1 | 4 | DB73 |
| b014 | 0 | 3 | 3 | E3F9 E7E5 EC24 |
| b015 | 0 | 2 | 4 | FDB0 FE07 Dark Hot Pot Party |
| b016 | 0 | 0 | 0 | Approved |
| fix2 (the 30 ids above, re-check) | 0 | 0 | 2 | Approved; both Minors applied (8E43, EC24 "The school intercom's on!") |

Result: every batch has a saved report, and no Critical/Important finding is open (phase-6 done-when met).
