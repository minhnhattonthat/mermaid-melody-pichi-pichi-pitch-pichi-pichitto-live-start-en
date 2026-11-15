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
| screens.md | screens seen so far, routes and savestates | partial |
