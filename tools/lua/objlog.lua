-- Log a text object's flags/spacing/colour at drawchar entry (0x080056CC), first call per (obj, flags) pair.
--   emu.py X.gba ... --script tools/lua/objlog.lua [--var FROM=0 --var TO=900]
local from, to, seen = FROM or 0, TO or math.huge, {}
L.on_exec(0x080056CC, 0x080056CC, function()
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  local o, m = s["cpu.r0"], emu.memType.gbaMemory
  local fl = emu.read32(o + 0x10, m)
  local key = string.format("%X/%X/%X/%X/%X/%X", o, fl, emu.read(o + 0x2C, m), emu.read(o + 0x30, m),
    emu.read(o + 0x2E, m), emu.read(o + 0x21, m))
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("f%d obj=%08X code=%X flags=%08X sp=%d col=%d x=%d row=%d W=%d map=%d owner=%d lr=%08X", L.frame,
    o, s["cpu.r1"], fl, emu.read(o + 0x2C, m), emu.read(o + 0x2D, m), emu.read(o + 0x20, m), emu.read(o + 0x21, m),
    emu.read(o + 0x22, m), emu.read(o + 0x30, m), emu.read(o + 0x2E, m), s["cpu.r14"]))
end)
