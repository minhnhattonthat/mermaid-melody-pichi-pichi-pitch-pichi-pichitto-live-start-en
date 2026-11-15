# Compression and resource tables

## Header and map
- Game code `B3MJ`, maker `A4` (Konami), title `PICHIPICHI02`. 32 MiB ROM; data ends at 0x1FDF760, rest is 0x00 padding (candidate free space 0x1FDF760-0x1FFFFFF, ~133 KB, not yet trap-tested). **verified** (byte scan).
- Save: `SRAM_V112` string at 0x4D24C -> SRAM. **verified** (string present).
- No Shift-JIS text anywhere (scan of every 2-byte SJIS run found only noise). **verified** (`work/` scan, 2026-11-15).
- Pointers use both mirrors: 0x08xxxxxx for the first 16 MiB, 0x09xxxxxx (= file offset + 0x08000000) for the second.

## Graphics compression (Konami-style LZ, `tools/kcomp.py`)
- Decoder: ARM code at ROM 0x08009328 (368 bytes), DMA'd to IWRAM 0x03000BA4 and called through `bx ip` veneer 0x080094C8, from Thumb wrapper `decompress(dst=r0, src=r1, size=r2, r3)` at 0x08000D20. r1 = 0 means "fill with zero". **verified** (calllog.lua on 0x08000D20 at the main menu).
- Stream: flags byte, then ops (see `tools/kcomp.py` docstring). Flags bit 0 = per-64-byte-block byte swap with the 62-byte table at IWRAM 0x03000B25 + (flags>>1); that IWRAM table equals ROM 0x1D36E21..+127. **verified**: blocks 0x1712CF7..0x1716023 (main-menu Lucia portrait, size 0x800 each) decode byte-identical to VRAM 0x4800..0x8FFF in `work/qa/ram2/ppu_000070.vram.bin`, and each stream ends exactly at the next block's start.
- Caller 0x08000EA0 decodes 0x800-byte chunks into IWRAM 0x03006900 then DMAs them into place with a row stride (layout args r2/r3). Not every decoded chunk appears verbatim in VRAM for that reason.
- BIOS LZ77 (swi 0x11/0x12): only 1 valid block in the whole ROM (0x7xxxxx); the game does not use it for its art. **verified** (full scan).

## Resource tables
- Records of 5 bytes: u32 pointer (byte-aligned stream), u8 attribute. Reader helpers: 0x08000E6C (pointer of record i) and 0x08000E94 (byte of record i). **verified** (disassembly).
- Main-menu table at 0x16F6CC8, 197 records, referenced by a literal at 0xE7F0. **verified** (contains the portrait pointers above).
- `tools/restables.py ROM` scans for runs of >= 6 valid records: 145 runs, 1973 distinct pointers (`work/restables.tsv`). Only 12 runs have a direct code literal (**verified** as tables): 16F6CC8 (197, menus, ~50 refs), 18AB9FC (41), 18C07DC (160), 1A280F8 (45), 1A97238 (35), 1ADA120 (170), 1B6AF58 (18), 1B77B2C (19), 1B7D52E (170), 1B9A7F8 (193, ~45 refs, likely gameplay), 1EFF434 (65, ~20 refs), 1F56AB0 (6). The other 133 runs are **guess** (nested tables or false positives).
- Block sizes are not stored in the stream (the caller passes them). For a static sweep, decode each pointer until the stream reaches the next pointer in sorted order (blocks are packed back to back).

## Text drawing
- Main menu: items and the bottom caption are pre-drawn graphics (caption = 4 OBJ 64x32 sprites, tiles 896-927, DMA'd from EWRAM 0x02003000 after decoding). **verified** (watch.lua + dmalog.lua).
- Name entry (first boot, no save): kana keyboard as graphics; the entered name is drawn somewhere from a kana font: encoding not yet found.
