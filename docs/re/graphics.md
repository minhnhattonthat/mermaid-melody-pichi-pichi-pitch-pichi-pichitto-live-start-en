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
- `tools/gfx_where.py SCENE OFF SPEC LAYOUT`: a block's VRAM runs in a scene dump, each OAM sprite on it with its
  rect in the block render, BG cells, and a render in the most-used palette (`work/gfx/w_<off>.png/.pal`).
  Rects of blank/duplicate tiles can map to the wrong copy: check odd ones by eye. `tools/gfx_grid.py` zooms a band
  with a tile grid.
- **Panelled atlases:** a 0x800 chain can be eight 128x32 panels laid 2 across in OBJ VRAM (256 px wide): layout
  `obj16x4*8/2` (`objWxH*N/R`, R units per image row). A word can straddle panels (big てん in 1F0F059 is 32x24).
- Group `btn` (done): cloud buttons 1F0D0FC (Quit/Continue), 1F0D56D (Quit/Retry), 1F0DA41 (Continue/New Game/
  crossed Continue/Select), 1F0E3F7 (Yes/No + prompt "Start a New Game?"), `tools/gfx_btn.py`; checked in pause,
  game over retry, tokoton (`work/qa/p8btn`). 1F0DA41/1F0E3F7 are on a screen no warp reaches yet (resource table
  1EFF434 entries 26/42): the prompt is drawn as one line in the first 128 px; check it when reached.
- Group `score` (done): HUD atlas 1F0F059 words pts/songs/Left/Song/Clear goal/High|Score/Rhythm, `tools/gfx_score.py`;
  checked in game over, tokoton, draw, results (`work/qa/p8score`). とくてん alone = と left half at (216,16) + x 48-87
  of さいこうとくてん. Left in the atlas (not seen in a warp yet): difficulty pills (128-224, 32-128: かんたん ふつう
  むずかしい いつもの きぶん きまぐれ パート ミックス, white 14-15 on the pill fill) and framed labels セー.. / あおあ.. /
  ポ / プ at (224-255, 16-64).
- 1F59B31 is a byte-identical copy of 17264E2 (difficulty sheet): a second row in `gfx/diff.tsv` with the same png.
  1F5ABD8 (800x4) has the same layout with パート/ミックス/シンクロ -> Part/Mix/Sync (`gfx_diff.SHEETS`; not warped yet).
- Group `draw` (done): 1F1345A is an 800x2 chain (not 0x40003): four 32x32 OBJ cells ひ/き/わ/け, each a separate
  bouncing sprite -> one letter of DRAW per cell at 3x (`tools/gfx_draw.py`), checked in scene 42.
- Group `winlose`: 1F12431 かち / 1F12CBD まけ (800x2: coloured word + silhouette, 64x32 each) -> WIN / LOSE at 2x
  centred across both 32x32 cells (`tools/gfx_winlose.py`); screen not warped yet (probably link/vs results): if the
  cells move apart like the draw screen, redo as one letter group per cell.
- Group `gameover` (done): 174AB9D (800x3, OBJ pal 1, tile 0): ゲ ム オ バ cells at screen x 32/74/104/152 + 32x8
  dash ×3 (x animated, no table in ROM: byte/halfword/Thumb-immediate searches found nothing) -> GAME (cell 1) OVER
  (cell 2), 1x wide 2x tall; クリアもくひょう strip -> CLEAR GOAL; big クリア -> CL/EA/R! one pair per 32 px cell
  (`tools/gfx_gameover.py`). GAME OVER checked in scene 37 (`work/qa/p8go`); CLEAR GOAL / CLEAR! not seen yet.
  Palettes dumped from a scene may repeat colours: `tools/palfix.py` nudges repeats so `gfx.load_pal` accepts them.
- **BG-mapped text:** `tools/gfx_bg.py show SCENE BG` renders a layer's whole map from a PPU dump with a cell grid
  (find BGs on with DISPCNT: an off layer still has stale VRAM); `Layer.compose(rect)` -> indices of map cells,
  `Layer.write(block_img, data, rect, img)` puts them back into the block's tiles (flips undone; raises on a tile
  shared with cells outside the rect, e.g. blank tile 0). Cells use several palettes: draw in colour space and pick
  each pixel's nearest index in its own cell's palette (`gfx_solo.edit`).
- Group `solo` (done): mode-carousel cards (scene 28, BG2 cb 0x4000, 64x32 map; the current card can be in either
  half) 1BF5582 とことん / 1BF7155 つづけて / 1BF8856 アニメで -> Marathon / Nonstop / Anime Pitch (D15),
  `tools/gfx_solo.py`: erase the fill strokes +3 px in banner-palette cells, redraw 1x wide 2x tall. The lettering
  is boxed in by art-palette cells and shared tiles, so each card has its own dx/dy and ring count. Checked in
  `work/qa/p8solo` (cold-boot warps). Polish: small transparent holes at the cloud / star edges where the old
  rings were.
- Group `options` (done): 1723EBE is a panelled atlas (`obj16x4*8/2`, 256x128; right half = background thumbnails).
  Labels are rows of OBJs 24 px tall on 2D VRAM rows (row = tile // 32), NOT on the 32 px panels: なまえ (80,0)
  はいけい (0,32) やじるし (64,32) ヘッドホン (0,56) あり (80,56) マーメイド (0,80) なし (80,80) -> Name / Background /
  Arrows / Headphones / On / Mermaid / Off (`tools/gfx_options.py`), checked in scene 14 (`work/qa/p8opt`).
  `gfx_where.py` rects are wrong for panelled layouts (it assumes 16-tile rows): take rects from the OAM tile numbers.
- Group `songsel` (done): 173F4E9 high-score panel labels かんたん/ふつう/むずかしい -> Easy/Normal/Hard, 8 px rows,
  plain font; group `pills`: 173FE48 six 16x8 difficulty pills か ふ む / い き き -> E N H / U M R (no warp shows the
  pills yet). `tools/gfx_songsel.py`, checked in song_select / difficulty (`work/qa/p8ss`).
- **Song titles (open):** 17403F7 1741079 1741389 17420A3 17426D4 1742B72 17430DC 17434B2 1743766 17439CC 1743CBB
  1743F0B (800x1 each, 128x32: title line 1 at y 0-15, line 2 continues at y 16-31, ruby kana in the rest). The OBJ
  list per title is data-driven, not a blank-tile scan: a test filling line 2 of 1742B72 showed only its first 40 px
  (32x16 + 8x16), the original title width. Titles: Taiyou no Rakuen ~Promised Land~ (200 px), Daiji na Takarabako,
  Koi wa Nan Darou, Sekai de Ichiban Hayaku Asa ga Kuru Basho, Yume no Sono Saki e, Kuro no Kyousoukyoku ~concerto~
  (168 px), Aurora no Kaze ni Notte, ヒッポと アルプス/すいか/おんがくか/カエル (Hippo and the Alps / Watermelon /
  the Musician / Frog), なにもないヨ! (Nothing here!). Romaji as in the credits (glossary). Byte/OAM-pattern searches
  for the sprite table found nothing: next, watch who writes the title OBJs (`watch.lua` on the OAM buffer) to find the
  table, then widen entries so the romaji fits.
- Group `clear` (done): 180F0F8 Kaito cut-in (BG3, map = tiles in order, 30 a row, a palette per cell) すごいぞ! /
  よくやったな -> Amazing! / Well done! on a white sticker over the old footprint (`tools/gfx_clear.py`), checked in
  scene 39 (`work/qa/p8clear`). Siblings 1813332 / 18170D4 (table 16F6CC8 entries 145/146, same size) are two more
  cut-ins: their per-cell palettes are not found yet (not a kcomp resource, not raw: `tools/findmap.py`); find what
  picks the picture in scene 39, warp each, then reuse `gfx_clear.edit` with their dumps.
- Episode-title strips 18AF223.. (45 rows, 800x2 each): episode grid (scene 25) loads 18AF223 into BG1 char 257+
  (pal 12, map rows 7-12, cols 7-22, tiles in map order, one tile per cell); locked episodes are mosaicked
  (`tools/lua/nomosaic.lua` clears the register but the bottom strip stayed blocky: not solved). Layout of the
  title text inside the block still unread; the map is per episode (find its source before redrawing).
- Old note: menu item labels (selected label: OBJ pal 2, tiles 768/776, two 64x32 at y 58; bag icons with two-line labels:
  OBJ pal 3 tile 512 64x64), then the rows of `graphics_sweep.tsv` by screen.
