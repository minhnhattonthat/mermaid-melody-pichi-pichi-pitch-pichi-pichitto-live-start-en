#!/bin/sh
# codex_vqa.sh [CHUNKDIR] [PAR]: independent read-only visual-QA verdicts by codex, one run per qa_gate chunk file.
#   python -X utf8 $SKILL/scripts/qa_gate.py todo work/qa/manifest.tsv work/qa/verdicts --size 8 --out-dir work/qa/chunks
#   sh tools/codex_vqa.sh work/qa/chunks 4      -> work/qa/verdicts/<chunk>.tsv (id<TAB>ok|issue<TAB>note)
# Sheet ids are paths under work/qa/tour/sheets without .png; the original ROM's sheet is the same id under tour_jp.
cd "$(dirname "$0")/.." || exit 1
dir=${1:-work/qa/chunks}; par=${2:-4}
mkdir -p work/qa/verdicts work/qa/vqa_log
brief=$(cat docs/visual-qa-brief.md)
for c in "$dir"/chunk_*.txt; do
  n=$(basename "$c" .txt)
  [ -s "work/qa/verdicts/$n.tsv" ] && continue
  args=""; list=""
  tab=$(printf '\t')
  while IFS="$tab" read -r id p; do
    p=$(printf '%s' "$p" | tr -d '\r')
    args="$args -i $p"
    list="$list
$id	$p	(original: work/qa/tour_jp/sheets/$id.png)"
  done < "$c"
  ( timeout 1800 codex exec --sandbox read-only --skip-git-repo-check $args -o "work/qa/vqa_log/$n.out" \
"$brief

You cannot write files: instead your FINAL message must be only the verdict lines, one per id below, tab-separated
id<TAB>ok|issue<TAB>note, nothing else. The sheets are attached in this order; you may open the original-ROM sheets
and glossary.md read-only. Sheet ids:$list" > "work/qa/vqa_log/$n.log" 2>&1
    grep -P '^\S+\t(ok|issue)\t' "work/qa/vqa_log/$n.out" > "work/qa/verdicts/$n.tsv" ) &
  while [ "$(jobs -r | wc -l)" -ge "$par" ]; do sleep 5; done
done
wait
cat work/qa/verdicts/chunk_*.tsv | awk -F'\t' '{c[$2]++} END {for (k in c) print k, c[k]}'
