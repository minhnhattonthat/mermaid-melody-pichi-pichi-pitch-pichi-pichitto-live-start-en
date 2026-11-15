-- Log every kcomp decode call (Thumb 0x08000D20: r0 dst, r1 src, r2 size), frames FROM..TO: finds the ROM stream
-- behind any VRAM tile (OBJ tile T is at 0x06010000 + 32 * T).
--   emu.py X.gba ... --script tools/lua/kcomplog.lua [--var FROM=600 --var TO=900]
local from, to = FROM or 0, TO or math.huge
local function r(s, n) return s["cpu.r" .. n] or -1 end
L.on_exec(0x08000D20, 0x08000D20, function()
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  L.log(string.format("f%d KCOMP dst=%08X src=%08X size=%X lr=%08X", L.frame, r(s, 0), r(s, 1), r(s, 2), r(s, 14)))
end)
