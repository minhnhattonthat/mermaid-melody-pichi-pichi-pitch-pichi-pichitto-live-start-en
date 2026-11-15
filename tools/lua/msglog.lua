-- Log each message the text engine starts (0x08007454 setup; id = u16 at text object +0x18, table ROM 0x09860CE0).
-- Lines: "MSG <frame> <id> obj=<addr>" and "TEXT <hex id>" (textcover.py format, ids in build/strings.tsv).
L.on_exec(0x08007488, 0x08007488, function()
  local s = emu.getState()
  local o = s["cpu.r5"]
  local id = emu.read16(o + 0x18, emu.memType.gbaMemory, false)
  L.log(string.format("MSG %d %d obj=%08X lr=%08X", L.frame, id, o, s["cpu.r14"]))
  L.log(string.format("TEXT %X", id))
end)
