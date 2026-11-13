"""Run FlipRate conversations and log JSONL trajectories."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from fliprate.grade import is_correct
from fliprate.ollama_client import chat
from fliprate.parse import parse_answer_confidence
from fliprate.prompts import (
    followups_for,
    format_user_turn,
    initial_user_message,
    load_items,
    load_templates,
)


CONDITIONS = ("pressure", "control", "evidence")


def run_trajectory(
    item: dict,
    *,
    model: str,
    condition: str,
    templates: dict,
    temperature: float = 0.0,
    seed: int = 0,
    num_predict: int = 96,
    label: str = "run",
) -> dict:
    messages: list[dict] = []
    if templates.get("system"):
        messages.append({"role": "system", "content": templates["system"]})
    user0 = initial_user_message(item, templates)
    messages.append({"role": "user", "content": user0})

    turns: list[dict] = [{"turn": 0, "role": "user", "name": "initial", "content": user0}]
    t0 = time.time()
    resp = chat(model, messages, temperature=temperature, seed=seed, num_predict=num_predict)
    parsed = parse_answer_confidence(resp["content"])
    correct = is_correct(parsed["answer"], item["answer"], item.get("aliases") or [])
    assistant = {
        "turn": 0,
        "role": "assistant",
        "name": "initial",
        "raw": parsed["raw"],
        "answer": parsed["answer"],
        "confidence": parsed["confidence"],
        "parse_rule": parsed.get("parse_rule"),
        "correct": correct,
        "eval_count": (resp.get("raw_response") or {}).get("eval_count"),
        "eval_duration_ns": (resp.get("raw_response") or {}).get("eval_duration"),
    }
    turns.append(assistant)
    messages.append({"role": "assistant", "content": resp["content"]})

    for i, step in enumerate(followups_for(condition, templates), start=1):
        user_text = format_user_turn(step["template"], item)
        messages.append({"role": "user", "content": user_text})
        turns.append({"turn": i, "role": "user", "name": step["name"], "content": user_text})
        resp = chat(model, messages, temperature=temperature, seed=seed, num_predict=num_predict)
        parsed = parse_answer_confidence(resp["content"])
        correct = is_correct(parsed["answer"], item["answer"], item.get("aliases") or [])
        turns.append({
            "turn": i,
            "role": "assistant",
            "name": step["name"],
            "raw": parsed["raw"],
            "answer": parsed["answer"],
            "confidence": parsed["confidence"],
            "parse_rule": parsed.get("parse_rule"),
            "correct": correct,
            "eval_count": (resp.get("raw_response") or {}).get("eval_count"),
            "eval_duration_ns": (resp.get("raw_response") or {}).get("eval_duration"),
        })
        messages.append({"role": "assistant", "content": resp["content"]})

    return {
        "item_id": item["id"],
        "category": item.get("category"),
        "gold": item["answer"],
        "wrong_answer": item.get("wrong_answer"),
        "model": model,
        "condition": condition,
        "temperature": temperature,
        "seed": seed,
        "label": label,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(time.time() - t0, 3),
        "turns": turns,
    }


def run_eval(
    *,
    dataset_path: Path,
    model: str,
    n: Optional[int],
    conditions: Iterable[str],
    out_path: Path,
    temperature: float = 0.0,
    seed: int = 42,
    label: str = "run",
    item_ids: Optional[list[str]] = None,
) -> list[dict]:
    items = load_items(dataset_path)
    if item_ids:
        want = set(item_ids)
        items = [it for it in items if it["id"] in want]
    if n is not None:
        items = items[:n]
    templates = load_templates()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written: list[dict] = []
    with open(out_path, "w", encoding="utf-8") as f:
        for item in items:
            for cond in conditions:
                if cond not in CONDITIONS:
                    raise ValueError(f"Unknown condition {cond}")
                traj = run_trajectory(
                    item,
                    model=model,
                    condition=cond,
                    templates=templates,
                    temperature=temperature,
                    seed=seed,
                    label=label,
                )
                f.write(json.dumps(traj, ensure_ascii=False) + "\n")
                f.flush()
                written.append(traj)
                print(
                    f"[{label}] {item['id']} {cond}: "
                    f"init={'OK' if traj['turns'][1]['correct'] else 'XX'} "
                    f"ans={traj['turns'][1]['answer']!r} "
                    f"{traj['elapsed_s']}s",
                    flush=True,
                )
    return written
