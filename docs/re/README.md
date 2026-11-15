# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| compression.md | header, free-space candidate, graphics compression (`tools/kcomp.py`), 5-byte resource tables (`tools/restables.py`), how menu text is drawn | decoder verified; table list partly guessed |
| screens.md | screens seen so far, routes and savestates | partial; superseded by scenes.md |
| scenes.md | scene dispatcher (0x0300287C, table 0x09D37060), all 43 scene ids, leftover debug menu, story episodes, debug tool | dispatcher and warps verified |
| text.md | message table + strings (24-bit offsets), 12x12 frequency-ordered font, drawchar, name-entry buffer and charset | table/strings/font verified; control codes guessed |
| vwf.md | English font (`fonts/en12.txt`), VWF patch (`tools/vwf.py`), blitter/tile allocator/auto-wrap facts, box widths (width gate) | VWF verified in game (msgview, story); box budgets measured |
| graphics.md + graphics_sweep.tsv | graphics-text survey: static sweep of every kcomp block (170 text blocks) + tour list | survey done; exact words read at redraw |
