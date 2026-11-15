-- Log each call of show_message (0x080046E4: r0 = text slot, r1 = message id) with its caller.
-- Lines: "SHOW <frame> slot=<n> id=<id> lr=<addr>".
L.on_exec(0x080046E4, 0x080046E4, function()
  local s = emu.getState()
  L.log(string.format("SHOW %d slot=%d id=%d lr=%08X", L.frame, s["cpu.r0"], s["cpu.r1"], s["cpu.r14"]))
end)
