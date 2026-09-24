"""Evidence-grounded public score policy for fact-check claims."""

from typing import Literal


ScoreBand = Literal["verified", "mostly_true", "neutral", "mostly_false", "false"]

SCORE_LABELS: dict[ScoreBand, str] = {
    "verified": "검증된 사실",
    "mostly_true": "대체적으로 사실",
    "neutral": "중립(검증되지 않음)",
    "mostly_false": "대체적으로 거짓",
    "false": "거짓",
}


def score_band(score: int) -> ScoreBand:
    """Return the public band for an inclusive 0–100 score."""
    if score >= 80:
        return "verified"
    if score >= 60:
        return "mostly_true"
    if score >= 40:
        return "neutral"
    if score >= 20:
        return "mostly_false"
    return "false"


def score_label(score: int) -> str:
    return SCORE_LABELS[score_band(score)]


def normalize_fact_score(verdict_code: str, requested_score: int) -> int:
    """Preserve the model's reasoned score, clamped only to the 0-100 range.

    The verdict no longer reshapes the score: the LLM judges certainty from
    the evidence and the server keeps its judgment verbatim. Band and label
    are derived from the preserved score for display. The verdict argument
    stays for call-site compatibility.
    """
    return max(0, min(100, int(requested_score)))


def default_fact_score(verdict_code: str) -> int:
    """Supply a compatible score when an older result omits the new field."""
    return {
        "mostly_supported": 80,
        "partially_supported": 70,
        "contradicted": 20,
    }.get(verdict_code, 50)
