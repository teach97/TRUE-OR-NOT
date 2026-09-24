# Graph Report - my-app  (2026-09-24)

## Corpus Check
- 124 files · ~98,988 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: (none) 5, .log 5, .css 5)

## Summary
- 1552 nodes · 3084 edges · 125 communities (97 shown, 28 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 325 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `85965493`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- contracts.py
- synthesize_answer
- verification.py
- search_sources
- sources.py
- build_workflow
- Four-Node LangGraph Runtime (extracting→searching→reading→verifying)
- search_google_free
- fact-check-dashboard.tsx
- test_source_fetch.py
- probe-recovery.py
- main.py
- request_structured
- fetch_youtube_data
- ref_node_assert
- extraction.py
- FactCheckDashboard
- extract_claims
- demo-state.ts
- agent.ts
- stream_events
- vector-wordmark.tsx
- fact-check-contract.ts
- FactCheckRequest
- score_band
- search.py
- compilerOptions
- test_contracts.py
- line-sidebar.tsx
- evaluate_claims_jev
- fact-check-reply.ts
- lattice-loader.tsx
- Next.js Wordmark Logo
- classify_intent
- _gemini_schema
- Backend Environment Keys Configuration
- Settings
- run
- next
- answer_synthesis.py
- ProviderCallError
- package.json
- providers.py
- test_runtime.py
- handler
- floating-lines.tsx
- floating-lines-background.tsx
- scramble-text.tsx
- fact-check-client.ts
- Framework Route Modules
- home.tsx
- devDependencies
- root.tsx
- fact-check/route.ts
- SVG root 1080x174
- test_runtime_assembly.py
- globe.svg
- ref_react_router_dev
- dependencies
- scripts
- Document File Icon
- intent/route.ts
- Dark Mode Logo SVG
- test_search.py
- eslint.config.mjs
- next-env.d.ts
- Browser Window Icon SVG in Gray
- Dashboard demo-state fixture shader implementation and checks
- Declarative Router Shape
- RSC Route Module Differences
- runtime.py
- make_runtime_adapters
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
- test_sources.py
- Globe Components and Clip Container
- Globe Layout and Meridian Grid
- FactLens frontend README
- FactLens frontend Next.js App Router TypeScript Tailwind
- public-source.ts
- LLMProvider
- recovery_probe_app.py
- youtube-context.ts
- jev/route.ts
- test_execution.py
- 12. API 계약 초안
- glide-select.tsx
- test_all_synthesis_providers_failing_preserves_verified_result
- test_forecast_synthesis_preserves_prediction_and_citations
- 19. 소개 문구와 데모 안내
- 9. 화면 설계
- probe-stage7.mjs
- test_post_runs_graph_and_returns_only_result
- 15. QA와 수용 기준
- 6. 주장 추출과 검증 계획
- 8. 판정 정책
- probe-cancellation.mjs
- 14. 보안·개인정보·이용 조건
- 4. MVP 범위와 단계별 확장
- 16. 팀 역할과 3일 실행 계획
- 1. 핵심 방향
- test_extractor_rejects_unsafe_outputs
- test_search_selects_diverse_source_types_instead_of_one_publisher
- test_search_still_rejects_token_limited_response_without_completed_search

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 67 edges
2. `make_runtime_adapters()` - 51 edges
3. `ProviderCallError` - 45 edges
4. `Settings` - 45 edges
5. `search_sources()` - 41 edges
6. `synthesize_answer()` - 34 edges
7. `search_google_free()` - 30 edges
8. `extract_claims()` - 29 edges
9. `ground_judgments()` - 29 edges
10. `verify_claims()` - 28 edges

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

## Communities (125 total, 28 thin omitted)

### Community 0 - "contracts.py"
Cohesion: 0.23
Nodes (14): AgentStatus, AnswerCitation, _ContractModel, FactCheckAnswer, FactCheckProgressCitation, FactCheckProgressClaim, FactCheckProgressSource, FactCheckResponse (+6 more)

### Community 1 - "synthesize_answer"
Cohesion: 0.12
Nodes (40): insufficient_answer(), AsyncClient, Generate and validate a grounded answer, leaving provider retries to runtime., Return a fixed answer that makes no unsupported assertions., synthesize_answer(), completed_response(), draft(), multi_section_draft() (+32 more)

### Community 2 - "verification.py"
Cohesion: 0.07
Nodes (60): html_text(), test_verify_claims_jev_builds_score_only_results(), run(), test_verify_claims_jev_without_sources_never_calls_gateway(), run(), claim(), Offline citation-grounding and judgment tests; no provider traffic., test_context_mismatch_is_reported_as_missing_context() (+52 more)

### Community 3 - "search_sources"
Cohesion: 0.17
Nodes (15): AsyncClient, search_sources(), parametrize, Offline failure, safety and empty-result tests., test_candidates_filter_unsafe_urls_and_limit_results(), run(), test_completed_empty_search_is_not_a_verdict(), run() (+7 more)

### Community 4 - "sources.py"
Cohesion: 0.06
Nodes (24): AbstractResolver, aiohttp, aiohttp_abc, checked_url(), _generic_title(), html_sections(), html_title(), _is_japanese_page_text() (+16 more)

### Community 5 - "build_workflow"
Cohesion: 0.13
Nodes (11): test_workflow_preserves_link_and_image_state_keys(), Offline orchestration tests; fixtures are not real fact-check results., test_provider_failure_stops_graph_without_fabricated_result(), test_updates_stream_uses_five_frontend_stage_names(), collect(), stage(), test_workflow_runs_stages_in_order_and_passes_state(), build_workflow() (+3 more)

### Community 6 - "Four-Node LangGraph Runtime (extracting→searching→reading→verifying)"
Cohesion: 0.06
Nodes (45): Document Input Panel (원문 입력 + 확인 요청), Evidence-First Verification Principle (결론보다, 근거를 먼저), FactLens (팩트렌즈) Brand, FactLens Evidence Workspace (09-21, settings check failed), Synthetic Example Documents (가상 도시의 문화 행사), FactLens Evidence Workspace (09-21, server check pending), External Transmission & YouTube Data API Consent, Answer Model Fallback Selector (Gemini 3.8 Flash → Gemini 3.7 Flash → GPT-6 Luna Max) (+37 more)

### Community 7 - "search_google_free"
Cohesion: 0.09
Nodes (32): FreeSearchUnavailable, _json_response(), AsyncClient, Optional SerpApi Google organic discovery, restricted to a free account., Safe failure code for the optional, free-only search path., Use only an account confirmed to be on the free plan with quota left., search_google_free(), main() (+24 more)

### Community 8 - "fact-check-dashboard.tsx"
Cohesion: 0.08
Nodes (23): BlurText(), CountUp(), CountUpProps, base, DEMO_FOCUS, DEMO_TEXT, demoPreview, documents (+15 more)

### Community 9 - "test_source_fetch.py"
Cohesion: 0.08
Nodes (22): parametrize, Deterministic HTTP response fixtures; resolver safety tested separately., Response, run(), Session, test_low_reach_youtube_source_is_dropped_from_results(), youtube_reader(), test_read_follows_same_origin_meta_refresh() (+14 more)

### Community 10 - "probe-recovery.py"
Cohesion: 0.10
Nodes (26): blocking_extract(), cancellation_state(), InstrumentedGraph, get, Explicit integration-test entry point ONLY; never imported by main/runtime. No…, record(), os, pathlib (+18 more)

### Community 11 - "main.py"
Cohesion: 0.09
Nodes (31): agent_status(), _code_revision(), fact_check(), fact_check_jev(), fact_check_stream(), get_workflow(), health(), HealthStatus (+23 more)

### Community 12 - "request_structured"
Cohesion: 0.25
Nodes (15): _endpoint_and_headers(), _gemini_text(), _openai_text(), Any, AsyncClient, Call a provider's structured-output endpoint and return only model text., Build the multimodal input parts for each provider's wire format., Call a provider's structured-output endpoint with an attached image. (+7 more)

### Community 13 - "fetch_youtube_data"
Cohesion: 0.12
Nodes (25): Offline YouTube Data API contract tests; no Google credentials or traffic., test_comments_unavailable_keeps_video_title_without_exposing_provider_error(), run(), test_fetches_official_video_title_and_bounded_plain_text_comments(), handler(), run(), test_ignores_malformed_youtube_metadata_without_rejecting_comments(), run() (+17 more)

### Community 14 - "ref_node_assert"
Cohesion: 0.13
Nodes (11): insufficientAnswer, result, verifiedSource, ref_node_assert, ref_node_fs, ref_node_test, ref_node_url, observations (+3 more)

### Community 15 - "extraction.py"
Cohesion: 0.22
Nodes (12): extract_image_claims(), extract_page_claims(), ExtractedClaim, Extraction, ImageObservation, _project_extracted_claims(), AsyncClient, BaseModel (+4 more)

### Community 16 - "FactCheckDashboard"
Cohesion: 0.12
Nodes (21): ChatIntent, CLAIM_PATTERNS, classifyChatInput(), describeHistory(), EARLY_META, FOLLOW_UP_PATTERNS, HELP_PATTERNS, isFollowUpText() (+13 more)

### Community 17 - "extract_claims"
Cohesion: 0.17
Nodes (16): extract_claims(), Return a LangGraph state update; callers own the client and credential., Offline provider transport fixtures, never real model responses., test_extractor_drops_invented_claim_without_fabricating_source_text(), run(), test_extractor_keeps_forecast_and_returns_search_keywords_separately(), handler(), run() (+8 more)

### Community 18 - "demo-state.ts"
Cohesion: 0.21
Nodes (14): Action, Claim, createPreview(), initialState, State, transition(), TrustIndex(), FACT_SCORE_BANDS (+6 more)

### Community 19 - "agent.ts"
Cohesion: 0.13
Nodes (21): AgentEvent, AttachedImage, FactClaim, FactEvidence, VerdictCode, canonical(), extractClaims(), extractionSchema (+13 more)

### Community 20 - "stream_events"
Cohesion: 0.15
Nodes (14): build_progress_preview(), build_progress_sources(), Expose only source identity and access state before final answer assembly., Build an early, strictly projected claim summary from validated evidence., encode(), NDJSON boundary: only stage labels and validated final results are public., Propagate cancellation and close the graph iterator on every exit path., stream_events() (+6 more)

### Community 21 - "vector-wordmark.tsx"
Cohesion: 0.17
Nodes (21): Atlas, buildAtlas(), clamp(), compile(), FontSpec, fontString(), fract(), HANDLE_DEFAULTS (+13 more)

### Community 22 - "fact-check-contract.ts"
Cohesion: 0.11
Nodes (17): AgentStage, AgentStatus, AnswerBlock, AnswerSection, FACT_CHECK_MODEL, FACT_CHECK_REASONING, FactSource, MODEL_OPTIONS (+9 more)

### Community 23 - "FactCheckRequest"
Cohesion: 0.10
Nodes (14): FactCheckRequest, ImageAttachment, BaseModel, model_validator, Link and image attachment paths; no external traffic (all transports mocked)., test_extract_image_claims_replaces_state_text(), test_extract_page_claims_replaces_state_text(), test_extract_url_only_fetches_page() (+6 more)

### Community 24 - "score_band"
Cohesion: 0.15
Nodes (16): FactClaim, model_validator, default_fact_score(), normalize_fact_score(), Evidence-grounded public score policy for fact-check claims., Return the public band for an inclusive 0–100 score., Preserve the model's reasoned score, clamped only to the 0-100 range. The…, Supply a compatible score when an older result omits the new field. (+8 more)

### Community 25 - "search.py"
Cohesion: 0.16
Nodes (17): read(), youtube_reader(), candidate_url(), is_japanese_candidate(), is_unreliable_candidate(), _normalized_host(), origin_group_for_url(), Candidate discovery only; pending sources and snippets are not evidence. URL… (+9 more)

### Community 26 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 27 - "test_contracts.py"
Cohesion: 0.29
Nodes (16): FactCheckResult, grounded_answer(), parametrize, Final Python contract tests; no provider calls., result_payload(), test_evidence_may_expose_only_a_bounded_matching_article_section(), test_final_contract_accepts_frontend_shape_and_wrapper(), test_final_contract_rejects_broken_links_or_unverified_evidence() (+8 more)

### Community 28 - "line-sidebar.tsx"
Cohesion: 0.29
Nodes (6): Falloff, FALLOFF_CURVES, LineSidebar(), LineSidebarItem, LineSidebarProps, LineSidebarStyle

### Community 29 - "evaluate_claims_jev"
Cohesion: 0.07
Nodes (42): evaluate_claims_jev(), JevError, _parse_strength(), _parse_verdict(), Any, AsyncClient, RuntimeError, Jev (TypeSafe System One) verdicts through Vercel AI Gateway. The gateway API… (+34 more)

### Community 30 - "fact-check-reply.ts"
Cohesion: 0.12
Nodes (20): safeSourceUrl(), AnswerBlockView(), AnswerOverview(), firstUrl(), ProgressReply(), ProgressSourceList(), YoutubeThumbnail(), AnswerCitationDisplay (+12 more)

### Community 31 - "lattice-loader.tsx"
Cohesion: 0.16
Nodes (14): DEFAULT_PATTERN, formatElapsed(), GridSize, LatticeLoader(), LatticeLoaderProps, LoaderStatus, LoaderStyle, MARKS (+6 more)

### Community 32 - "Next.js Wordmark Logo"
Cohesion: 0.17
Nodes (15): Geometric Brand Emblem (Red & Black Circles), Light Theme Variant (Dark Glyphs on Light Background), logo-light.svg light-mode branding logo, Path-Drawn Brand Wordmark, Next.js Framework Brand, Default template branding, next.svg, .js suffix glyphs (+7 more)

### Community 33 - "classify_intent"
Cohesion: 0.50
Nodes (4): classify_intent(), Any, AsyncClient, Return a verify/reply decision; invalid model output is a retryable failure.

### Community 34 - "_gemini_schema"
Cohesion: 0.67
Nodes (3): _gemini_schema(), clean(), Remove JSON Schema keywords unsupported by Gemini structured output.

### Community 35 - "Backend Environment Keys Configuration"
Cohesion: 0.16
Nodes (14): Backend Environment Keys Configuration, FactLens Backend Fact-check API, Search Verification Flow Max 3 Claims 6 Sources, Fact-check Streaming Endpoint, Five Stage Search Improvement Pipeline, Free Google Organic Search via SerpApi, Multi-LLM Fallback Priority Order, Duplicate Link and Japanese Search Result Correction (+6 more)

### Community 36 - "Settings"
Cohesion: 0.11
Nodes (21): BaseModel, Settings, parametrize, Offline API boundary checks; no provider calls., test_health_and_status_do_not_claim_provider_readiness(), test_jev_endpoint_maps_gateway_failure_to_502(), test_jev_endpoint_returns_scored_result(), handler() (+13 more)

### Community 37 - "run"
Cohesion: 0.13
Nodes (14): run(), extract(), search(), verify(), test_real_graph_carries_free_search_fallback_notice_to_later_stages(), extract(), read(), search() (+6 more)

### Community 38 - "next"
Cohesion: 0.15
Nodes (6): app_globals, metadata, metadata, metadata, nextConfig, next

### Community 39 - "answer_synthesis.py"
Cohesion: 0.13
Nodes (20): eligible_sources(), _limit_sections_to_source_breadth(), _project_claims(), Any, BaseModel, model_validator, Synthesize a user-facing answer from verified source text only., Build a minimal JSON-safe input; never forward raw source/search records. (+12 more)

### Community 40 - "ProviderCallError"
Cohesion: 0.12
Nodes (23): _openai_schema(), clean(), ProviderCallError, providers_for_preference(), RuntimeError, Normalize Pydantic schemas for OpenAI strict structured output., A provider attempt failed and the next configured provider may retry., Project provider search output to candidate URL annotations. (+15 more)

### Community 41 - "package.json"
Cohesion: 0.15
Nodes (12): name, private, type, postcss, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+4 more)

### Community 42 - "providers.py"
Cohesion: 0.18
Nodes (13): asyncio, IntentDecision, BaseModel, Cheap intent gate: verify with the pipeline or answer conversationally., openai_provider(), Provider-neutral requests and ordered LLM fallback policy. Credentials stay in…, Jev verdicts through AI Gateway; no live traffic (all transports mocked)., Safe diagnostics for failed provider fallbacks. (+5 more)

### Community 43 - "test_runtime.py"
Cohesion: 0.12
Nodes (20): build_extraction_graph(), load_settings(), Stage, End after extraction; do not simulate search, sources, or judgments., Read the backend-local file without mutating process environment., Isolated settings and extraction graph tests; no paid API calls., test_configured_free_google_search_is_selected_before_llm_search(), handler() (+12 more)

### Community 44 - "handler"
Cohesion: 0.12
Nodes (13): test_prediction_claims_are_searched_with_primary_query_in_provider_order(), run(), test_search_collects_deduplicated_candidates_without_evidence(), run(), test_search_keeps_completed_sources_when_response_has_nonterminal_search_item(), run(), test_search_keeps_completed_sources_when_response_hits_output_token_limit(), run() (+5 more)

### Community 45 - "floating-lines.tsx"
Cohesion: 0.22
Nodes (9): DEFAULT_BOTTOM_WAVE_POSITION, DEFAULT_ENABLED_WAVES, DEFAULT_LINE_COUNT, DEFAULT_LINE_DISTANCE, FloatingLines(), FloatingLinesProps, hexToVec3(), WavePosition (+1 more)

### Community 46 - "floating-lines-background.tsx"
Cohesion: 0.20
Nodes (7): BackgroundBoundary, FloatingLines, FloatingLinesBackground(), floatingLinesCount, floatingLinesDistance, floatingLinesGradient, floatingLinesWaves

### Community 47 - "scramble-text.tsx"
Cohesion: 0.36
Nodes (9): getRevealOrder(), randomCharacter(), randomizeText(), ScrambleRun, ScrambleText(), resetVisual(), startRun(), writeVisual() (+1 more)

### Community 48 - "fact-check-client.ts"
Cohesion: 0.21
Nodes (15): FactCheckError, Options, readFactCheckStream(), line(), validAnswer(), validEvidenceSection(), validProgressCitation(), validProgressClaim() (+7 more)

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

### Community 53 - "fact-check/route.ts"
Cohesion: 0.19
Nodes (11): backend(), dynamic, error(), GET(), headers, MODEL_OPTIONS, POST(), runtime (+3 more)

### Community 54 - "SVG root 1080x174"
Cohesion: 0.29
Nodes (8): Dark circular dots, logo-light.svg, Logo icon mark, Light theme variant, Red accent path, SVG root 1080x174, Welcome page branding, Wordmark letter paths

### Community 55 - "test_runtime_assembly.py"
Cohesion: 0.10
Nodes (21): build_fact_check_result(), build_runtime_workflow(), synthesizing(), Validate and assemble the only result shape exposed by the API., Compile five ordered stages and assemble the result after synthesis., The five graph stages, injectable for offline orchestration tests., RuntimeAdapters, Runtime assembly tests; explicit adapters keep the five-node graph offline. (+13 more)

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

### Community 63 - "test_search.py"
Cohesion: 0.17
Nodes (15): build_search_query(), _project_candidates(), Preserve provider order with a strict site cap, not a Google rank claim., Canonicalize common URL variants for deduplication, never fetching., Preserve the provider's candidate order and its origin, not a SERP rank., Conservative fallback when extraction did not supply semantic keywords., _select_diverse_sources(), _source_identity() (+7 more)

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

### Community 70 - "runtime.py"
Cohesion: 0.12
Nodes (18): _normalize_source(), AsyncClient, Server settings and the assembled four-stage verification workflow., Project internal source state onto the public TypeScript contract., Truncate to a UTF-16 unit budget without splitting astral characters., Single Jev verdict for Jev mode: no extract/search/read/synthesize stages., _result_warnings(), run_jev_fast_check() (+10 more)

### Community 71 - "make_runtime_adapters"
Cohesion: 0.12
Nodes (20): _http_status_from_exception(), make_runtime_adapters(), extract(), page_operation(), search(), synthesize(), operation(), verify() (+12 more)

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

### Community 95 - "test_sources.py"
Cohesion: 0.22
Nodes (14): module(), parametrize, Public-source security tests; no external traffic., test_html_excludes_noncontent(), test_html_excludes_video_and_custom_player_elements(), test_html_extracts_article_text_without_navigation_or_player_chrome(), test_html_fallback_still_excludes_menu_and_player_without_article_markers(), test_html_preserves_paragraph_breaks_for_readable_source_text() (+6 more)

### Community 100 - "public-source.ts"
Cohesion: 0.26
Nodes (10): Address, fetchPublicText(), htmlToText(), publicAddress(), resolvePublicUrl(), Resolver, ref_node_dns, ref_node_http (+2 more)

### Community 101 - "LLMProvider"
Cohesion: 0.30
Nodes (11): LLMProvider, test_structured_image_payload_shapes(), handler(), run(), decision_response(), Intent gate tests; no external traffic (all transports mocked)., test_intent_reply_requires_text(), run_empty() (+3 more)

### Community 102 - "recovery_probe_app.py"
Cohesion: 0.22
Nodes (6): get, post, TEST ONLY deterministic recovery app. Never imported by runtime/main., recover(), status(), verify()

### Community 103 - "youtube-context.ts"
Cohesion: 0.43
Nodes (6): download(), YoutubeVideoMetadata(), formatYoutubePublishedAt(), formatYoutubeViewCount(), stripYoutubeApiDataForExport(), youtubeThumbnailUrl()

### Community 104 - "jev/route.ts"
Cohesion: 0.27
Nodes (7): backend(), dynamic, error(), headers, POST(), runtime, input

### Community 105 - "test_execution.py"
Cohesion: 0.27
Nodes (7): parametrize, Real LangGraph via HTTP boundary; adapters contain offline fixtures only., test_graph_failure_returns_safe_error(), stage(), test_invalid_http_input_is_safe_and_never_runs_graph(), test_post_rejects_malformed_result_contract(), fastapi_testclient

### Community 106 - "12. API 계약 초안"
Cohesion: 0.29
Nodes (7): start(), 12.1 엔드포인트, 12.2 입력 예시, 12.3 최소 데이터 모델, 12.4 원문 위치 규약, 12.5 오류 분류, 12. API 계약 초안

### Community 107 - "glide-select.tsx"
Cohesion: 0.31
Nodes (8): GlideSelect(), GlideSelectOption, GlideSelectProps, labelText(), nextEnabled(), normalizeOption(), OptionInput, SIZES

### Community 108 - "test_all_synthesis_providers_failing_preserves_verified_result"
Cohesion: 0.33
Nodes (5): test_all_synthesis_providers_failing_preserves_verified_result(), failing_provider(), mock_client(), read(), search()

### Community 109 - "test_forecast_synthesis_preserves_prediction_and_citations"
Cohesion: 0.33
Nodes (3): test_forecast_synthesis_preserves_prediction_and_citations(), mock_client(), provider_response()

### Community 110 - "19. 소개 문구와 데모 안내"
Cohesion: 0.40
Nodes (5): 19. 소개 문구와 데모 안내, 검증 결과 하단 문구, 데모 고지 권장 문구, 서비스 소개, 짧은 소개

### Community 111 - "9. 화면 설계"
Cohesion: 0.40
Nodes (5): 9.1 정보 구조, 9.2 주장 카드, 9.3 요약 지표, 9.4 접근성·반응형, 9. 화면 설계

### Community 112 - "probe-stage7.mjs"
Cohesion: 0.29
Nodes (3): errors, observations, responses

### Community 114 - "15. QA와 수용 기준"
Cohesion: 0.50
Nodes (4): 15. QA와 수용 기준, 출시 조건, 테스트 케이스, 평가 방법

### Community 115 - "6. 주장 추출과 검증 계획"
Cohesion: 0.50
Nodes (4): 6.1 분류 체계, 6.2 주장 구조, 6.3 검색 계획, 6. 주장 추출과 검증 계획

### Community 116 - "8. 판정 정책"
Cohesion: 0.50
Nodes (4): 8.1 결과 분류, 8.2 겹치는 경우의 결정 규칙, 8.3 근거 충족 규칙, 8. 판정 정책

### Community 117 - "probe-cancellation.mjs"
Cohesion: 0.50
Nodes (4): observations, responses, state(), waitCounts()

### Community 118 - "14. 보안·개인정보·이용 조건"
Cohesion: 0.67
Nodes (3): 14. 보안·개인정보·이용 조건, URL과 외부 콘텐츠, 입력·저장

### Community 119 - "4. MVP 범위와 단계별 확장"
Cohesion: 0.67
Nodes (3): 4.1 3일 MVP 필수 범위, 4.2 MVP 이후, 4. MVP 범위와 단계별 확장

### Community 122 - "test_extractor_rejects_unsafe_outputs"
Cohesion: 0.50
Nodes (3): parametrize, test_extractor_rejects_unsafe_outputs(), run()

## Knowledge Gaps
- **268 isolated node(s):** `input`, `runtime`, `dynamic`, `headers`, `runtime` (+263 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 612 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_runtime_adapters()` connect `make_runtime_adapters` to `synthesize_answer`, `verification.py`, `search_sources`, `sources.py`, `search_google_free`, `fetch_youtube_data`, `extraction.py`, `extract_claims`, `FactCheckRequest`, `search.py`, `evaluate_claims_jev`, `Settings`, `answer_synthesis.py`, `ProviderCallError`, `providers.py`, `test_runtime.py`, `test_runtime_assembly.py`, `runtime.py`, `test_all_synthesis_providers_failing_preserves_verified_result`, `test_forecast_synthesis_preserves_prediction_and_citations`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `True or Not 고도화 기획서 v2` connect `True or Not 고도화 기획서 v2` to `12. API 계약 초안`, `19. 소개 문구와 데모 안내`, `9. 화면 설계`, `15. QA와 수용 기준`, `6. 주장 추출과 검증 계획`, `8. 판정 정책`, `14. 보안·개인정보·이용 조건`, `4. MVP 범위와 단계별 확장`, `16. 팀 역할과 3일 실행 계획`, `1. 핵심 방향`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `start()` connect `12. API 계약 초안` to `fact-check/route.ts`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `LLMProvider` (e.g. with `synthesize_answer()` and `extract_claims()`) actually correct?**
  _`LLMProvider` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `make_runtime_adapters()` (e.g. with `FreeSearchUnavailable` and `JevError`) actually correct?**
  _`make_runtime_adapters()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `ProviderCallError` (e.g. with `extract_claims()` and `extract_image_claims()`) actually correct?**
  _`ProviderCallError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `search_sources()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`search_sources()` has 2 INFERRED edges - model-reasoned connections that need verification._