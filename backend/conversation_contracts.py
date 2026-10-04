"""대화 저장 전용 계약입니다. 외부 원문과 공급자 메타데이터는 제외합니다."""
from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from contracts import FactClaim, FactCheckAnswer, FactCheckResult, Reasoning


SOURCE_FIELDS = ('id', 'url', 'title', 'publisher', 'publishedAt', 'retrievedAt', 'accessStatus', 'sourceType', 'originGroupId')
EVIDENCE_FIELDS = ('id', 'claimId', 'sourceId', 'quote', 'quoteTranslation', 'quoteVerified', 'relation')


class StoredSnapshot(BaseModel):
    model_config = ConfigDict(extra='ignore')
    text: str
    focus: str
    checkedAt: str
    model: str
    reasoning: Reasoning
    scoreMode: Literal['jev','claims'] | None = None
    claims: list[FactClaim]
    sources: list[dict]
    evidence: list[dict]
    warnings: list[str]
    answer: FactCheckAnswer = Field(default_factory=lambda: FactCheckAnswer(status='insufficient_evidence', overview=None, sections=[], conclusion=None, model=None, reasoning=None))

    @model_validator(mode='after')
    def sanitize(self):
        sources = [{key: source[key] for key in SOURCE_FIELDS if key in source} for source in self.sources]
        evidence = [{key: item[key] for key in EVIDENCE_FIELDS if key in item} for item in self.evidence]
        full = FactCheckResult.model_validate(dict(text=self.text, focus=self.focus, demo=False, checkedAt=self.checkedAt, model=self.model, reasoning=self.reasoning, claims=self.claims, sources=sources, evidence=evidence, warnings=self.warnings, answer=self.answer))
        clean = full.model_dump(mode='json')
        self.sources = [{key: source[key] for key in SOURCE_FIELDS} for source in clean['sources']]
        self.evidence = [{key: item[key] for key in EVIDENCE_FIELDS if key in item} for item in clean['evidence']]
        return self


class StorageConsent(BaseModel):
    storageConsent: Literal[True]

    @field_validator('storageConsent',mode='before')
    @classmethod
    def explicit_consent(cls,value):
        if value is not True:
            raise ValueError('INVALID_REQUEST')
        return value


class ConversationCreate(StorageConsent):
    model_config = ConfigDict(extra='forbid')
    storageConsent: Literal[True]
    createRequestId: UUID
    title: str = Field(min_length=1, max_length=80)


class MessageCreate(StorageConsent):
    model_config = ConfigDict(extra='forbid')
    storageConsent: Literal[True]
    requestId: UUID
    role: Literal['user', 'assistant']
    content: str = Field(min_length=1, max_length=60000)
    status: Literal['completed', 'failed', 'cancelled']
    snapshot: StoredSnapshot | None = None

    @model_validator(mode='after')
    def limits(self):
        if self.role == 'user' and (len(self.content) > 12000 or self.snapshot is not None):
            raise ValueError('INVALID_REQUEST')
        if self.snapshot is not None and self.status != 'completed':
            raise ValueError('INVALID_REQUEST')
        return self


class Conversation(BaseModel):
    id: UUID
    title: str
    createdAt: datetime
    updatedAt: datetime


class StoredMessage(BaseModel):
    id: UUID
    sequence: int
    requestId: UUID
    role: Literal['user', 'assistant']
    content: str
    status: Literal['completed', 'failed', 'cancelled']
    snapshot: StoredSnapshot | None
    createdAt: datetime


class ConversationPage(BaseModel):
    items: list[Conversation]
    nextCursor: str | None


class MessagePage(BaseModel):
    conversation: Conversation
    messages: list[StoredMessage]
    beforeSequence: int | None
