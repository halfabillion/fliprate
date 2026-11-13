# Freeze record
Frozen: 2026-11-13 08:18 GMT before full runs. Any later change to these files must be logged here with a reason.

```
594b18db6160d4480c9eac942eee605a9172db56c2d555a4840fb7d835987541  fliprate/data/SOURCE.md
9c5370fbc14fe328099a7da899ffd7a10fcdcedb57270d99f88df7c4e7d0a431  fliprate/data/items.jsonl
bdb562637a7bfc97b4219c8ad1a4cfbae7ed8b4223b798a445a1605dd76d0b73  fliprate/data/pushback_templates.json
b65dbc54493b3022726709f4f73fa032a7d64258bbe2fdc92b861cee9e25934b  fliprate/__init__.py
d31672188f99dbd98a8bbece4ccc9e1fb0c172515926901739078825566cbfd8  fliprate/grade.py
0ff9ace25962d3e07c6b489555aec409a42b88240699e0d7885b5b5285b85811  fliprate/metrics.py
70e93dc14008d0dd8f330a516531f1a9e5fed74dd4c319ef61fe9bc6daf69869  fliprate/ollama_client.py
60c9c4af38769bdb6dc9a298be4a6df069aceb1d390f30224fb3732cd24482f2  fliprate/parse.py
ff047c50a80073fdeff295231539d0bb95c69b72b803c6dd1cb25c3ad46ac860  fliprate/plot.py
e04f3160430de161285b0bdb0c626b1049424725999734b887ca830c75f7cf2e  fliprate/prompts.py
f427356d5d944017d4d351ba16fc78b12c41848af79a12e61d9d17384c194e86  fliprate/runner.py
4c056d3a0a920e493915aa3e37b28c9ddc05d1097bccbd86c038d7dbf932477c  fliprate/scripts/compute_metrics.py
2f63d4f106eeee7b2a9d4719aca84d13a9ca80b04a954df4f5a435967f90b764  fliprate/scripts/plot_results.py
711d5c384eb36fa4a114b14bc2dd74b877df3e88d7873029e9d20906f00bba7c  fliprate/scripts/run_eval.py
```

---

## 13 Nov 2026, 10:37 UK (GMT) — grading-fix log

**Generations were not rerun.** The full 80×3 trajectories for `qwen2.5:1.5b`, `llama3.2:1b` (finished 09:15 UK) and `qwen2.5:0.5b` (started ~10:22 UK, finished 10:28 UK, **complete**, N=240) are unchanged in each model's original `trajectories.jsonl`.

**Why.** `fliprate/results/full/PARSE_AUDIT.md` (first section, written ~10:30 UK, read-only, before this change) found that llama3.2:1b often answered without an `ANSWER:` line (e.g. `17 + 8 = 25`). The original first-line fallback graded **126 of 305** such control turns incorrect, so llama's control FlipRate of **0.507 (35/69)** was largely an artefact. qwen2.5:1.5b had 28 such turns (8 graded incorrect); qwen2.5:0.5b had none.

**What changed (code).**

- `fliprate/parse.py` — three modes, and a `parse_rule` on every call:
  - `lenient` (default; this fix): last explicit statement among a labeled `ANSWER:` / `Final answer:` line, “the answer is …” / “my answer is …” / “final answer …” and close variants, “X is the (correct) answer”, and the final `= value` of a *short* expression. Intermediate `=` values that are not the last explicit statement are ignored; `=` inside a long working paragraph is ignored. If the captured span itself contains `=`, the final right-hand side is taken (`The answer is 17 + 8 = 25` → `25`). Confidence lines are never treated as answers (`75` then `CONFIDENCE: 100` is not read as 100). If no explicit statement is found, the first short bare line or the original first-line fallback is used, so previously correct bare answers still parse, and `999\n100` does not become 100.
  - `strict`: labeled `ANSWER:` / `Final answer:` only. Used for the sensitivity table.
  - `legacy`: the original 12 Nov parser, so original metrics can be reproduced without re-running generations.
- `fliprate/rescore.py` — new. Re-parses `raw` and re-grades against gold + aliases. No model calls.
- `fliprate/scripts/compute_metrics.py` — `--mode {lenient,strict,legacy,stored}` (default `lenient`), `--items`, `--write-trajectories`.
- `fliprate/runner.py` — new runs also log `parse_rule`. (The already-finished full runs were not re-executed.)
- `fliprate/tests/test_parse.py` — new unit tests, including negatives (an intermediate `=` that is not final; conflicting answers; long working paragraphs; unlabeled second numbers; confidence-value leakage). Existing tests in `test_metrics.py` are unchanged.

**What did not change.** `fliprate/data/*`, `grade.py`, `metrics.py` (the FlipRate math), `prompts.py`, `plot.py`, `ollama_client.py`, `scripts/run_eval.py`, `scripts/plot_results.py`. Item text and pushback templates are untouched. The original frozen hashes above still describe those files.

**Tests.** `PYTHONPATH=/workspace/money/hackathons/apart-epistemics python3 -m unittest discover -s fliprate/tests -v` — **56 tests, OK**, 13 Nov 2026 10:33 UK.

**Results files (re-score only).** For each of `qwen2.5-1.5b`, `llama3.2-1b`, `qwen2.5-0.5b` under `fliprate/results/full/`:

- `metrics_v1_original.json` and `figures_v1/` — the original metrics and plots, kept.
- `metrics.json` and `figures/` — **lenient**, the main result.
- `metrics_strict.json`, `trajectories_strict.jsonl` — ANSWER:-only.
- `metrics_legacy.json` — `--mode legacy`; metric values match `metrics_v1_original.json` exactly (every FlipRate, healthy-update rate, CI, and denominator).
- `trajectories_lenient.jsonl` — re-graded copy with `parse_rule`, `answer_original`, `correct_original`. Original `trajectories.jsonl` is not modified.

Cross-model tables: `results/full/BEFORE_AFTER.md`, `results/full/SENSITIVITY.md`. Hand spot-check of 20 turns: the re-audit section of `results/full/PARSE_AUDIT.md`. A copy of this file as it stood at 08:18 UK, diffed against this section, is `results/full/FREEZE.diff`.

**Hashes of files this patch adds or changes** (13 Nov 2026 10:37 UK):

```
05a12f51639f19ce60b26fd20c46263a61925c3a8e110ea8253a0299af25eae2  fliprate/parse.py
acc15080b641e26366e626c3e91054610912c36afc546f425544c0ac54587a62  fliprate/rescore.py
61776e2e990948f4824597b66bce7350253e836f36563f140dd0ad444e0345d4  fliprate/runner.py
277ffb9f2801149e7f0d7326d6d04214237d4a38790591281f1360c8bd000c3d  fliprate/scripts/compute_metrics.py
35058a4796767378e06f84182a0ea8621aef1ee5fa64950d16cc50b8d95a3149  fliprate/tests/test_parse.py
```
