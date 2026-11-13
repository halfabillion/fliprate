#!/usr/bin/env python3
"""Compute FlipRate metrics + bootstrap CIs from a trajectories JSONL.

By default, assistant turns are re-parsed and re-graded from the logged
``raw`` text (``--mode lenient``, the 13 Nov 2026 grading fix). Pass
``--mode strict`` for ANSWER:-only grading, ``--mode legacy`` for the
original first-line fallback, or ``--mode stored`` to use the grades
already written on the file. Generations are never rerun.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fliprate.metrics import summarize
from fliprate.parse import MODES
from fliprate.prompts import ITEMS_PATH
from fliprate.rescore import rescore_trajectories


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("trajectories", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--n-boot", type=int, default=1000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--mode",
        choices=(*MODES, "stored"),
        default="lenient",
        help="Parser/grader mode. 'stored' keeps the grades already on the file.",
    )
    p.add_argument(
        "--items",
        type=Path,
        default=ITEMS_PATH,
        help="items.jsonl, used for aliases when re-grading",
    )
    p.add_argument(
        "--write-trajectories",
        type=Path,
        default=None,
        help="If set, write the re-scored trajectories (with parse_rule) here.",
    )
    args = p.parse_args()
    trajs = load_jsonl(args.trajectories)
    if args.mode != "stored":
        trajs = rescore_trajectories(trajs, mode=args.mode, items_path=args.items)
    summary = summarize(trajs, n_boot=args.n_boot, seed=args.seed)
    labels = sorted({t.get("label") for t in trajs if t.get("label")})
    summary["labels"] = labels
    summary["grade_mode"] = args.mode
    if "smoke" in labels:
        summary["warning"] = "SMOKE TEST — these numbers are a pipeline check, not findings."
    # Parse-rule histogram, when present.
    rules: dict[str, int] = {}
    for t in trajs:
        for turn in t.get("turns") or []:
            if turn.get("role") != "assistant":
                continue
            r = turn.get("parse_rule")
            if r:
                rules[r] = rules.get(r, 0) + 1
    if rules:
        summary["parse_rules"] = dict(sorted(rules.items()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if args.write_trajectories is not None:
        args.write_trajectories.parent.mkdir(parents=True, exist_ok=True)
        with open(args.write_trajectories, "w", encoding="utf-8") as f:
            for t in trajs:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
        print(f"Wrote {args.write_trajectories}")
    printable = {k: summary[k] for k in ("n_trajectories", "labels", "grade_mode", "warning") if k in summary}
    print(json.dumps(printable, indent=2))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
