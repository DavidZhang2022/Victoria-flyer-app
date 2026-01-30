from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional, Tuple

LB_TO_G = 453.59237
OZ_TO_G = 28.349523125
L_TO_ML = 1000.0

@dataclass
class ParsedQty:
    qty: float
    unit: str  # "g" / "ml" / "each"

def _to_float(s: str) -> Optional[float]:
    try:
        return float(s)
    except Exception:
        return None

def parse_price_text(text: str | None) -> Tuple[Optional[float], Optional[int], Optional[float]]:
    if not text:
        return None, None, None
    t = str(text).strip().lower()

    m = re.search(r"(\d+)\s*(for|/)\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)", t)
    if m:
        qty = int(m.group(1))
        total = _to_float(m.group(3))
        if total is None or qty <= 0:
            return None, None, None
        return round(total / qty, 4), qty, float(total)

    m = re.search(r"\$?\s*([0-9]+(?:\.[0-9]{1,2})?)", t)
    if m:
        return _to_float(m.group(1)), None, None

    return None, None, None

def parse_quantity_text(text: str | None) -> Optional[ParsedQty]:
    if not text:
        return None
    t = str(text).strip().lower().replace("×", "x")

    if any(k in t for k in ["each", "ea", "per item", "per each", "per ea"]):
        return ParsedQty(1.0, "each")

    mx = re.search(r"(\d+)\s*x\s*([0-9]+(?:\.[0-9]+)?)\s*(kg|g|lb|oz|l|ml)\b", t)
    if mx:
        count = int(mx.group(1))
        amount = _to_float(mx.group(2))
        unit = mx.group(3)
        if amount is None:
            return None
        return _normalize(amount * count, unit)

    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(kg|g|lb|oz|l|ml)\b", t)
    if m:
        amount = _to_float(m.group(1))
        unit = m.group(2)
        if amount is None:
            return None
        return _normalize(amount, unit)

    return None

def _normalize(amount: float, unit: str) -> Optional[ParsedQty]:
    unit = unit.lower()
    if unit == "kg":
        return ParsedQty(amount * 1000.0, "g")
    if unit == "g":
        return ParsedQty(amount, "g")
    if unit == "lb":
        return ParsedQty(amount * LB_TO_G, "g")
    if unit == "oz":
        return ParsedQty(amount * OZ_TO_G, "g")
    if unit == "l":
        return ParsedQty(amount * L_TO_ML, "ml")
    if unit == "ml":
        return ParsedQty(amount, "ml")
    return None

def compute_unit_price(price: float | None, parsed: ParsedQty | None) -> tuple[float | None, str | None]:
    if price is None or parsed is None or parsed.qty <= 0:
        return None, None
    if parsed.unit == "g":
        return round(price / (parsed.qty / 100.0), 6), "$/100g"
    if parsed.unit == "ml":
        return round(price / (parsed.qty / 100.0), 6), "$/100ml"
    if parsed.unit == "each":
        return round(price, 6), "$/each"
    return None, None
