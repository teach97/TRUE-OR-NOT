"""Fact score policy tests; no provider calls."""

import pytest

from scoring import normalize_fact_score, score_band, score_label


@pytest.mark.parametrize(
    ("score", "band", "label"),
    [
        (0, "false", "거짓"),
        (19, "false", "거짓"),
        (20, "mostly_false", "대체적으로 거짓"),
        (39, "mostly_false", "대체적으로 거짓"),
        (40, "neutral", "중립(검증되지 않음)"),
        (59, "neutral", "중립(검증되지 않음)"),
        (60, "mostly_true", "대체적으로 사실"),
        (79, "mostly_true", "대체적으로 사실"),
        (80, "verified", "검증된 사실"),
        (100, "verified", "검증된 사실"),
    ],
)
def test_score_boundaries_have_stable_public_labels(score, band, label):
    assert score_band(score) == band
    assert score_label(score) == label


@pytest.mark.parametrize(
    ("verdict", "requested", "expected"),
    [
        ("mostly_supported", 70, 80),
        ("mostly_supported", 96, 96),
        ("partially_supported", 95, 79),
        ("partially_supported", 61, 61),
        ("contradicted", 50, 39),
        ("contradicted", 8, 8),
        ("missing_context", 95, 50),
        ("conflicting_sources", 10, 50),
        ("insufficient_evidence", 2, 50),
        ("not_checkable", 100, 50),
    ],
)
def test_grounding_normalizes_scores_to_the_verified_verdict(verdict, requested, expected):
    assert normalize_fact_score(verdict, requested) == expected
