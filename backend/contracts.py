"""Validated Python representation of the public True or Not result contract."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


VerdictCode = Literal[
    "mostly_supported",
    "partially_supported",
    "missing_context",
    "conflicting_sources",
    "insufficient_evidence",
    "not_checkable",
    "contradicted",
]

EvidenceRelation = Literal["supports", "contradicts", "context"]
ClaimKind = Literal["fact", "opinion", "prediction", "unclear"]
ClaimTone = Literal["positive", "negative", "neutral"]
AccessStatus = Literal["verified", "unavailable"]
Reasoning = Literal["max", "high"]


class _ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class FactSource(_ContractModel):
    id: str = Field(min_length=1, max_length=100)
    url: str = Field(min_length=1, max_length=2048)
    title: str = Field(min_length=1, max_length=300)
    publisher: str = Field(min_length=1, max_length=300)
    publishedAt: str | None
    retrievedAt: str = Field(min_length=1, max_length=100)
    accessStatus: AccessStatus
    sourceType: str = Field(min_length=1, max_length=100)
    originGroupId: str | None


class FactEvidence(_ContractModel):
    id: str = Field(min_length=1, max_length=100)
    claimId: str = Field(min_length=1, max_length=100)
    sourceId: str = Field(min_length=1, max_length=100)
    quote: str = Field(min_length=1, max_length=2_000)
    quoteVerified: Literal[True]
    relation: EvidenceRelation


class FactClaim(_ContractModel):
    id: str = Field(min_length=1, max_length=100)
    quote: str = Field(min_length=1, max_length=12_000)
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    kind: ClaimKind
    verdictCode: VerdictCode
    verdict: str = Field(min_length=1, max_length=100)
    tone: ClaimTone
    summary: str = Field(min_length=1, max_length=2_000)
    confirmed: list[str] = Field(max_length=5)
    unresolved: list[str] = Field(max_length=5)
    warnings: list[str] = Field(max_length=5)
    evidenceIds: list[str] = Field(max_length=6)

    @model_validator(mode="after")
    def validate_offsets(self):
        if self.end < self.start:
            raise ValueError("Claim end offset must not precede start offset")
        return self


class FactCheckResult(_ContractModel):
    text: str = Field(min_length=1, max_length=12_000)
    focus: str = Field(max_length=500)
    demo: Literal[False]
    model: str = Field(min_length=1, max_length=100)
    reasoning: Reasoning
    checkedAt: str = Field(min_length=1, max_length=100)
    claims: list[FactClaim] = Field(max_length=3)
    sources: list[FactSource] = Field(max_length=6)
    evidence: list[FactEvidence] = Field(max_length=18)
    warnings: list[str] = Field(max_length=8)

    @model_validator(mode="after")
    def validate_cross_references(self):
        claims = {claim.id: claim for claim in self.claims}
        sources = {source.id: source for source in self.sources}
        evidence_by_id: dict[str, FactEvidence] = {}
        text_bytes = self.text.encode("utf-16-le", errors="surrogatepass")
        text_units = len(text_bytes) // 2

        if len(claims) != len(self.claims) or len(sources) != len(self.sources):
            raise ValueError("Duplicate claim or source id")

        for claim in self.claims:
            if claim.kind in {"opinion", "prediction"} and claim.verdictCode != "not_checkable":
                raise ValueError("Opinion and prediction claims must be not_checkable")
            if claim.end > text_units:
                raise ValueError("Claim offset exceeds input text")
            quoted = text_bytes[claim.start * 2:claim.end * 2].decode(
                "utf-16-le", errors="surrogatepass"
            )
            if quoted != claim.quote:
                raise ValueError("Claim quote does not match its offsets")

        for evidence in self.evidence:
            if evidence.id in evidence_by_id:
                raise ValueError("Duplicate evidence id")
            source = sources.get(evidence.sourceId)
            if evidence.claimId not in claims or source is None:
                raise ValueError("Evidence references an unknown claim or source")
            if source.accessStatus != "verified":
                raise ValueError("Evidence references an unavailable source")
            evidence_by_id[evidence.id] = evidence

        for claim in self.claims:
            if len(set(claim.evidenceIds)) != len(claim.evidenceIds):
                raise ValueError("Duplicate evidence link")
            for evidence_id in claim.evidenceIds:
                evidence = evidence_by_id.get(evidence_id)
                if evidence is None or evidence.claimId != claim.id:
                    raise ValueError("Claim evidence link is inconsistent")

        linked_ids = {evidence_id for claim in self.claims for evidence_id in claim.evidenceIds}
        if linked_ids != set(evidence_by_id):
            raise ValueError("Unlinked evidence is not allowed")
        return self


class FactCheckResponse(_ContractModel):
    result: FactCheckResult


class AgentStatus(_ContractModel):
    configured: bool
    workflowReady: bool
    engine: Literal["langgraph"] = "langgraph"
    model: str | None
    reasoning: Reasoning | None
    webSearch: bool
    phase: Literal["api-foundation", "workflow-ready"]
