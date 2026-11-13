#!/usr/bin/env python3
"""Run FlipRate conversations against local Ollama and write JSONL."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fliprate.prompts import ITEMS_PATH
from fliprate.runner import CONDITIONS, run_eval


def main() -> None:
    p = argparse.ArgumentParser(description="Run FlipRate on local Ollama (no cloud APIs).")
    p.add_argument("--dataset", type=Path, default=ITEMS_PATH)
    p.add_argument("--model", required=True, help="Ollama model tag, e.g. qwen2.5:1.5b")
    p.add_argument("--n", type=int, default=None, help="Use only the first N items")
    p.add_argument("--conditions", default="pressure,control,evidence")
    p.add_argument("--out", type=Path, required=True, help="Output directory")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--label", default="run", help="Use 'smoke' for the pipeline check")
    args = p.parse_args()
    conds = [c.strip() for c in args.conditions.split(",") if c.strip()]
    for c in conds:
        if c not in CONDITIONS:
            p.error(f"unknown condition {c}; choose from {CONDITIONS}")
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    traj_path = out_dir / "trajectories.jsonl"
    run_eval(
        dataset_path=args.dataset,
        model=args.model,
        n=args.n,
        conditions=conds,
        out_path=traj_path,
        temperature=args.temperature,
        seed=args.seed,
        label=args.label,
    )
    print(f"Wrote {traj_path}")


if __name__ == "__main__":
    main()
