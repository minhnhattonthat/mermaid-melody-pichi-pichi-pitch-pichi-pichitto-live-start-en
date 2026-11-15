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

## Redraws (phase 8)
- Pipeline: `gfx/<group>.tsv` (offset, size, layout, png, English, Japanese) + `gfx/<group>.pal` (16 colours from a
  palette dump) -> build stage `gfx` (`tools/gfx.py`): decode, png -> indices, `kcomp.compress`, write over the original
  stream (must fit; the encoder is ~5% smaller than Konami's on all 258 unscrambled blocks tried). Write zones = each
  row's original stream chain (`tools/writelog.py`). `python -X utf8 tools/gfx.py export GROUP` writes the originals to
  `gfx/orig/<group>/` (gitignored); `gfx.py check` prints slot vs new size. Typesetting: `gfx.typeset` (dialogue font
  `fonts/en12.txt`, bold column, fill/top/outline indices). One generator per group (`tools/gfx_<group>.py`).
- **Chains:** many sweep "blocks" of size 0x1018/0x103E are really two (or more) 0x800-byte kcomp streams back to back
  (caller 0x08000EA0). The sweep decoded them as one stream, so their second half renders garbled on the sweep sheets.
  tsv size `800x2` decodes a chain; check that the chain ends at the next block (it did for all 6 menu captions).
  **verified** (menu captions match VRAM tile rows 1-2 in `work/qa/ram2/ppu_000070`).
- Group `menu` (done, pilot): main-menu captions 0x1708763..0x170B89B, OBJ pal 15, 2D OBJ map, tiles 896+ (4 sprites
  64x32 at y 128); each chain = two 16x4-tile halves (`obj16x4*2`). Text uses only indices 12-15; the clean banner is
  composed from the 6 captions (`tools/gfx_menu.py`). Cold-boot shots: `work/qa/p8menu/sheet/`.
- Finding a screen's blocks: `tools/gfx_chain.py` (every sweep row's chain spec -> `work/gfx/chain.tsv`, decoded
  blocks `work/gfx/blocks/`, grey sheets), `tools/gfx_scenes.py` (vramfind of each scene's PPU dump from
  `regen.py --script ppudump.lua` -> `work/gfx/scenes.tsv`: 62 jp/mixed rows seen in a warped scene, 83 not).
  OAM tells the layout: OBJ VRAM is 2D (32 tiles a row), so a block of 16-tile rows at OBJ tile T is `tiles16`.
  `tools/gfx_render.py OFF SPEC LAYOUT OUT [PAL]` renders one block. Palette for a group: 16 distinct colours
  (`gfx.load_pal` asserts it), else erased text keeps its index and shows under another palette.
- Group `modes` (done): 6 mode labels 170D7EE..170EB49 (one 0x800 stream each, 128x32), `tools/gfx_modes.py`.
- Group `icons` (done): 170C1F2 (800x6, 128x192 sheet of six 64x64 icons, OBJ tile 0), `tools/gfx_icons.py`.
- Group `diff` (done): 17264E2 (800x4, 128x128 at OBJ tile 272): 6 difficulty bubbles (affine-scaled when not
  selected) + 32x16 header pieces ボタン/スタート/もどる/けってい -> Button/Start/Back/OK, `tools/gfx_diff.py`.
- Episode-title strips 18AF223.. (45 rows, 800x2 each): episode grid (scene 25) loads 18AF223 into BG1 char 257+
  (pal 12, map rows 7-12, cols 7-22, tiles in map order, one tile per cell); locked episodes are mosaicked
  (`tools/lua/nomosaic.lua` clears the register but the bottom strip stayed blocky: not solved). Layout of the
  title text inside the block still unread; the map is per episode (find its source before redrawing).
- Old note: menu item labels (selected label: OBJ pal 2, tiles 768/776, two 64x32 at y 58; bag icons with two-line labels:
  OBJ pal 3 tile 512 64x64), then the rows of `graphics_sweep.tsv` by screen.
