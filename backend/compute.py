"""Deterministic arithmetic for verification; the model must not compute."""
import re

_NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
_UNIT = r"(?:[천만억조][ \t]*)?(?:원|달러|명|개|건)"
_CHANGE = re.compile(
    rf"(?<![A-Za-z\d.,+\-−])(?P<old>{_NUMBER.pattern})[ \t]*(?P<old_unit>{_UNIT})[ \t]*"
    r"(?P<relation>에서|→|->)[ \t]*"
    rf"(?P<new>{_NUMBER.pattern})[ \t]*(?P<new_unit>{_UNIT})"
)
_MIN_YEAR = 1900
_MAX_YEAR = 2100


def extract_numbers(text: str) -> list[float]:
    """Skip possible years, but retain numbers with explicit measurement units."""
    values: list[float] = []
    if not isinstance(text, str):
        return values
    for match in _NUMBER.finditer(text):
        raw = match.group(0).replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            continue
        if (
            value.is_integer() and _MIN_YEAR <= int(value) <= _MAX_YEAR
            and not re.match(rf"[ \t]*{_UNIT}", text[match.end():])
        ):
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
    """Compute explicit directed changes in the same unit; skip ambiguous pairs."""
    computations: list[dict[str, object]] = []
    if not isinstance(quote, str):
        return computations
    for match in _CHANGE.finditer(quote):
        if quote[:match.start()].rstrip().endswith(tuple("+-−~～/／")):
            continue
        suffix = quote[match.end():]
        if match["relation"] == "에서":
            if not re.match(r"[ \t]*(?:으로|로)", suffix):
                continue
        elif suffix and (
            not (suffix[0].isspace() or suffix[0] in ".!?;," or suffix.startswith(("으로", "로")))
            or re.match(r"\s*(?:[+\-−~～/／]|부터|까지|사이)", suffix)
        ):
            continue
        if re.sub(r"\s+", "", match["old_unit"]) != re.sub(r"\s+", "", match["new_unit"]):
            continue
        old = float(match["old"].replace(",", ""))
        new = float(match["new"].replace(",", ""))
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
