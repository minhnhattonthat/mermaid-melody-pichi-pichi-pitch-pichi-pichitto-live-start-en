-- Log each drawchar call (0x080056CC: r0 = text object, r1 = code) with the object's first 0x40 bytes, to find the
-- string pointer. GBA.  emu.py X.gba ... --script tools/lua/textobj.lua [--var FROM=0 --var TO=900 --var MAX=40]
local from, to, max, n = FROM or 0, TO or math.huge, MAX or 40, 0
L.on_exec(0x080056CC, 0x080056CC, function()
  if L.frame < from or L.frame > to or n >= max then return end
  n = n + 1
  local s = emu.getState()
  local o, b = s["cpu.r0"], {}
  for i = 0, 0x3F, 4 do
    b[#b + 1] = string.format("%08X", emu.read32(o + i, emu.memType.gbaMemory, false))
  end
  L.log(string.format("f%d code=%04X obj=%08X lr=%08X | %s", L.frame, s["cpu.r1"], o, s["cpu.r14"], table.concat(b, " ")))
end)
