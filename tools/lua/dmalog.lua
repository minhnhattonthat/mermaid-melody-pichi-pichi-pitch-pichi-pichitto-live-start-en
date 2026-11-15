-- GBA DMA log: every write of a DMA source/dest/count register, frames FROM..TO, with the PC.
--   emu.py X.gba ... --script tools/lua/dmalog.lua [--var FROM=20 --var TO=40]
local from, to = FROM or 0, TO or math.huge
L.on_write(0x040000B0, 0x040000DF, function(addr, value)
  if L.frame < from or L.frame > to then return end
  L.log(string.format("f%d pc=%08X reg=%08X val=%08X", L.frame, L.pc(), addr, value or 0))
end)
