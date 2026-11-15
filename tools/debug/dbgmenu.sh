#!/bin/sh
# Open each leftover debug-menu item (scene 0) from a cold boot: tools/debug/dbgmenu.sh OUTDIR COL,ROW...
# Menu is 3 columns x 8 rows (docs/re/scenes.md); each run presses right*COL, down*ROW, A, then waits.
cd "$(dirname "$0")/../.." || exit 1
S="$(python tools/skill.py)"
ROM="${ROM:-rom/Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba}"
SAV="${SAV:-work/saves/default.sav}"
out="$1"; shift
for cr in "$@"; do
  c=${cr%,*}; r=${cr#*,}; route="60 -"
  i=0; while [ $i -lt "$c" ]; do route="$route;6 right;20 -"; i=$((i+1)); done
  i=0; while [ $i -lt "$r" ]; do route="$route;6 down;20 -"; i=$((i+1)); done
  route="$route;6 a;${WAIT:-300} -${EXTRA:+;$EXTRA}"
  echo "$c$r|$route"
done | xargs -P "${JOBS:-6}" -I{} sh -c 'n="${1%%|*}"; r="${1#*|}"; python -X utf8 "$2/scripts/emu.py" "$3" --sav "$4" --out "$5/d$n" --script tools/debug/warp.lua --script tools/lua/scenelog.lua --var SCENE_ID=0 --var "ROUTE_AFTER=[[$r]]" --frames "${FRAMES:-1500}" --shot-every "${EVERY:-60}" --sheet --timeout 300 > /dev/null 2>&1' _ {} "$S" "$ROM" "$SAV" "$out"
