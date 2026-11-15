# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress. Last build: none.
- **Done:**
  - Step 0 (2026-11-15): template, rom.sha1, MesenCE 2.2.1 + GBA BIOS in tools/mesen, guard hook proven, pre-commit (tools/check.py) rejects a failing test, original ROM smoke-boots, scripted input and Lua probe ok.
  - Phase 1 so far: no prior English patch found; no SJIS text in ROM; Konami-style graphics compression decoded (`tools/kcomp.py`, verified byte-exact vs VRAM, test in tests/test_kcomp.py); 5-byte resource tables found (`tools/restables.py`); main menu text is compressed graphics; boot route to main menu (`tools/routes/boot.txt`, state work/states/menu.mss). Notes: docs/re/compression.md, docs/re/screens.md. Probes: tools/lua/dmalog.lua, tools/lua/calllog.lua.
- **Next (phase 1):**
  1. Static sweep: decode every pointer in work/restables.tsv (re-run `tools/restables.py work/orig.gba`; work/orig.gba = copy of the rom) up to the next pointer, render gba4 + gba8 sheets with `tiles.py render`, list Japanese cells (read-only pass), print skipped regions.
  2. Find any font-drawn text: name-entry name display, results, save/option messages. Watch VRAM writes on the name-entry screen to find the font and its code table -> tbl/jp.tbl if a font exists.
  3. Tour the unvisited modes (docs/re/screens.md list) and write docs/re/graphics.md (every tile-drawn Japanese element with screen, layer, source block).
  4. Trap-test the free-space candidate 0x1FDF760-0x1FFFFFF.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) GUI keyboard input in tools/mesen not checked by hand; emu.py wrote default key mappings.
