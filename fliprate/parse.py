"""Parse ANSWER / CONFIDENCE from a model reply.

Modes
-----
lenient (default)
    The 13 Nov 2026 grading fix. Among explicit statements, the *last*
    one wins (conservative when the reply contains several candidates):

      - a labeled ``ANSWER:`` / ``Final answer:`` line   (rule: ``answer_line``)
      - ``The answer is ...`` / ``My answer is ...`` /
        ``The final answer is ...`` / ``final answer ...``
        and close variants such as ``the answer is: ...``  (rule: ``the_answer_is``)
      - ``X is the (correct) answer``                     (rule: ``is_the_answer``)
      - the final ``= value`` of an expression              (rule: ``equals_value``)

    If the captured span itself contains ``=``, the final right-hand side
    is taken, so ``The answer is 17 + 8 = 25`` yields ``25``. Intermediate
    ``=`` values that are not the last explicit statement are ignored.

    If no explicit statement is found, the first short bare line (rule: ``bare_line``)
    or the original first-line fallback (rule: ``legacy_first_line``) is
    used, so previously correct bare answers such as ``Paris`` still parse.
    Confidence lines are never treated as answers (so ``75`` followed by
    ``CONFIDENCE: 100`` is not read as ``100``).

strict
    Labeled ``ANSWER:`` / ``Final answer:`` lines only. No fallback.
    Used for the strict-format sensitivity table.

legacy
    The original 12 Nov parser: a labeled ``ANSWER:`` line, else the first
    non-empty non-confidence line taken as a whole. Kept so original
    metrics can be reproduced without re-running generations.

Every call records ``parse_rule`` naming the rule that fired, or
``unparsed`` if no answer was extracted.
"""

from __future__ import annotations

import re
from typing import Optional

# Labeled "ANSWER:" / "Final answer:" / "Answer -" (colon or hyphen required).
# Same spirit as the original ANSWER_RE; the value runs to a newline or "confidence".
ANSWER_LINE_RE = re.compile(
    r"(?i)\b(?:final\s+)?answer\s*[:\-]\s*(.+?)(?=(?:\n|\r|$)|(?:\bconfidence\b))",
    re.DOTALL,
)

# "The answer is 12", "the answer is: 12", "My answer is: 63",
# "The final answer is 30", "The correct answer is 32", "final answer is 30".
THE_ANSWER_IS_RE = re.compile(
    r"(?i)\b(?:(?:the|my)\s+)?(?:correct\s+)?(?:final\s+)?answer\s+is\b\s*[:\-]?\s*"
    r"(.+?)(?=(?:\n|\r|$)|(?:\bconfidence\b))",
    re.DOTALL,
)

# "final answer 30" / "final answer: 30" already covered above when "is" or ":"
# is present; this catches "final answer 30" with neither.
FINAL_ANSWER_BARE_RE = re.compile(
    r"(?i)\bfinal\s+answer\b(?!\s+is\b)(?!\s*[:\-])\s+"
    r"(.+?)(?=(?:\n|\r|$)|(?:\bconfidence\b))",
    re.DOTALL,
)

# "32 is the correct answer" / "32 is the answer" / "32 is the final answer".
IS_THE_ANSWER_RE = re.compile(
    r"(?i)(?:^|\n)\s*(.+?)\s+is\s+the\s+(?:correct\s+)?(?:final\s+)?answer\b",
)

# Assignment "=", but not ==, !=, <=, >=. The last match is the final RHS.
EQUALS_RE = re.compile(r"(?<![<>=!])=\s*(?![=])([^\n=]+)")

# Leading fillers after "the answer is indeed 64".
# One whitespace class is enough: "indeed 64" has a single space.
_FILLER_RE = re.compile(
    r"(?i)^(indeed|actually|clearly|simply|just|definitely|obviously|really|"
    r"still|now|yes|certainly|of course),?\s+(?=\S)"
)

CONF_RE = re.compile(
    r"(?i)\bconfidence\s*[:\-]?\s*(\d{1,3})\s*(?:%|percent)?",
)
CONF_FALLBACK_RE = re.compile(
    r"(?i)(?:i(?:'m| am)\s+)?(\d{1,3})\s*(?:%|percent)\s*(?:sure|confident|certain)",
)

# Kept under the original name so any import of ANSWER_RE still works.
ANSWER_RE = ANSWER_LINE_RE

MODES = ("lenient", "strict", "legacy")

# Short bare-line answers: a handful of tokens, not a sentence / expression.
_MAX_BARE_WORDS = 8
# Equals is only treated as an explicit answer when the *line* is a short
# expression ("17 + 8 = 25"), not a long multi-step working paragraph.
_MAX_EQUALS_LINE_WORDS = 16
_HEDGE_START_RE = re.compile(
    r"(?i)^(i(?:'ll| will| can|'d| would)|let me|sorry|wait|hmm|uh)\b"
)
# "I am 90% confident in this answer" — a confidence clause, not an answer.
_PURE_CONF_UTTERANCE_RE = re.compile(
    r"(?i)^(?:i(?:'m| am)\s+)?\d{1,3}\s*(?:%|percent)\s*(?:sure|confident|certain)\b"
    r"(?:\s+in\s+(?:this|my)\s+answer)?\s*\.?$"
)


def parse_answer_confidence(text: str, mode: str = "lenient") -> dict:
    """Return {answer, confidence, raw, parse_rule}. Missing fields are None.

    ``mode`` is ``lenient`` (default; the 13 Nov fix), ``strict``
    (ANSWER:-only), or ``legacy`` (original first-line fallback).
    """
    if mode not in MODES:
        raise ValueError(f"unknown parse mode {mode!r}; expected one of {MODES}")
    raw = text or ""
    if mode == "legacy":
        answer, rule = _parse_legacy(raw)
    elif mode == "strict":
        answer, rule = _parse_strict(raw)
    else:
        answer, rule = _parse_lenient(raw)
    confidence = _parse_confidence(raw)
    return {
        "answer": answer or None,
        "confidence": confidence,
        "raw": raw,
        "parse_rule": rule if (answer or None) else "unparsed",
    }


def _parse_strict(raw: str) -> tuple[Optional[str], str]:
    """Last labeled ANSWER: / Final answer: line only."""
    matches = list(ANSWER_LINE_RE.finditer(raw))
    if not matches:
        return None, "unparsed"
    answer = _clean_extracted(matches[-1].group(1))
    return (answer or None), "answer_line"


def _parse_legacy(raw: str) -> tuple[Optional[str], str]:
    """Original 12 Nov behaviour, preserved byte-for-byte in spirit."""
    answer = None
    rule = "unparsed"
    m = ANSWER_LINE_RE.search(raw)
    if m:
        answer = _clean_answer(m.group(1))
        rule = "answer_line"
    if not answer:
        for line in raw.splitlines():
            s = line.strip()
            if not s:
                continue
            if re.match(r"(?i)^(confidence|conf)\b", s):
                continue
            answer = _clean_answer(re.sub(r"(?i)^(final\s+)?answer\s*[:\-]\s*", "", s))
            rule = "legacy_first_line"
            break
    return (answer or None), (rule if (answer or None) else "unparsed")


def _parse_lenient(raw: str) -> tuple[Optional[str], str]:
    """Last explicit statement, then a conservative bare / first-line fallback."""
    candidates: list[tuple[int, str, str]] = []  # (end_pos, rule, captured)

    for regex, rule in (
        (ANSWER_LINE_RE, "answer_line"),
        (THE_ANSWER_IS_RE, "the_answer_is"),
        (FINAL_ANSWER_BARE_RE, "the_answer_is"),
        (IS_THE_ANSWER_RE, "is_the_answer"),
    ):
        for m in regex.finditer(raw):
            captured = m.group(1)
            # Skip matches that live inside a confidence line.
            line_start = raw.rfind("\n", 0, m.start()) + 1
            line_end = raw.find("\n", m.start())
            if line_end < 0:
                line_end = len(raw)
            if _is_confidence_line(raw[line_start:line_end]):
                continue
            candidates.append((m.end(), rule, captured))

    for m in EQUALS_RE.finditer(raw):
        line = _line_at(raw, m.start())
        if _is_confidence_line(line):
            continue
        if not _is_short_equals_line(line):
            continue
        candidates.append((m.end(), "equals_value", m.group(1)))

    if candidates:
        # Last explicit statement by end position. Ties: prefer the more
        # specific phrasal/labeled rule over a raw equals on the same span.
        _priority = {
            "answer_line": 3,
            "the_answer_is": 3,
            "is_the_answer": 3,
            "equals_value": 1,
        }
        candidates.sort(key=lambda c: (c[0], _priority.get(c[1], 0)))
        _, rule, captured = candidates[-1]
        answer = _clean_extracted(captured)
        if answer:
            return answer, rule

    # No explicit statement (or it cleaned to empty): bare / first-line fallback.
    bare = _first_bare_line(raw)
    if bare:
        return bare, "bare_line"

    first = _legacy_first_line(raw)
    if first:
        return first, "legacy_first_line"

    return None, "unparsed"


def _clean_extracted(s: str) -> str:
    """Clean a captured span; if it contains ``=``, take the final RHS."""
    s = s or ""
    # Prefer the final equals-value *inside* the captured span (e.g.
    # "The answer is 17 + 8 = 25" → "25") before other cleanup.
    eqs = [m for m in EQUALS_RE.finditer(s)]
    if eqs:
        s = eqs[-1].group(1)
    # Cut at a sentence-ending period that is not a decimal point.
    s = re.split(r"(?<!\d)\.(?!\d)", s, maxsplit=1)[0]
    # And at a trailing confidence clause on the same line.
    s = re.split(r"(?i)\bconfidence\b", s, maxsplit=1)[0]
    s = _clean_answer(s)
    # Strip leading fillers only when something remains after them.
    while s:
        m = _FILLER_RE.match(s)
        if not m:
            break
        s = s[m.end():].strip()
        s = _clean_answer(s)
    return s


def _clean_answer(s: str) -> str:
    s = s.strip().strip("\"'`").strip()
    s = s.splitlines()[0].strip() if s else s
    s = re.sub(r"\s+", " ", s)
    s = s.rstrip(" .;:")
    return s


def _clip_conf(n: int) -> Optional[int]:
    if 0 <= n <= 100:
        return n
    return None


def _parse_confidence(raw: str) -> Optional[int]:
    c = CONF_RE.search(raw)
    if c:
        return _clip_conf(int(c.group(1)))
    c2 = CONF_FALLBACK_RE.search(raw)
    if c2:
        return _clip_conf(int(c2.group(1)))
    return None


def _is_confidence_line(s: str) -> bool:
    """True for a line that is *only* a confidence report (never an answer).

    "CONFIDENCE: 90" and "I am 100% confident in this answer." qualify.
    "I am 100% confident that a right angle is 90 degrees." does *not*:
    the original first-line fallback must still see that sentence.
    """
    t = s.strip()
    if not t:
        return False
    if re.match(r"(?i)^(my\s+)?(confidence|conf)\b", t):
        return True
    if _PURE_CONF_UTTERANCE_RE.match(t):
        return True
    return False


def _line_at(raw: str, pos: int) -> str:
    start = raw.rfind("\n", 0, pos) + 1
    end = raw.find("\n", pos)
    if end < 0:
        end = len(raw)
    return raw[start:end]


def _is_short_equals_line(line: str) -> bool:
    """Accept '17 + 8 = 25', reject a multi-step working paragraph."""
    s = line.strip()
    if not s:
        return False
    if len(s.split()) > _MAX_EQUALS_LINE_WORDS:
        return False
    return True


def _legacy_first_line(raw: str) -> Optional[str]:
    # Same skip rule as the original parser: only lines starting with
    # confidence/conf, so a factual sentence that happens to mention
    # confidence is still used as a fallback answer.
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if re.match(r"(?i)^(confidence|conf)\b", s):
            continue
        answer = _clean_answer(re.sub(r"(?i)^(final\s+)?answer\s*[:\-]\s*", "", s))
        return answer or None
    return None


def _first_bare_line(raw: str) -> Optional[str]:
    """First short, non-sentence, non-confidence line — a bare answer like '25'.

    The first line is used, not the last: an unlabeled second number
    (e.g. ``999\\n100``) is often a confidence with a missing label, and
    taking it would invent a flip. Last-wins applies to explicit
    statements (ANSWER: / the answer is / X = value) only. A short bare
    line *after* a long sentence (``...rating.\\n\\n0``) is still found,
    because the sentence is not bare.
    """
    for line in raw.splitlines():
        s = line.strip()
        if not s or _is_confidence_line(s):
            continue
        s = re.sub(r"(?i)^(final\s+)?answer\s*[:\-]\s*", "", s)
        s = _clean_answer(s)
        if not s:
            continue
        if EQUALS_RE.search(s):
            continue
        if _HEDGE_START_RE.match(s):
            continue
        words = s.split()
        if len(words) > _MAX_BARE_WORDS:
            continue
        # Reject obvious sentences ("A hexagon has 6 sides", "144 divided by 12 is 12").
        if re.search(r"(?i)\b(is|are|has|have|was|were|consists|equals|equal)\b", s):
            continue
        return s
    return None
