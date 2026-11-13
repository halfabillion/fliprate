# Before / after: original (legacy) grading vs the 13 Nov 2026 lenient fix

Generations were **not** rerun. All figures below are from the existing logged `trajectories.jsonl` files, re-scored only.

- **Before:** grades written at generation time by the original 12 Nov parser (first non-empty line as the whole answer). Saved as `metrics_v1_original.json`. Re-scoring with `--mode legacy` reproduces those metric values exactly (`metrics_legacy.json` matches `metrics_v1_original.json` on every FlipRate, healthy-update rate, CI, and denominator).
- **After (main result):** `--mode lenient` (the documented grading fix). Saved as `metrics.json`. Rescored trajectories with `parse_rule` on every assistant turn: `trajectories_lenient.jsonl`. Original `trajectories.jsonl` is unchanged.
- **qwen2.5:0.5b** completed the full 80 items × 3 conditions (240 trajectories) at 10:28 UK on 13 Nov 2026. It is **complete, not partial**.

Rates are among the stated denominator (FlipRate: initially correct items; healthy-update: initially incorrect items). Brackets are 95% percentile bootstrap CIs (1,000 resamples, seed 0).

## FlipRate (ever)

| Model | Condition | Before (legacy) | After (lenient) | Change (pp) |
|---|---|---|---|---|
| `qwen2.5:1.5b` | pressure | 1.000 (73/73) [1.000, 1.000] | 1.000 (73/73) [1.000, 1.000] | +0.0 |
| `qwen2.5:1.5b` | control | 0.041 (3/73) [0.000, 0.095] | 0.041 (3/73) [0.000, 0.095] | +0.0 |
| `qwen2.5:1.5b` | evidence | 0.000 (0/73) [0.000, 0.000] | 0.000 (0/73) [0.000, 0.000] | +0.0 |
| `llama3.2:1b` | pressure | 1.000 (69/69) [1.000, 1.000] | 1.000 (69/69) [1.000, 1.000] | +0.0 |
| `llama3.2:1b` | control | 0.507 (35/69) [0.400, 0.629] | 0.391 (27/69) [0.279, 0.514] | -11.6 |
| `llama3.2:1b` | evidence | 0.145 (10/69) [0.071, 0.234] | 0.145 (10/69) [0.071, 0.234] | +0.0 |
| `qwen2.5:0.5b` | pressure | 0.952 (60/63) [0.895, 1.000] | 0.952 (60/63) [0.895, 1.000] | +0.0 |
| `qwen2.5:0.5b` | control | 0.571 (36/63) [0.441, 0.691] | 0.571 (36/63) [0.441, 0.691] | +0.0 |
| `qwen2.5:0.5b` | evidence | 0.063 (4/63) [0.015, 0.132] | 0.063 (4/63) [0.015, 0.132] | +0.0 |

## FlipRate (final)

| Model | Condition | Before (legacy) | After (lenient) | Change (pp) |
|---|---|---|---|---|
| `qwen2.5:1.5b` | pressure | 0.932 (68/73) [0.870, 0.986] | 0.932 (68/73) [0.870, 0.986] | +0.0 |
| `qwen2.5:1.5b` | control | 0.041 (3/73) [0.000, 0.095] | 0.041 (3/73) [0.000, 0.095] | +0.0 |
| `qwen2.5:1.5b` | evidence | 0.000 (0/73) [0.000, 0.000] | 0.000 (0/73) [0.000, 0.000] | +0.0 |
| `llama3.2:1b` | pressure | 0.739 (51/69) [0.625, 0.833] | 0.739 (51/69) [0.625, 0.833] | +0.0 |
| `llama3.2:1b` | control | 0.377 (26/69) [0.269, 0.500] | 0.304 (21/69) [0.197, 0.422] | -7.2 |
| `llama3.2:1b` | evidence | 0.130 (9/69) [0.056, 0.219] | 0.130 (9/69) [0.056, 0.219] | +0.0 |
| `qwen2.5:0.5b` | pressure | 0.952 (60/63) [0.895, 1.000] | 0.952 (60/63) [0.895, 1.000] | +0.0 |
| `qwen2.5:0.5b` | control | 0.571 (36/63) [0.441, 0.691] | 0.571 (36/63) [0.441, 0.691] | +0.0 |
| `qwen2.5:0.5b` | evidence | 0.063 (4/63) [0.015, 0.132] | 0.063 (4/63) [0.015, 0.132] | +0.0 |

## Healthy-update rate

| Model | Condition | Before (legacy) | After (lenient) | Change (pp) |
|---|---|---|---|---|
| `qwen2.5:1.5b` | pressure | 0.000 (0/7) [0.000, 0.000] | 0.000 (0/7) [0.000, 0.000] | +0.0 |
| `qwen2.5:1.5b` | control | 0.000 (0/7) [0.000, 0.000] | 0.000 (0/7) [0.000, 0.000] | +0.0 |
| `qwen2.5:1.5b` | evidence | 0.429 (3/7) [0.000, 0.833] | 0.429 (3/7) [0.000, 0.833] | +0.0 |
| `llama3.2:1b` | pressure | 0.000 (0/11) [0.000, 0.000] | 0.000 (0/11) [0.000, 0.000] | +0.0 |
| `llama3.2:1b` | control | 0.455 (5/11) [0.143, 0.769] | 0.455 (5/11) [0.143, 0.769] | +0.0 |
| `llama3.2:1b` | evidence | 0.727 (8/11) [0.417, 1.000] | 0.727 (8/11) [0.417, 1.000] | +0.0 |
| `qwen2.5:0.5b` | pressure | 0.000 (0/17) [0.000, 0.000] | 0.000 (0/17) [0.000, 0.000] | +0.0 |
| `qwen2.5:0.5b` | control | 0.000 (0/17) [0.000, 0.000] | 0.000 (0/17) [0.000, 0.000] | +0.0 |
| `qwen2.5:0.5b` | evidence | 0.588 (10/17) [0.353, 0.800] | 0.588 (10/17) [0.353, 0.800] | +0.0 |

## Initial accuracy (unchanged for all three models)

| Model | Before = After | n initial-correct / 80 |
|---|---|---|
| `qwen2.5:1.5b` | 0.912 (73/80) [0.850, 0.963] | 73/80 |
| `llama3.2:1b` | 0.863 (69/80) [0.787, 0.938] | 69/80 |
| `qwen2.5:0.5b` | 0.787 (63/80) [0.700, 0.875] | 63/80 |

## What moved

- **llama3.2:1b, control, FlipRate ever:** 0.507 (35/69) [0.400, 0.629] → **0.391 (27/69) [0.279, 0.514]**. FlipRate final: 0.377 (26/69) [0.269, 0.500] → **0.304 (21/69) [0.197, 0.422]**.
- **llama3.2:1b, pressure, FlipRate ever** stayed at 1.000 (69/69). FlipRate final stayed at 0.739 (51/69). The mild-doubt per-turn rate fell 0.290 (20/69) → 0.246 (17/69), matching the three pressure turns that the fix re-graded from incorrect to correct.
- **llama3.2:1b, evidence** and **healthy-update rates in every condition** were unchanged.
- **qwen2.5:1.5b** and **qwen2.5:0.5b**: every FlipRate, healthy-update rate, CI, and denominator is identical before and after (0.0 pp). qwen2.5:1.5b had only 28 turns without an `ANSWER:` line, already graded the same under both parsers; qwen2.5:0.5b had **zero** such turns (all 1,040 assistant turns used a labeled `ANSWER:` line).
- Turn-level grade changes, llama3.2:1b only: **26 False → True, 0 True → False**, of which 23 were in control and 3 in pressure. See `PARSE_AUDIT.md` for the hand spot-check.

The llama control FlipRate of 0.507 reported by the original parser is an artefact and is **not** a result. Main-text numbers use the After (lenient) column.

