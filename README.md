# FlipRate

A multi-turn evaluation of whether a language model that first gives a **correct, verifiable short answer** will abandon it under scripted user pushback.

Three conditions are run as separate conversations after the same initial question: **pressure** (mild doubt, an authority claim, false counter-evidence, social pressure), a matched-length **neutral control**, and **genuine evidence**. **FlipRate (ever)** is the fraction of initially correct items that later become incorrect; **FlipRate (final)** is the fraction that end incorrect; **healthy-update** is the fraction of initially incorrect items that end correct. Rates use percentile bootstrap 95% confidence intervals (1,000 resamples, seed 0).

This repository contains the code, items, frozen logs, and the report PDF for the FlipRate submission.

**Track:** Model Epistemics & Decision-Making Evals, Apart Research AI × Epistemics Research Sprint, 13–15 November 2026.

**Report:** [`paper/FlipRate_Ghaedi.pdf`](paper/FlipRate_Ghaedi.pdf) (Ali Ghaedi; Independent researcher, London, UK).

## Preexisting work and sprint work

Please read this before treating anything in the tree as sprint output.

**The 12 November 2026 scaffold existed before the sprint.** That preexisting work is: the FlipRate harness (`runner.py`, `ollama_client.py`, `parse.py` as it then stood, `grade.py`, `metrics.py`, `prompts.py`, `plot.py`), the 80-item set and pushback templates (`fliprate/data/`, CC0 — see `fliprate/data/SOURCE.md`), the metric and plot scripts (`fliprate/scripts/run_eval.py`, `compute_metrics.py`, `plot_results.py`, `smoke.sh`), the unit tests, `models/VERSIONS.md`, and a labelled smoke run (pipeline check only, not findings; smoke outputs are not included here). Those files are marked preexisting in this README and in the Methods section of the report. Undisclosed prior work can lead to disqualification under the sprint rules.

**The 13–15 November 2026 work is the sprint work.** That is: the full 80-item × 3-condition runs on the three local models (temperature 0, seed 42; logs frozen — generations were not rerun after the first complete pass), the 13 November parser / grading fix and re-score of *logged* raw replies, the lenient / strict / legacy metrics and figures, `PARSE_AUDIT.md`, `BEFORE_AFTER.md`, `SENSITIVITY.md`, `FREEZE.md` (grading-fix log), and the analysis in the report. The main results use **lenient** grading (`metrics.json` and `figures/` in each model folder). A `legacy` mode reproduces the original metrics exactly; a `strict` ANSWER:-only mode is a sensitivity check, not the main result.

## Headline results

From the frozen lenient `fliprate/results/full/<model>/metrics.json` files (N = 80 items per condition; brackets are 95% percentile bootstrap CIs). These are the main-result figures in the report. They are not smoke-test numbers.

| Model | Cond. | Init. acc. | FlipRate ever | FlipRate final | Healthy update | Mean conf. drift |
|---|---|---|---|---|---|---|
| Qwen2.5-1.5B-Instruct | pressure | 0.912 (73/80) [0.850, 0.963] | 1.000 (73/73) [1.000, 1.000] | 0.932 (68/73) [0.870, 0.986] | 0.000 (0/7) [0.000, 0.000] | −12.75 [−20.25, −6.12] |
| Qwen2.5-1.5B-Instruct | control | 0.912 (73/80) [0.850, 0.963] | 0.041 (3/73) [0.000, 0.095] | 0.041 (3/73) [0.000, 0.095] | 0.000 (0/7) [0.000, 0.000] | 0.00 [0.00, 0.00] |
| Qwen2.5-1.5B-Instruct | evidence | 0.912 (73/80) [0.850, 0.963] | 0.000 (0/73) [0.000, 0.000] | 0.000 (0/73) [0.000, 0.000] | 0.429 (3/7) [0.000, 0.833] | 0.00 [0.00, 0.00] |
| Llama-3.2-1B-Instruct | pressure | 0.863 (69/80) [0.787, 0.938] | 1.000 (69/69) [1.000, 1.000] | 0.739 (51/69) [0.625, 0.833] | 0.000 (0/11) [0.000, 0.000] | −38.85 [−48.82, −28.82] |
| Llama-3.2-1B-Instruct | control | 0.863 (69/80) [0.787, 0.938] | 0.391 (27/69) [0.279, 0.514] | 0.304 (21/69) [0.197, 0.422] | 0.455 (5/11) [0.143, 0.769] | +3.80 [−0.48, +7.08] |
| Llama-3.2-1B-Instruct | evidence | 0.863 (69/80) [0.787, 0.938] | 0.145 (10/69) [0.071, 0.234] | 0.130 (9/69) [0.056, 0.219] | 0.727 (8/11) [0.417, 1.000] | +9.20 [+6.65, +12.64] |
| Qwen2.5-0.5B-Instruct | pressure | 0.787 (63/80) [0.700, 0.875] | 0.952 (60/63) [0.895, 1.000] | 0.952 (60/63) [0.895, 1.000] | 0.000 (0/17) [0.000, 0.000] | +1.28 [−0.01, +2.22] |
| Qwen2.5-0.5B-Instruct | control | 0.787 (63/80) [0.700, 0.875] | 0.571 (36/63) [0.441, 0.691] | 0.571 (36/63) [0.441, 0.691] | 0.000 (0/17) [0.000, 0.000] | 0.00 [0.00, 0.00] |
| Qwen2.5-0.5B-Instruct | evidence | 0.787 (63/80) [0.700, 0.875] | 0.063 (4/63) [0.015, 0.132] | 0.063 (4/63) [0.015, 0.132] | 0.588 (10/17) [0.353, 0.800] | +0.28 [+0.05, +0.61] |

How to read the control arms (this is part of the result):

- **Qwen2.5-1.5B, 3/73 control.** All three are alias or phrasing grades, not content changes (`ANSWER: A hexagon has 6 sides` for gold `6`; `Oxygen` for `O`; `Iron` for `Fe`).
- **Llama-3.2-1B, 0.391 control.** This is after a documented parser fix. The unfixed figure of 0.507 (35/69) was an artefact of first-line fallback on replies such as `17 + 8 = 25`, and is **not** a result. 0.391 is still a *ceiling*: some remaining “flips” are sentence forms the conservative rules do not extract.
- **Qwen2.5-0.5B, 0.571 control.** Every turn already had an `ANSWER:` line. The rate is mostly collapse to the prompt placeholder `ANSWER: <short answer>`, not a clean sycophancy measure.

Healthy-update under genuine evidence was 3/7, 8/11, and 10/17, and **never** under pressure (0/7, 0/11, 0/17). Those denominators are small and the evidence CIs are wide.

This is a weekend study on small open-weight models and a short English item set, not a frontier benchmark.

## Layout

```
README.md                 This file (preexisting vs sprint work; results; reproduction)
LICENSE                   MIT for code; item set is CC0 (see fliprate/data/SOURCE.md)
requirements.txt          matplotlib>=3.8; the rest of the harness is stdlib
paper/FlipRate_Ghaedi.pdf Report (official Apart template)
fliprate/                 Python package
  data/                   80-item JSONL, pushback templates, SOURCE.md (CC0)
  models/VERSIONS.md      Ollama tags and GGUF SHA-256 hashes (no weights in this repo)
  FREEZE.md               Frozen-file hashes and the 13 Nov grading-fix log
  scripts/                run_eval.py, compute_metrics.py, plot_results.py, smoke.sh
  tests/                  Unit tests (no model calls)
  results/full/
    PARSE_AUDIT.md        Parser audit and 20-turn hand spot-check
    BEFORE_AFTER.md       Original vs lenient metrics
    SENSITIVITY.md        Lenient vs strict
    <model>/
      trajectories.jsonl          Original frozen logs (raw replies, unchanged)
      trajectories_lenient.jsonl  Re-score, main (lenient) grades
      trajectories_strict.jsonl   Re-score, ANSWER:-only
      metrics.json                Main result (lenient)
      metrics_legacy.json         Original parser, exact reproduction of first metrics
      metrics_strict.json
      metrics_v1_original.json    Metrics as first computed (matches legacy)
      figures/                    Plots from the lenient metrics
      figures_v1/                 Plots from the original metrics
```

The three model folders are `qwen2.5-1.5b`, `llama3.2-1b`, and `qwen2.5-0.5b`.

## Reproduction

Do **not** rerun model generations to obtain the reported numbers. The raw replies are frozen in each `trajectories.jsonl`. Metrics can be recomputed from those logs. All inference for the reported runs was local via Ollama, at **temperature 0** and **seed 42**, with **zero spend**.

From the repository root:

```bash
export PYTHONPATH="$(pwd)"

# Unit tests (56 tests; no model, no network)
python3 -m unittest discover -s fliprate/tests -v
```

Re-score and recompute the main (lenient) metrics from a frozen original log, and plot them. This does not call a model. The written `metrics.json` should match the frozen file in that folder (same rates, counts, and CIs; bootstrap seed 0, 1,000 resamples):

```bash
export PYTHONPATH="$(pwd)"
MODEL=qwen2.5-1.5b   # or llama3.2-1b, or qwen2.5-0.5b
DIR=fliprate/results/full/$MODEL

# Lenient — the main result. --write-trajectories is optional.
python3 fliprate/scripts/compute_metrics.py \
  "$DIR/trajectories.jsonl" \
  --mode lenient --n-boot 1000 --seed 0 \
  --out /tmp/fliprate-$MODEL-metrics-lenient.json \
  --write-trajectories /tmp/fliprate-$MODEL-traj-lenient.jsonl

python3 fliprate/scripts/plot_results.py \
  /tmp/fliprate-$MODEL-metrics-lenient.json \
  --out /tmp/fliprate-$MODEL-figures --label full

# Sensitivity: ANSWER:-only, and the original first-line-fallback parser
python3 fliprate/scripts/compute_metrics.py \
  "$DIR/trajectories.jsonl" --mode strict --n-boot 1000 --seed 0 \
  --out /tmp/fliprate-$MODEL-metrics-strict.json
python3 fliprate/scripts/compute_metrics.py \
  "$DIR/trajectories.jsonl" --mode legacy --n-boot 1000 --seed 0 \
  --out /tmp/fliprate-$MODEL-metrics-legacy.json
```

`legacy` should match `metrics_v1_original.json` / `metrics_legacy.json` exactly. `rescore.py` is the library used by `compute_metrics.py`; it only re-parses logged `raw` text.

### Models (only if you want a new run)

The reported evaluation used three local Q4_K_M GGUFs, registered with Ollama. Weights are **not** in this repository. Tags, Hugging Face sources, byte sizes, and SHA-256 hashes are in [`fliprate/models/VERSIONS.md`](fliprate/models/VERSIONS.md). The tags actually run were `qwen2.5:1.5b`, `llama3.2:1b`, and `qwen2.5:0.5b`. Seeded llama.cpp / Ollama calls can be only approximately reproducible because of KV-cache reuse; that is why the raw logs are kept.

A new full run would look like the following. **Do not overwrite the frozen folders.** Write to a new output directory, and treat any new traces as a fresh experiment, not as a replacement for the reported numbers.

```bash
export PYTHONPATH="$(pwd)"
# Point PATH and OLLAMA_MODELS at your local Ollama install, then:
#   ollama serve
python3 fliprate/scripts/run_eval.py \
  --dataset fliprate/data/items.jsonl \
  --model qwen2.5:1.5b \
  --conditions pressure,control,evidence \
  --seed 42 --temperature 0 --label full \
  --out /tmp/fliprate-new-run
```

The preexisting smoke script, `fliprate/scripts/smoke.sh`, is a 10-item pipeline check. Its outputs are **not findings**.

## Licence

Code is under the MIT License (see [`LICENSE`](LICENSE)), Copyright (c) 2026 Ali Ghaedi. The item set and pushback templates are dedicated to the public domain under **CC0 1.0**, as recorded in [`fliprate/data/SOURCE.md`](fliprate/data/SOURCE.md): they were hand-authored on 12 November 2026; no third-party quiz dump was copied.

## Citation

Ali Ghaedi (2026). *FlipRate: Measuring Multi-Turn Answer Flipping Under User Pushback.* Report for the Apart Research AI × Epistemics Research Sprint, 13–15 November 2026. See `paper/FlipRate_Ghaedi.pdf`.
