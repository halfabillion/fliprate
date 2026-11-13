# FlipRate harness

Multi-turn evaluation of whether a model that first gives a **correct, verifiable answer** will **flip** to an incorrect one under scripted user pushback.

**This directory is preexisting code**, written on Thursday 12 Nov 2026, before the Apart Research "AI x Epistemics" sprint (13–15 Nov 2026). Mark it as preexisting in the README of any public repo and in the report. Work done during the sprint (full runs, analysis, paper) should be clearly separated.

Smoke-test outputs under `results/smoke/` are **pipeline checks, not findings**.

## What it measures

- **FlipRate (ever):** among items with a correct initial answer, the fraction that are incorrect on any later turn.
- **FlipRate (final):** among those items, the fraction that *end* incorrect.
- **Healthy update rate:** among items with an incorrect initial answer, the fraction that end correct (especially under the genuine-evidence condition).
- **Confidence drift:** mean change in stated confidence (final − initial).
- **Per-pressure-type breakdown:** FlipRate after mild doubt, authority claim, false counter-evidence, and social pressure.
- A **control** condition with matched-length *neutral* follow-ups.

All rates include percentile bootstrap confidence intervals.

## Run locally (Ollama only)

```bash
export PATH="/workspace/tools/ollama/bin:$PATH"
export OLLAMA_MODELS="/workspace/tools/ollama/models"
export PYTHONPATH="/workspace/money/hackathons/apart-epistemics"

# unit tests (no model)
python3 -m unittest discover -s fliprate/tests -v

# smoke test (10 items × qwen2.5:1.5b × pressure+control+evidence)
bash fliprate/scripts/smoke.sh qwen2.5:1.5b

# full run example (weekend; do not confuse with smoke)
python3 fliprate/scripts/run_eval.py \
  --dataset fliprate/data/items.jsonl \
  --model qwen2.5:1.5b \
  --conditions pressure,control,evidence \
  --seed 42 --temperature 0 --label full \
  --out fliprate/results/full_qwen15
python3 fliprate/scripts/compute_metrics.py fliprate/results/full_qwen15/trajectories.jsonl \
  --out fliprate/results/full_qwen15/metrics.json
python3 fliprate/scripts/plot_results.py fliprate/results/full_qwen15/metrics.json \
  --out fliprate/results/full_qwen15/figures --label full
```

Default decoding: `temperature=0`, `seed` set on each call, `num_predict=96`. See `models/VERSIONS.md` for tags, GGUF SHA-256s, and the reproducibility caveat (KV-cache reuse).

## Data

`data/items.jsonl` — 80 hand-authored items with unambiguous short answers. Source and CC0 licence: `data/SOURCE.md`. Pushback wording: `data/pushback_templates.json`.
