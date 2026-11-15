# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

All of D1-D7 came from the owner's standing answers injected into the one-shot run (Orca coordinator brief).

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-15 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing default. |
| D2 | 2026-11-15 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-15 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-15 | Abbreviations | engine work first (default), abbreviate | Default: full names and terms, engine work (VWF, wider boxes, relocation) before abbreviating; abbreviation only as a flagged last resort. |
| D5 | 2026-11-15 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); leave the original Japanese logo only if it has no official English version. |
| D6 | 2026-11-15 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint, report at the end. |
| D7 | 2026-11-15 | Existing saves / savestates | user's saves, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-15 | Release / visibility | — | Never run `gh release create` or change repo visibility; the run ends at a built and verified release zip. |
| D9 | 2026-11-15 | English font (agent default under D4/D6) | existing 12 px Latin glyphs at 12 px pitch; half-width 8 px mode; new proportional font + VWF | New hand-drawn proportional font with a VWF hook: ~38 chars per 216 px line vs 18 Japanese, so no abbreviation and boxes roughly keep their size; story bubbles grow per message in the build. |
| D10 | 2026-11-15 | Song lyrics (agent default under D6, user may overrule) | romaji, English meaning | Romaji: matches the sung audio and the karaoke colour sweep. English-word loans stay English (Melody, Kiss); Japanese-ised loans stay romaji (doa, garasu). |
| D11 | 2026-11-15 | ラブ②シャワーピッチ (agent default) | Love♥Shower Pitch, Love Shower Pitch, Love Love Shower Pitch | "Love Love Shower Pitch": ② in the font is a plain circled 2 (rendered from the ROM), read as the repeat mark; the Japanese font has no heart (the English font has ♥, so "Love♥Shower Pitch" is possible); two reviewers read it so and Lucia reacts to it as a variant. |
| D12 | 2026-11-15 | Plural of called names (agent default) | glue "s", reword, write out | Write "Mermaid Princesses" out in place of `{call:@2B27}` or reword; a glued "s" draws "Princesss". Gaito-sama, never "Lord Gaito" (glossary -sama rule). |
| D13 | 2026-11-15 | Leftover debug menu text 0040/0110 (agent default) | English (abbreviated to fit the grid), keep Japanese | Keep Japanese (status keep-jp): the debug menu draws with the original Japanese font, so English codes come out as junk kana; dev-only, never seen in normal play (docs/re/scenes.md). |
| D14 | 2026-11-15 | Main-menu mode names and difficulty labels in graphics (agent default under D6) | keep "...de Pitch" pattern as "X Pitch"; plain words (Solo, Link...) | "Solo/Link/Hippo/Your/Collect/Live Pitch" keep the shared "Pitch" of every mode; difficulty Easy/Normal/Hard/Usual/Mood/Random; header pieces ボタン/けってい/もどる = Button/OK/Back (pieces are shared sprites, so "Ⓐ Button OK"). |
| D15 | 2026-11-15 | Solo Pitch sub-mode names (agent default under D6/D14, non-blocking) | Endless/Marathon; Continue/Nonstop/Medley; Anime | とことん = all the way (100-song run) -> "Marathon Pitch"; つづけて = keep going -> "Nonstop Pitch"; アニメで -> "Anime Pitch". Game over lettering "GAME OVER", クリアもくひょう "CLEAR GOAL" (matches the HUD "Clear goal"). |
| D16 | 2026-11-16 | Title logo マーメイドメロディー ぴちぴちピッチ / ぴちぴちっと ライブスタート! and copyright line (agent default under D5, non-blocking) | redraw in English; keep | Keep the logo blocks 1703236 1CA6F51 1C2D4F9 and the copyright line as they are: no official English logo of this game exists (D5's exception), the series logo is the brand art, and the copyright names are legal text. The README gives the English title. |
| D17 | 2026-11-16 | Card game (くらべてピッチ) wording (agent default) | literal; short | おおきい!/ちいさい! -> Higher!/Lower!; あたり -> Right!; ざんねん -> Too bad!; つづける/やめておく -> Keep going/Stop here. |
