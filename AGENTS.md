# Mermaid Melody Pichi Pichi Pitch: Pichi Pichitto Live Start! (GBA) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, `python tools/skill.py` prints it). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py` -> build/mermaid_en.gba (checks the dump against `rom.sha1` first; build.py arrives in phase 3)
- Check:    `python -X utf8 tools/check.py` (tests + lint; the pre-commit hook runs this; hook path set by `git config core.hooksPath tools/hooks`)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/mermaid_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 $SKILL/scripts/emu.py build/mermaid_en.gba --sav work/saves/default.sav --out work/qa/w --script tools/debug/warp.lua --var "SCENE='<name>'" [--var EP=N | MSG=N] --frames 1200 --sheet` (scenes: `tools/debug/scenes.tsv`, notes `docs/re/scenes.md`; never ask the user to play to a scene). Save fixture: `python -X utf8 tools/debug/make_save.py`. All scenes + states: `python -X utf8 tools/debug/regen.py [ROM]`
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba` (32 MiB, gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own copy in `tools/mesen/` (MesenCE 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored; GBA BIOS in `tools/mesen/Firmware/gba_bios.bin`; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/msg_NN.json` (units in address order: id, ids, used, jp, en, status, notes; text form and codes in `tools/msgcodec.py`, `docs/re/text.md`). Dump: `python -X utf8 tools/msgcodec.py dump [--force]` (--force keeps en/status/notes). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.
- Build helpers copied from the skill: `tools/tbl.py`, `tools/bps.py`, `tools/romdiff.py`. QA tools (`emu.py`, `play.py`, `qa_gate.py`, `jp_left.py`) run from `$SKILL/scripts/`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- 32 MiB ROM: patch as BPS or xdelta, never IPS. No armips on PATH; assemble with Python keystone (check conditional `bl` bytes).
- Gotchas met while working go in `docs/skill-gotchas.md`, one line each.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
