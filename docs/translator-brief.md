# Translator brief - Mermaid Melody Pichi Pichi Pitch: Pichi Pichitto Live Start! (GBA, 2004)

You translate part of the Japanese script of this Konami rhythm/adventure game (based on the shoujo anime: mermaid
princesses Lucia, Hanon and Rina sing to defeat villains) into English for a fan patch. Audience: young fans; tone
bright and warm, comedy and light drama. Work only on the batches named in your dispatch, one at a time in the order
given, each to a passing check before the next. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - character voices and example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table and rules in `glossary.md`: read its
   Rulings and Style rules sections once).
3. `docs/synopsis.md` - who is who.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>(empty)<TAB>limit<TAB>Japanese`. Japanese is the game's text with control codes in braces and
`\n` for a line break. Lines are in story order: use neighbours for context (story bubbles carry no speaker; work it
out from the conversation). `limit` = box kind, pixel width of one line and lines per page (`bubble 212px x3`); a `?`
after the kind means the box was not measured yet (the limit is what the Japanese uses).

Control codes you will see:
- `{call:@2A5B}` etc. = a name the game inserts (2A5B Lucia, 2A70 Hanon, 2A96 Rina, 2AAC Karen, 2AB0 Hippo, 2AB4 Meru,
  2AE7 Kaito, 2B32 "Mermaid", 2B27 Mermaid Princess; the rest: look the id up in `script/msg_04.json`'s `en`).
  `{call:@2B8C}{call:@NAME}{call:@2B92}` at the start = the speaker's name tag; keep it exactly at the start.
- `{FA:06}` = new page (wait for the button, clear the box); `{wait}` = wait for the button then new page.
- `{FA:FF....}`, `{FA:0B..}`, `{FA:18}`, `{FA:8x}` (colour) etc. = scene effects, portraits, colours: copy every one,
  in the same order and the same place relative to the words they wrap (a colour code before a word stays before
  its English equivalent, its reset after it).
- `{FD:01}（よみ）{FD:00}` = furigana reading: drop the whole run (codes included) and write the name/word in English.
  Other `{FD:..}` codes stay.
- `{F6:..}` = the player's name, `{FB:..}` = a number: no suffix glued on ("No. {FB:..}" not "{FB:..}th"), no a/an
  right before them.
- `{end}` stays at the very end.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Only these characters: ASCII letters, digits, space,
`! ? . , ' " : ; - ( ) [ ] / & ~ * + = % # < > _` and `… ♪ ♥ ★ é`. No tabs, no curly quotes, no em dash, no
Japanese or fullwidth characters (no `　`: use a normal space), no `\uXXXX`.

Line breaks: **don't copy the Japanese line breaks.** Write each page as one run of text; the check word-wraps it to
the box. Write `\n` only where a break must fall: where the Japanese has a `\n` right before its trailing codes
(`...ます！\n{FA:0B78}...{end}` -> `...!\n{FA:0B78}...{end}`), in lists/menus/credits laid out line by line, and
in lyrics if the Japanese breaks there. If the check says a page has too many lines, split it with `{FA:06}` at a
sentence boundary (page breaks may be added or dropped freely) or tighten the wording.

Menus and the debug menu laid out with `　` padding in columns: keep the same number of characters per line (pad
with spaces) so columns still line up; those boxes draw 8 px monospace.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Keep the speaker audible (voices in `docs/style-reference.md`). A line any speaker could have said is a mistake.
  Villains' わ/のよ/ですわ sneer -> theatrical English ("How pathetic!", "my dear"); Hippo's fussy ですよ/さま ->
  "Lucia-sama!", "Honestly!"; children's ～ drawl -> stretched words.
- Names and terms exactly as in the glossary. Never abbreviate to fit: rephrase, add a `{FA:06}` page, and if it
  still won't fit report `LONG: id`.
- Honorifics kept, hyphenated, Western name order: ～さん -san, ～くん -kun, ～ちゃん -chan, ～せんせい -sensei,
  ～さま on a name -sama. お姉ちゃん/ねーちゃん -> "Sis"; ママ -> "Mom". Not honorifics: みなさん "everyone",
  おかあさん "Mom", たくさん "lots".
- Punctuation: 「」 -> "...", 『』 -> '...' (titles), …… -> `...`, ！？ -> `?!`, ～ at the end of a cheerful line -> `~`
  or `!`. ♪ ♥ stay. Thoughts in （…） stay in ( ).
- Song lyrics (ids 256-305, 512-1023; most `lyrics` limit rows): **romaji, not English**, Hepburn without macrons
  (おう -> ou in names is "o": Hosho; in lyrics write long vowels as sung: "kimi wo omou"), particles は へ を as
  `wa e o` (write `wo` only where the song clearly sings "wo"), words separated by spaces, lowercase except names and
  English words (`Love`, `Pichi Pichi`). Song titles in their official romanised form.
- Credits: staff names Western order, Hepburn, no macrons (大内哲也 -> Tetsuya Ouchi); roles in English
  (作詞 Lyrics, 作曲 Music, 編曲 Arrangement).

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
