#!/usr/bin/env bash
# End-to-end SMOKE test: 10 items × 1 model × 3 conditions.
# Outputs are pipeline checks, NOT findings.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PATH="/workspace/tools/ollama/bin:${PATH:-}"
export OLLAMA_MODELS="${OLLAMA_MODELS:-/workspace/tools/ollama/models}"
export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"

MODEL="${1:-qwen2.5:1.5b}"
OUT="$ROOT/fliprate/results/smoke"

if ! curl -sf "http://${OLLAMA_HOST#http://}/api/version" >/dev/null 2>&1; then
  echo "Starting local Ollama..."
  nohup /workspace/tools/ollama/bin/ollama serve > /tmp/ollama-serve.log 2>&1 &
  sleep 2
fi

python3 -m unittest discover -s fliprate/tests -v
python3 fliprate/scripts/run_eval.py \
  --dataset fliprate/data/items.jsonl \
  --model "$MODEL" \
  --n 10 \
  --conditions pressure,control,evidence \
  --seed 42 \
  --temperature 0 \
  --label smoke \
  --out "$OUT"
python3 fliprate/scripts/compute_metrics.py "$OUT/trajectories.jsonl" --out "$OUT/metrics.json"
python3 fliprate/scripts/plot_results.py "$OUT/metrics.json" --out "$OUT/figures" --label smoke
echo "SMOKE complete. See $OUT (not findings)."
