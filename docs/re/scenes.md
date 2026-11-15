# Scene system and debug tool (phase 2)

## Scene dispatcher (verified)
- Main loop 0x0800E1C0 calls `scene_table[u8 0x0300287C](0x0300287C)` every frame. Table: ROM 0x09D37060, 43 Thumb
  pointers (ids 0-42). **verified**: writing the u16 id from Lua switches scenes (`tools/debug/warp.lua`, all 43 ids).
- Struct at 0x0300287C: +0 id, +1 flags (bit 7 = scene initialised; writing the id as u16 clears it, so the next
  frame runs the scene's init), +4 return-stack depth, +5.. return stack (B/back pops it, e.g. scene 8 at 0x0800CD8E).
- Before the main loop a pre-loop shows the logos with id 0 until ~frame 731 and overwrites the id; then scene 9
  (opening) is pushed over 2. The save is read at boot (0x080038F4 / 0x08003E18 from AgbMain), so warping at scene 9
  keeps the save's name and settings.
- Scene id 0 run from the main loop is a **leftover debug menu** (font text, message 4): 歌 / 内田 / モード選択 / 曲作り /
  MOVIE / Song / メッセージ / 止め絵チェック | 歌選択 / ライブ / 川原 / ミニゲーム / アニメ / - / ちびキャラ / BMP | SE / BGM /
  しゃべり / Option / 通信 / - / SRAM消去 / EXIT. A opens a number box (value u16 0x03003B98, reset when the box opens:
  poke it after), A again launches. Debug-only text: never shown in normal play.

## Scene ids (warp from cold boot; shots in `work/qa/warp/sheet/`)
| id | screen | id | screen |
|---|---|---|---|
| 0 | debug menu | 22 | difficulty (とことん, A/B header) |
| 1 | KONAMI logo -> menu | 23 | difficulty, green (アニメで) |
| 2 | opening movie (name box overlay) | 24 | difficulty, green variant |
| 3 | title | 25 | episode grid 01-39 |
| 4 | ライブのデータがこわれているよ! | 26 | story dialogue (アニメでピッチ) |
| 5 | gameplay, then results | 27 | framed dialogue with name tag |
| 6 | results with セーブ | 28 | ひとりでピッチ mode carousel |
| 7 | song select (live) | 29 | つづける / やめる |
| 8 | main menu (6-item ring) | 30, 31 | blank when warped (need context) |
| 9 | opening / name entry (blank save) | 32 | song title list |
| 10 | song select + difficulty | 33, 34 | jump to 35 at once |
| 11 | link check (いっしょにピッチ) | 35 | difficulty (Hippo) |
| 12, 19 | live list (ライブでピッチ) | 36 | とことん progress + つづける/もういちど/やめる |
| 13 | composer (ヒッポでピッチ) | 37 | ゲームオーバー + もういちど/やめる |
| 14 | options (あなたのピッチ) | 38 | returns to menu at once |
| 15 | room (あつめてピッチ) + minigames | 39 | すごいぞ!よくやったね (clear) |
| 16 | returns to menu at once | 40 | とことん start (あと100きょく) |
| 17 | blank when warped | 41 | とことん progress -> ゲームオーバー |
| 18 | Hippo picture + dialogue box | 42 | ひきわけ (draw) |
| 20, 21 | staff roll (原作, cast...) | | |

Menu ring order (Down): ひとりで -> いっしょに -> あつめて -> ヒッポで -> ライブで -> あなたの. ひとりで (28) modes (Right):
とことんピッチ -> つづけてピッチ (33 -> 35 -> 5) -> アニメでピッチ (23 -> 26).

## Story (アニメでピッチ)
- Debug アニメ N (N = 1..39; 0 = 1, 40+ = 39) starts episode N in scene 26. Episode script: message id = s16 script
  word + 0x500 (0x08035CCE), shown by show_message (0x080046E4: r0 slot, r1 id). First message 1280 + N (episode 22
  starts at 1367). **verified** (`work/qa/eps`, 45 runs).

## Text hooks
- `tools/lua/showmsg.lua`: each show_message call (slot, id, caller). `tools/lua/msglog.lua`: each message the
  engine starts (0x08007488, id at text object +0x18), plus `TEXT <hex id>` lines for `textcover.py`.
- Gameplay lyrics are messages 512+ (song 1: 512-539; つづけて first song 480-501), set up at song start.

## Debug tool
- `tools/debug/scenes.tsv`: name, id, expect, writes, route, note. `tools/debug/warp.lua` (doc in its header).
- Save fixture: `python -X utf8 tools/debug/make_save.py` (blank SRAM -> name あい -> menu, written by the game) ->
  `work/saves/default.sav`. Warps run with `--sav work/saves/default.sav`.
- All scenes: `python -X utf8 tools/debug/regen.py [ROM]` -> shots `work/qa/warp/sheet/<name>.png`, states
  `work/states/<name>.mss`; exit 1 if any scene does not arrive. Regenerate after code/font/graphics changes.
- Parameter sweeps: `tools/debug/warp_many.sh story EP work/qa/eps 1 2 3` (one run per value);
  `tools/debug/warp_ids.sh OUT ID..` (raw ids), `tools/debug/dbgmenu.sh OUT COL,ROW..` (debug-menu items).
- Not yet: GOD mode (gameplay life gauge address unknown: unhit songs end in game over), 止め絵チェック (box did not open
  with this route), movies 0-7 (FMV, no text seen).
