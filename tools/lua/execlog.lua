-- Log registers each time code at PC_LO..PC_HI runs (frames FROM..TO, at most MAX lines): who calls a copy routine.
--   emu.py X.gba ... --script tools/lua/execlog.lua --var PC_LO=0x03000C00 [--var PC_HI=..] [--var FROM=750 --var TO=770]
local lo = assert(PC_LO, "set --var PC_LO=0x...")
local hi, from, to, max = PC_HI or lo, FROM or 0, TO or math.huge, MAX or 200
local n = 0
local function r(s, i) return s["cpu.r" .. i] or -1 end
L.on_exec(lo, hi, function()
  if L.frame < from or L.frame > to or n >= max then return end
  n = n + 1
  local s = emu.getState()
  local t = {}
  for i = 0, 14 do t[#t + 1] = string.format("r%d=%08X", i, r(s, i)) end
  L.log(string.format("f%d EXEC pc=%08X %s", L.frame, L.pc(), table.concat(t, " ")))
end)
