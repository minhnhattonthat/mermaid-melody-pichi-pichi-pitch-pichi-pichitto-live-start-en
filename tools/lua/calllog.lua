-- Log r0-r3 and lr at every entry of the function at CALL (GBA), frames FROM..TO.
--   emu.py X.gba ... --script tools/lua/calllog.lua --var CALL=0x08000D20 [--var FROM=0 --var TO=900]
local from, to = FROM or 0, TO or math.huge
L.on_exec(CALL, CALL, function()
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  local sp, m = s["cpu.r13"], emu.memType.gbaMemory
  L.log(string.format("f%d r0=%08X r1=%08X r2=%08X r3=%08X lr=%08X sp0=%X sp4=%X sp8=%X", L.frame, s["cpu.r0"] or -1,
    s["cpu.r1"] or -1, s["cpu.r2"] or -1, s["cpu.r3"] or -1, s["cpu.r14"] or -1, emu.read32(sp, m), emu.read32(sp + 4, m),
    emu.read32(sp + 8, m)))
end)
