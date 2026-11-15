# Skill gotchas

One line each: the skill reference file it belongs in, then the fact.

- scripts/fetch_emu.py: `gba-bios` 404s; retrobios renamed the file to `bios/Nintendo/Game Boy Advance/GBA_bios.rom` (same SHA-1 300c20df...). Downloaded by hand with curl into `tools/mesen/Firmware/gba_bios.bin`; the BIOS table in fetch_emu.py needs the new path.
- SKILL.md / context-mode: with the context-mode plugin active, plain `cat`/Read of long reference files gets truncated to an index; read them through `ctx_execute` instead.
