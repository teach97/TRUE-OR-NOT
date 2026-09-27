# Graph Report - my-app  (2026-09-27)

## Corpus Check
- 143 files · ~120,194 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 28 file(s) not represented in the graph (top: .css 8, .log 7, (none) 6)

## Summary
- 1676 nodes · 3237 edges · 140 communities (109 shown, 31 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 351 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6f3cf803`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- contracts.py
- LLMProvider
- verification.py
- runtime.py
- sources.py
- build_workflow
- Four-Node LangGraph Runtime (extracting→searching→reading→verifying)
- search_tavily
- fact-check-dashboard.tsx
- test_source_fetch.py
- probe-recovery.py
- main.py
- providers.py
- fetch_youtube_data
- ref_node_assert
- test_providers.py
- FactCheckDashboard
- make_runtime_adapters
- demo-state.ts
- agent.ts
- Response
- What You Must Do When Invoked
- fact-check-contract.ts
- FactCheckRequest
- stream_events
- search.py
- compilerOptions
- FactCheckResult
- evaluate_claims_jev
- test_jev.py
- fact-check-reply.ts
- lattice-loader.tsx
- Next.js Wordmark Logo
- border-glow.tsx
- test_runtime.py
- Backend Environment Keys Configuration
- Settings
- tech-text.tsx
- next
- answer_synthesis.py
- ProviderCallError
- package.json
- run_jev_fast_check
- public-source.ts
- search_sources
- floating-lines.tsx
- floating-lines-background.tsx
- scramble-text.tsx
- fact-check-client.ts
- Framework Route Modules
- home.tsx
- devDependencies
- root.tsx
- Q: jev 키 입력되있음 env에 AI_GATEWAY_API_KEY=; Vercel AI Gateway Jev
- SVG root 1080x174
- test_runtime_assembly.py
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
- asyncio
- fact-check/route.ts
- True or Not agent architecture
- Globe Icon 16x16
- Vercel Triangle Logo SVG in White
- AGENTS.md Next.js agent rules
- Installed Docs as Source of Truth
- FactCheckAnswer AnswerBlock Citation Section contract
- Grounded answer synthesis plan
- Shared contract app lib fact-check-contract.ts
- Floating Lines Background Component
- postcss.config.mjs
- Seven trust boundaries untrusted input citations grounding
- True or Not UI design direction
- True or Not UI verification record
- Seven verdict codes mostly_supported to contradicted
- True or Not advanced planning v2
- True or Not 고도화 기획서 v2
- Next.js Logo (next.svg)
- factlens-backend
- FactLens Evidence Workspace
- FactLens Evidence Workspace Snapshot 13:08
- FactLens Evidence Workspace Snapshot 13:11
- FactLens Evidence Workspace Snapshot 13:12
- FactLens Evidence Workspace Snapshot 13:14
- reader
- Globe Components and Clip Container
- Globe Layout and Meridian Grid
- FactLens frontend README
- FactLens frontend Next.js App Router TypeScript Tailwind
- Q: JEV 선택이 안 되고 8010에서 Errno 10048이 발생함
- Q: 지금 레이아웃이 이상해 애니메이션 위치도 이상한곳에 걸쳐지고
- Q: 지금 jev가 제대로 작동하지 않아
- safeSourceUrl
- Q: 점수 판정이 이상해
- _TextParser
- 12. API 계약 초안
- glide-select.tsx
- build_search_query
- graphify reference: extra exports and benchmark
- 19. 소개 문구와 데모 안내
- 9. 화면 설계
- test_intent_reply_requires_text
- test_fast_check_skips_search_when_the_link_reads_cleanly
- 15. QA와 수용 기준
- 6. 주장 추출과 검증 계획
- 8. 판정 정책
- graphify reference: query, path, explain
- 14. 보안·개인정보·이용 조건
- 4. MVP 범위와 단계별 확장
- 16. 팀 역할과 3일 실행 계획
- 1. 핵심 방향
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- test_structured_image_payload_shapes
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- extraction-spec.md
- itertools
- handler
- completed_response
- test_jev_endpoint_maps_gateway_failure_to_502
- _TitleParser
- jev/route.ts
- bell-toggle.tsx
- recovery_probe_app.py
- line-sidebar.tsx
- _gemini_schema

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 67 edges
2. `Settings` - 62 edges
3. `make_runtime_adapters()` - 52 edges
4. `ProviderCallError` - 47 edges
5. `search_sources()` - 43 edges
6. `synthesize_answer()` - 34 edges
7. `extract_claims()` - 29 edges
8. `ground_judgments()` - 29 edges
9. `verify_claims()` - 28 edges
10. `FactCheckDashboard()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `12.4 원문 위치 규약` --references--> `start()`  [INFERRED]
  docs/True or Not 고도화-기획서-v2.md → app/lib/server/route.test.mjs
- `Next.js Wordmark Logo` --semantically_similar_to--> `Path-Drawn Brand Wordmark`  [INFERRED] [semantically similar]
  public/next.svg → app/welcome/logo-light.svg
- `Backend Model Fallback Order (Gemini 3.8 Flash → Gemini 3.7 Flash → GPT-6 Luna)` --semantically_similar_to--> `LLM Fallback Chain (Gemini 3.8 Flash → Gemini 3.7 Flash → GPT-6 Luna)`  [INFERRED] [semantically similar]
  backend/README.md → HANDOFF.md
- `Backend Search & Verification Flow` --semantically_similar_to--> `Four-Node LangGraph Runtime (extracting→searching→reading→verifying)`  [INFERRED] [semantically similar]
  backend/README.md → HANDOFF.md
- `Verification Response Format Error State (검증 응답 형식 오류)` --conceptually_related_to--> `Citation Verification & Judgment Rules (5-C, ground_judgments)`  [INFERRED]
  .playwright-cli/page-2026-09-24T01-05-41-775Z.yml → HANDOFF.md

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
- **True or Not Workspace States (empty → error → result)** — _playwright_cli_page_2026_09_24t01_03_06_200z_true_or_not_workspace, _playwright_cli_page_2026_09_24t01_05_41_775z_true_or_not_workspace, _playwright_cli_page_2026_09_24t01_08_40_011z_true_or_not_workspace [INFERRED 0.75]
- **Answer Model Fallback Chain Agreed Across UI, HANDOFF, and README** — _playwright_cli_page_2026_09_24t01_03_06_200z_model_fallback_selector, handoff_llm_fallback_chain, backend_readme_model_fallback [INFERRED 0.95]
- **logo_light_composition** — logo_light_red_accent, logo_light_dark_dots, logo_light_wordmark [INFERRED 0.85]
- **public_globe_composition** — public_globe_globe_path, public_globe_clip_path, public_globe_wireframe [INFERRED 0.85]
- **public_next_composition** — public_next_n_mark, public_next_main_letterforms, public_next_js_suffix [INFERRED 0.85]

## Communities (140 total, 31 thin omitted)

### Community 0 - "contracts.py"
Cohesion: 0.17
Nodes (15): AgentStatus, AnswerCitation, _ContractModel, FactCheckAnswer, FactCheckProgressCitation, FactCheckProgressClaim, FactCheckProgressSource, FactCheckResponse (+7 more)

### Community 1 - "LLMProvider"
Cohesion: 0.22
Nodes (25): AsyncClient, Generate and validate a grounded answer, leaving provider retries to runtime., synthesize_answer(), LLMProvider, Offline tests for source-bounded, citation-grounded answer synthesis., source(), state_with_source(), test_eligible_sources_excludes_unverified_empty_and_youtube_and_bounds_text() (+17 more)

### Community 2 - "verification.py"
Cohesion: 0.06
Nodes (73): FactClaim, default_fact_score(), normalize_fact_score(), Evidence-grounded public score policy for fact-check claims., Return the public band for an inclusive 0–100 score., Preserve the model's reasoned score, clamped only to the 0-100 range. The…, Supply a compatible score when an older result omits the new field., score_band() (+65 more)

### Community 3 - "runtime.py"
Cohesion: 0.21
Nodes (10): Server settings and the assembled four-stage verification workflow., Request boundary compatible with the existing TypeScript request fields., Provider-independent graph. All real service adapters must be supplied…, collections_abc, dotenv, langgraph_graph, pathlib, pydantic (+2 more)

### Community 4 - "sources.py"
Cohesion: 0.14
Nodes (16): AbstractResolver, aiohttp, aiohttp_abc, checked_url(), _generic_title(), html_sections(), html_title(), _is_japanese_page_text() (+8 more)

### Community 5 - "build_workflow"
Cohesion: 0.06
Nodes (21): test_workflow_preserves_link_and_image_state_keys(), parametrize, Real LangGraph via HTTP boundary; adapters contain offline fixtures only., test_graph_failure_returns_safe_error(), stage(), test_invalid_http_input_is_safe_and_never_runs_graph(), test_post_rejects_malformed_result_contract(), test_post_runs_graph_and_returns_only_result() (+13 more)

### Community 6 - "Four-Node LangGraph Runtime (extracting→searching→reading→verifying)"
Cohesion: 0.06
Nodes (45): Document Input Panel (원문 입력 + 확인 요청), Evidence-First Verification Principle (결론보다, 근거를 먼저), FactLens (팩트렌즈) Brand, FactLens Evidence Workspace (09-21, settings check failed), Synthetic Example Documents (가상 도시의 문화 행사), FactLens Evidence Workspace (09-21, server check pending), External Transmission & YouTube Data API Consent, Answer Model Fallback Selector (Gemini 3.8 Flash → Gemini 3.7 Flash → GPT-6 Luna Max) (+37 more)

### Community 7 - "search_tavily"
Cohesion: 0.20
Nodes (15): AsyncClient, Tavily web search discovery. Optional; LLM search remains the fallback., Search each checkable claim once with Tavily basic depth (1 credit each)., Tavily could not serve this request; the caller falls back., search_tavily(), TavilyUnavailable, Tavily search discovery; no live traffic (all transports mocked)., run_search() (+7 more)

### Community 8 - "fact-check-dashboard.tsx"
Cohesion: 0.07
Nodes (23): BlurText(), CountUp(), CountUpProps, base, DEMO_FOCUS, DEMO_TEXT, demoPreview, documents (+15 more)

### Community 9 - "test_source_fetch.py"
Cohesion: 0.16
Nodes (14): parametrize, Deterministic HTTP response fixtures; resolver safety tested separately., run(), Session, test_low_reach_youtube_source_is_dropped_from_results(), youtube_reader(), test_oversized_page_is_truncated_and_parsed_instead_of_rejected(), test_read_follows_same_origin_meta_refresh() (+6 more)

### Community 10 - "probe-recovery.py"
Cohesion: 0.07
Nodes (39): blocking_extract(), cancellation_state(), InstrumentedGraph, get, Explicit integration-test entry point ONLY; never imported by main/runtime. No…, record(), module(), parametrize (+31 more)

### Community 11 - "main.py"
Cohesion: 0.11
Nodes (23): _code_revision(), fact_check(), fact_check_jev(), fact_check_stream(), health(), HealthStatus, intent(), IntentClaim (+15 more)

### Community 12 - "providers.py"
Cohesion: 0.12
Nodes (28): classify_intent(), IntentDecision, Any, AsyncClient, BaseModel, Cheap intent gate: verify with the pipeline or answer conversationally., Return a verify/reply decision; invalid model output is a retryable failure., _endpoint_and_headers() (+20 more)

### Community 13 - "fetch_youtube_data"
Cohesion: 0.12
Nodes (25): Offline YouTube Data API contract tests; no Google credentials or traffic., test_comments_unavailable_keeps_video_title_without_exposing_provider_error(), run(), test_fetches_official_video_title_and_bounded_plain_text_comments(), handler(), run(), test_ignores_malformed_youtube_metadata_without_rejecting_comments(), run() (+17 more)

### Community 14 - "ref_node_assert"
Cohesion: 0.11
Nodes (15): ref_node_assert, ref_node_fs, ref_node_test, ref_node_url, observations, responses, state(), waitCounts() (+7 more)

### Community 15 - "test_providers.py"
Cohesion: 0.15
Nodes (17): agent_status(), Report whether the real four-stage workflow can be constructed., configured_model_options(), configured_providers(), _openai_schema(), clean(), providers_for_preference(), Normalize Pydantic schemas for OpenAI strict structured output. (+9 more)

### Community 16 - "FactCheckDashboard"
Cohesion: 0.12
Nodes (24): ChatIntent, CLAIM_PATTERNS, classifyChatInput(), describeHistory(), EARLY_META, FOLLOW_UP_PATTERNS, HELP_PATTERNS, IDENTITY_PATTERNS (+16 more)

### Community 17 - "make_runtime_adapters"
Cohesion: 0.06
Nodes (50): extract_claims(), extract_image_claims(), extract_page_claims(), ExtractedClaim, Extraction, ImageObservation, _project_extracted_claims(), AsyncClient (+42 more)

### Community 18 - "demo-state.ts"
Cohesion: 0.23
Nodes (13): Action, Claim, createPreview(), initialState, State, transition(), TrustIndex(), FACT_SCORE_LABELS (+5 more)

### Community 19 - "agent.ts"
Cohesion: 0.14
Nodes (19): FactClaim, FactEvidence, VerdictCode, canonical(), extractClaims(), extractionSchema, format(), JsonObject (+11 more)

### Community 21 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 22 - "fact-check-contract.ts"
Cohesion: 0.10
Nodes (21): download(), YoutubeVideoMetadata(), AgentStage, AgentStatus, AnswerSection, AttachedImage, FACT_CHECK_MODEL, FACT_CHECK_REASONING (+13 more)

### Community 23 - "FactCheckRequest"
Cohesion: 0.09
Nodes (18): FactCheckRequest, ImageAttachment, BaseModel, model_validator, parametrize, test_request_preserves_original_text(), test_request_rejects_invalid_input(), test_request_requires_all_contract_fields() (+10 more)

### Community 24 - "stream_events"
Cohesion: 0.13
Nodes (16): build_progress_preview(), build_progress_sources(), Expose only source identity and access state before final answer assembly., Build an early, strictly projected claim summary from validated evidence., encode(), NDJSON boundary: only stage labels and validated final results are public., Propagate cancellation and close the graph iterator on every exit path., stream_events() (+8 more)

### Community 25 - "search.py"
Cohesion: 0.14
Nodes (23): candidate_url(), is_japanese_candidate(), is_unreliable_candidate(), _normalized_host(), _project_candidates(), Candidate discovery only; pending sources and snippets are not evidence. URL…, Classify a URL for display and diversity selection, not truth scoring., Reject Japanese-domain or Japanese-script pages across search providers. (+15 more)

### Community 26 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 27 - "FactCheckResult"
Cohesion: 0.29
Nodes (16): FactCheckResult, grounded_answer(), parametrize, Final Python contract tests; no provider calls., result_payload(), test_evidence_may_expose_only_a_bounded_matching_article_section(), test_final_contract_accepts_frontend_shape_and_wrapper(), test_final_contract_rejects_broken_links_or_unverified_evidence() (+8 more)

### Community 28 - "evaluate_claims_jev"
Cohesion: 0.16
Nodes (19): evaluate_claims_jev(), JevError, _parse_strength(), _parse_verdict(), Any, AsyncClient, RuntimeError, Jev (TypeSafe System One) verdicts through Vercel AI Gateway. The gateway API… (+11 more)

### Community 29 - "test_jev.py"
Cohesion: 0.09
Nodes (30): jev_response(), _jev_runtime_state(), Jev verdicts through AI Gateway; no live traffic (all transports mocked)., handler(), test_fast_check_llm_search_honors_the_selected_model(), handler(), run(), test_fast_check_propagates_jev_failure_without_llm_fallback() (+22 more)

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

### Community 34 - "test_runtime.py"
Cohesion: 0.10
Nodes (23): get_workflow(), Build the provider-backed graph only when a server-side key is configured., build_extraction_graph(), load_settings(), Stage, Read the backend-local file without mutating process environment., End after extraction; do not simulate search, sources, or judgments., Isolated settings and extraction graph tests; no paid API calls. (+15 more)

### Community 35 - "Backend Environment Keys Configuration"
Cohesion: 0.16
Nodes (14): Backend Environment Keys Configuration, FactLens Backend Fact-check API, Search Verification Flow Max 3 Claims 6 Sources, Fact-check Streaming Endpoint, Five Stage Search Improvement Pipeline, Free Google Organic Search via SerpApi, Multi-LLM Fallback Priority Order, Duplicate Link and Japanese Search Result Correction (+6 more)

### Community 36 - "Settings"
Cohesion: 0.17
Nodes (18): BaseModel, Settings, main(), Offline API boundary checks; no provider calls., test_health_and_status_do_not_claim_provider_readiness(), test_request_rejects_unknown_model_preference(), test_status_reports_gemini_fallback_when_openai_is_missing(), test_status_reports_gpt6_luna_when_only_openai_is_configured() (+10 more)

### Community 37 - "tech-text.tsx"
Cohesion: 0.20
Nodes (13): approach(), Art, Box, Glyph, hexToRgb(), noise(), rgba(), Settings (+5 more)

### Community 38 - "next"
Cohesion: 0.15
Nodes (6): app_globals, metadata, metadata, metadata, nextConfig, next

### Community 39 - "answer_synthesis.py"
Cohesion: 0.13
Nodes (20): eligible_sources(), _limit_sections_to_source_breadth(), _project_claims(), Any, BaseModel, model_validator, Synthesize a user-facing answer from verified source text only., Build a minimal JSON-safe input; never forward raw source/search records. (+12 more)

### Community 40 - "ProviderCallError"
Cohesion: 0.18
Nodes (15): ProviderCallError, RuntimeError, A provider attempt failed and the next configured provider may retry., Run an operation in priority order and return its result and provider., run_with_fallback(), test_invalid_citation_from_first_provider_retries_and_uses_next_provider_metadata(), run(), Safe diagnostics for failed provider fallbacks. (+7 more)

### Community 41 - "package.json"
Cohesion: 0.15
Nodes (12): name, private, type, postcss, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+4 more)

### Community 42 - "run_jev_fast_check"
Cohesion: 0.18
Nodes (13): read(), youtube_reader(), AsyncClient, Truncate to a UTF-16 unit budget without splitting astral characters., Search and read evidence, then return Jev's score-only claim result., _result_warnings(), run_jev_fast_check(), search_once() (+5 more)

### Community 43 - "public-source.ts"
Cohesion: 0.26
Nodes (10): Address, fetchPublicText(), htmlToText(), publicAddress(), resolvePublicUrl(), Resolver, ref_node_dns, ref_node_http (+2 more)

### Community 44 - "search_sources"
Cohesion: 0.11
Nodes (21): AsyncClient, search_sources(), test_nonfacts_skip_network(), run(), test_prediction_claims_are_searched_with_primary_query_in_provider_order(), run(), test_search_collects_deduplicated_candidates_without_evidence(), run() (+13 more)

### Community 45 - "floating-lines.tsx"
Cohesion: 0.22
Nodes (9): DEFAULT_BOTTOM_WAVE_POSITION, DEFAULT_ENABLED_WAVES, DEFAULT_LINE_COUNT, DEFAULT_LINE_DISTANCE, FloatingLines(), FloatingLinesProps, hexToVec3(), WavePosition (+1 more)

### Community 46 - "floating-lines-background.tsx"
Cohesion: 0.22
Nodes (6): BackgroundBoundary, FloatingLines, FloatingLinesBackground(), floatingLinesDistance, floatingLinesGradient, floatingLinesWaves

### Community 47 - "scramble-text.tsx"
Cohesion: 0.36
Nodes (9): getRevealOrder(), randomCharacter(), randomizeText(), ScrambleRun, ScrambleText(), resetVisual(), startRun(), writeVisual() (+1 more)

### Community 48 - "fact-check-client.ts"
Cohesion: 0.15
Nodes (19): FactCheckError, Options, readFactCheckStream(), line(), validAnswer(), validEvidenceSection(), validProgressCitation(), validProgressClaim() (+11 more)

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

### Community 55 - "test_runtime_assembly.py"
Cohesion: 0.07
Nodes (36): insufficient_answer(), Return a fixed answer that makes no unsupported assertions., build_fact_check_result(), build_runtime_workflow(), synthesizing(), _normalize_source(), Project internal source state onto the public TypeScript contract., Validate and assemble the only result shape exposed by the API. (+28 more)

### Community 56 - "globe.svg"
Cohesion: 0.33
Nodes (7): Clip path definition, Default template icon, globe.svg, Globe wireframe path, Monochrome gray variant, SVG root 16x16, Globe wireframe motif

### Community 57 - "ref_react_router_dev"
Cohesion: 0.33
Nodes (3): ref_react_router_dev, ref_tailwindcss_vite, ref_vite

### Community 58 - "dependencies"
Cohesion: 0.33
Nodes (6): dependencies, motion, next, react, react-dom, three

### Community 59 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, start, typecheck

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

### Community 70 - "asyncio"
Cohesion: 0.14
Nodes (11): asyncio, Offline failure, safety and empty-result tests., graph(), parametrize, Offline streaming tests; fixtures do not represent real verification., test_stream_endpoint_emits_ordered_stages_and_valid_result(), test_stream_errors_are_safe(), run() (+3 more)

### Community 71 - "fact-check/route.ts"
Cohesion: 0.19
Nodes (11): backend(), dynamic, error(), GET(), headers, MODEL_OPTIONS, POST(), runtime (+3 more)

### Community 72 - "True or Not agent architecture"
Cohesion: 0.67
Nodes (3): True or Not agent architecture, Gemini Interactions API docs citation, GPT-6 Luna model docs citation

### Community 73 - "Globe Icon 16x16"
Cohesion: 0.67
Nodes (3): Globe Grid Lines (Meridians & Parallels), Globe Outer Ring, Globe Icon 16x16

### Community 74 - "Vercel Triangle Logo SVG in White"
Cohesion: 0.67
Nodes (3): Vercel Brand Mark Purpose for Deployment Branding, White Filled Triangle Mark viewBox 1155x1000, Vercel Triangle Logo SVG in White

### Community 87 - "True or Not 고도화 기획서 v2"
Cohesion: 0.14
Nodes (13): 10. 현재 프론트엔드와의 차이 및 이행 우선순위, 11. 기술 구성 제안, 13. 상태 관리와 비동기 실행, 17. 구현 백로그, 18. 미확정 사항과 착수 전 결정, 20. 기준 자료와 문서 이력, 2. 문제 정의와 사용자 시나리오, 3. 제품 원칙 (+5 more)

### Community 95 - "reader"
Cohesion: 0.12
Nodes (10): test_read_node_attempts_all_sources_concurrently_even_after_failure(), reader(), test_read_node_deduplicates_distinct_search_urls_that_resolve_to_the_same_page(), test_read_node_fetches_slow_sources_in_parallel(), test_read_node_keeps_bounded_article_sections_for_the_verified_source(), reader(), test_read_node_keeps_candidate_order_when_slow_sources_finish_first(), test_read_node_records_failure_without_inventing_text() (+2 more)

### Community 100 - "Q: JEV 선택이 안 되고 8010에서 Errno 10048이 발생함"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: JEV 선택이 안 되고 8010에서 Errno 10048이 발생함, Source Nodes

### Community 101 - "Q: 지금 레이아웃이 이상해 애니메이션 위치도 이상한곳에 걸쳐지고"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 지금 레이아웃이 이상해 애니메이션 위치도 이상한곳에 걸쳐지고, Source Nodes

### Community 102 - "Q: 지금 jev가 제대로 작동하지 않아"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 지금 jev가 제대로 작동하지 않아, Source Nodes

### Community 103 - "safeSourceUrl"
Cohesion: 0.16
Nodes (10): faviconUrlFor(), safeSourceUrl(), insufficientAnswer, result, verifiedSource, firstUrl(), JevSourceList(), ProgressReply() (+2 more)

### Community 104 - "Q: 점수 판정이 이상해"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 점수 판정이 이상해, Source Nodes

### Community 106 - "12. API 계약 초안"
Cohesion: 0.29
Nodes (7): start(), 12.1 엔드포인트, 12.2 입력 예시, 12.3 최소 데이터 모델, 12.4 원문 위치 규약, 12.5 오류 분류, 12. API 계약 초안

### Community 107 - "glide-select.tsx"
Cohesion: 0.31
Nodes (8): GlideSelect(), GlideSelectOption, GlideSelectProps, labelText(), nextEnabled(), normalizeOption(), OptionInput, SIZES

### Community 108 - "build_search_query"
Cohesion: 0.40
Nodes (5): build_search_query(), Conservative fallback when extraction did not supply semantic keywords., parametrize, test_build_search_query_keeps_entity_and_year_from_forecast_question(), test_query_fallback_preserves_negation_names_and_numbers()

### Community 109 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 110 - "19. 소개 문구와 데모 안내"
Cohesion: 0.40
Nodes (5): 19. 소개 문구와 데모 안내, 검증 결과 하단 문구, 데모 고지 권장 문구, 서비스 소개, 짧은 소개

### Community 111 - "9. 화면 설계"
Cohesion: 0.40
Nodes (5): 9.1 정보 구조, 9.2 주장 카드, 9.3 요약 지표, 9.4 접근성·반응형, 9. 화면 설계

### Community 112 - "test_intent_reply_requires_text"
Cohesion: 0.33
Nodes (6): decision_response(), test_intent_reply_requires_text(), run_empty(), run_reply(), test_intent_verify_passes_focus_through(), run()

### Community 113 - "test_fast_check_skips_search_when_the_link_reads_cleanly"
Cohesion: 0.53
Nodes (5): test_fast_check_skips_search_when_the_link_reads_cleanly(), handler(), jev_handler(), router(), run()

### Community 114 - "15. QA와 수용 기준"
Cohesion: 0.50
Nodes (4): 15. QA와 수용 기준, 출시 조건, 테스트 케이스, 평가 방법

### Community 115 - "6. 주장 추출과 검증 계획"
Cohesion: 0.50
Nodes (4): 6.1 분류 체계, 6.2 주장 구조, 6.3 검색 계획, 6. 주장 추출과 검증 계획

### Community 116 - "8. 판정 정책"
Cohesion: 0.50
Nodes (4): 8.1 결과 분류, 8.2 겹치는 경우의 결정 규칙, 8.3 근거 충족 규칙, 8. 판정 정책

### Community 117 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 118 - "14. 보안·개인정보·이용 조건"
Cohesion: 0.67
Nodes (3): 14. 보안·개인정보·이용 조건, URL과 외부 콘텐츠, 입력·저장

### Community 119 - "4. MVP 범위와 단계별 확장"
Cohesion: 0.67
Nodes (3): 4.1 3일 MVP 필수 범위, 4.2 MVP 이후, 4. MVP 범위와 단계별 확장

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

### Community 126 - "test_structured_image_payload_shapes"
Cohesion: 1.00
Nodes (3): test_structured_image_payload_shapes(), handler(), run()

### Community 131 - "handler"
Cohesion: 0.17
Nodes (10): parametrize, test_candidates_filter_unsafe_urls_and_limit_results(), run(), test_completed_empty_search_is_not_a_verdict(), run(), test_question_claims_are_searchable(), run(), test_search_fails_closed() (+2 more)

### Community 132 - "completed_response"
Cohesion: 0.23
Nodes (12): completed_response(), draft(), multi_section_draft(), parametrize, handler(), handler(), handler(), handler() (+4 more)

### Community 133 - "test_jev_endpoint_maps_gateway_failure_to_502"
Cohesion: 0.24
Nodes (8): test_jev_endpoint_maps_gateway_failure_to_502(), mock_client(), test_jev_endpoint_reports_low_confidence_with_its_own_code(), mock_client(), test_jev_endpoint_returns_scored_result(), fake_fetch(), handler(), mock_client()

### Community 134 - "_TitleParser"
Cohesion: 0.18
Nodes (4): Reader result with optional metadata and backwards-compatible unpacking., SourceReadResult, _TitleParser, HTMLParser

### Community 135 - "jev/route.ts"
Cohesion: 0.27
Nodes (7): backend(), dynamic, error(), headers, POST(), runtime, input

### Community 136 - "bell-toggle.tsx"
Cohesion: 0.29
Nodes (9): BellToggle(), BellToggleProps, BellToggleSize, liveAngle(), passOffset(), ringKeyframes(), SIZES, SPRING_UI (+1 more)

### Community 137 - "recovery_probe_app.py"
Cohesion: 0.22
Nodes (6): get, post, TEST ONLY deterministic recovery app. Never imported by runtime/main., recover(), status(), verify()

### Community 138 - "line-sidebar.tsx"
Cohesion: 0.29
Nodes (6): Falloff, FALLOFF_CURVES, LineSidebar(), LineSidebarItem, LineSidebarProps, LineSidebarStyle

### Community 139 - "_gemini_schema"
Cohesion: 0.67
Nodes (3): _gemini_schema(), clean(), Remove JSON Schema keywords unsupported by Gemini structured output.

## Knowledge Gaps
- **338 isolated node(s):** `input`, `runtime`, `dynamic`, `headers`, `runtime` (+333 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 703 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `agent_status()` (2× useful, score=1.998072925) _(code changed — re-verify)_
- `Backend Environment Keys Configuration` (2× useful, score=1.998072925) _(code changed — re-verify)_
- `Next.js → FastAPI Proxy Route (6-B, app/api/fact-check/route.ts)` (2× useful, score=1.998072925)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_runtime_adapters()` connect `make_runtime_adapters` to `LLMProvider`, `verification.py`, `runtime.py`, `Settings`, `test_runtime.py`, `answer_synthesis.py`, `ProviderCallError`, `search_tavily`, `run_jev_fast_check`, `search_sources`, `fetch_youtube_data`, `test_providers.py`, `FactCheckRequest`, `test_runtime_assembly.py`, `search.py`, `evaluate_claims_jev`, `test_jev.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `Settings` connect `Settings` to `test_runtime.py`, `runtime.py`, `test_jev_endpoint_maps_gateway_failure_to_502`, `asyncio`, `recovery_probe_app.py`, `run_jev_fast_check`, `probe-recovery.py`, `test_providers.py`, `make_runtime_adapters`, `test_fast_check_skips_search_when_the_link_reads_cleanly`, `FactCheckRequest`, `test_runtime_assembly.py`, `test_jev.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `LLMProvider` connect `LLMProvider` to `verification.py`, `completed_response`, `Settings`, `answer_synthesis.py`, `ProviderCallError`, `providers.py`, `search_sources`, `test_providers.py`, `test_intent_reply_requires_text`, `make_runtime_adapters`, `FactCheckRequest`, `search.py`, `test_structured_image_payload_shapes`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `LLMProvider` (e.g. with `synthesize_answer()` and `extract_claims()`) actually correct?**
  _`LLMProvider` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `make_runtime_adapters()` (e.g. with `JevError` and `extract()`) actually correct?**
  _`make_runtime_adapters()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `ProviderCallError` (e.g. with `extract_claims()` and `extract_image_claims()`) actually correct?**
  _`ProviderCallError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `search_sources()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`search_sources()` has 2 INFERRED edges - model-reasoned connections that need verification._