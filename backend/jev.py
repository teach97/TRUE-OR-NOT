"""Jev (TypeSafe System One) verdicts through Vercel AI Gateway.

The gateway API key stays server-side; it never leaves this module.
Contract: POST /typesafe/v1/systemone with model/state/questions,
answers keyed by question id. See https://docs.typesafe.ai/api.md.
"""
from typing import Any

import httpx

JEV_MODEL = "typesafe-ai/jev"
JEV_SYSTEMONE_URL = "https://ai-gateway.vercel.sh/typesafe/v1/systemone"
JEV_TIMEOUT_SECONDS = 60.0
JEV_MIN_CONFIDENCE = 0.5
JEV_MAX_EVIDENCE_CHARS = 4_000
JEV_SCORE_LEVELS = 5

_VERDICT_OPTIONS = (
    "mostly_supported",
    "partially_supported",
    "contradicted",
    "insufficient_evidence",
)

_VERDICT_CRITERIA = {
    "mostly_supported": "The evidence directly establishes the claim with no material gaps.",
    "partially_supported": "The evidence supports parts of the claim but leaves material gaps.",
    "contradicted": "The evidence directly refutes the claim.",
    "insufficient_evidence": "The evidence neither establishes nor refutes the claim, or no usable evidence was supplied.",
}

_STRENGTH_LEVELS = [
    "No support at all in the evidence",
    "Weak or indirect support only",
    "Partial support with gaps",
    "Strong support with minor gaps",
    "Fully established by the evidence",
]


class JevError(RuntimeError):
    """A Jev evaluation failed; the caller escalates to the LLM path."""

    def __init__(self, message: str, *, code: str = "AGENT_FAILED"):
        super().__init__(message)
        self.code = code


def _require_answer(answers: Any, claim_id: str, question_id: str) -> dict[str, Any]:
    if not isinstance(answers, dict):
        raise JevError("Jev answers must be a map", code="BAD_RESPONSE")
    answer = answers.get(question_id)
    if not isinstance(answer, dict):
        raise JevError(f"Jev answer missing for claim {claim_id}", code="BAD_RESPONSE")
    return answer


def _parse_verdict(answer: dict[str, Any], claim_id: str) -> tuple[str, float]:
    if answer.get("type") != "choice":
        raise JevError(f"Jev verdict has wrong type for claim {claim_id}", code="BAD_RESPONSE")
    choice = answer.get("choice")
    if choice not in _VERDICT_OPTIONS:
        raise JevError(f"Jev verdict option invalid for claim {claim_id}", code="BAD_RESPONSE")
    confidence = answer.get("confidence", 1.0)
    if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
        raise JevError(f"Jev verdict confidence invalid for claim {claim_id}", code="BAD_RESPONSE")
    return choice, float(confidence)


def _parse_strength(answer: dict[str, Any], claim_id: str) -> tuple[int, float]:
    if answer.get("type") != "score":
        raise JevError(f"Jev strength has wrong type for claim {claim_id}", code="BAD_RESPONSE")
    score = answer.get("score")
    if not isinstance(score, (int, float)) or not 0.0 <= score <= float(JEV_SCORE_LEVELS - 1):
        raise JevError(f"Jev strength out of range for claim {claim_id}", code="BAD_RESPONSE")
    confidence = answer.get("confidence", 1.0)
    if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
        raise JevError(f"Jev strength confidence invalid for claim {claim_id}", code="BAD_RESPONSE")
    fact_score = round(score / (JEV_SCORE_LEVELS - 1) * 100)
    return max(0, min(100, fact_score)), float(confidence)


async def evaluate_claims_jev(
    claims: list[dict[str, Any]],
    evidence_by_claim: dict[str, str],
    *,
    client: httpx.AsyncClient,
    api_key: str | None,
) -> list[dict[str, Any]]:
    """Judge each claim with one verdict Choice and one strength Score.

    Returns [{claimId, verdictCode, factScore}]. Raises JevError on transport
    failure, malformed output, or confidence below threshold so the caller
    can escalate to the LLM verification path.
    """
    if not api_key or not api_key.strip():
        raise JevError("Jev gateway key is not configured", code="NOT_CONFIGURED")
    results: list[dict[str, Any]] = []
    for claim in claims:
        claim_id = claim.get("id", "")
        state = {
            "claim": claim.get("quote", ""),
            "kind": claim.get("kind", ""),
            "evidence": evidence_by_claim.get(claim_id, "")[:JEV_MAX_EVIDENCE_CHARS],
        }
        payload = {
            "model": JEV_MODEL,
            "state": state,
            "questions": {
                "verdict": {
                    "type": "choice",
                    "instructions": (
                        "Given the claim and the evidence quotes, which verdict fits best? "
                        "Judge only what the supplied evidence establishes."
                    ),
                    "criteria": _VERDICT_CRITERIA,
                },
                "strength": {
                    "type": "score",
                    "instructions": (
                        "How strongly does the supplied evidence establish "
                        "the claim exactly as stated?"
                    ),
                    "criteria": _STRENGTH_LEVELS,
                },
            },
        }
        try:
            response = await client.post(
                JEV_SYSTEMONE_URL,
                json=payload,
                headers={"Authorization": f"Bearer {api_key.strip()}"},
                timeout=JEV_TIMEOUT_SECONDS,
            )
        except (httpx.HTTPError, TimeoutError) as exc:
            raise JevError(f"Jev transport failed for claim {claim_id}", code="GATEWAY_ERROR") from exc
        if response.status_code != 200:
            raise JevError(f"Jev request failed for claim {claim_id}: HTTP {response.status_code}", code="GATEWAY_ERROR")
        try:
            data = response.json()
        except ValueError as exc:
            raise JevError(f"Jev response is not JSON for claim {claim_id}", code="GATEWAY_ERROR") from exc
        answers = data.get("answers") if isinstance(data, dict) else None
        verdict_code, verdict_conf = _parse_verdict(
            _require_answer(answers, claim_id, "verdict"), claim_id
        )
        fact_score, strength_conf = _parse_strength(
            _require_answer(answers, claim_id, "strength"), claim_id
        )
        if min(verdict_conf, strength_conf) < JEV_MIN_CONFIDENCE:
            raise JevError(f"Jev confidence too low for claim {claim_id}", code="LOW_CONFIDENCE")
        results.append({
            "claimId": claim_id,
            "verdictCode": verdict_code,
            "factScore": fact_score,
        })
    return results
