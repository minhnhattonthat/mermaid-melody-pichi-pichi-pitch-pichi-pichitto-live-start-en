-- Warp to a scene from a cold boot. Scene list: tools/debug/scenes.tsv (name, id, expect, writes, route, note).
--   emu.py ROM --sav work/saves/default.sav --script tools/debug/warp.lua --var "SCENE='menu'" --frames 1200
--   --var SCENE_ID=15      raw scene id instead of a name (scene table ROM 0x09D37060, 43 entries); optional
--                          --var "WRITES='...'" --var "ROUTE_AFTER=[[...]]" as in the tsv
--   --var EP=3 / MSG=1028 / GAME=1   values for rows whose writes use $EP, $MSG, $GAME
-- How: the main loop (0x0800E1C0) runs scene[u8 0x0300287C] each frame; writing the u16 id (flags byte +1 = 0)
-- makes the next frame init that scene. +4 = stack depth, +5.. = return stack (B/back pops it).
-- The warp waits for scene 9 (opening, ~frame 731: the save is loaded at boot, before the main loop), pushes
-- title and menu on the return stack as the real menu does, applies the row's writes, switches, then plays the
-- row's route. "ARRIVED <frame> <id>" is logged once the expected scene id (column expect, default id) has held
-- for 30 frames after the route ended; the run fails (exit 2) if that never happens within 1500 frames.
local A = 0x0300287C
local M = emu.memType.gbaMemory
local function rd(a) return emu.read(a, M) end
local function wr8(a, v) emu.write(a, v & 0xFF, M) end
local function wr16(a, v) wr8(a, v); wr8(a + 1, v >> 8) end
local function wr32(a, v) wr16(a, v & 0xFFFF); wr16(a + 2, v >> 16) end
local function wr(a, v, n) if n == 4 then wr32(a, v) elseif n == 2 then wr16(a, v) else wr8(a, v) end end

local function load_scenes(path)
  local t = {}
  for line in io.lines(path) do
    if line ~= "" and not line:match("^#") and not line:match("^name\t") then
      local f = {}
      for c in (line .. "\t"):gmatch("([^\t]*)\t") do f[#f + 1] = c end
      t[f[1]] = { id = tonumber(f[2]), expect = tonumber(f[3]), writes = f[4] or "", route = f[5] or "" }
    end
  end
  return t
end

local sc
if SCENE_ID then
  sc = { id = SCENE_ID, writes = WRITES or "", route = ROUTE_AFTER or "" }
else
  local all = load_scenes(SCENES_TSV or "../debug/scenes.tsv")  -- Mesen runs in tools/mesen
  sc = all[SCENE] or error("unknown SCENE " .. tostring(SCENE))
end
sc.expect = sc.expect or sc.id

-- writes: "addr:val[:size][@delay]" separated by spaces ("-" = none); size 1 (default), 2 or 4; hex with 0x.
-- @delay applies it that many frames after the warp (for screens that reset the value on init).
-- "!0xPC" instead of @delay writes it each time code at PC runs (a choice the game reads right there: room hotspot).
-- "$NAME" is replaced by the global NAME (--var MSG=1028), so one row serves many ids.
local later = {}
local function apply(ws, now)
  ws = ws:gsub("%$(%u+)", function(k) return tostring(_G[k] or error("scene needs --var " .. k)) end)
  for item in ws:gmatch("%S+") do
    if item ~= "-" then
      local a, v, n, d, pc = item:match("^([^:]+):([^:@!]+):?(%d*)@?(%d*)!?(%w*)$")
      if not a then error("bad write " .. item) end
      a, v, n, d = tonumber(a), tonumber(v), tonumber(n ~= "" and n or "1"), tonumber(d ~= "" and d or "0")
      if pc ~= "" then
        pc = tonumber(pc)
        L.on_exec(pc, pc, function() wr(a, v, n) end)
      elseif d > 0 then later[#later + 1] = { at = now + d, a = a, v = v, n = n } else wr(a, v, n) end
    end
  end
end

local warped, arrived, holdFrom = nil, false, nil
L.on_frame(function(f)
  for i = #later, 1, -1 do
    local w = later[i]
    if f >= w.at then wr(w.a, w.v, w.n); table.remove(later, i) end
  end
  local cur = rd(A)
  if not warped then
    if cur == 9 or cur == 2 then  -- scene 0 is the logo pre-loop (to ~frame 731): it overwrites the id
      warped = f
      wr8(A + 4, 2); wr8(A + 5, 2); wr8(A + 6, 8)  -- return stack: title, menu
      if sc.id == 8 then wr8(A + 4, 1) end
      apply(sc.writes, f)
      wr16(A, sc.id)
      L.log(string.format("WARP %d %d", f, sc.id))
      for step in sc.route:gmatch("[^;]+") do
        local n, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
        if n then L.press(spec, tonumber(n)) end
      end
    end
    return
  end
  if arrived or not L.route_done() then return end
  if cur == sc.expect then
    holdFrom = holdFrom or f
    if f - holdFrom >= 30 then arrived = true; L.log(string.format("ARRIVED %d %d", f, cur)) end
  else holdFrom = nil end
  if not arrived and f - warped > (ARRIVE_LIMIT or 1500) then
    L.fail("scene " .. sc.expect .. " never held (now " .. cur .. ")")
  end
end)
