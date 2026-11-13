"""Normalize and grade short answers against gold + aliases."""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable, Optional


_PUNCT_RE = re.compile(r"[^\w\s\.\-\+/]")
_WS_RE = re.compile(r"\s+")


def normalize(text: Optional[str]) -> str:
    if not text:
        return ""
    s = unicodedata.normalize("NFKC", text).strip().lower()
    s = s.replace("the ", " ")
    s = s.replace("city of ", " ")
    s = _PUNCT_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    # drop trailing "city"/"units" noise
    for suffix in (" city", " units", " unit"):
        if s.endswith(suffix):
            s = s[: -len(suffix)].strip()
    return s


def _numeric(s: str) -> Optional[float]:
    # Accept "1,000", "1 000", or "1000"
    compact = s.replace(",", "").replace(" ", "")
    try:
        return float(compact)
    except ValueError:
        return None


def is_correct(pred: Optional[str], gold: str, aliases: Iterable[str] | None = None) -> bool:
    if pred is None:
        return False
    candidates = [gold, *(aliases or [])]
    pn = normalize(pred)
    if not pn:
        return False
    pnum = _numeric(pn)
    for c in candidates:
        cn = normalize(c)
        if not cn:
            continue
        if pn == cn:
            return True
        # containment for short gold in a slightly longer pred ("paris france")
        if cn in pn and len(cn) >= 3:
            return True
        cnum = _numeric(cn)
        if pnum is not None and cnum is not None and abs(pnum - cnum) < 1e-9:
            return True
    return False
