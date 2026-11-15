-- Which drawchar path a glyph takes in the English build: VWF English path (0x09FDF82A), original path
-- (0x09FDF81E), the 8 px font blitter call (0x080058A8). One line per call, frames FROM..TO.
--   emu.py X.gba ... --script tools/lua/pathlog.lua [--var FROM=0 --var TO=900]
local from, to = FROM or 0, TO or math.huge
local function hook(pc, name)
  L.on_exec(pc, pc, function()
    if L.frame < from or L.frame > to then return end
    local s, m = emu.getState(), emu.memType.gbaMemory
    local o = s["cpu.r0"]
    L.log(string.format("f%d %s r0=%08X r1=%X flags=%08X sp=%d map=%d owner=%d", L.frame, name, o, s["cpu.r1"],
      emu.read32(o + 0x10, m), emu.read(o + 0x2C, m), emu.read(o + 0x30, m), emu.read(o + 0x2E, m)))
  end)
end
hook(0x09FDF82A, "english")
hook(0x09FDF81E, "orig")
hook(0x080058A8, "font8")
