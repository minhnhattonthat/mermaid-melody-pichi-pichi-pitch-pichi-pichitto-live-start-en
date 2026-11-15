-- Turn mosaic off: locked episodes in the episode grid show their title art mosaicked.
-- The VBlank copy at 0x08000B6C loads the register value from the shadow u16 at 0x030000B0 and stores it at
-- 0x0400004C (0x08000B6E); zero the shadow just before that load (writing the register itself gets overwritten).
-- Usage: emu.py ROM ... --script tools/lua/nomosaic.lua   (QA shots of episode titles)
local M = emu.memType.gbaMemory
L.on_exec(0x08000B6C, 0x08000B6C, function()
  emu.write(0x030000B0, 0, M)
  emu.write(0x030000B1, 0, M)
end)
