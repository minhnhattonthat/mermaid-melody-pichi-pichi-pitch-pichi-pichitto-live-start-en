#!/bin/sh
# codex_review.sh DIR PROMPT CHUNK PAR: read-only codex review of DIR/sheet_*.png in chunks of CHUNK sheets,
# PAR at a time; answers land in DIR/review_NNN.txt (an independent read that keeps images out of the main agent).
dir=$1; prompt=$(cat "$2"); chunk=${3:-6}; par=${4:-4}
cd "$dir" || exit 1
ls sheet_*.png | split -l "$chunk" -d -a 3 - chunk_
for c in chunk_*; do
  n=${c#chunk_}
  [ -s "review_$n.txt" ] && continue
  args=""; names=""
  for f in $(cat "$c"); do args="$args -i $f"; names="$names $f"; done
  ( timeout 1200 codex exec --sandbox read-only --skip-git-repo-check $args -o "review_$n.txt" \
      "$prompt The attached images, in order:$names" > "log_$n.txt" 2>&1 ) &
  while [ "$(jobs -r | wc -l)" -ge "$par" ]; do sleep 5; done
done
wait
rm -f chunk_*
awk 1 review_[0-9]*.txt > review_all.tsv  # awk 1: a reply without a final newline must not merge with the next
echo "done: $(ls review_[0-9]*.txt | wc -l) chunks"
