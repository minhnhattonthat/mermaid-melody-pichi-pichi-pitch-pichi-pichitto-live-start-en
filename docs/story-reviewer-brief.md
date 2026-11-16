# Story reviewer brief - Mermaid Melody Pichi Pichi Pitch: Pichi Pichitto Live Start! (GBA)

You read one chapter (one story-mode episode) of a JP->English fan translation straight through, in story order, the
way a player meets it. Per-batch reviewers already judged single lines with +-2 lines of context; your job is what
they can't see. Read-only: no edits, no git, no subagents. Return the report as your final message; the controller
saves it.

## Inputs (paths in your dispatch)
- Chapter file: every line of the episode, `>> id | speaker | JP` / `EN`. Read ALL of it before judging.
  - Order: the order a tour run showed the lines (Lucia's intro narration, the story bubbles, the song), then lines
    the run never reached (marked `(+)`: after the song, endings, branches), placed by message id. Treat the `(+)`
    placement as approximate; don't report an ordering problem it causes.
  - Calls are resolved (names inline), control codes dropped, ` / ` = a page break. `【name】` mid-line = a new
    speaker. Speaker `-` = narration or no name tag.
  - Song lyrics are romaji by ruling (D10), not English: skip them.
  - `extras` is not an episode: lines whose episode is unknown. Judge each line alone plus its neighbours.
- `docs/synopsis.md` (plot, who is who), `docs/style-reference.md` (voice per character), `glossary.md` (rulings at
  the top), `docs/decisions.md` (the owner's rulings: honorifics, names, romaji lyrics).

## Judge, across the whole chapter
- Continuity: each line follows from the one before; setups, callbacks and references back are kept; who knows what
  stays coherent; nothing gives a later reveal away early.
- Voice: each character sounds like the same person all chapter and matches their style-reference row: speech quirks,
  register, how they address others (Hippo's "Lucia-sama" etc.). Name the line where a voice drifts or goes neutral.
- Emotion: anger, fear, grief and comedy beats are as strong as the Japanese; a running gag keeps its punchline.
- Names exactly as in glossary.md; no "1th"-style suffix on a variable; no awkward stock phrases.
- Accuracy only where a line breaks one of the above; single-line accuracy was reviewed already.
- Line width, wrapping and box fit are checked by tools: don't report them.

## Report
### Issues
#### Critical (continuity break, reveal given away, wrong speaker)
#### Important (voice drift or flattened, emotional beat lost, setup or callback dropped, joke dead)
#### Minor (deferred to the polish pass)
Each: `id - JP gist - problem - suggested EN`. Write `none` under an empty severity.
### Assessment
`ok` (no Critical/Important) | `issue` - one sentence why. The controller writes this word into the chapter's verdict.
