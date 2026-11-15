# Skill gotchas

One line each: the skill reference file it belongs in, then the fact.

- scripts/fetch_emu.py: `gba-bios` 404s; retrobios renamed the file to `bios/Nintendo/Game Boy Advance/GBA_bios.rom` (same SHA-1 300c20df...). Downloaded by hand with curl into `tools/mesen/Firmware/gba_bios.bin`; the BIOS table in fetch_emu.py needs the new path.
- SKILL.md / context-mode: with the context-mode plugin active, plain `cat`/Read of long reference files gets truncated to an index; read them through `ctx_execute` instead.
- references/emulator-qa.md: Mesen (portable) keeps a GBA battery save in `tools/mesen/Saves/<rom>.sav` across emu.py runs without `--sav`, so first-boot screens (name entry) appear once and never again; pass `--sav` with a blank file (32 KiB of FF) to reach them.
- references/emulator-qa.md: watch.lua logs one line per PC, so a loop or DMA writing a whole glyph shows only its first write (often 0); diff two ppu dumps to see what really changed.
- references/emulator-qa.md: GBA `.io.bin` BG scroll registers are write-only; the dump read back 48,48 for every BG while the real scroll was 0. Do not compute map positions from them.
- references/pipeline.md (Recon, code = font cell): template matching against MS Gothic failed on this bold 2bpp-antialiased 12 px font (<30% right, even greyscale + bbox-centred); a name-entry charset table (code -> glyph in gojuon order) gave every kana for free, and reading 300 kanji off 16-wide labelled sheets plus word-list checks for look-alikes was faster.
- references/pipeline.md (Extract): bytecode with call/goto/jump-table pointers into the text (F8/F9/FA here) needs units split at every pointer target and the pointers rewritten on repack; jump tables indexed at runtime have no length, so read entries until the lowest target seen (worked for every table in this ROM, checked by an op/arg-conflict coverage pass).
- references/graphics.md (Survey): with no reviewer subagent (Orca worker), `codex exec --sandbox read-only -i sheet.png ...` reviewed 104 sweep sheets in 18 calls (tools/codex_review.sh); it misread ~5% of hex labels and replies lack a final newline (concatenate with `awk 1`).
- references/emulator-qa.md (Debug tool): look for a scene dispatcher in AgbMain's loop first (here `table[u8 id]`, table of 43 pointers); writing the id from Lua warped to every scene and id 0 turned out to be a leftover debug menu (message viewer, episode select). Took ~20 min vs. hours of ramsearch.
- references/emulator-qa.md: ramsearch across runs that all start from the same savestate matches uninitialised/random RAM as "stable per screen"; compare runs from different starts or go to the code.
- scripts/emu.py: rows of a TSV edited with the Edit tool lose a tab if old_string ends in `\t` and new_string does not re-add it; rewrite small TSVs whole and keep a parse test (tests/test_scenes.py).
