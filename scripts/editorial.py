"""Deterministic editorial checks for the always-on anti-AI markers in SKILL.md.

Code (fenced blocks, inline spans), quotations (blockquotes, quoted strings)
and machine output under an output schema are exempt, as the skill allows.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "flow-lean" / "SKILL.md"
EM_DASH = "—"
# Plural and adverb inflections of the listed tokens, nothing broader: "defis" must not match "defiscalisation".
INFLECTIONS = r"(?:s|e|es|le|les|aux|ly|ness)?"

_FENCE = re.compile(r"^(`{3,}|~{3,}).*?^\1[ \t]*$", re.MULTILINE | re.DOTALL)
_INLINE_CODE = re.compile(r"(`+)(?!`).+?(?<!`)\1", re.DOTALL)
_BLOCKQUOTE = re.compile(r"^[ \t]*>.*$", re.MULTILINE)
_QUOTED = re.compile(r"\"[^\"\n]*\"|“[^”\n]*”|«[^»\n]*»")


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


def banned_tokens(skill: Path = SKILL) -> list[str]:
    """Read the banned-token block so the check and the skill share one list."""
    match = re.search(r"Banned tokens:\s*```[^\n]*\n(.*?)```", skill.read_text(encoding="utf-8"), re.DOTALL)
    if not match:
        raise ValueError(f"{skill}: no fenced block after 'Banned tokens:'")
    return [_fold(token.strip()) for token in re.split(r"[,\n]", match.group(1)) if token.strip()]


def prose(text: str) -> str:
    for pattern in (_FENCE, _INLINE_CODE, _BLOCKQUOTE, _QUOTED):
        text = pattern.sub(" ", text)
    return text


def is_schema_output(text: str) -> bool:
    try:
        return isinstance(json.loads(text), (dict, list))
    except json.JSONDecodeError:
        return False


def check(text: str, tokens: list[str], output_schema: bool = False) -> dict[str, Any]:
    if output_schema or is_schema_output(text):
        return {"exempt": "output-schema", "em_dashes": 0, "banned": []}
    body = prose(text)
    folded = _fold(body)
    # One alternation, so "robuste" counts once although both "robuste" and "robust" + "e" match it.
    alternatives = "|".join(re.escape(token) for token in tokens)
    banned = re.findall(rf"\b(?:{alternatives}){INFLECTIONS}\b", folded)
    return {"exempt": None, "em_dashes": body.count(EM_DASH), "banned": banned}
