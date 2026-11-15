# Visual-QA reviewer brief - Mermaid Melody Pichi Pichi Pitch: Pichi Pichitto Live Start! (GBA)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Optional: the original ROM's sheets (`work/qa/tour_jp/`, same ids) and `glossary.md`.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.
- Zoom into every Yes/No prompt, selection box, menu row and speech bubble: a few pixels of misalignment don't show
  at sheet scale. To measure one: `python -X utf8 $SKILL/scripts/inkbox.py SHOT.png x,y,w,h`.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- text off-centre where the original centres it: an option in its selection box or cursor brackets, a label, a bubble;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok` (the controller adds the game's own below):
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- Japanese kept by ruling (`docs/decisions.md`): the title logo マーメイドメロディー ぴちぴちピッチ / ライブスタート!
  and its copyright line (D16); the faded ぴちぴちピッチ logo wallpaper behind story dialogue; the debug menu and its
  message viewer (D13: the viewer's box uses the old font, so English there is junk by design: `debug_menu`,
  `msgview`); the compose screen's kana keyboard and kana lyric glyphs (compose writes sung kana); the KONAMI logo.
- Minigame logos くらべてピッチ / そろえてピッチ / あわせてピッチ / キャッチでピッチ on the minigame title pages: known
  and tracked (`tools/gfx_left.py`): `ok` with the note "known logo".
- Song lyrics are romaji by ruling (D10); the player name in the save fixture is two Latin letters.
- Story runs mash A every 30 frames, so frames catch pages mid-typing and the song after the dialogue; a gameplay
  screen ending in game over (nobody plays the notes) is expected.
- Scenes 17/30/31 warp to a blank screen (the debug tool's known gap), same in the original.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
