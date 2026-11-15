-- Write RAM at given frames of a run (from a savestate, where warp.lua's writes don't apply).
--   emu.py X.gba --state-in S.mss ... --script tools/lua/poke.lua --var "POKES='0x03003CB5:16@240 0x0300...:1:2@300'"
-- Memory game (minigame_2) sub-state = u8 0x03003CB5 (jump table 0x0803FD9C): 6-8 flips, 14/15 mismatch, 9-13 and
-- 29-33 lose, 16 win (やったね), 20/21/24 later win steps; see docs/re/graphics.md.
local m = emu.memType.gbaMemory
local todo = {}
for item in (POKES or ""):gmatch("%S+") do
  local a, v, n, f = item:match("^([^:]+):([^:@]+):?(%d*)@(%d+)$")
  assert(a, "bad poke " .. item)
  todo[#todo + 1] = { a = tonumber(a), v = tonumber(v), n = tonumber(n ~= "" and n or "1"), f = tonumber(f) }
end
L.on_frame(function(fr)
  for _, p in ipairs(todo) do
    if fr == p.f then
      if p.n == 1 then emu.write(p.a, p.v, m) elseif p.n == 2 then emu.write16(p.a, p.v, m) else emu.write32(p.a, p.v, m) end
      L.log(string.format("POKE %d %08X=%X", fr, p.a, p.v))
    end
  end
end)
