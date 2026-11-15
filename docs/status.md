# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress. Last build: none (Step 0 done 2026-11-15).
- **Done:** Step 0: template, rom.sha1, MesenCE 2.2.1 + GBA BIOS in tools/mesen, guard hook proven, pre-commit (tools/check.py) proven to reject a failing test, original ROM smoke-boots (route tools/routes/boot.txt), Start skips intro (scripted input ok), Lua probe log ok.
- **Next:** Phase 1 recon: encoding, pointer tables, compression, text ranges, free space, graphics-text survey -> docs/re/.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in tools/mesen not checked by hand (emu.py wrote default key mappings).
