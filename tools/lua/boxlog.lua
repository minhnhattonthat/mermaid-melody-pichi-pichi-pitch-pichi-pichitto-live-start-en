-- Log the geometry of every text object that draws a glyph (docs/re/vwf.md), once per distinct box:
--   BOX msg=<id> col/row=<+0x20/+0x21> W=<+0x22 width, cells> H=<+0x23 height, tile rows> step=<+0x2A line step>
--       sp=<+0x2C spacing> fl=<+0x10 flags> c=<+0x2D colour> own=<+0x2E tile owner>
--   emu.py X.gba ... --script tools/lua/boxlog.lua
local seen = {}
local function rd8(a) return emu.read(a, emu.memType.gbaMemory) end
L.on_exec(0x080056CC, 0x080056CC, function()
  local o = emu.getState()["cpu.r0"]
  local id = emu.read16(o + 0x18, emu.memType.gbaMemory)
  local key = string.format("msg=%d col=%d row=%d W=%d H=%d step=%d sp=%d fl=%X c=%X own=%d", id, rd8(o + 0x20),
    rd8(o + 0x21), rd8(o + 0x22), rd8(o + 0x23), rd8(o + 0x2A), rd8(o + 0x2C),
    emu.read32(o + 0x10, emu.memType.gbaMemory) & 0xFFFFFFFB, rd8(o + 0x2D), rd8(o + 0x2E))
  if not seen[key] then
    seen[key] = true
    L.log(string.format("f%d BOX %s", L.frame, key))
  end
end)
