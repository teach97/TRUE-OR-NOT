# Graph Report - my-app  (2026-09-29)

## Corpus Check
- 151 files · ~107,722 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .css 8, (none) 6, .example 2)

## Summary
- 1736 nodes · 3345 edges · 140 communities (115 shown, 25 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 361 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0b1d02e7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- contracts.py
- LLMProvider
- verification.py
- test_attachments.py
- SourceReadResult
- build_workflow
- Four-Node LangGraph Runtime (extracting→searching→reading→verifying)
- search_tavily
- fact-check-dashboard.tsx
- test_source_fetch.py
- probe-recovery.py
- main.py
- fact-check-client.ts
- fetch_youtube_data
- ref_node_assert
- test_providers.py
- FactCheckDashboard
- extract_claims
- demo-state.ts
- agent.ts
- PolyForm Shield License 1.0.0
- What You Must Do When Invoked
- test_search_errors.py
- make_runtime_adapters
- stream_events
- test_search.py
- compilerOptions
- True or Not 고도화 기획서 v4
- build_runtime_workflow
- test_fast_check_propagates_jev_failure_without_llm_fallback
- fact-check-reply.ts
- lattice-loader.tsx
- Next.js Wordmark Logo
- border-glow.tsx
- test_llm_runtime_ignores_environment_proxy_for_provider_connection
- Backend Environment Keys Configuration
- Settings
- tech-text.tsx
- next
- runtime.py
- fact-check-contract.ts
- package.json
- run_jev_fast_check
- FactCheckResult
- search_sources
- floating-lines.tsx
- floating-lines-background.tsx
- scramble-text.tsx
- test_finnhub.py
- Framework Route Modules
- home.tsx
- devDependencies
- root.tsx
- Q: jev 키 입력되있음 env에 AI_GATEWAY_API_KEY=; Vercel AI Gateway Jev
- SVG root 1080x174
- extraction.py
- globe.svg
- ref_react_router_dev
- dependencies
- scripts
- Document File Icon
- intent/route.ts
- Dark Mode Logo SVG
- Q: 미설정으로 뜨는데? API 입력은 되있는데
- eslint.config.mjs
- next-env.d.ts
- Browser Window Icon SVG in Gray
- Dashboard demo-state fixture shader implementation and checks
- Declarative Router Shape
- RSC Route Module Differences
- test_runtime.py
- FactLens UI MVP (dark glassmorphism dashboard)
- True or Not agent architecture
- Globe Icon 16x16
- Vercel Triangle Logo SVG in White
- AGENTS.md Next.js agent rules
- Installed Docs as Source of Truth
- FactCheckAnswer AnswerBlock Citation Section contract
- Grounded answer synthesis plan
- Shared contract app lib fact-check-contract.ts
- Demo vs Real Verification Separation
- postcss.config.mjs
- Seven trust boundaries untrusted input citations grounding
- True or Not UI design direction
- True or Not UI verification record
- Seven verdict codes mostly_supported to contradicted
- True or Not advanced planning v2
- source
- Next.js Logo (next.svg)
- factlens-backend
- evaluate_claims_jev
- sources.py
- True or Not 고도화 기획서 v4-요약
- test_jev.py
- asyncio
- fetch_public_text
- Globe Components and Clip Container
- Globe Layout and Meridian Grid
- FactLens frontend README
- FactLens frontend Next.js App Router TypeScript Tailwind
- Q: JEV 선택이 안 되고 8010에서 Errno 10048이 발생함
- Q: 지금 레이아웃이 이상해 애니메이션 위치도 이상한곳에 걸쳐지고
- Q: 지금 jev가 제대로 작동하지 않아
- test_fast_check_skips_search_when_the_link_reads_cleanly
- Q: 점수 판정이 이상해
- 17. 소개 문구와 데모 안내
- 10. 기술 구성 (As-built)
- glide-select.tsx
- 4. 현재 구현 범위 (As-built)
- graphify reference: extra exports and benchmark
- 8. 판정 정책
- Q: 지금 또 검증실패 뜸
- liquid-logo.tsx
- 13. QA와 수용 기준
- 6. 주장 추출과 검증 계획
- 9. 화면 설계
- _TextParser
- graphify reference: query, path, explain
- 18. 기준 자료와 문서 이력
- test_runtime_assembly.py
- test_extract_link_with_extra_words_falls_back_to_page
- recovery_probe_app.py
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- ProviderCallError
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- extraction-spec.md
- itertools
- SynthesisDraft
- youtube-context.ts
- test_jev_endpoint_maps_gateway_failure_to_502
- run_with_fallback
- test_read_searches_related_coverage_from_the_linked_page_title
- bell-toggle.tsx
- test_fast_check_collects_youtube_context_when_the_key_is_configured
- _source_identity
- YouTube Data API Metadata & Comments Integration (videos.list / commentThreads.list)

## God Nodes (most connected - your core abstractions)
1. `Settings` - 68 edges
2. `LLMProvider` - 67 edges
3. `make_runtime_adapters()` - 58 edges
4. `ProviderCallError` - 47 edges
5. `search_sources()` - 43 edges
6. `synthesize_answer()` - 34 edges
7. `ground_judgments()` - 30 edges
8. `extract_claims()` - 29 edges
9. `run_jev_fast_check()` - 29 edges
10. `verify_claims()` - 28 edges

## Surprising Connections (you probably didn't know these)
- `4.2 채택된 확장 (v3 3.5절 대체)` --references--> `extract_image_claims()`  [INFERRED]
  docs/True_or_Not_고도화-기획서-v4.md → backend/extraction.py
- `독립성 처리 (현재 구현 기준)` --references--> `origin_group_for_url()`  [INFERRED]
  docs/True_or_Not_고도화-기획서-v4.md → backend/search.py
- `14. 알려진 한계와 기술 부채` --references--> `limitedText()`  [INFERRED]
  docs/True_or_Not_고도화-기획서-v4.md → app/lib/server/agent.ts
- `14. 알려진 한계와 기술 부채` --references--> `run_jev_fast_check()`  [INFERRED]
  docs/True_or_Not_고도화-기획서-v4.md → backend/runtime.py
- `10.8 원문 위치 규약` --references--> `start()`  [INFERRED]
  docs/True_or_Not_고도화-기획서-v4.md → app/lib/server/route.test.mjs

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Light Logo Composition (Emblem + Wordmark)** — app_welcome_logo_light_logo, app_welcome_logo_light_emblem, app_welcome_logo_light_wordmark [EXTRACTED 1.00]
- **Fact-check request pipeline** — readme_fact_check_proxy, backend_readme_factlens_backend, docs_true_or_not_agent_architecture_pipeline [EXTRACTED 1.00]
- **Grounded answer synthesis vertical slice** — docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_answer_contract, docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_synthesis_stage [EXTRACTED 1.00]
- **Four-Stage Fact-Check Pipeline (extracting → searching → reading → verifying)** — handoff_extraction_adapter, handoff_search_connector, handoff_source_fetcher, handoff_verification_rules [EXTRACTED 1.00]
- **Elements that form the document file icon** — public_file_document_file_icon, public_file_document_outline, public_file_folded_corner, public_file_text_lines [EXTRACTED 1.00]
- **Globe Icon Composition** — public_globe_svg_globe_icon, public_globe_outerring, public_globe_gridlines [EXTRACTED 1.00]
- **Next.js Wordmark Letterform Group** — public_next_wordmark, public_next_nglyph, public_next_textglyphs [EXTRACTED 1.00]
- **React Router mode selection** — agents_skills_react_router_skill_react_router_modes, agents_skills_react_router_skill_framework_mode_detection, agents_skills_react_router_skill_data_mode_detection, agents_skills_react_router_skill_declarative_mode_detection [EXTRACTED 1.00]
- **logo_light_composition** — logo_light_red_accent, logo_light_dark_dots, logo_light_wordmark [INFERRED 0.85]
- **public_globe_composition** — public_globe_globe_path, public_globe_clip_path, public_globe_wireframe [INFERRED 0.85]
- **public_next_composition** — public_next_n_mark, public_next_main_letterforms, public_next_js_suffix [INFERRED 0.85]

## Communities (140 total, 25 thin omitted)

### Community 0 - "contracts.py"
Cohesion: 0.16
Nodes (16): AgentStatus, AnswerBlock, AnswerCitation, AnswerSection, _ContractModel, FactCheckAnswer, FactCheckProgressCitation, FactCheckProgressClaim (+8 more)

### Community 1 - "LLMProvider"
Cohesion: 0.13
Nodes (40): AsyncClient, Generate and validate a grounded answer, leaving provider retries to runtime., synthesize_answer(), LLMProvider, completed_response(), draft(), multi_section_draft(), parametrize (+32 more)

### Community 2 - "verification.py"
Cohesion: 0.06
Nodes (73): FactClaim, default_fact_score(), normalize_fact_score(), Evidence-grounded public score policy for fact-check claims., Return the public band for an inclusive 0–100 score., Preserve the model's reasoned score, clamped only to the 0-100 range. The…, Supply a compatible score when an older result omits the new field., score_band() (+65 more)

### Community 3 - "test_attachments.py"
Cohesion: 0.11
Nodes (15): FactCheckRequest, ImageAttachment, BaseModel, model_validator, parametrize, test_request_rejects_invalid_input(), test_request_requires_all_contract_fields(), Link and image attachment paths; no external traffic (all transports mocked). (+7 more)

### Community 4 - "SourceReadResult"
Cohesion: 0.17
Nodes (6): html_title(), Reader result with optional metadata and backwards-compatible unpacking., _read_url(), SourceReadResult, _TitleParser, HTMLParser

### Community 5 - "build_workflow"
Cohesion: 0.06
Nodes (34): test_workflow_preserves_link_and_image_state_keys(), parametrize, Real LangGraph via HTTP boundary; adapters contain offline fixtures only., test_graph_failure_returns_safe_error(), stage(), test_invalid_http_input_is_safe_and_never_runs_graph(), test_post_rejects_malformed_result_contract(), test_post_runs_graph_and_returns_only_result() (+26 more)

### Community 6 - "Four-Node LangGraph Runtime (extracting→searching→reading→verifying)"
Cohesion: 0.09
Nodes (24): Backend API Endpoints (health/fact-check/stream), Backend Environment Variables (GEMINI/OPENAI/SERPAPI/YOUTUBE keys), FactLens Backend (FastAPI + LangGraph), Backend Model Fallback Order (Gemini 3.8 Flash → Gemini 3.7 Flash → GPT-6 Luna), Google Serp Smoke Script (smoke_google_serp.py), Backend Search & Verification Flow, Verification pipeline extract search read verify synthesize, MVP F01-F11 and claim-centered product principles (+16 more)

### Community 7 - "search_tavily"
Cohesion: 0.20
Nodes (15): AsyncClient, Tavily web search discovery. Optional; LLM search remains the fallback., Search each checkable claim once with Tavily basic depth (1 credit each). Pass…, Tavily could not serve this request; the caller falls back., search_tavily(), TavilyUnavailable, Tavily search discovery; no live traffic (all transports mocked)., run_search() (+7 more)

### Community 8 - "fact-check-dashboard.tsx"
Cohesion: 0.06
Nodes (29): BlurText(), CountUp(), CountUpProps, base, DEMO_FOCUS, DEMO_TEXT, demoPreview, documents (+21 more)

### Community 9 - "test_source_fetch.py"
Cohesion: 0.07
Nodes (25): parametrize, Deterministic HTTP response fixtures; resolver safety tested separately., Response, run(), Session, test_low_reach_youtube_source_is_dropped_from_results(), youtube_reader(), test_oversized_page_is_truncated_and_parsed_instead_of_rejected() (+17 more)

### Community 10 - "probe-recovery.py"
Cohesion: 0.09
Nodes (27): blocking_extract(), cancellation_state(), InstrumentedGraph, get, Explicit integration-test entry point ONLY; never imported by main/runtime. No…, record(), glob, os (+19 more)

### Community 11 - "main.py"
Cohesion: 0.08
Nodes (31): classify_intent(), IntentDecision, Any, AsyncClient, BaseModel, Cheap intent gate: verify with the pipeline or answer conversationally., Return a verify/reply decision; invalid model output is a retryable failure., _code_revision() (+23 more)

### Community 12 - "fact-check-client.ts"
Cohesion: 0.10
Nodes (25): FactCheckError, faviconUrlFor(), Options, readFactCheckStream(), line(), safeSourceUrl(), insufficientAnswer, result (+17 more)

### Community 13 - "fetch_youtube_data"
Cohesion: 0.12
Nodes (25): Offline YouTube Data API contract tests; no Google credentials or traffic., test_comments_unavailable_keeps_video_title_without_exposing_provider_error(), run(), test_fetches_official_video_title_and_bounded_plain_text_comments(), handler(), run(), test_ignores_malformed_youtube_metadata_without_rejecting_comments(), run() (+17 more)

### Community 14 - "ref_node_assert"
Cohesion: 0.11
Nodes (15): ref_node_assert, ref_node_fs, ref_node_test, ref_node_url, observations, responses, state(), waitCounts() (+7 more)

### Community 15 - "test_providers.py"
Cohesion: 0.12
Nodes (24): agent_status(), get_workflow(), Report whether the real four-stage workflow can be constructed., Build the provider-backed graph only when a server-side key is configured., configured_model_options(), configured_providers(), _gemini_schema(), clean() (+16 more)

### Community 16 - "FactCheckDashboard"
Cohesion: 0.12
Nodes (24): ChatIntent, CLAIM_PATTERNS, classifyChatInput(), describeHistory(), EARLY_META, FOLLOW_UP_PATTERNS, HELP_PATTERNS, IDENTITY_PATTERNS (+16 more)

### Community 17 - "extract_claims"
Cohesion: 0.14
Nodes (19): extract_claims(), Return a LangGraph state update; callers own the client and credential., parametrize, Offline provider transport fixtures, never real model responses., test_extractor_drops_invented_claim_without_fabricating_source_text(), run(), test_extractor_keeps_forecast_and_returns_search_keywords_separately(), handler() (+11 more)

### Community 18 - "demo-state.ts"
Cohesion: 0.21
Nodes (14): Action, Claim, createPreview(), initialState, State, transition(), TrustIndex(), FACT_SCORE_BANDS (+6 more)

### Community 19 - "agent.ts"
Cohesion: 0.05
Nodes (49): backend(), dynamic, error(), headers, POST(), runtime, input, backend() (+41 more)

### Community 20 - "PolyForm Shield License 1.0.0"
Cohesion: 0.11
Nodes (18): Acceptance, Changes and New Works License, Competition, Copyright License, Definitions, Discontinued Products, Distribution License, Fair Use (+10 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "test_search_errors.py"
Cohesion: 0.14
Nodes (13): parametrize, Offline failure, safety and empty-result tests., test_candidates_filter_unsafe_urls_and_limit_results(), run(), test_completed_empty_search_is_not_a_verdict(), run(), test_nonfacts_skip_network(), run() (+5 more)

### Community 23 - "make_runtime_adapters"
Cohesion: 0.12
Nodes (20): _http_status_from_exception(), make_runtime_adapters(), extract(), extract_from_page(), page_operation(), search(), synthesize(), operation() (+12 more)

### Community 24 - "stream_events"
Cohesion: 0.10
Nodes (21): build_progress_preview(), build_progress_sources(), Expose only source identity and access state before final answer assembly., Build an early, strictly projected claim summary from validated evidence., encode(), NDJSON boundary: only stage labels and validated final results are public., Propagate cancellation and close the graph iterator on every exit path., stream_events() (+13 more)

### Community 25 - "test_search.py"
Cohesion: 0.13
Nodes (22): read(), cached_reader(), youtube_reader(), build_search_query(), is_japanese_candidate(), _normalized_host(), origin_group_for_url(), _project_candidates() (+14 more)

### Community 26 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 27 - "True or Not 고도화 기획서 v4"
Cohesion: 0.14
Nodes (13): 0. 한눈에 보기, 11. 상태 관리와 비동기 실행, 12. 보안·개인정보·이용 조건, 15. 팀 역할과 실행 계획, 16. 팀 결정이 필요한 사항, 1. 핵심 방향, 2. 문제 정의와 사용자 시나리오, 3. 제품 원칙 (+5 more)

### Community 28 - "build_runtime_workflow"
Cohesion: 0.09
Nodes (23): build_runtime_workflow(), Compile five ordered stages and assemble the result after synthesis., The five graph stages, injectable for offline orchestration tests., RuntimeAdapters, test_all_synthesis_providers_failing_preserves_verified_result(), failing_provider(), mock_client(), test_forecast_keywords_reach_search_through_graph_without_leaking_into_result() (+15 more)

### Community 29 - "test_fast_check_propagates_jev_failure_without_llm_fallback"
Cohesion: 0.12
Nodes (12): test_fast_check_llm_search_honors_the_selected_model(), handler(), run(), test_fast_check_propagates_jev_failure_without_llm_fallback(), run(), test_fast_check_searches_with_llm_and_sends_read_source_text_to_jev(), fake_fetch(), handler() (+4 more)

### Community 30 - "fact-check-reply.ts"
Cohesion: 0.15
Nodes (18): AnswerBlockView(), AnswerOverview(), AnswerCitationDisplay, AnswerCitationDisplayState, AssistantReply, composeAssistantReply(), createAnswerCitationDisplayState(), modelLabel() (+10 more)

### Community 31 - "lattice-loader.tsx"
Cohesion: 0.16
Nodes (14): DEFAULT_PATTERN, formatElapsed(), GridSize, LatticeLoader(), LatticeLoaderProps, LoaderStatus, LoaderStyle, MARKS (+6 more)

### Community 32 - "Next.js Wordmark Logo"
Cohesion: 0.17
Nodes (15): Geometric Brand Emblem (Red & Black Circles), Light Theme Variant (Dark Glyphs on Light Background), logo-light.svg light-mode branding logo, Path-Drawn Brand Wordmark, Next.js Framework Brand, Default template branding, next.svg, .js suffix glyphs (+7 more)

### Community 33 - "border-glow.tsx"
Cohesion: 0.20
Nodes (13): AnimateOpts, animateValue(), BorderGlow(), BorderGlowProps, buildGlowVars(), buildGradientVars(), COLOR_MAP, easeInCubic() (+5 more)

### Community 34 - "test_llm_runtime_ignores_environment_proxy_for_provider_connection"
Cohesion: 0.18
Nodes (11): test_llm_runtime_ignores_environment_proxy_for_provider_connection(), mock_async_client(), test_llm_search_is_used_directly_without_a_search_notice(), handler(), mock_async_client(), test_runtime_read_stage_uses_youtube_adapter_without_adding_comments_to_source_texts(), mock_async_client(), test_tavily_outage_falls_back_to_llm_search() (+3 more)

### Community 35 - "Backend Environment Keys Configuration"
Cohesion: 0.18
Nodes (11): Backend Environment Keys Configuration, FactLens Backend Fact-check API, Search Verification Flow Max 3 Claims 6 Sources, Fact-check Streaming Endpoint, Five Stage Search Improvement Pipeline, Free Google Organic Search via SerpApi, Multi-LLM Fallback Priority Order, Duplicate Link and Japanese Search Result Correction (+3 more)

### Community 36 - "Settings"
Cohesion: 0.15
Nodes (20): BaseModel, Settings, main(), Offline API boundary checks; no provider calls., test_health_and_status_do_not_claim_provider_readiness(), test_request_preserves_original_text(), test_request_rejects_unknown_model_preference(), test_status_reports_gemini_fallback_when_openai_is_missing() (+12 more)

### Community 37 - "tech-text.tsx"
Cohesion: 0.20
Nodes (13): approach(), Art, Box, Glyph, hexToRgb(), noise(), rgba(), Settings (+5 more)

### Community 38 - "next"
Cohesion: 0.15
Nodes (6): app_globals, metadata, metadata, metadata, nextConfig, next

### Community 39 - "runtime.py"
Cohesion: 0.15
Nodes (19): eligible_sources(), _project_claims(), Any, Synthesize a user-facing answer from verified source text only., Build a minimal JSON-safe input; never forward raw source/search records., Project at most six verified non-YouTube texts into a provider-safe shape., _string_value(), _synthesis_input() (+11 more)

### Community 40 - "fact-check-contract.ts"
Cohesion: 0.12
Nodes (16): AgentStage, AgentStatus, AnswerSection, FACT_CHECK_MODEL, FACT_CHECK_REASONING, FactSource, ModelId, ModelOption (+8 more)

### Community 41 - "package.json"
Cohesion: 0.14
Nodes (13): name, private, type, @paper-design/shaders-react, postcss, react-dom, tailwindcss, @tailwindcss/postcss (+5 more)

### Community 42 - "run_jev_fast_check"
Cohesion: 0.20
Nodes (10): _normalize_source(), AsyncClient, Project internal source state onto the public TypeScript contract., Truncate to a UTF-16 unit budget without splitting astral characters., Search and read evidence, then return Jev's score-only claim result., _result_warnings(), run_jev_fast_check(), search_once() (+2 more)

### Community 43 - "FactCheckResult"
Cohesion: 0.29
Nodes (16): FactCheckResult, grounded_answer(), parametrize, Final Python contract tests; no provider calls., result_payload(), test_evidence_may_expose_only_a_bounded_matching_article_section(), test_final_contract_accepts_frontend_shape_and_wrapper(), test_final_contract_rejects_broken_links_or_unverified_evidence() (+8 more)

### Community 44 - "search_sources"
Cohesion: 0.12
Nodes (19): AsyncClient, search_sources(), test_prediction_claims_are_searched_with_primary_query_in_provider_order(), run(), test_search_collects_deduplicated_candidates_without_evidence(), run(), test_search_keeps_completed_sources_when_response_has_nonterminal_search_item(), run() (+11 more)

### Community 45 - "floating-lines.tsx"
Cohesion: 0.22
Nodes (9): DEFAULT_BOTTOM_WAVE_POSITION, DEFAULT_ENABLED_WAVES, DEFAULT_LINE_COUNT, DEFAULT_LINE_DISTANCE, FloatingLines(), FloatingLinesProps, hexToVec3(), WavePosition (+1 more)

### Community 46 - "floating-lines-background.tsx"
Cohesion: 0.22
Nodes (6): BackgroundBoundary, FloatingLines, FloatingLinesBackground(), floatingLinesDistance, floatingLinesGradient, floatingLinesWaves

### Community 47 - "scramble-text.tsx"
Cohesion: 0.36
Nodes (9): getRevealOrder(), randomCharacter(), randomizeText(), ScrambleRun, ScrambleText(), resetVisual(), startRun(), writeVisual() (+1 more)

### Community 48 - "test_finnhub.py"
Cohesion: 0.18
Nodes (12): fetch_stock_quote(), AsyncClient, Small, read-only adapter for Finnhub stock quotes., Fetch the current quote for a ticker symbol. Returns {"symbol", "current",…, Finnhub quote adapter; no live traffic (all transports mocked)., run(), run_once(), test_finnhub_key_is_server_only_and_redacted() (+4 more)

### Community 49 - "Framework Route Modules"
Cohesion: 0.22
Nodes (9): Data Loading with Loaders and Actions, Data Router Shape, Forms Fetchers and Pending UI, Middleware Sessions and Auth, Framework Rendering Strategy, Framework Route Modules, Framework Type Safety with Generated Route Types, Data Mode Detection Signals (+1 more)

### Community 50 - "home.tsx"
Cohesion: 0.25
Nodes (5): app_welcome_logo_dark, app_welcome_logo_light, resources, Welcome(), ref_types_home

### Community 51 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, postcss, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom, @types/three (+1 more)

### Community 52 - "root.tsx"
Cohesion: 0.25
Nodes (3): app_app, ref_react_router, ref_types_root

### Community 53 - "Q: jev 키 입력되있음 env에 AI_GATEWAY_API_KEY=; Vercel AI Gateway Jev"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: jev 키 입력되있음 env에 AI_GATEWAY_API_KEY=; Vercel AI Gateway Jev, Source Nodes

### Community 54 - "SVG root 1080x174"
Cohesion: 0.29
Nodes (8): Dark circular dots, logo-light.svg, Logo icon mark, Light theme variant, Red accent path, SVG root 1080x174, Welcome page branding, Wordmark letter paths

### Community 55 - "extraction.py"
Cohesion: 0.22
Nodes (13): extract_image_claims(), extract_page_claims(), ExtractedClaim, Extraction, ImageObservation, _project_extracted_claims(), AsyncClient, BaseModel (+5 more)

### Community 56 - "globe.svg"
Cohesion: 0.33
Nodes (7): Clip path definition, Default template icon, globe.svg, Globe wireframe path, Monochrome gray variant, SVG root 16x16, Globe wireframe motif

### Community 57 - "ref_react_router_dev"
Cohesion: 0.33
Nodes (3): ref_react_router_dev, ref_tailwindcss_vite, ref_vite

### Community 58 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, motion, next, @paper-design/shaders-react, react, react-dom, three

### Community 59 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, start, test, typecheck

### Community 60 - "Document File Icon"
Cohesion: 0.40
Nodes (5): Document File Icon, Document Page Outline, Folded Corner, Gray Fill Style, Text Content Lines

### Community 61 - "intent/route.ts"
Cohesion: 0.83
Nodes (3): backend(), error(), POST()

### Community 62 - "Dark Mode Logo SVG"
Cohesion: 0.50
Nodes (4): Dark Background Variant Purpose for Welcome Page, Geometric Icon Mark with Red Accent and White Nodes, Dark Mode Logo SVG, React Router Wordmark in White

### Community 63 - "Q: 미설정으로 뜨는데? API 입력은 되있는데"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 미설정으로 뜨는데? API 입력은 되있는데, Source Nodes

### Community 64 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, ref_eslint, ref_eslint_config_next

### Community 65 - "next-env.d.ts"
Cohesion: 0.50
Nodes (3): next_dev_types_root_params_d, next_dev_types_routes_d, NOTE: This file should not be edited

### Community 66 - "Browser Window Icon SVG in Gray"
Cohesion: 0.50
Nodes (4): Minimal Window Chrome Icon Purpose for UI, Three Circular Window Control Dots in Title Bar, Window Frame Outline with Rounded Bottom Corners, Browser Window Icon SVG in Gray

### Community 67 - "Dashboard demo-state fixture shader implementation and checks"
Cohesion: 0.67
Nodes (3): Next.js breaking changes guide and verification cleanup, Premium research workspace dark glass design, Dashboard demo-state fixture shader implementation and checks

### Community 68 - "Declarative Router Shape"
Cohesion: 0.67
Nodes (3): Declarative Router Shape, Declarative Mode Boundary, Declarative Mode Detection Signals

### Community 69 - "RSC Route Module Differences"
Cohesion: 0.67
Nodes (3): RSC Client Server Boundaries, RSC Route Module Differences, RSC Detection Signals

### Community 70 - "test_runtime.py"
Cohesion: 0.21
Nodes (11): build_extraction_graph(), load_settings(), Stage, Read the backend-local file without mutating process environment., End after extraction; do not simulate search, sources, or judgments., Isolated settings and extraction graph tests; no paid API calls., test_extraction_graph_ends_without_fabricating_verdict(), test_settings_load_file_without_exposing_key() (+3 more)

### Community 72 - "True or Not agent architecture"
Cohesion: 0.67
Nodes (3): True or Not agent architecture, Gemini Interactions API docs citation, GPT-6 Luna model docs citation

### Community 73 - "Globe Icon 16x16"
Cohesion: 0.67
Nodes (3): Globe Grid Lines (Meridians & Parallels), Globe Outer Ring, Globe Icon 16x16

### Community 74 - "Vercel Triangle Logo SVG in White"
Cohesion: 0.67
Nodes (3): Vercel Brand Mark Purpose for Deployment Branding, White Filled Triangle Mark viewBox 1155x1000, Vercel Triangle Logo SVG in White

### Community 87 - "source"
Cohesion: 0.33
Nodes (6): source(), test_eligible_sources_excludes_unverified_empty_and_youtube_and_bounds_text(), read(), search(), read(), search()

### Community 90 - "evaluate_claims_jev"
Cohesion: 0.15
Nodes (21): evaluate_claims_jev(), JevError, _parse_strength(), _parse_verdict(), Any, AsyncClient, RuntimeError, Jev (TypeSafe System One) verdicts through Vercel AI Gateway. The gateway API… (+13 more)

### Community 91 - "sources.py"
Cohesion: 0.20
Nodes (11): aiohttp, aiohttp_abc, _generic_title(), html_sections(), _is_japanese_page_text(), Bounded public-source reader. TLS validation stays enabled; no credentials., Read one candidate. Returns (item, text, sections); item None drops it., _read_candidate() (+3 more)

### Community 92 - "True or Not 고도화 기획서 v4-요약"
Cohesion: 0.22
Nodes (8): 0. 한눈에 보기, 10. 기술 구성, 14. 알려진 한계 (상위), 15. 우선순위, 16. 팀 결정 사항, 4. 구현 범위, QA 수용 기준 (발췌), True or Not 고도화 기획서 v4-요약

### Community 93 - "test_jev.py"
Cohesion: 0.16
Nodes (16): _jev_runtime_state(), Jev verdicts through AI Gateway; no live traffic (all transports mocked)., test_evaluate_maps_verdict_and_strength_to_fact_score(), handler(), run(), test_fast_check_truncates_long_text_to_contract_limit(), handler(), run() (+8 more)

### Community 94 - "asyncio"
Cohesion: 0.21
Nodes (7): asyncio, read_sources(), bounded(), Read-node integration preserves source text for later citation verification., test_graph_keeps_source_texts_for_verification(), read(), reader()

### Community 95 - "fetch_public_text"
Cohesion: 0.18
Nodes (9): AbstractResolver, fetch_page(), candidate_url(), is_unreliable_candidate(), Exclude hosts judged too unreliable to cite (Naver Knowledge iN, ad doorways)., checked_url(), fetch_public_text(), public_ip() (+1 more)

### Community 100 - "Q: JEV 선택이 안 되고 8010에서 Errno 10048이 발생함"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: JEV 선택이 안 되고 8010에서 Errno 10048이 발생함, Source Nodes

### Community 101 - "Q: 지금 레이아웃이 이상해 애니메이션 위치도 이상한곳에 걸쳐지고"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 지금 레이아웃이 이상해 애니메이션 위치도 이상한곳에 걸쳐지고, Source Nodes

### Community 102 - "Q: 지금 jev가 제대로 작동하지 않아"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 지금 jev가 제대로 작동하지 않아, Source Nodes

### Community 103 - "test_fast_check_skips_search_when_the_link_reads_cleanly"
Cohesion: 0.53
Nodes (5): test_fast_check_skips_search_when_the_link_reads_cleanly(), handler(), jev_handler(), router(), run()

### Community 104 - "Q: 점수 판정이 이상해"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 점수 판정이 이상해, Source Nodes

### Community 105 - "17. 소개 문구와 데모 안내"
Cohesion: 0.40
Nodes (5): 17. 소개 문구와 데모 안내, 검증 결과 하단 문구, 데모 고지 권장 문구, 서비스 소개 (D1 잠정안 반영), 짧은 소개

### Community 106 - "10. 기술 구성 (As-built)"
Cohesion: 0.20
Nodes (10): start(), 10.1 구성, 10.2 엔드포인트, 10.3 요청 계약 (`FactCheckRequest`) [코드], 10.4 결과 계약 (`FactCheckResult`) [코드], 10.5 제한값 (현재 코드 기준), 10.6 환경변수와 실행, 10.7 오류 코드 (+2 more)

### Community 107 - "glide-select.tsx"
Cohesion: 0.31
Nodes (8): GlideSelect(), GlideSelectOption, GlideSelectProps, labelText(), nextEnabled(), normalizeOption(), OptionInput, SIZES

### Community 108 - "4. 현재 구현 범위 (As-built)"
Cohesion: 0.40
Nodes (5): 4.1 핵심 기능, 4.2 채택된 확장 (v3 3.5절 대체), 4.3 범위 밖 (갱신), 4.4 MVP 이후 후보, 4. 현재 구현 범위 (As-built)

### Community 109 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 110 - "8. 판정 정책"
Cohesion: 0.40
Nodes (5): 8.1 결과 분류, 8.2 겹치는 경우의 결정 규칙, 8.3 근거 충족 규칙, 8.4 점수와 판정의 관계 (잠정), 8. 판정 정책

### Community 111 - "Q: 지금 또 검증실패 뜸"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 지금 또 검증실패 뜸, Source Nodes

### Community 112 - "liquid-logo.tsx"
Cohesion: 0.47
Nodes (3): LiquidLogo(), makeBevel(), liquidFragSource

### Community 113 - "13. QA와 수용 기준"
Cohesion: 0.50
Nodes (4): 13.1 테스트 케이스와 현재 확인 수준, 13.2 검증 현황 (인계서 2026-09-24 기록), 13.3 출시(시연) 조건, 13. QA와 수용 기준

### Community 114 - "6. 주장 추출과 검증 계획"
Cohesion: 0.50
Nodes (4): 6.1 분류 체계, 6.2 주장 구조, 6.3 검색 계획, 6. 주장 추출과 검증 계획

### Community 115 - "9. 화면 설계"
Cohesion: 0.50
Nodes (4): 9.1 현재 확인된 구현 [인계서], 9.2 설계 지침 (v3 유지, 검증 수준은 별도 표기), 9.3 UI 검증 수준, 9. 화면 설계

### Community 117 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 118 - "18. 기준 자료와 문서 이력"
Cohesion: 0.67
Nodes (3): 18. 기준 자료와 문서 이력, v3 대비 변경 사항, 기준 자료

### Community 119 - "test_runtime_assembly.py"
Cohesion: 0.27
Nodes (11): insufficient_answer(), Return a fixed answer that makes no unsupported assertions., FactCheckResponse, build_fact_check_result(), synthesizing(), Validate and assemble the only result shape exposed by the API., Runtime assembly tests; explicit adapters keep the five-node graph offline., test_final_result_warns_when_llm_search_was_unavailable() (+3 more)

### Community 120 - "test_extract_link_with_extra_words_falls_back_to_page"
Cohesion: 0.16
Nodes (7): test_extract_link_with_extra_words_falls_back_to_page(), fake_claims(), test_extract_link_with_real_claims_keeps_draft_text(), test_extract_url_only_fetches_page(), fake_page(), test_extract_url_only_truncates_long_pages_to_the_contract_limit(), fake_fetch()

### Community 121 - "recovery_probe_app.py"
Cohesion: 0.22
Nodes (6): get, post, TEST ONLY deterministic recovery app. Never imported by runtime/main., recover(), status(), verify()

### Community 122 - "graphify.js"
Cohesion: 0.40
Nodes (3): IMPORTANT: keep the reminder string free of backticks and $(...) constructs., ref_fs, ref_path

### Community 123 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 124 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 125 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 126 - "ProviderCallError"
Cohesion: 0.11
Nodes (32): _endpoint_and_headers(), _gemini_text(), _openai_text(), ProviderCallError, AsyncClient, RuntimeError, Provider-neutral requests and ordered LLM fallback policy. Credentials stay in…, Call a provider's structured-output endpoint and return only model text. (+24 more)

### Community 131 - "SynthesisDraft"
Cohesion: 0.22
Nodes (8): _limit_sections_to_source_breadth(), BaseModel, model_validator, Keep answer breadth proportional to the cited source base. A single supporting…, Require every citation to resolve to an exact substring of supplied text., Provider-owned answer fields; server-owned model metadata is excluded., SynthesisDraft, _validate_answer_grounding()

### Community 132 - "youtube-context.ts"
Cohesion: 0.43
Nodes (6): download(), YoutubeVideoMetadata(), formatYoutubePublishedAt(), formatYoutubeViewCount(), stripYoutubeApiDataForExport(), youtubeThumbnailUrl()

### Community 133 - "test_jev_endpoint_maps_gateway_failure_to_502"
Cohesion: 0.24
Nodes (8): test_jev_endpoint_maps_gateway_failure_to_502(), mock_client(), test_jev_endpoint_reports_low_confidence_with_its_own_code(), mock_client(), test_jev_endpoint_returns_scored_result(), fake_fetch(), handler(), mock_client()

### Community 134 - "run_with_fallback"
Cohesion: 0.40
Nodes (6): Run an operation in priority order and return its result and provider., run_with_fallback(), test_run_with_fallback_reaches_third_provider_when_first_two_fail(), operation(), test_run_with_fallback_tries_next_provider_after_failure(), operation()

### Community 135 - "test_read_searches_related_coverage_from_the_linked_page_title"
Cohesion: 0.33
Nodes (4): test_read_prepends_link_seed_without_network(), fake_read(), test_read_searches_related_coverage_from_the_linked_page_title(), mock_async_client()

### Community 136 - "bell-toggle.tsx"
Cohesion: 0.29
Nodes (9): BellToggle(), BellToggleProps, BellToggleSize, liveAngle(), passOffset(), ringKeyframes(), SIZES, SPRING_UI (+1 more)

### Community 137 - "test_fast_check_collects_youtube_context_when_the_key_is_configured"
Cohesion: 0.40
Nodes (3): test_fast_check_collects_youtube_context_when_the_key_is_configured(), handler(), run()

### Community 138 - "_source_identity"
Cohesion: 0.50
Nodes (4): Preserve provider order with a strict site cap, not a Google rank claim., Canonicalize common URL variants for deduplication, never fetching., _select_diverse_sources(), _source_identity()

## Knowledge Gaps
- **367 isolated node(s):** `input`, `runtime`, `dynamic`, `headers`, `runtime` (+362 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 750 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `agent_status()` (2× useful, score=1.998072925) _(code changed — re-verify)_
- `Backend Environment Keys Configuration` (2× useful, score=1.998072925) _(code changed — re-verify)_
- `Next.js → FastAPI Proxy Route (6-B, app/api/fact-check/route.ts)` (2× useful, score=1.998072925)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `14. 알려진 한계와 기술 부채` connect `test_runtime_assembly.py` to `True or Not 고도화 기획서 v4`, `run_jev_fast_check`, `agent.ts`?**
  _High betweenness centrality (0.327) - this node is a cross-community bridge._
- **Why does `limitedText()` connect `agent.ts` to `test_runtime_assembly.py`?**
  _High betweenness centrality (0.299) - this node is a cross-community bridge._
- **Why does `run_jev_fast_check()` connect `run_jev_fast_check` to `verification.py`, `Settings`, `run_with_fallback`, `runtime.py`, `search_tavily`, `FactCheckResult`, `main.py`, `search_sources`, `fetch_youtube_data`, `test_providers.py`, `asyncio`, `test_runtime_assembly.py`, `test_search.py`, `evaluate_claims_jev`, `ProviderCallError`, `fetch_public_text`?**
  _High betweenness centrality (0.193) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `LLMProvider` (e.g. with `synthesize_answer()` and `extract_claims()`) actually correct?**
  _`LLMProvider` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `make_runtime_adapters()` (e.g. with `JevError` and `extract()`) actually correct?**
  _`make_runtime_adapters()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `ProviderCallError` (e.g. with `extract_claims()` and `extract_image_claims()`) actually correct?**
  _`ProviderCallError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `search_sources()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`search_sources()` has 2 INFERRED edges - model-reasoned connections that need verification._