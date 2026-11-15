# Graphics-text survey (phase 1)

Most on-screen Japanese is pre-drawn graphics in kcomp-compressed blocks (`docs/re/compression.md`). Font-drawn text
(script, names) is in `docs/re/text.md`.

## Static sweep
- `python -X utf8 tools/sweep.py work/orig.gba` decodes every pointer of `work/restables.tsv` until the stream reaches
  the next valid pointer, writes `work/sweep/blocks/<off>.bin`, `index.tsv`, `gaps.tsv` and 104 labelled gba4 sheets
  (2x). Status: 1189 exact, 63 over, 6 short, 715 err (false-positive records, not kcomp streams; listed as `skip`).
- Uncovered ROM regions >= 16 KiB are rendered raw (sheets 086-103), except 7 big ones that look like PCM audio by eye
  (`work/gapview.png`): 0x1D1000-0x341202, 0x34122D-0xF68308, 0xF6831A-0xFB830E, 0x1074117-0x10C0110,
  0x10D101E-0x112920B, 0x1171107-0x14813B8, 0x14CB028-0x16F70A1. **guess** (audio). Gaps < 16 KiB are not rendered.
- Known limit: some blocks are chains of 0x800-byte kcomp chunks (caller 0x08000EA0) with no pointer per chunk; the
  sweep decodes past the first chunk as one stream, so later chunks render garbled (e.g. the menu portrait). Text in
  such chains may be missed; the tour list below covers the screens seen.
- Review: `tools/codex_review.sh work/sweep work/sweep/prompt.txt 6 4` (codex exec, read-only, 6 sheets per call).
  Result: **`docs/re/graphics_sweep.tsv`**: 170 blocks with text (123 jp-text, 22 mixed, 13 digits, 12 en-text), with
  offset, sheet and a short description. 9 labels were misread by the reviewer and snapped to the closest label on
  the same sheet (marked `[label read as ...]`).
- Each row is a block to redraw or check in phase 8; the sheets are coarse (no palette), so a row's exact words are
  read when it is redrawn.

## Tour (screens seen, original ROM)
| Screen | Element | Layer / source |
|---|---|---|
| Name entry | header `STARTボタン けってい / SELECTボタン きりかえ`, kana keyboard | OBJ (header 32x16 sprites, pal 15), BG/OBJ keyboard; blocks 0x171F78F / 0x17212DD match VRAM (`vramfind`) |
| Name entry | entered name | font (BG0), `docs/re/text.md` |
| Title | logo `ぴちぴちピッチ` / `ぴちぴちっと ライブスタート!`, copyright line | graphics; logo has no official English version: keep (D5) |
| Main menu | items, per-item caption | BG + OBJ, block 0x16F6CC8 table (`compression.md`) |
| Character select | name banner, top-right label | graphics |
| Song select / difficulty | `むずかしい / かんたん / いつもの / ふつう / きまぐれ`, `Aボタン けってい / Bボタン もどる` | graphics (0x17264E2 has かんたん/ふつう) |
| Link mode (あなたのピッチ) | `Bボタン もどる`, box text `つうしんせつぞくをしらべています` | graphics + font |

Not yet visited (phase 2 debug tool will reach them): results, game over, collection (あつめて), options/save
prompts, ending and credits, story scenes if any.
