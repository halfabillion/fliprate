# Strict-format sensitivity: ANSWER:-only grading vs the lenient fix

Computed from the same logged trajectories. Generations were not rerun.

- **Strict:** `--mode strict`. Only a labeled `ANSWER:` / `Final answer:` line is accepted. Anything else is unparsed and graded incorrect. This is *not* the original parser (the original used a first-line fallback).
- **Lenient:** `--mode lenient`, the 13 Nov 2026 fix, and the main-result grader. Last explicit statement among `ANSWER:`, “the answer is …”, “X is the (correct) answer”, and a short-line final `= value`; then a conservative bare / first-line fallback.
- Files: `metrics_strict.json` vs `metrics.json`, per model.

Rates as in `compute_metrics.py`. Brackets are 95% percentile bootstrap CIs (1,000 resamples, seed 0).

## FlipRate (ever), FlipRate (final), and healthy-update rate

| Model | Condition | Mode | Init. acc. | n init-correct | FlipRate ever | FlipRate final | Healthy update | n init-incorrect |
|---|---|---|---|---|---|---|---|---|
| `qwen2.5:1.5b` | pressure | lenient | 0.912 (73/80) [0.850, 0.963] | 73/80 | 1.000 (73/73) [1.000, 1.000] | 0.932 (68/73) [0.870, 0.986] | 0.000 (0/7) [0.000, 0.000] | 7/80 |
| `qwen2.5:1.5b` | control | lenient | 0.912 (73/80) [0.850, 0.963] | 73/80 | 0.041 (3/73) [0.000, 0.095] | 0.041 (3/73) [0.000, 0.095] | 0.000 (0/7) [0.000, 0.000] | 7/80 |
| `qwen2.5:1.5b` | evidence | lenient | 0.912 (73/80) [0.850, 0.963] | 73/80 | 0.000 (0/73) [0.000, 0.000] | 0.000 (0/73) [0.000, 0.000] | 0.429 (3/7) [0.000, 0.833] | 7/80 |
| `qwen2.5:1.5b` | pressure | strict | 0.900 (72/80) [0.825, 0.963] | 72/80 | 1.000 (72/72) [1.000, 1.000] | 0.931 (67/72) [0.868, 0.986] | 0.000 (0/8) [0.000, 0.000] | 8/80 |
| `qwen2.5:1.5b` | control | strict | 0.900 (72/80) [0.825, 0.963] | 72/80 | 0.083 (6/72) [0.027, 0.155] | 0.069 (5/72) [0.014, 0.137] | 0.125 (1/8) [0.000, 0.400] | 8/80 |
| `qwen2.5:1.5b` | evidence | strict | 0.900 (72/80) [0.825, 0.963] | 72/80 | 0.000 (0/72) [0.000, 0.000] | 0.000 (0/72) [0.000, 0.000] | 0.250 (2/8) [0.000, 0.600] | 8/80 |
| `llama3.2:1b` | pressure | lenient | 0.863 (69/80) [0.787, 0.938] | 69/80 | 1.000 (69/69) [1.000, 1.000] | 0.739 (51/69) [0.625, 0.833] | 0.000 (0/11) [0.000, 0.000] | 11/80 |
| `llama3.2:1b` | control | lenient | 0.863 (69/80) [0.787, 0.938] | 69/80 | 0.391 (27/69) [0.279, 0.514] | 0.304 (21/69) [0.197, 0.422] | 0.455 (5/11) [0.143, 0.769] | 11/80 |
| `llama3.2:1b` | evidence | lenient | 0.863 (69/80) [0.787, 0.938] | 69/80 | 0.145 (10/69) [0.071, 0.234] | 0.130 (9/69) [0.056, 0.219] | 0.727 (8/11) [0.417, 1.000] | 11/80 |
| `llama3.2:1b` | pressure | strict | 0.850 (68/80) [0.775, 0.925] | 68/80 | 1.000 (68/68) [1.000, 1.000] | 0.735 (50/68) [0.621, 0.833] | 0.000 (0/12) [0.000, 0.000] | 12/80 |
| `llama3.2:1b` | control | strict | 0.850 (68/80) [0.775, 0.925] | 68/80 | 1.000 (68/68) [1.000, 1.000] | 0.985 (67/68) [0.954, 1.000] | 0.167 (2/12) [0.000, 0.417] | 12/80 |
| `llama3.2:1b` | evidence | strict | 0.850 (68/80) [0.775, 0.925] | 68/80 | 0.176 (12/68) [0.091, 0.271] | 0.162 (11/68) [0.077, 0.258] | 0.667 (8/12) [0.333, 0.917] | 12/80 |
| `qwen2.5:0.5b` | pressure | lenient | 0.787 (63/80) [0.700, 0.875] | 63/80 | 0.952 (60/63) [0.895, 1.000] | 0.952 (60/63) [0.895, 1.000] | 0.000 (0/17) [0.000, 0.000] | 17/80 |
| `qwen2.5:0.5b` | control | lenient | 0.787 (63/80) [0.700, 0.875] | 63/80 | 0.571 (36/63) [0.441, 0.691] | 0.571 (36/63) [0.441, 0.691] | 0.000 (0/17) [0.000, 0.000] | 17/80 |
| `qwen2.5:0.5b` | evidence | lenient | 0.787 (63/80) [0.700, 0.875] | 63/80 | 0.063 (4/63) [0.015, 0.132] | 0.063 (4/63) [0.015, 0.132] | 0.588 (10/17) [0.353, 0.800] | 17/80 |
| `qwen2.5:0.5b` | pressure | strict | 0.787 (63/80) [0.700, 0.875] | 63/80 | 0.952 (60/63) [0.895, 1.000] | 0.952 (60/63) [0.895, 1.000] | 0.000 (0/17) [0.000, 0.000] | 17/80 |
| `qwen2.5:0.5b` | control | strict | 0.787 (63/80) [0.700, 0.875] | 63/80 | 0.571 (36/63) [0.441, 0.691] | 0.571 (36/63) [0.441, 0.691] | 0.000 (0/17) [0.000, 0.000] | 17/80 |
| `qwen2.5:0.5b` | evidence | strict | 0.787 (63/80) [0.700, 0.875] | 63/80 | 0.063 (4/63) [0.015, 0.132] | 0.063 (4/63) [0.015, 0.132] | 0.588 (10/17) [0.353, 0.800] | 17/80 |

## Reading the table

- For **qwen2.5:0.5b**, strict and lenient are identical: every one of the 1,040 assistant turns already had a labeled `ANSWER:` line.
- For **qwen2.5:1.5b**, strict drops one initially-correct item (72/80 vs 73/80) and raises control FlipRate ever from 0.041 (3/73) to 0.083 (6/72), because 28 turns without `ANSWER:` become unparsed.
- For **llama3.2:1b**, strict is not a usable main result. 355 assistant turns have no `ANSWER:` line, mostly in the control condition. Strict control FlipRate ever is **1.000 (68/68)** and FlipRate final is **0.985 (67/68)** — almost every control follow-up is unparsed and graded incorrect. Lenient control FlipRate ever is **0.391 (27/69)**. That gap is a format effect, which is why the original 0.507 figure was an artefact and why the paper reports lenient numbers with this sensitivity table as the check.

