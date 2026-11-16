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
  of さいこうとくてん. Results pills + buttons (session 27, `SPRITES` in `tools/gfx_score.py`, mapped from the OAM of
  the user's real-song state `work/states/results_real.mss`): pills = 48x16 top at (128|176, y) + 48x8 bottom strip
  in column x 176-223 (Easy Normal Hard Usual Mood Random Part Mix); buttons すすむ/セーブ -> Next/Save = 32+16 x 16+8
  pieces at x 224-255. Only Easy/Usual seen in game (fixture save); the other six pills checked on the atlas only.
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
  `tools/gfx_solo.py`: the old lettering +3 px, closed by 4 px, becomes a white plate edged in its old outline
  colour, painted in every non-shared cell it covers in that cell's nearest colour (art cells held outline bits:
  erasing banner cells only left them loose, tour3 verdicts); English 1x wide 2x tall, centred on the old lettering.
  Ring pixels on shared tiles or with no near colour are left out (Nonstop: 26). Checked in `work/qa/p8s`.
- Group `live` (done session 21, `tools/gfx_live.py`): live-data error (warp `live_broken`) BG3 picture chain 1747BC1
  800x10 (not in the sweep: `tools/lua/kcomplog.lua` at the warp). Bubble text cells use BG pals 4/5, gaps between
  letters pal 3 (no dark colour) and the map is not raw in ROM, so "Your live data / is broken!" sits in the two
  all-pal-4/5 bands (map rows 5-6, 9-10).
- Group `options` (done): 1723EBE is a panelled atlas (`obj16x4*8/2`, 256x128; right half = background thumbnails).
  Labels are rows of OBJs 24 px tall on 2D VRAM rows (row = tile // 32), NOT on the 32 px panels: なまえ (80,0)
  はいけい (0,32) やじるし (64,32) ヘッドホン (0,56) あり (80,56) マーメイド (0,80) なし (80,80) -> Name / Background /
  Arrows / Headphones / On / Mermaid / Off (`tools/gfx_options.py`), checked in scene 14 (`work/qa/p8opt`).
  `gfx_where.py` rects are wrong for panelled layouts (it assumes 16-tile rows): take rects from the OAM tile numbers.
- Group `songsel` (done): 173F4E9 high-score panel labels かんたん/ふつう/むずかしい -> Easy/Normal/Hard, 8 px rows,
  plain font; group `pills`: 173FE48 six 16x8 difficulty pills か ふ む / い き き -> E N H / U M R (no warp shows the
  pills yet). `tools/gfx_songsel.py`, checked in song_select / difficulty (`work/qa/p8ss`).
- **Song titles (done, session 13, group `songs`, `tools/gfx_songs.py`, `tests/test_songs.py`):** all 19 titles are
  ONE chain 17403F7 800x19 (the song list decodes it whole, so a title row written in place alone garbled every title
  after it, English ones too: each chunk having its own pointer does not mean it is read alone). Sprite system: OAM
  shadow 0x03001A98 (DMA at 0x08000624); 0x08008A74 draws an object: list = bank table 0x1D36F90[obj+0x1C] + obj+8;
  list = u8 count, u8 flag, count x (u16 y<<6|shape<<2|flip<<4, u16 x<<6|size, u16 tile). Titles are bank 0x1EFA714
  (entry 0); frame entries u8 + u16 offset (unaligned, 3 bytes) at 0x1EFEF2E. List per title (flag 0 / flag 1):
  3350/3558 太陽, 33C8/35D0 大事, 33E8/35F0 恋, 3464/366C 世界, 34BA/36C2 夢, 34F4/36FC 黒, 352C/3734 オーロラ;
  English titles 3388 33A8 3402 341C 3430 3444 34E6. Romaji (credits spelling) as one 16 px line in 32x16 pieces,
  lists rewritten in place (`gfx/songs.objs`, build stage `objs`). Checked: `work/qa/p8songs/sheet.png` (list top,
  list bottom, song select). Hippo songs 17434B2.. (ヒッポと.. / なにもないヨ!) are not in the song list with the
  fixture save; their lists are among 3760 3788 37A8 37C2 37D6 (+B), all showing block x 0-95 of rows 0-15, so the
  English is drawn there unchanged-list (unseen; may sit off-centre by up to 24 px).
- Old notes (song titles, before session 13): 128x32 blocks: title line 1 at y 0-15, line 2 continues at y 16-31, ruby
  kana in the rest. The OBJ list per title is data-driven, not a blank-tile scan: a test filling line 2 of 1742B72
  showed only its first 40 px (32x16 + 8x16), the original title width. Titles: Taiyou no Rakuen ~Promised Land~ (200 px), Daiji na Takarabako,
  Koi wa Nan Darou, Sekai de Ichiban Hayaku Asa ga Kuru Basho, Yume no Sono Saki e, Kuro no Kyousoukyoku ~concerto~
  (168 px), Aurora no Kaze ni Notte, ヒッポと アルプス/すいか/おんがくか/カエル (Hippo and the Alps / Watermelon /
  the Musician / Frog), なにもないヨ! (Nothing here!). Romaji as in the credits (glossary). Byte/OAM-pattern searches
  for the sprite table found nothing: next, watch who writes the title OBJs (`watch.lua` on the OAM buffer) to find the
  table, then widen entries so the romaji fits.
- Group `clear` (done): 180F0F8 Kaito cut-in (BG3, map = tiles in order, 30 a row, a palette per cell) すごいぞ! /
  よくやったな -> Amazing! / Well done! on a white sticker over the old footprint (`tools/gfx_clear.py`), checked in
  scene 39 (`work/qa/p8clear`). Siblings 1813332 / 18170D4 (done, session 16, checked `work/qa/p8clr12.png`): the
  scene code 0x08013E3C picks r4 = s8 0x0202FA0D (0 Kaito, 1, 2): block 0xBA + r4 of table 16F6CC8, BG palettes 0-13
  raw at 0x183AC40 + 32 * (14 * r4 + 0x5E9), map = table 0x184ECF4 entry 0x43 + r4 -> 3 bytes (?, u16 offset from the
  table) -> u16 0x8400 (compressed, 1024 cells) + stream for IWRAM decoder 0x080091A0: op n = (b & 0x3F) + 1,
  b < 0x80: n LE u16 literals, 0x80|: n x last+1, 0xC0|: n x last (`gfx_clear.decode_rec/encode_rec`). Warp: SCENE_ID=39
  WRITES 0x0202FA0D:<r4>. Both read よくがんばりましたね -> "You worked hard!" (2x3 en12, one tone, white sticker,
  blue sticker shadow; `gfx_clear.rainbow`). Cells whose palette lacks the tone or white (all 15 slots in use) move to
  a palette that has both, unpainted pixels remapped; the map record is rewritten in place via `gfx/clear.raw` (new
  build stage `raw`: in-place byte rows from `gfx/*.raw`, the generator checks each fits).
- Groups `cardbtn` `roombub` `hint` `prompt` (done, `tools/gfx_cards.py`, checked in room / card_game, `work/qa/p8cards`):
  1D031F4 buttons あそぶ/する/やめる/しない -> Play/Yes/Quit/No; 1D09C87 room bubbles (5 x 96x24) -> Put up a poster? /
  Play a game? / Place a mascot? / Listen to a song? / View cards?; 1D01FD9 chain (not in the sweep: found with
  `tools/lua/kcomplog.lua`, which logs every kcomp call's src/dst) Aきめる / Bやめる -> A OK / B Quit; 1C07510 BG1 prompt
  ゲームする? -> Play a game?. `tools/gfx_obj.py` = gfx_bg for sprites (compose OAM cells, write back by byte match;
  byte twins resolved by the VRAM - block delta). `tools/oamlist.py` lists sprites in a rect, `tools/objsrc.py` finds
  the swept block holding an OBJ tile. Open: 1C0657A (same frame tiles as 1C07510, another prompt, not seen yet);
  1D095BE おまけムービー! banner (room, unseen); 1D0B2A4 cards (no text: drop).
- **Relocation + chunk pointers (session 7):** `gfx.plan` moves a chain that outgrows its slot to just below
  0x2000000 (0x00 padding; text fills upward from 0x1FE0200 and ends ~0x1FEA0A0) and repoints every 32-bit pointer
  0x08000000|start (resource tables hold them unaligned, e.g. 16F6CC8 entries 5 bytes apart). Every chunk of a chain
  whose start moves is repointed too: a chunk can have its own pointer. Gotcha met: 179BC34..179E1E1 each have a
  pointer (episode cursor) but the grid reads the whole run as one chain, including pointerless 179E33F..179EFE4,
  so shrinking one chunk in place garbled the grid. `tests/test_gfx.py` fails when a pointerless stream follows a row.
- Group `epnum` (done): 179BC34 800x16 (cells 00-40, frames, tails): each cell's 話 plate -> "EP" (plain caps, pink 8 on
  white), `tools/gfx_epnum.py`; checked in scene 25 (`work/qa/p8ep`: grid 01-39 clean, cursor 01 EP). Palette = pause
  dump OBJ pal 0 (same ramp; scene 25 shows the locked grey fade).
- Group `bonus` (done, unseen): 1D095BE おまけムービー! -> Bonus Movie! (`tools/gfx_cards.py`).
- 1C0657A (open): second prompt panel, text つづけてあそぶ? (Keep playing?), frame tiles shared with 1C07510 but its own BG
  map, which is not in ROM as raw u16s and not a kcomp block starting with it (`findmap.py`, a raw search of the
  card_game map row): reach the screen (end of a minigame) and dump it, then reuse `gfx_cards.prompt`. Its map is
  probably a run-stream record like the minigame panels (execlog at 0x03000BF0 while it loads; retile as
  `gfx_minigame.retile`).
- Read (session 6): 179BC34 = the episode-select cursor OBJ (32x32, OAM 0 tile 4, pal 2; grid
  numbers are separate 16x16 OBJs without 話): each cell is two digits plus a small 話 plate at x 14-31 y 18-30 that
  overlaps the right digit's foot (x 16-20 y 18-21) -> plan "EP" on the plate (en12 plain caps, 11x7 fits x 21-31);
  the dumped palette is the grey fade, so take a palette from a non-faded frame. 1B6AFB2 (story BG2) is the series
  logo ぴちぴちピッチ tiled as a 64x16 wallpaper, many cell palettes: kept for now (see status). 170633B (results)
  showed only bars, numerals and icons in the warp: re-check its "small kana labels" after a real song.
- Group `eptitle` (done, session 11, `tools/gfx_eptitle.py`, `tests/test_eptitle.py`): 40 episode titles 18AF223..
  18BFC9C (800x2 each, blank tile 0 + the title's tiles; BG1 char 0x100+, pal 12, scene 25, cursor moves load the
  next). The BG1 map of title N is a record at u16 table 0x1881720 entry N (offset from the table; entry 0 = another
  screen): 5-byte header, then a stream that fills 1024 cells: byte < 0x80 = BE u16 literal (flips in the high byte),
  0x80|n = n+1 cells of last+1, 0xC0|n = n+1 repeats of last (writer: 0x08001FFC.., IWRAM fill 0x03000BF0). Our
  encoder reproduces all 40 records byte for byte. Build stage `maps` rewrites every record in place to one 24x5 cell
  rect at (3,8) (44 bytes; smallest old record 54; the rest is never read: decoding stops at 1024 cells), and each
  title is redrawn as one 2x-tall en12 line in it (roles kept: 1 body, 7/4 edge rings). The fixture save shows every
  title greyed + mosaicked (locked): `tools/lua/nomosaic.lua` now zeroes the mosaic shadow 0x030000B0 before the
  VBlank copy (0x08000B6C), which works. Checked: `work/qa/p8ept2/zc.png` (title 2). Unlocked colours not seen.
  `tools/lua/execlog.lua` logs registers at a PC (found the map stream via r7/r12 of the fill calls).
- **Name entry (session 8, read, not drawn yet):** the kana keyboard is OBJ pal 0 sprites (OAM 14-~60, tiles 0-210)
  from 171EAB9 (800x4), loaded as table 16F6CC8 record 39 (0x27) by the name screen (0x08010C44, table literal at
  0x08010E10, read only by the ldr at 0x08010C3A; r8 keeps it for record 0x76 = 179B69F header) AND by compose
  (0x0800E768, record 39; compose also loads record 42 = the same block for its lyric glyphs, record 38 into BG).
  Compose lyrics are sung kana, so compose keeps the kana keyboard: give the name screen its own copy (new chain +
  a copy of the 197-record table with record 39 repointed, literal 0x08010E10 -> the copy). `tools/lua/reslog.lua`
  logs record loads (lr of 0x080012D4 = the scene code). Records 39/40/42 all point at 171EAB9 (attr fa/3a/70);
  record 40 changed nothing visible in either scene. Layout per page (SELECT toggles hiragana/katakana): row 1
  あいうえお たちつてと まみむめも わをん゛゜, row 2 かきくけこ なにぬねの やゆよー ぁぃぅぇぉ, row 3 さしすせそ
  はひふへほ らりるれろ っゃゅょ (56 code keys a page). In the English build a kana name draws as junk: the name
  charset 0x187EA84 maps codes to glyph slots that now hold English letters. Plan: Latin keys (page 1 upper, page 2
  lower, digits/punctuation in the spare keys), charset entries of those codes -> en.tbl slots, ゛゜ keys blank
  (voiced codes -> the base letter). Shots of both original pages: `work/qa/ne_orig/kb.png`.
- Groups `names` `nehead` `nametag` (done, session 9, `tools/gfx_names.py`, checked in `work/qa/p8names`, `p8tag`):
  record 39 is ONE chain of 16 streams 171EAB9..1721BEB loaded whole into OBJ VRAM, 16 block tiles per 32-tile VRAM
  row (hiragana keys tiles 0+, katakana keys 512+ = chunk 4 171F78F, record 41; SELECT only swaps OAM tile numbers),
  so the fork row is `800x16` (a shorter fork would leave the game reading the rest past the copy). Keys: 8 px apart,
  groups at x 16/64/112/160, rows y 110/124/138, OAM 18-44 both pages (`name_kata` dump = warp + SELECT). Compose
  still shows kana (checked). Header 179B69F (800x2, OBJ pal 15): ボタン (OBJ 7 and 2 share tiles) けってい きりかえ ->
  Button / OK / A/a. Name tag 1F0CEC0 (opening movie, link_check; OBJ 9+5 at 122,136) なまえ -> Name. Compose's
  header (OBJ pal 3: ボタン OBJ 2, メニューへ OBJ 0+1) sits in the original 171EAB9 chain itself: group `cohead`
  rewrites that chain in place (FORKS keyed by group, so the same offset has the fork and the in-place row).
  `gfx_obj.write` now resolves byte twins with a strided-load model first (VRAM t = base + k//tw*32 + k%tw), since
  the plain delta differs per VRAM row on such loads.
- **Room sub-screens (session 10):** from the room warp state, `6 up;40 -;6 a` opens the minigame title (4 games,
  left/right), `up` x3 + `a` the mascot picker (route in `work/qa/p8room`). Dumps (original ROM): `work/qa/ppu/minititle`
  (page 1), `minititle2..4`, `mascot`. Group `roomsel` (done): 1CFC7D6 BG2 banner どのマスコットをおく? -> Place which
  mascot? (`tools/gfx_roomsel.py`, checked in `work/qa/p8room/mascot_z.png`). Group `roombtn` (done, unseen: the save
  owns no mascots): 1D0ADC0 slot buttons ひみつ★ / おかない / はらない -> Secret / No mascot / No poster. 1CE3D71 (poster
  banner) has another map than the mascot one (composing it with the mascot map gives garbage): open until the poster
  picker is reached (A on the wall did nothing with this save: probably needs an owned poster). 1CFDD65 (card
  collection banner) likewise unreached.
- Group `minipanel` (done, session 12, checked `work/qa/p8mini/sheet.png`, all 4 pages): 1C00CFF (pages 1-2) /
  1C00403 (page 3) / 1C01554 (page 4), BG1 pal 10. Their BG1 maps are run-stream records (eptitle format, no header
  offset: r12 of `tools/lua/execlog.lua --var PC_LO=0x03000BF0` on page load is the stream start): 1D250BA (pages
  1-2), 1D2502C (p3), 1D25156 (p4). Each record sits after `00 c4`, reached by a 32-bit pointer to that `00 c4`
  (1D250B4 -> 1D250B8 etc.); a table at 1D1E6D0 points at the `00 <ptr>` entries. `tools/gfx_minigame.py` gives every
  cell of the text rect its own tile (content dedup broke the increment runs: 189 > 149 bytes; unique = 124 bytes,
  114 of 117 free slots) and writes `gfx/minipanel.maps`; build stage `maps` (`gfx_eptitle.apply`) now also applies
  every `gfx/*.maps` row in place (zones too).
- **Minigame logos (done session 20, `tools/gfx_logos.py`, D18):** the loader adds 2 (pages 1, 3) or 6 (pages 2, 4)
  to the record's pal bits 0-3 and a tile base (VRAM 256 for pages 1/3, 640 for 2/4: each slot holds 384 tiles);
  palettes cut from the dumps into `gfx/logos.pals`. The generator renders the whole screen in RGB, erases the kana
  (fill components in a box, letter colours only, plus joined shadow), inpaints holes from neighbours, letters
  English, re-picks each cell's palette, and retiles the whole screen (dedup with flips: 223-253 tiles); records
  that grow are moved by stage `maps`. In game the first page is くらべて (Compare), right -> Line Up, Match, Catch
  (warp `SCENE_ID=15` route `30 -;6 up;40 -;6 a;200 -` then `6 right;150 -`, `work/qa/p8logos`). Old notes:
  BG2 (char 0x4000, map 0x600D000 64x32; pages 2/4 go to the right screen 0x600D800), map
  records also run-stream with palette bits in the stream (pals 0-3): page 1 くらべてピッチ chain 1BF198F 800x4 map
  1D243B9 (280 bytes); p2 そろえてピッチ 1BF2D7E 800x4 map 1D244D8 (316); p3 あわせてピッチ 1BF039E 800x6 map 1D24266
  (332); p4 キャッチでピッチ 1BF416C 800x4 map 1D2461B (327). Lettering is interleaved with card/character art and
  stars, and the 256 tile slots are nearly full (max tile 229-258), so a redraw needs a design (top word + "Pitch"
  lettering over the art, retile by content) and maybe a longer chain (check the loader's chunk count first). Some
  logo cells use tiles loaded from another chain (composite `work/qa/p8mini/logos.png` showed blanks there).
- **Card game (session 14, `tools/gfx_cards.py`, D17):** reached by warp `SCENE_ID=15` + A presses (route in
  status) or `work/play/cards` (play.py; step 0002 = the higher/lower question; right+a wins with left K). Dumps
  (original ROM): `work/qa/ppu/card_pick|card_hilo|card_lose|card_win|card_cont`. Groups `hilo` 1D02946 (Higher!/
  Lower! buttons), `cont` 1D02DEB (Keep going/Stop here), panels `pick` 1C04DE8, `hilotxt` 1C0537C, `conttxt` 1C078DE,
  big words `zannen` 1C023B4 (Too bad!) and `atari` 1C030D4 (Right!). Their BG1 maps are run-stream records
  0x1D254B7 0x1D25528 0x1D258E7 0x1D252A4 0x1D2532D (found by decoding every offset near the minigame records and
  matching the dumped map), rewritten through `gfx/cards.maps`. Each record sits behind resource table 0x1D1E6xx
  (5-byte entries -> record - 7, which holds a self pointer to record - 2): relocation possible but not built. Big
  words use `gfx_minigame.retile_keep` (edit tiles in place; allocate only for edited shared tiles, reuse identical
  tiles) so the record does not grow. All checked in game (`work/qa/p8hilo`, `work/qa/p8win`).
- **Minigame prompt panels (session 15, `tools/gfx_cards.py` PANELS):** same run-stream records, back to back:
  1D25428 (`guess` 1C047A6 このなかから おなじカードをあててね!, screen unknown), 1D254B7 `pick`, 1D25528 `hilotxt`,
  1D255BC (`memo` 1C05A1E おなじえをそろえてね。, memory game start; dump `work/qa/ppu/mem_panel`), 1D2563D (`crane`
  1C05F03 Aボタンでいどう、はなすとつかむよ!, crane start), 1D256CE (`again` 1C0657A つづけてあそぶ?, smaller frame),
  1D25730 (`nocoin` 1C06A00 コインがたりないよ!), then 1D25791 1D2587A (other frames), 1D258E7 `conttxt`. Found by
  rendering each block through each record (the right pair reads cleanly). Each block letters with its own core index
  (4, 5 or 7: most common non-fill index in the text tiles). In the small frame the kana tops reach the ornament's cell
  row: PANELS `keep` keeps its top 3 pixel rows. 1C06EBF: another frame, record not found. Memory/crane games reached
  from cold boot: warp SCENE_ID=0 WRITES 0x03003B98:<1 crane|2 memory>:2@200 + the minigame row's route + `6 a;200 -;6
  a;200 -` (work/qa/p8crane, p8mg2b). The play.py session `work/play/mem` started from an original-ROM state, so its
  OBJ tiles (hint Aきめる) are stale Japanese: not a bug (cold boot shows A OK).
- **Unreached minigame words (session 17):** match a block to its run-stream record by tile count: decode the
  block's chain until its last non-blank tile, then the record (scan `00 c4` + stream near 0x1D24000-0x1D26200) whose
  max cell index equals it. 1C01D37 800x2 (last 106) -> 1D251F3 ゲット!; 1C03D2A 800x4 (143) -> 1D2539F やったね;
  1C06EBF 800x2 (95) -> 1D25791 (card frame + bottom panel すきなところでとめてね!). Same palette roles as ざんねん.
  A record that grows is moved by stage `maps` (`gfx_eptitle.placed`: `00 c4` + stream at MAP_RELOC, pointer at
  record - 6 repointed); checked by moving zannen's record with the old stream zeroed (card game loss still drew it).
- **Unreached rows, loaders (session 17):** 1721BEB (800x4, pill words かんたん ふつう むずかしい いつもの きぶん, NOT
  part of the names chain, which ends at 1721BA8) and 1722E8B (800x4) = records 47 / 48 of table 16F6CC8. Table
  1B9A7F8 (193 records; literal pools 0x3AEC8 0x3B5A8 0x3C250 0x3C784 0x3CED0 0x3D90C = the loading code): character
  banners 1BFA943 1BFC919 1BFE551 = records 50-52, poster banner 1CE3D71 = 137, card collection 1CFDD65 = 173.
  `reslog.lua` on warps to the uncovered scene ids 16 17 26 30 31 33 34 38 (original ROM): none loads any of these.
  Room (state work/states/room.mss): only `up` + A reacts (minigame title; up x3 = mascot); left/right/down, held
  or tapped, do nothing there. Next: break on the loaders above (execlog at the functions owning those literal
  pools) to learn which scene/sub-mode calls them, then add a warp.
- **Room state machine (session 18):** scene 15 runs a state machine at 0x03003DFC (layout of 0x08049F70: +0 table,
  +4 state, +5 next state; log it with `tools/lua/smlog.lua`), table 0x09F730C0: 0 0803AAC1, 1 0803B369 (room idle),
  2 minigames, 3 0803C389 poster picker (loads 1CE3D71 = record 0x89), 4, 5 0803E79D card collection (1CFDD65 =
  0xAD), 8 mascot. Room state 1 reads the hotspot u16 0x03003D7A at 0x0803BB1A on A (1 poster, 2 -> 4, 3 mascot, 4
  card collection, else minigames); warp rows `poster`, `card_coll` force it there (warp.lua write `addr:val:size!pc`).
  Groups `poster` (どのポスターをはる? -> Which poster?) and `cardcoll` (★カードコレクション★ -> ★Card Collection★),
  `tools/gfx_roomsel.py` BANNERS, checked `work/qa/p8banners.png`.
- **Minigames (session 18):** per-game update functions (sub-state u8 0x03003CB5 for all): memory 0803FD70 (jump
  table 0x0803FD9C: 6-8 flips, 14/15 mismatch, 9-13 + 29-33 lose, 16 やったね, 20 すきなところでとめてね!, 21 ゲット!,
  then つづけてあそぶ?), crane 08043278, card game 08045548 (room minigame page 1), slot 08048674 (page 2: reels
  0x03003D9C/9E/A0 u16 positions, stop flags 0x03003D98-9A; state 7 spin, 8 check, 9-15 result; all reel positions 2
  = あたり win, record 0x3A). Warp `memory_win` forces 16 at state 6 (0x08040736): Hooray! / Stop it wherever you
  like! / Got it! all checked from a cold boot (`work/qa/w_memwin`; `tools/lua/poke.lua` pokes RAM at frames from a
  state). A pink おなじえをそろえてね。 seen there from `work/play/mem` states was stale VRAM (original-ROM states).
  Character banners 1BFA943 1BFC919 1BFE551 (records 0x32-0x34): no immediate 0x32-0x34 reaches table 1B9A7F8 in
  0x0803A000-0x08050C2C, not loaded by the room, its sub-states, memory win, slot win or slot lose (reslog): still
  unlocated (crane win? story?).
- Old note: menu item labels (selected label: OBJ pal 2, tiles 768/776, two 64x32 at y 58; bag icons with two-line labels:
  OBJ pal 3 tile 512 64x64), then the rows of `graphics_sweep.tsv` by screen.
