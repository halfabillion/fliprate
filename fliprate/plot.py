"""Plot FlipRate summaries. Label smoke figures as smoke, not findings."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _ci_bar(ax, labels, values, lows, highs, title: str, banner: Optional[str]):
    xs = range(len(labels))
    y = [0 if v is None else v for v in values]
    yerr_lo = []
    yerr_hi = []
    for v, lo, hi in zip(values, lows, highs):
        if v is None or lo is None or hi is None:
            yerr_lo.append(0)
            yerr_hi.append(0)
        else:
            yerr_lo.append(max(0.0, v - lo))
            yerr_hi.append(max(0.0, hi - v))
    ax.bar(list(xs), y, yerr=[yerr_lo, yerr_hi], capsize=4, color="#3b6d99")
    ax.set_xticks(list(xs), labels, rotation=20, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("rate")
    ax.set_title(title)
    if banner:
        ax.text(
            0.5,
            1.12,
            banner,
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=9,
            color="#8a1c1c",
            fontweight="bold",
        )


def plot_summary(summary: dict, out_dir: Path, label: str = "run") -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    banner = "SMOKE TEST — NOT FINDINGS" if label == "smoke" else None
    paths: list[Path] = []
    conds = list(summary.get("by_condition", {}).items())
    if conds:
        labels = [k for k, _ in conds]
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
        for ax, key, title in (
            (axes[0], "fliprate_ever", "FlipRate (ever, among initially correct)"),
            (axes[1], "fliprate_final", "FlipRate (final turn, among initially correct)"),
        ):
            vals, lows, highs = [], [], []
            for _, s in conds:
                m = s.get(key) or {}
                vals.append(m.get("value"))
                lows.append(m.get("ci_low"))
                highs.append(m.get("ci_high"))
            _ci_bar(ax, labels, vals, lows, highs, title, banner)
        fig.tight_layout()
        p = out_dir / "fliprate_by_condition.png"
        fig.savefig(p, dpi=140, bbox_inches="tight")
        plt.close(fig)
        paths.append(p)

        # healthy update + initial accuracy
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
        for ax, key, title in (
            (axes[0], "healthy_update_rate", "Healthy update (incorrect → correct)"),
            (axes[1], "initial_accuracy", "Initial accuracy"),
        ):
            vals, lows, highs = [], [], []
            for _, s in conds:
                m = s.get(key) or {}
                vals.append(m.get("value"))
                lows.append(m.get("ci_low"))
                highs.append(m.get("ci_high"))
            _ci_bar(ax, labels, vals, lows, highs, title, banner)
        fig.tight_layout()
        p = out_dir / "update_and_accuracy.png"
        fig.savefig(p, dpi=140, bbox_inches="tight")
        plt.close(fig)
        paths.append(p)

        # per-turn for pressure if present
        pressure = summary.get("by_condition", {}).get("pressure", {})
        per = pressure.get("per_turn") or {}
        if per:
            labels = list(per.keys())
            vals = [per[k]["flip_at_turn"].get("value") for k in labels]
            lows = [per[k]["flip_at_turn"].get("ci_low") for k in labels]
            highs = [per[k]["flip_at_turn"].get("ci_high") for k in labels]
            fig, ax = plt.subplots(figsize=(8, 4.2))
            _ci_bar(ax, labels, vals, lows, highs, "Flip at turn (pressure, initially correct)", banner)
            fig.tight_layout()
            p = out_dir / "fliprate_by_pressure_type.png"
            fig.savefig(p, dpi=140, bbox_inches="tight")
            plt.close(fig)
            paths.append(p)

        # confidence drift
        fig, ax = plt.subplots(figsize=(6, 4.2))
        labels = [k for k, _ in conds]
        vals = [s.get("confidence_drift_mean", {}).get("value") for _, s in conds]
        # drift can be negative; simple bar without 0-1 ylim
        xs = range(len(labels))
        y = [0 if v is None else v for v in vals]
        ax.bar(list(xs), y, color="#3b6d99")
        ax.axhline(0, color="#444", linewidth=0.8)
        ax.set_xticks(list(xs), labels, rotation=20, ha="right")
        ax.set_ylabel("mean confidence change (final − initial)")
        ax.set_title("Confidence drift")
        if banner:
            ax.text(0.5, 1.12, banner, transform=ax.transAxes, ha="center", va="bottom",
                    fontsize=9, color="#8a1c1c", fontweight="bold")
        fig.tight_layout()
        p = out_dir / "confidence_drift.png"
        fig.savefig(p, dpi=140, bbox_inches="tight")
        plt.close(fig)
        paths.append(p)
    return paths
