#!/usr/bin/env bash
# Usage: tests/run_tests.sh [--evals]
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
step() { printf '\n== %s\n' "$1"; }

step "static validation"
python3 tests/validate.py || fail=1

step "script self-tests"
for s in humanize_score post_stats; do
  python3 "skills/creator/scripts/$s.py" --selftest >/dev/null && echo "  $s: ok" || { echo "  $s: FAIL"; fail=1; }
done

step "analytics on fixture"
python3 skills/creator/scripts/post_stats.py tests/fixtures/sample_posts.csv --followers 12000 --json \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d; print("  post_stats json: ok")' || fail=1

step "humanizer separates AI vs human fixtures"
ai=$(python3 skills/creator/scripts/humanize_score.py tests/fixtures/ai_text.md --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["score"])')
hu=$(python3 skills/creator/scripts/humanize_score.py tests/fixtures/human_text.md --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["score"])')
echo "  ai=$ai human=$hu"
python3 -c "import sys; sys.exit(0 if $hu - $ai >= 20 else 1)" || { echo "  FAIL: gap < 20"; fail=1; }

step "live trend sources (network; soft)"
for cmd in "google --limit 3" "wiki --limit 3" "hn --limit 3" "news --q fitness --limit 3" "suggest --q fitness" "reddit --sub fitness --limit 3"; do
  n=$(python3 skills/creator/scripts/trends.py $cmd 2>/dev/null | python3 -c 'import json,sys;r=json.load(sys.stdin)["results"][0];print(len(r.get("items",[])) if "items" in r else "ERR "+r["error"][:60])')
  printf '  %-28s %s\n' "$cmd" "$n"
done

if [[ "${1:-}" == "--evals" ]]; then
  step "skill evals (claude plugin eval)"
  CLAUDE_BIN="${CLAUDE_BIN:-claude}"
  "$CLAUDE_BIN" plugin validate . || fail=1
  "$CLAUDE_BIN" plugin eval . --trust-plugin --runs 1 --ablation none --threshold 0.6 \
    --allow-tools Bash WebFetch Write -j 4 --no-publish || fail=1
fi

step "result"
[[ $fail == 0 ]] && echo "ALL PASS" || echo "FAILURES ABOVE"
exit $fail
