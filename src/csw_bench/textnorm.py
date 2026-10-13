"""Shared by scoring (matching responses) and the schema (rejecting items whose members
collapse together under it). Lives apart from both so neither imports the other.
"""

from __future__ import annotations

import re
import unicodedata


def normalize(text: str) -> str:
    """Casefold, strip diacritics, collapse punctuation and whitespace runs to single
    spaces. Scoring compares normalized forms so that orthographic noise in a response
    -- quotes, list markers, a dropped accent -- does not read as a wrong answer.
    """
    folded = unicodedata.normalize("NFKD", text.casefold())
    stripped = "".join(c for c in folded if not unicodedata.combining(c))
    despaced = re.sub(r"[^\w\s]", " ", stripped)
    return re.sub(r"\s+", " ", despaced).strip()


def tokenize(text: str) -> list[str]:
    return normalize(text).split()
