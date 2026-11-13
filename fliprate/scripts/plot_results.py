#!/usr/bin/env python3
"""Plot a metrics JSON file written by compute_metrics.py."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fliprate.plot import plot_summary


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("metrics", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--label", default=None)
    args = p.parse_args()
    summary = json.loads(args.metrics.read_text(encoding="utf-8"))
    label = args.label
    if label is None:
        labels = summary.get("labels") or []
        label = "smoke" if "smoke" in labels else "run"
    paths = plot_summary(summary, args.out, label=label)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
