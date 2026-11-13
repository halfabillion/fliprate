"""Load items and format pushback / control / evidence turns."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent / "data"
TEMPLATES_PATH = DATA_DIR / "pushback_templates.json"
ITEMS_PATH = DATA_DIR / "items.jsonl"


def load_templates(path: Path | None = None) -> dict:
    with open(path or TEMPLATES_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_items(path: Path | None = None) -> list[dict]:
    items = []
    with open(path or ITEMS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            items.append(json.loads(line))
    return items


def format_user_turn(template: str, item: dict) -> str:
    return template.format(
        wrong_answer=item.get("wrong_answer", "something else"),
        evidence=item.get("evidence", f"The correct answer is {item.get('answer')}."),
        answer=item.get("answer", ""),
    )


def followups_for(condition: str, templates: dict) -> list[dict[str, str]]:
    if condition not in templates:
        raise ValueError(f"Unknown condition {condition!r}; expected pressure, control, or evidence")
    return list(templates[condition])


def initial_user_message(item: dict, templates: dict) -> str:
    q = item["question"].rstrip()
    suffix = templates.get("initial_suffix", "")
    return f"{q}\n\n{suffix}".strip()
