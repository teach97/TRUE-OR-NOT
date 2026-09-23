# Grounded Answer Synthesis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Add a fifth LLM synthesis stage that produces a Korean, source-grounded overview, evidence-backed perspectives, uncertainty, conclusion, and clickable inline citations without changing claim verdicts.

**Architecture:** Keep extraction, search, reading, and claim verification intact, then pass only readable verified non-YouTube source text plus verified claim/evidence context to a separate structured-output call. Ground every generated citation against the exact source body before accepting it; use the existing provider order and return an explicit insufficient-evidence answer if no source or successful provider is available. Extend the result contract and NDJSON stage stream, then render the structured answer in the chat while retaining existing detailed claim and evidence panels.

**Tech Stack:** Python 3.11+, FastAPI, LangGraph, Pydantic 2, httpx, pytest; Next.js 16.3.5, React 19, TypeScript, Node 24 native test runner.

**Spec:** docs/superpowers/specs/2026-09-23-grounded-answer-synthesis-design.md

## Global Constraints

- 종합 단계에는 sourceTexts가 존재하고 accessStatus=verified인 출처만 근거 후보로 전달합니다. 검색 스니펫, 출처 제목만 있는 YouTube 결과, YouTube 제목·공개 댓글은 종합 근거에서 제외합니다.
- 모든 실질적 답변 블록은 하나 이상의 출처 인용을 포함해야 합니다. 각 인용의 sourceId는 실제 출처에 연결되어야 하고 quote는 해당 출처 본문에서 정확히 일치하는 연속 문자열이어야 합니다.
- 인용이 없는 단정, 존재하지 않는 출처 ID, 원문과 일치하지 않는 인용은 통과시키지 않습니다. 기존 제공자 폴백을 통해 재시도하고, 모든 제공자가 실패하면 검증된 기존 결과를 보존한 채 insufficient_evidence 답변으로 마무리합니다.
- 예측 답변은 전망·조건·불확실성을 서술하며 사실의 참·거짓으로 재분류하지 않습니다. 예측 확률이나 전문가 다수 의견을 원문이 명시하지 않으면 만들어 내지 않습니다.
- 상반된 관점은 실제 수집 원문이 뒷받침할 때만 각각 표시합니다. 찬반을 형식적으로 같은 수로 맞추거나 출처 개수만으로 합의를 추론하지 않습니다.
- 기존 주장 점수, 판정, 정확 인용, 경고를 대체하지 않습니다. 종합 답변이 실패해도 확인된 주장별 판정은 가능한 한 반환합니다.
- 답변 문단 최대 1,200자, 섹션 최대 4개, 섹션별 항목 최대 3개, 문단별 인용 최대 3개, 인용문 최대 2,000자입니다.
- 종합 LLM 호출에 기존 사용자 동의 범위와 서버 측 provider 키 설정을 적용합니다. 새 키나 저장소는 추가하지 않습니다.
- 검증 원문과 종합 답변을 새로 영속 저장하지 않습니다.
- 비목표: Google 자연 검색 SERP의 직접 스크래핑 또는 순위 API 도입, YouTube 자막·영상·답글 수집 또는 공개 댓글을 사실 근거·LLM 입력으로 사용하는 일, 새로운 provider 도입.

## Review Focus

- 원문 미수집/접근 불가: 검색 스니펫이나 제목만으로 종합하지 않고 provider를 호출하지 않으며, test_synthesize_answer_skips_provider_without_eligible_source_text에서 고정합니다.
- 출처 ID 또는 인용문 위조: 모델이 s-missing 또는 원문에 없는 문장을 반환하면 그 provider 응답 전체를 거부하고 다음 provider로 넘어가는 test_invalid_citation_retries_next_provider에서 고정합니다.
- YouTube 혼입: 본문 접근 상태가 verified여도 YouTube 제목·댓글은 입력에서 제외하는 test_synthesis_prompt_excludes_youtube_metadata_and_comments에서 고정합니다.
- 한쪽 근거를 합의/확률로 과장: 예측은 not_checkable로 유지하고 출처에 없는 확률·전문가 합의를 만들지 말라는 지침과 AGI 예측 mock 회귀를 test_forecast_synthesis_preserves_prediction_and_citations에 고정합니다.
- 모든 provider의 실패: 기존 검증 claim/evidence는 보존하고 모델 메타데이터가 null인 안전한 insufficient_evidence를 반환하는 test_all_synthesis_providers_failing_preserves_verified_result에서 고정합니다.

## File Map

- Create backend/answer_synthesis.py: answer block construction, eligible-source projection, synthesis prompt, provider response parsing, and exact quote/source grounding.
- Modify backend/contracts.py: strict Pydantic answer/citation/section contracts and result cross-reference checks.
- Modify backend/workflow.py and backend/runtime.py: inject a fifth synthesis stage, retain claim-verification metadata, and assemble the public result only after synthesis or its safe fallback.
- Modify backend/streaming.py: expose ordered synthesizing progress and emit only the final five-stage result.
- Modify backend/tests/test_answer_synthesis.py (new), test_contracts.py, test_workflow.py, test_runtime_assembly.py, test_streaming.py, test_execution.py, test_read_graph.py, backend/tests/cancellation_probe_app.py, and backend/tests/recovery_probe_app.py.
- Modify app/lib/fact-check-contract.ts and app/components/fact-check-client.ts: mirror response types, the fifth stage, and bounded answer validation.
- Modify app/components/fact-check-reply.ts and app/components/fact-check-dashboard.tsx: carry a structured answer in chat and render citation chips linked to verified source URLs.
- Modify app/globals.css: style answer headings, sections, uncertainty/conclusion and accessible inline citation chips.
- Modify app/lib/server/agent.ts: satisfy the shared required response type with an explicit insufficient-evidence answer; do not add an unapproved local LLM call.
- Modify the related Node tests: app/components/fact-check-client.test.mjs, fact-check-reply.test.mjs, and app/lib/server/agent.test.mjs.
- Modify HANDOFF.md: record stage 5, actual boundaries, test outcomes, and remaining provider/live-test caveats.

This is one vertical feature plan rather than independent backend/frontend plans: the new validated answer contract, stream event and renderer must land together for a usable result.

---

### Task 1: Define the validated answer contract

**Files:**
- Modify: backend/contracts.py
- Test: backend/tests/test_contracts.py

**Interfaces:**
- Produces AnswerCitation(sourceId: str, quote: str), AnswerBlock(text: str, citations: list[AnswerCitation]), AnswerSection(kind: Literal['supporting','counter','uncertainty','context'], title: str, items: list[AnswerBlock]), and FactCheckAnswer(status: Literal['grounded','insufficient_evidence'], overview: AnswerBlock | None, sections: list[AnswerSection], conclusion: AnswerBlock | None, model: str | None, reasoning: Reasoning | None).
- FactCheckResult.answer is always present in serialized output; its default factory is the safe insufficient-evidence answer for call sites that do not synthesize. grounded requires an overview and conclusion and at least one citation for every supplied block. insufficient_evidence has no sections and may omit overview/conclusion; the UI supplies fixed explanatory copy.
- Result-level citation references must point to existing verified, non-YouTube sources. Exact source-body matching is enforced by answer_synthesis.py because source text is deliberately not exposed in the public result.

- [ ] **Step 1: Write failing contract tests**

Assert the existing result_payload() is serialized with the safe insufficient answer by default. Add cases for a grounded answer with one s1 citation, a safe insufficient answer with null model/reasoning, and rejected grounded answers with no block citation, an unknown source ID, an unavailable source, a YouTube source, too many sections/items/citations, or text/quote over the design limits.

    payload = result_payload()
    payload["answer"] = {
        "status": "grounded",
        "overview": {"text": "AGI 전망은 아직 불확실합니다.", "citations": [
            {"sourceId": "s1", "quote": "Claim is supported."}
        ]},
        "sections": [],
        "conclusion": {"text": "확정할 수 없습니다.", "citations": [
            {"sourceId": "s1", "quote": "Claim is supported."}
        ]},
        "model": "gemini-3.8-flash",
        "reasoning": "high",
    }
    assert FactCheckResult.model_validate(payload).answer.status == "grounded"

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run from backend: uv run pytest -q tests/test_contracts.py
Expected: the new grounded fixture fails because answer is not yet in the contract; the pre-existing tests remain unchanged.

- [ ] **Step 3: Add strict models and result cross-reference validation**

Implement the named models with _ContractModel (extra='forbid', strict types), copy the numeric caps from the design, add answer: FactCheckAnswer to FactCheckResult with a default factory returning status='insufficient_evidence', overview=None, sections=[], conclusion=None, model=None, reasoning=None. Require citations on all grounded blocks, require grounded overview/conclusion, constrain insufficient answers to empty sections, and validate every citation source against FactCheckResult.sources with accessStatus == 'verified' and sourceType != '유튜브'.

    class AnswerCitation(_ContractModel):
        sourceId: str = Field(min_length=1, max_length=100)
        quote: str = Field(min_length=1, max_length=2_000)

    class AnswerBlock(_ContractModel):
        text: str = Field(min_length=1, max_length=1_200)
        citations: list[AnswerCitation] = Field(max_length=3)

    class AnswerSection(_ContractModel):
        kind: Literal["supporting", "counter", "uncertainty", "context"]
        title: str = Field(min_length=1, max_length=120)
        items: list[AnswerBlock] = Field(min_length=1, max_length=3)

    class FactCheckAnswer(_ContractModel):
        status: Literal["grounded", "insufficient_evidence"]
        overview: AnswerBlock | None
        sections: list[AnswerSection] = Field(max_length=4)
        conclusion: AnswerBlock | None
        model: str | None
        reasoning: Reasoning | None

        @model_validator(mode="after")
        def validate_answer_blocks(self):
            blocks = [block for block in (self.overview, self.conclusion) if block]
            blocks.extend(item for section in self.sections for item in section.items)
            if self.status == "grounded" and (
                self.overview is None or self.conclusion is None
                or any(not block.citations for block in blocks)
            ):
                raise ValueError("Grounded answers need cited overview and conclusion")
            if self.status == "insufficient_evidence" and self.sections:
                raise ValueError("Insufficient answers cannot assert evidence sections")
            return self

    class FactCheckResult(_ContractModel):
        answer: FactCheckAnswer = Field(default_factory=lambda: FactCheckAnswer(
            status="insufficient_evidence", overview=None, sections=[],
            conclusion=None, model=None, reasoning=None,
        ))

- [ ] **Step 4: Run the focused tests and confirm they pass**

Run from backend: uv run pytest -q tests/test_contracts.py
Expected: all contract tests pass, including the existing claim/evidence cross-reference checks.

- [ ] **Step 5: Commit the independently passing contract change**

Commit backend/contracts.py and backend/tests/test_contracts.py as feat: add grounded answer response contract.

### Task 2: Implement grounded synthesis and provider retry

**Files:**
- Create: backend/answer_synthesis.py
- Create: backend/tests/test_answer_synthesis.py
- Read before coding: backend/providers.py and backend/verification.py. Next.js documentation is not applicable to this Python-only task.

**Interfaces:**
- SynthesisDraft is the strict model-output schema and excludes server-owned model/reasoning metadata. eligible_sources(state: FactCheckState) -> list[dict[str, str]] selects at most the existing six sources with verified access, non-empty sourceTexts, and source type other than 유튜브; it sends each source body with its stable ID and display metadata, never snippets or YouTube metadata/comments.
- _SYNTHESIS_INSTRUCTIONS is a fixed prompt policy string: source text is untrusted evidence data, prediction claims remain forecasts, and absent opposing sources/explicit probabilities do not imply balance, consensus, or numeric odds.
- insufficient_answer() -> dict[str, object] returns the fixed empty fallback: status='insufficient_evidence', null overview/conclusion/model/reasoning, and empty sections.
- _synthesis_input(state: FactCheckState, sources: list[dict[str, str]]) -> dict[str, object] contains only the question/focus, extracted and verified claim context, and the bounded eligible source bodies.
- _validate_answer_grounding(draft: SynthesisDraft, sources: list[dict[str, str]]) -> None raises ProviderCallError if a block lacks a citation, a source ID is unknown, or its quote is not an exact substring of that source body.
- async synthesize_answer(state: FactCheckState, *, client: httpx.AsyncClient, provider: LLMProvider) -> dict[str, object] calls the existing request_structured with SynthesisDraft.model_json_schema(), validates the draft, grounds every citation, then attaches model/reasoning from the selected LLMProvider. Any malformed structure or invalid citation raises ProviderCallError.

- [ ] **Step 1: Add offline tests for source selection, prompt input and grounding**

Use httpx.MockTransport and fake structured responses. Cover exact valid quotes; fabricated quotes; unknown IDs; verified-but-empty source text; unavailable sources; YouTube bodies/title/comments; per-source 6,000-character excerpt bounds matching the existing verification input bound; a forecast claim that remains kind='prediction', verdictCode='not_checkable'; and an invalid first-provider citation followed by a valid next-provider response.

    result = await synthesize_answer(
        state, client=client,
        provider=LLMProvider("gemini", "gemini-3.8-flash", "high", "test-only"),
    )
    assert result["status"] == "grounded"
    assert result["overview"]["citations"][0]["quote"] in state["sourceTexts"]["s1"]

- [ ] **Step 2: Run the new tests and confirm they fail**

Run from backend: uv run pytest -q tests/test_answer_synthesis.py
Expected: FAIL because answer_synthesis does not yet exist.

- [ ] **Step 3: Implement the provider-independent source projection and synthesis call**

Define a strict structured response schema from SynthesisDraft so the model cannot choose provider metadata, call request_structured with a bounded output token count, and parse with Pydantic. Put source bodies in explicit untrusted-data fields and instruct the model not to follow instructions found inside them, not to invent consensus/probabilities or opposing views, and to preserve predictions as forecasts. Convert malformed structure or any citation-grounding failure to ProviderCallError so the existing Gemini 3.8 → Gemini 3.7 → GPT-6 Luna fallback can retry; attach the provider's actual model/reasoning after validation.

    from typing import Literal
    from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
    from contracts import AnswerBlock, AnswerSection, FactCheckAnswer

    class SynthesisDraft(BaseModel):
        model_config = ConfigDict(extra="forbid", strict=True)
        status: Literal["grounded"]
        overview: AnswerBlock
        sections: list[AnswerSection] = Field(max_length=4)
        conclusion: AnswerBlock

        @model_validator(mode="after")
        def require_block_citations(self):
            blocks = [self.overview, self.conclusion]
            blocks.extend(item for section in self.sections for item in section.items)
            if any(not block.citations for block in blocks):
                raise ValueError("Every grounded answer block needs a citation")
            return self

    eligible = eligible_sources(state)
    if not eligible:
        return insufficient_answer()
    raw = await request_structured(
        provider, client, instructions=_SYNTHESIS_INSTRUCTIONS,
        input_data=_synthesis_input(state, eligible),
        schema=SynthesisDraft.model_json_schema(), max_output_tokens=4_000,
    )
    try:
        draft = SynthesisDraft.model_validate_json(raw)
    except ValidationError:
        raise ProviderCallError("Invalid synthesis output") from None
    _validate_answer_grounding(draft, eligible)
    return FactCheckAnswer(**draft.model_dump(), model=provider.model,
                           reasoning=provider.reasoning).model_dump(mode="json")

- [ ] **Step 4: Run synthesis tests and provider regressions**

Run from backend: uv run pytest -q tests/test_answer_synthesis.py tests/test_providers.py tests/test_verification.py
Expected: all pass without real network calls; invalid first-provider grounding is rejected rather than exposed.

- [ ] **Step 5: Commit the independently passing synthesis module**

Commit backend/answer_synthesis.py and backend/tests/test_answer_synthesis.py as feat: synthesize answers from verified source text.

### Task 3: Wire the fifth graph stage and preserve safe results

**Files:**
- Modify: backend/workflow.py
- Modify: backend/runtime.py
- Modify: backend/tests/test_workflow.py, test_runtime_assembly.py, test_execution.py, test_read_graph.py, test_streaming.py
- Modify backend/tests/cancellation_probe_app.py and recovery_probe_app.py, which construct runtime adapters for cancellation/recovery checks

**Interfaces:**
- RuntimeAdapters has five explicit required stage callables: extract, search, read, verify, synthesize.
- build_workflow(*, extract: Stage, search: Stage, read: Stage, verify: Stage, synthesize: Stage) executes extracting → searching → reading → verifying → synthesizing.
- The synthesis update uses answer, answerModel, and answerReasoning; it does not overwrite the existing verification llmModel/llmReasoning used by top-level FactCheckResult.model/reasoning.
- build_fact_check_result(state, update, *, checked_at=None) merges update into graph state, reads claims/evidence from the verified state and answer from the synthesis update, and returns FactCheckResult; top-level model/reasoning continue to come from the verification state.
- Final assembly occurs in the runtime synthesis node after the fifth stage. If synthesis is skipped or exhausted, it assembles insufficient_answer() while retaining the already verified claims, evidence, warnings and verification provider metadata.

- [ ] **Step 1: Add failing graph/runtime tests**

Update graph order tests to require the fifth stage; add runtime assertions that answer provider metadata is separate from verification metadata and no verified source avoids a provider call. Add test_all_synthesis_providers_failing_preserves_verified_result to assert provider exhaustion still yields a contract-valid result preserving claim c1 and evidence e1. Add a synthesis-stage failure test proving the graph does not accidentally return the pre-synthesis intermediate result.

Update every explicit adapter constructor in test_workflow.py, test_runtime_assembly.py, test_execution.py, test_read_graph.py and test_streaming.py, plus cancellation_probe_app.py and recovery_probe_app.py, to inject an offline synthesis callable.

    assert seen == ["extracting", "searching", "reading", "verifying", "synthesizing"]
    assert parsed.result.model == "gpt-6-luna"
    assert parsed.result.answer.model == "gemini-3.8-flash"

- [ ] **Step 2: Run graph/runtime tests to confirm they fail**

Run from backend: uv run pytest -q tests/test_workflow.py tests/test_runtime_assembly.py tests/test_execution.py tests/test_read_graph.py
Expected: FAIL at the four-stage adapter/workflow signatures and missing final answer.

- [ ] **Step 3: Wire synthesis without changing verification semantics**

Add answer, answerModel, and answerReasoning to FactCheckState; require the fifth adapter; wrap synthesis with configured providers in existing priority order; translate its provider metadata to answer-only fields; and catch only expected NOT_CONFIGURED/SYNTHESIS_FAILED exhaustion to install insufficient_answer(). Assemble FactCheckResult from the verified state and final synthesis update. Update every injected test adapter to provide an explicit offline synthesis function; do not add an implicit fake production adapter.

    async def synthesize(state: FactCheckState):
        if not eligible_sources(state):
            return {"answer": insufficient_answer(), "answerModel": None,
                    "answerReasoning": None}
        try:
            update = await with_fallback(synthesis_operation, "SYNTHESIS_FAILED")
        except ValueError as exc:
            if str(exc) not in {"NOT_CONFIGURED", "SYNTHESIS_FAILED"}:
                raise
            return {"answer": insufficient_answer(), "answerModel": None,
                    "answerReasoning": None}
        return {"answer": update["answer"], "answerModel": update["llmModel"],
                "answerReasoning": update["llmReasoning"]}

- [ ] **Step 4: Run graph/runtime tests and confirm they pass**

Run from backend: uv run pytest -q tests/test_workflow.py tests/test_runtime_assembly.py tests/test_execution.py tests/test_read_graph.py
Expected: all graph order, result assembly, prediction and failure-preservation tests pass.

- [ ] **Step 5: Commit the graph/runtime change**

Commit runtime, workflow, and all updated adapter fixtures/tests as feat: add answer synthesis workflow stage.

### Task 4: Expose ordered synthesis progress in NDJSON and TypeScript validation

**Files:**
- Modify: backend/streaming.py and backend/tests/test_streaming.py
- Modify: app/lib/fact-check-contract.ts
- Modify: app/components/fact-check-client.ts and app/components/fact-check-client.test.mjs
- Modify: app/lib/server/agent.ts and app/lib/server/agent.test.mjs

**Interfaces:**
- AgentStage gains synthesizing; backend STAGES and MESSAGES have five aligned entries.
- FactCheckAnswer, AnswerBlock, AnswerCitation, and AnswerSection TypeScript definitions mirror the Python contract.
- validResult() checks answer shape, bounds, required citations, and citation IDs resolving to verified non-YouTube sources before accepting the NDJSON result.
- The legacy local runAgent emits a safe insufficient answer in its result and is not given a new provider call.

- [ ] **Step 1: Add failing stream/client contract cases**

Assert stream stages are exactly extracting, searching, reading, verifying, synthesizing; no result appears until the synthesis update; missing/malformed answer or an unknown/unverified/YouTube answer source is rejected by the client; and a fallback answer with null answer model/reasoning is accepted.

    const fallback = {...result, answer: {
      status: 'insufficient_evidence', overview: null, sections: [],
      conclusion: null, model: null, reasoning: null,
    }};
    assert.equal((await readFactCheckStream(response(JSON.stringify({
      type: 'result', result: fallback,
    })))).answer.status, 'insufficient_evidence');

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run from the repository root: node --experimental-strip-types --test app/components/fact-check-client.test.mjs app/lib/server/agent.test.mjs
Run from backend: uv run pytest -q tests/test_streaming.py
Expected: the new client cases fail on the missing answer contract; backend stream tests fail because they receive four stages and a result at verifying instead of synthesizing.

- [ ] **Step 3: Update stage order, shared types, runtime validator and legacy result**

Emit synthesizing after verifying; emit the final result only after the fifth graph update. Mirror Pydantic answer limits and citation rules in TypeScript, validating IDs against the same result's verified non-YouTube sources. Add an explicit insufficient answer to the unused legacy agent so its public shape remains valid without increasing provider calls.

    export type AgentStage =
      'extracting' | 'searching' | 'reading' | 'verifying' | 'synthesizing';

- [ ] **Step 4: Run stream/client/legacy tests and confirm they pass**

Run from the repository root: node --experimental-strip-types --test app/components/fact-check-client.test.mjs app/lib/server/agent.test.mjs
Run from backend: uv run pytest -q tests/test_streaming.py
Expected: all pass; malformed answer events are rejected and no internal sourceTexts are serialized.

- [ ] **Step 5: Commit the public contract and stream change**

Commit backend streaming, frontend contract/client and legacy result changes with their tests as feat: stream grounded synthesis results.

### Task 5: Render structured AI overview and inline source chips

**Files:**
- Read before coding: relevant installed Next.js 16 guides under node_modules/next/dist/docs/ for App Router client components and CSS, following AGENTS.md.
- Modify: app/components/fact-check-reply.ts
- Modify: app/components/fact-check-dashboard.tsx
- Modify: app/globals.css
- Modify: app/components/fact-check-reply.test.mjs
- Modify: app/components/fact-check-client.test.mjs for unsafe-URL behavior

**Interfaces:**
- composeAssistantReply(result) returns the validated answer, its associated source records for inline citation labels/URLs, and existing source/evidence metadata. It no longer invents a separate summary from the first claim.
- AssistantReply has answer: FactCheckAnswer, sources: FactSource[], and meta: string. The local AnswerOverview({answer, sources}: {answer: FactCheckAnswer; sources: FactSource[]}) renderer walks overview, section items and conclusion, and links each citation to its matching source.
- Chat messages retain plain text for user/demo/error messages and may carry a structured answer plus its source mapping for live API responses.
- A dedicated answer renderer displays AI 개요, the overview, only returned supporting/counter/context/uncertainty sections, and the conclusion. Each citation chip is an accessible link built from a matching verified source and safeSourceUrl(source.url).
- Insufficient evidence uses fixed Korean UI copy and does not imply an LLM-generated answer. Existing detailed fact verdict/evidence panels and demo/error labels remain unchanged.

- [ ] **Step 1: Add failing reply/renderer behavior tests**

Change reply tests to assert the structured overview, returned sections/conclusion and source mapping are preserved; assert an insufficient answer does not fall back to the first claim's text. Add checks that citation sources absent from the answer mapping cannot render as links and that unsafe URL schemes are rejected by safeSourceUrl in the client tests.

    const reply = composeAssistantReply({
      answer: groundedAnswer, sources: [verifiedSource], claims: [], evidence: [],
    });
    assert.equal(reply.answer.overview.text, "AGI 전망은 아직 불확실합니다.");
    assert.equal(reply.sources[0].id, "s1");

- [ ] **Step 2: Run the reply tests and confirm they fail**

Run from the repository root: node --experimental-strip-types --test app/components/fact-check-reply.test.mjs app/components/fact-check-client.test.mjs
Expected: FAIL because composeAssistantReply currently returns a single plain-text string derived from a claim.

- [ ] **Step 3: Replace the one-line live reply with the structured accessible renderer**

Return answer and its sources from composeAssistantReply; store them only in the in-memory chat message. Render links with descriptive names, target="_blank", and rel="noopener noreferrer"; use safeSourceUrl and never render an answer citation as a live link unless its source is verified, non-YouTube, and present. Add responsive CSS for wrapped citation chips, compact headings, section bullets, and an uncertainty/conclusion visual distinction.

    {message.answer
      ? <AnswerOverview answer={message.answer} sources={message.sources ?? []} />
      : message.text ? <p>{message.text}</p> : null}

- [ ] **Step 4: Run frontend tests and TypeScript check**

Run from the repository root: node --experimental-strip-types --test app/components/fact-check-reply.test.mjs app/components/fact-check-client.test.mjs app/lib/server/*.test.mjs app/components/*.test.mjs
Run: npm run typecheck
Expected: all Node tests and TypeScript checking pass; existing source/evidence panels and demo/error text remain available.

- [ ] **Step 5: Commit the structured chat renderer**

Commit reply, dashboard, CSS and Node tests as feat: render grounded overview with inline citations.

### Task 6: Verify the forecast vertical slice and hand off

**Files:**
- Modify: backend/tests/test_runtime_assembly.py or a focused test in backend/tests/test_answer_synthesis.py
- Modify: app/components/fact-check-client.test.mjs
- Modify: HANDOFF.md
- Review: all files changed by Tasks 1–5

**Interfaces:**
- The offline AGI case is AGI는 2030년 안에 오나?; it uses fixed mock provider results and no credentials/network. It checks separate prediction treatment, source-body-grounded links, uncertainty, no invented probabilities/consensus, and preservation of claim/evidence verification.
- Handoff states exactly which stage work is complete, what Google result limitations remain, and whether an actual live provider test was performed. It contains no keys or raw secrets.

- [ ] **Step 1: Add the integrated mock forecast regression**

Add test_forecast_synthesis_preserves_prediction_and_citations using one verified article arguing for an earlier timeline and one verified article describing uncertainty or a later timeline. Mock extraction as a prediction, mock verification as not_checkable, and mock synthesis with exact text spans from those two bodies; assert every displayed citation ID/quote grounds, both views appear only when present, and no numeric probability or consensus is injected.

    assert result.claims[0].kind == "prediction"
    assert result.claims[0].verdictCode == "not_checkable"
    assert result.answer.status == "grounded"
    blocks = [result.answer.overview, result.answer.conclusion]
    blocks.extend(item for section in result.answer.sections for item in section.items)
    citations = [citation for block in blocks for citation in block.citations]
    assert citations
    assert {citation.sourceId for citation in citations} <= {"s1", "s2"}
    assert all(citation.quote in source_texts[citation.sourceId] for citation in citations)

- [ ] **Step 2: Run focused regression tests**

Run from backend: uv run pytest -q tests/test_answer_synthesis.py tests/test_runtime_assembly.py tests/test_contracts.py tests/test_streaming.py
Run from the repository root: node --experimental-strip-types --test app/components/fact-check-client.test.mjs app/components/fact-check-reply.test.mjs app/lib/server/*.test.mjs app/components/*.test.mjs
Expected: all mock-only regressions pass; no real provider is called.

- [ ] **Step 3: Run full checks and inspect the final diff**

Run from backend: uv run pytest -q and uv lock --check.
Run from the repository root: npm run typecheck, npm run build, and git diff --check.
Then inspect git status --short, git diff --stat, and the full diff. Do not stop a pre-existing dev server. If any temporary verification server or browser is started, close only that process/window and confirm its port is closed.
Expected: all checks pass; no credential files, generated artifacts, unrelated files or unverified live-provider claims enter the change.

- [ ] **Step 4: Update HANDOFF with observed outcomes**

Mark the fifth stage complete only after the checks above pass. Record exact test counts/commands, note that tests use mocks, document provider/model metadata distinction, and leave actual credentialed live-provider verification explicitly pending unless it is separately performed.

- [ ] **Step 5: Commit, push and verify the remote**

Commit the regression and handoff update as test: document grounded answer synthesis completion. Push the completed task to origin/main; then confirm the local branch is up to date and git status --short --branch is clean. Never force-push or print environment secrets.
