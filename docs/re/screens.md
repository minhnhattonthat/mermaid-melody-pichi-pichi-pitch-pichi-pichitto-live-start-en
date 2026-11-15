# Screens seen (phase 1 tour, original ROM)

Game type: rhythm game (DDR-style arrows). Most Japanese on screen is pre-drawn graphics; no font-drawn dialogue seen yet.

| Screen | How to reach (cold boot) | Japanese seen | Drawn as |
|---|---|---|---|
| Name entry (first boot, no save) | boot, ~frame 900 | header `STARTボタン けってい / SELECTボタン きりかえ`, kana keyboard | graphics (keyboard); entered name: font, encoding unknown |
| Intro movie | boot, ~1000-1800 | none seen | video |
| Title | Start at 1800 skips movie | logo ぴちぴちっと ライブスタート!, Push Start Button (English), copyright line (JP kanji) | graphics |
| Main menu | `tools/routes/boot.txt` (Start at 1800 and ~2130); state `work/states/menu.mss` | items ひとりでピッチ / あなたのピッチ / いっしょにピッチ / あつめて.. / ラ.. ; bottom caption per item (こうとくてんめざしてがんばろう! etc.) | BG + OBJ graphics, compressed (`docs/re/compression.md`) |
| Character select | menu, A | name banner (e.g. るちあ), top-right label | graphics |
| Song select | then A | song title `Rainbow Notes` (English), small JP labels | graphics |
| Difficulty | then A | かんたん / ふつう / むずかしい-style buttons | graphics |
| Gameplay | then A | none seen in the first seconds | - |

Not yet visited: あなたのピッチ, いっしょにピッチ, あつめて (collection), options, results, game over, ending/credits, save prompts.
