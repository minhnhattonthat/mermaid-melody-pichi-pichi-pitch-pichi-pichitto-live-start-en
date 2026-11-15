# Skill gotchas

One line each: the skill reference file it belongs in, then the fact.

- scripts/fetch_emu.py: `gba-bios` 404s; retrobios renamed the file to `bios/Nintendo/Game Boy Advance/GBA_bios.rom` (same SHA-1 300c20df...). Downloaded by hand with curl into `tools/mesen/Firmware/gba_bios.bin`; the BIOS table in fetch_emu.py needs the new path.
- SKILL.md / context-mode: with the context-mode plugin active, plain `cat`/Read of long reference files gets truncated to an index; read them through `ctx_execute` instead.
- references/emulator-qa.md: Mesen (portable) keeps a GBA battery save in `tools/mesen/Saves/<rom>.sav` across emu.py runs without `--sav`, so first-boot screens (name entry) appear once and never again; pass `--sav` with a blank file (32 KiB of FF) to reach them.
- references/emulator-qa.md: watch.lua logs one line per PC, so a loop or DMA writing a whole glyph shows only its first write (often 0); diff two ppu dumps to see what really changed.
- references/emulator-qa.md: GBA `.io.bin` BG scroll registers are write-only; the dump read back 48,48 for every BG while the real scroll was 0. Do not compute map positions from them.
- references/graphics.md (Survey): with no reviewer subagent (Orca worker), `codex exec --sandbox read-only -i sheet.png ...` reviewed 104 sweep sheets in 18 calls (tools/codex_review.sh); it misread ~5% of hex labels and replies lack a final newline (concatenate with `awk 1`).
