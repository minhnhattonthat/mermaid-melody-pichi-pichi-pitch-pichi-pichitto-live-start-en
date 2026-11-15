-- Log the text blitter's calls, tile allocations and tile-usage writes (docs/re/vwf.md), frames FROM..TO.
--   emu.py X.gba ... --script tools/lua/tilelog.lua [--var FROM=1700 --var TO=1900]
local from, to = FROM or 0, TO or math.huge
local function on() return L.frame >= from and L.frame <= to end
local function r(s, n) return s["cpu.r" .. n] or -1 end
L.on_exec(0x08004E68, 0x08004E68, function()
  if not on() then return end
  local s = emu.getState()
  L.log(string.format("f%d BLIT code=%X x=%d row=%d", L.frame, r(s, 0), (-r(s, 1)) & 0xFFFFFFFF, r(s, 2)))
end)
L.on_exec(0x08004A00, 0x08004A00, function()
  if not on() then return end
  local s = emu.getState()
  L.log(string.format("f%d ALLOC n=%d owner=%d lr=%08X", L.frame, r(s, 0), r(s, 1), r(s, 14)))
end)
L.on_exec(0x08004A6A, 0x08004A6A, function()
  if not on() then return end
  L.log(string.format("f%d  -> t=%X", L.frame, r(emu.getState(), 2)))
end)
L.on_exec(0x080047A0, 0x080047A0, function()
  if not on() then return end
  local s = emu.getState()
  L.log(string.format("f%d CLEAR map=%08X col=%d row=%d w=%d h=%d lr=%08X", L.frame, r(s, 0), r(s, 1), r(s, 2), r(s, 3),
    emu.read32(r(s, 13), emu.memType.gbaMemory), r(s, 14)))
end)
L.on_write(0x03002A42, 0x03002C02, function(addr, value)
  if not on() or value ~= 0 then return end
  L.log(string.format("f%d FREE t=%X pc=%08X", L.frame, addr - 0x03002A42, L.pc()))
end)
