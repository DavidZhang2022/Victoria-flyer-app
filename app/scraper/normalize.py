from __future__ import annotations
import re

STOP_WORDS = {"fresh", "new", "large", "medium", "small", "assorted", "select", "premium"}

def normalize_name(raw: str) -> str:
    s = (raw or "").lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    tokens = [t for t in s.split() if t and t not in STOP_WORDS]
    return " ".join(tokens[:16])
