"""Deterministic arithmetic for verification; the model must not compute."""
import re

_NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
_MIN_YEAR = 1900
_MAX_YEAR = 2100


def extract_numbers(text: str) -> list[float]:
    """Parse plain numbers, skipping 4-digit years that skew pairing."""
    values: list[float] = []
    if not isinstance(text, str):
        return values
    for match in _NUMBER.finditer(text):
        raw = match.group(0).replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            continue
        if value.is_integer() and _MIN_YEAR <= int(value) <= _MAX_YEAR:
            continue
        values.append(value)
    return values


def percent_change(old: float, new: float) -> float | None:
    """Return the rounded percent change from old to new, or None."""
    if not isinstance(old, (int, float)) or not isinstance(new, (int, float)):
        return None
    if isinstance(old, bool) or isinstance(new, bool) or old == 0:
        return None
    return round((new - old) / old * 100, 1)


def claim_computations(quote: str, limit: int = 3) -> list[dict[str, object]]:
    """Pair adjacent numbers in a claim into checkable computations."""
    numbers = extract_numbers(quote)
    computations: list[dict[str, object]] = []
    for old, new in zip(numbers, numbers[1:]):
        percent = percent_change(old, new)
        if percent is None:
            continue
        computations.append({
            "expression": "%g→%g" % (old, new),
            "percent": percent,
        })
        if len(computations) >= limit:
            break
    return computations
