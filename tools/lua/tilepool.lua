-- Text tile pool use (allocator 0x08004A00: usage byte per tile at 0x03002A42 + t, 0 = free; pool 0..0x1C0) every
-- EVERY frames (default 60): "POOL <frame> used=<n> cursor=<[0x03002A38]>".
--   emu.py X.gba ... --script tools/lua/tilepool.lua [--var EVERY=10]
local every = EVERY or 60
L.on_frame(function(f)
  if f % every ~= 0 then return end
  local m, n = emu.memType.gbaMemory, 0
  for t = 0, 0x1BF do
    if emu.read(0x03002A42 + t, m) ~= 0 then n = n + 1 end
  end
  L.log(string.format("POOL %d used=%d cursor=%X", f, n, emu.read32(0x03002A38, m)))
end)
