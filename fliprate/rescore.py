"""Re-parse and re-grade logged trajectories. Does not call a model.

Used to apply a parser change (or a sensitivity mode) to already-generated
raw replies. Generations are never rerun.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Iterable, Optional

from fliprate.grade import is_correct
from fliprate.parse import MODES, parse_answer_confidence
from fliprate.prompts import ITEMS_PATH, load_items


def alias_map(items_path: Optional[Path] = None) -> dict[str, list[str]]:
    return {it["id"]: list(it.get("aliases") or []) for it in load_items(items_path or ITEMS_PATH)}


def rescore_trajectory(
    traj: dict,
    *,
    mode: str = "lenient",
    aliases: Optional[Iterable[str]] = None,
    keep_original: bool = True,
) -> dict:
    """Return a copy of ``traj`` with answers re-parsed from ``raw`` and re-graded."""
    if mode not in MODES:
        raise ValueError(f"unknown parse mode {mode!r}; expected one of {MODES}")
    out = deepcopy(traj)
    gold = out.get("gold") or ""
    als = list(aliases or [])
    for turn in out.get("turns") or []:
        if turn.get("role") != "assistant":
            continue
        raw = turn.get("raw") or ""
        parsed = parse_answer_confidence(raw, mode=mode)
        if keep_original:
            if "answer_original" not in turn:
                turn["answer_original"] = turn.get("answer")
            if "correct_original" not in turn:
                turn["correct_original"] = turn.get("correct")
            if "confidence_original" not in turn:
                turn["confidence_original"] = turn.get("confidence")
        turn["answer"] = parsed["answer"]
        turn["confidence"] = parsed["confidence"]
        turn["correct"] = is_correct(parsed["answer"], gold, als)
        turn["parse_rule"] = parsed["parse_rule"]
    out["grade_mode"] = mode
    return out


def rescore_trajectories(
    trajs: Iterable[dict],
    *,
    mode: str = "lenient",
    items_path: Optional[Path] = None,
    keep_original: bool = True,
) -> list[dict]:
    amap = alias_map(items_path)
    return [
        rescore_trajectory(
            t,
            mode=mode,
            aliases=amap.get(t.get("item_id") or "", []),
            keep_original=keep_original,
        )
        for t in trajs
    ]
