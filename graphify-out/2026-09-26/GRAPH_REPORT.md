# Graph Report - my-app  (2026-09-25)

## Corpus Check
- 130 files · ~107,651 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 24 file(s) not represented in the graph (top: .log 7, (none) 5, .css 5)

## Summary
- 1588 nodes · 3122 edges · 117 communities (91 shown, 26 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 333 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f3934721`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- contracts.py
- LLMProvider
- verification.py
- test_search_errors.py
- sources.py
- build_workflow
- Four-Node LangGraph Runtime (extracting→searching→reading→verifying)
- search_google_free
- fact-check-dashboard.tsx
- test_source_fetch.py
- probe-recovery.py
- main.py
- providers.py
- fetch_youtube_data
- ref_node_assert
- extraction.py
- FactCheckDashboard
- extract_claims
- demo-state.ts
- agent.ts
- test_providers.py
- vector-wordmark.tsx
- fact-check-contract.ts
- FactCheckRequest
- score_band
- search.py
- compilerOptions
- FactCheckResult
- test_verification.py
- test_jev.py
- fact-check-reply.ts
- lattice-loader.tsx
- Next.js Wordmark Logo
- verify_claims
- test_runtime.py
- Backend Environment Keys Configuration
- Settings
- source
- next
- answer_synthesis.py
- ProviderCallError
- package.json
- test_jev_endpoint_maps_gateway_failure_to_502
- test_free_quota_exhaustion_falls_back_with_an_explicit_notice
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
- Q: JEV 선택이 안 되고 8010에서 Errno 10048이 발생함
- Q: 지금 레이아웃이 이상해 애니메이션 위치도 이상한곳에 걸쳐지고
- Q: 지금 jev가 제대로 작동하지 않아
- youtube-context.ts
- Q: 점수 판정이 이상해
- test_extract_url_only_fetches_page
- 12. API 계약 초안
- glide-select.tsx
- 19. 소개 문구와 데모 안내
- 9. 화면 설계
- 15. QA와 수용 기준
- 6. 주장 추출과 검증 계획
- 8. 판정 정책
- 14. 보안·개인정보·이용 조건
- 4. MVP 범위와 단계별 확장
- 16. 팀 역할과 3일 실행 계획
- 1. 핵심 방향

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 67 edges
2. `make_runtime_adapters()` - 51 edges
3. `ProviderCallError` - 45 edges
4. `Settings` - 45 edges
5. `search_sources()` - 41 edges
6. `synthesize_answer()` - 34 edges
7. `search_google_free()` - 31 edges
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

## Communities (117 total, 26 thin omitted)

### Community 0 - "contracts.py"
Cohesion: 0.15
Nodes (17): AgentStatus, AnswerCitation, _ContractModel, FactCheckAnswer, FactCheckProgressCitation, FactCheckProgressClaim, FactCheckProgressSource, FactClaim (+9 more)

### Community 1 - "LLMProvider"
Cohesion: 0.10
Nodes (49): eligible_sources(), insufficient_answer(), AsyncClient, Generate and validate a grounded answer, leaving provider retries to runtime., Project at most six verified non-YouTube texts into a provider-safe shape., Return a fixed answer that makes no unsupported assertions., synthesize_answer(), LLMProvider (+41 more)

### Community 2 - "verification.py"
Cohesion: 0.22
Nodes (19): _claim_index(), _evidence_dict(), ground_judgments(), Judgment, JudgmentEvidence, _normalize_text(), _parse_judgments(), Any (+11 more)

### Community 3 - "test_search_errors.py"
Cohesion: 0.14
Nodes (13): parametrize, Offline failure, safety and empty-result tests., test_candidates_filter_unsafe_urls_and_limit_results(), run(), test_completed_empty_search_is_not_a_verdict(), run(), test_nonfacts_skip_network(), run() (+5 more)

### Community 4 - "sources.py"
Cohesion: 0.12
Nodes (19): AbstractResolver, aiohttp, aiohttp_abc, asyncio, checked_url(), _generic_title(), html_title(), _is_japanese_page_text() (+11 more)

### Community 5 - "build_workflow"
Cohesion: 0.06
Nodes (22): test_workflow_preserves_link_and_image_state_keys(), parametrize, Real LangGraph via HTTP boundary; adapters contain offline fixtures only., test_graph_failure_returns_safe_error(), stage(), test_invalid_http_input_is_safe_and_never_runs_graph(), test_post_rejects_malformed_result_contract(), test_post_runs_graph_and_returns_only_result() (+14 more)

### Community 6 - "Four-Node LangGraph Runtime (extracting→searching→reading→verifying)"
Cohesion: 0.06
Nodes (45): Document Input Panel (원문 입력 + 확인 요청), Evidence-First Verification Principle (결론보다, 근거를 먼저), FactLens (팩트렌즈) Brand, FactLens Evidence Workspace (09-21, settings check failed), Synthetic Example Documents (가상 도시의 문화 행사), FactLens Evidence Workspace (09-21, server check pending), External Transmission & YouTube Data API Consent, Answer Model Fallback Selector (Gemini 3.8 Flash → Gemini 3.7 Flash → GPT-6 Luna Max) (+37 more)

### Community 7 - "search_google_free"
Cohesion: 0.09
Nodes (30): FreeSearchUnavailable, _json_response(), AsyncClient, Safe failure code for the optional, free-only search path., Use only an account confirmed to be on the free plan with quota left., search_google_free(), main(), One-query live check for the optional free-only Google search adapter. (+22 more)

### Community 8 - "fact-check-dashboard.tsx"
Cohesion: 0.06
Nodes (29): BlurText(), CountUp(), CountUpProps, base, DEMO_FOCUS, DEMO_TEXT, demoPreview, documents (+21 more)

### Community 9 - "test_source_fetch.py"
Cohesion: 0.06
Nodes (25): html_sections(), _TextParser, _TitleParser, parametrize, Deterministic HTTP response fixtures; resolver safety tested separately., run(), Session, test_low_reach_youtube_source_is_dropped_from_results() (+17 more)

### Community 10 - "probe-recovery.py"
Cohesion: 0.10
Nodes (26): blocking_extract(), cancellation_state(), InstrumentedGraph, get, Explicit integration-test entry point ONLY; never imported by main/runtime. No…, record(), os, pathlib (+18 more)

### Community 11 - "main.py"
Cohesion: 0.12
Nodes (21): _code_revision(), fact_check(), fact_check_jev(), fact_check_stream(), health(), HealthStatus, IntentClaim, IntentContext (+13 more)

### Community 12 - "providers.py"
Cohesion: 0.12
Nodes (31): _endpoint_and_headers(), _gemini_schema(), clean(), _gemini_text(), _openai_schema(), clean(), _openai_text(), Any (+23 more)

### Community 13 - "fetch_youtube_data"
Cohesion: 0.11
Nodes (26): youtube_reader(), Offline YouTube Data API contract tests; no Google credentials or traffic., test_comments_unavailable_keeps_video_title_without_exposing_provider_error(), run(), test_fetches_official_video_title_and_bounded_plain_text_comments(), handler(), run(), test_ignores_malformed_youtube_metadata_without_rejecting_comments() (+18 more)

### Community 14 - "ref_node_assert"
Cohesion: 0.08
Nodes (18): insufficientAnswer, result, verifiedSource, ref_node_assert, ref_node_fs, ref_node_test, ref_node_url, observations (+10 more)

### Community 15 - "extraction.py"
Cohesion: 0.13
Nodes (20): extract_image_claims(), extract_page_claims(), ExtractedClaim, Extraction, ImageObservation, _project_extracted_claims(), AsyncClient, BaseModel (+12 more)

### Community 16 - "FactCheckDashboard"
Cohesion: 0.11
Nodes (25): ChatIntent, CLAIM_PATTERNS, classifyChatInput(), describeHistory(), EARLY_META, FOLLOW_UP_PATTERNS, HELP_PATTERNS, isFollowUpText() (+17 more)

### Community 17 - "extract_claims"
Cohesion: 0.14
Nodes (19): extract_claims(), Return a LangGraph state update; callers own the client and credential., parametrize, Offline provider transport fixtures, never real model responses., test_extractor_drops_invented_claim_without_fabricating_source_text(), run(), test_extractor_keeps_forecast_and_returns_search_keywords_separately(), handler() (+11 more)

### Community 18 - "demo-state.ts"
Cohesion: 0.21
Nodes (14): Action, Claim, createPreview(), initialState, State, transition(), TrustIndex(), FACT_SCORE_BANDS (+6 more)

### Community 19 - "agent.ts"
Cohesion: 0.06
Nodes (47): backend(), dynamic, error(), headers, POST(), runtime, input, backend() (+39 more)

### Community 20 - "test_providers.py"
Cohesion: 0.11
Nodes (17): agent_status(), Report whether the real four-stage workflow can be constructed., configured_model_options(), configured_providers(), providers_for_preference(), Return configured providers in the user-requested priority order., Return the automatic chain or exactly one explicitly selected model., Provider priority and fallback policy tests; no network traffic. (+9 more)

### Community 21 - "vector-wordmark.tsx"
Cohesion: 0.17
Nodes (21): Atlas, buildAtlas(), clamp(), compile(), FontSpec, fontString(), fract(), HANDLE_DEFAULTS (+13 more)

### Community 22 - "fact-check-contract.ts"
Cohesion: 0.10
Nodes (18): AgentEvent, AgentStage, AgentStatus, AnswerSection, FACT_CHECK_MODEL, FACT_CHECK_REASONING, FactSource, MODEL_OPTIONS (+10 more)

### Community 23 - "FactCheckRequest"
Cohesion: 0.12
Nodes (13): FactCheckRequest, ImageAttachment, BaseModel, model_validator, Link and image attachment paths; no external traffic (all transports mocked)., test_extract_image_claims_replaces_state_text(), test_extract_page_claims_replaces_state_text(), test_read_prepends_link_seed_without_network() (+5 more)

### Community 24 - "score_band"
Cohesion: 0.20
Nodes (14): default_fact_score(), normalize_fact_score(), Evidence-grounded public score policy for fact-check claims., Return the public band for an inclusive 0–100 score., Preserve the model's reasoned score, clamped only to the 0-100 range. The…, Supply a compatible score when an older result omits the new field., score_band(), score_label() (+6 more)

### Community 25 - "search.py"
Cohesion: 0.15
Nodes (21): Optional SerpApi Google organic discovery, restricted to a free account., read(), candidate_url(), is_japanese_candidate(), is_unreliable_candidate(), _normalized_host(), origin_group_for_url(), _project_candidates() (+13 more)

### Community 26 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 27 - "FactCheckResult"
Cohesion: 0.15
Nodes (22): FactCheckResult, get, post, TEST ONLY deterministic recovery app. Never imported by runtime/main., recover(), status(), verify(), grounded_answer() (+14 more)

### Community 28 - "test_verification.py"
Cohesion: 0.21
Nodes (17): html_text(), claim(), Offline citation-grounding and judgment tests; no provider traffic., test_context_mismatch_is_reported_as_missing_context(), test_date_or_context_mismatch_cannot_support_a_claim(), test_ground_judgments_accepts_a_verified_contiguous_quote(), test_ground_judgments_accepts_a_verified_quote_for_an_unclear_checkable_claim(), test_ground_judgments_attaches_only_the_matching_section_not_the_whole_page() (+9 more)

### Community 29 - "test_jev.py"
Cohesion: 0.06
Nodes (52): evaluate_claims_jev(), JevError, _parse_strength(), _parse_verdict(), Any, AsyncClient, RuntimeError, Jev (TypeSafe System One) verdicts through Vercel AI Gateway. The gateway API… (+44 more)

### Community 30 - "fact-check-reply.ts"
Cohesion: 0.12
Nodes (19): safeSourceUrl(), AnswerBlockView(), AnswerOverview(), firstUrl(), ProgressReply(), ProgressSourceList(), YoutubeThumbnail(), AnswerCitationDisplay (+11 more)

### Community 31 - "lattice-loader.tsx"
Cohesion: 0.16
Nodes (14): DEFAULT_PATTERN, formatElapsed(), GridSize, LatticeLoader(), LatticeLoaderProps, LoaderStatus, LoaderStyle, MARKS (+6 more)

### Community 32 - "Next.js Wordmark Logo"
Cohesion: 0.17
Nodes (15): Geometric Brand Emblem (Red & Black Circles), Light Theme Variant (Dark Glyphs on Light Background), logo-light.svg light-mode branding logo, Path-Drawn Brand Wordmark, Next.js Framework Brand, Default template branding, next.svg, .js suffix glyphs (+7 more)

### Community 33 - "verify_claims"
Cohesion: 0.17
Nodes (15): test_verify_claims_bounds_source_text_sent_to_model(), run(), test_verify_claims_requires_a_key_when_verified_source_text_exists(), run(), test_verify_claims_sends_only_verified_source_text(), handler(), run(), test_verify_claims_supports_gemini_interactions_structured_output() (+7 more)

### Community 34 - "test_runtime.py"
Cohesion: 0.17
Nodes (13): get_workflow(), Build the provider-backed graph only when a server-side key is configured., build_extraction_graph(), load_settings(), Stage, Read the backend-local file without mutating process environment., End after extraction; do not simulate search, sources, or judgments., Isolated settings and extraction graph tests; no paid API calls. (+5 more)

### Community 35 - "Backend Environment Keys Configuration"
Cohesion: 0.16
Nodes (14): Backend Environment Keys Configuration, FactLens Backend Fact-check API, Search Verification Flow Max 3 Claims 6 Sources, Fact-check Streaming Endpoint, Five Stage Search Improvement Pipeline, Free Google Organic Search via SerpApi, Multi-LLM Fallback Priority Order, Duplicate Link and Japanese Search Result Correction (+6 more)

### Community 36 - "Settings"
Cohesion: 0.16
Nodes (14): BaseModel, Settings, parametrize, Offline API boundary checks; no provider calls., test_health_and_status_do_not_claim_provider_readiness(), test_request_preserves_original_text(), test_request_rejects_invalid_input(), test_request_rejects_unknown_model_preference() (+6 more)

### Community 37 - "source"
Cohesion: 0.40
Nodes (5): source(), read(), search(), read(), search()

### Community 38 - "next"
Cohesion: 0.15
Nodes (6): app_globals, metadata, metadata, metadata, nextConfig, next

### Community 39 - "answer_synthesis.py"
Cohesion: 0.10
Nodes (24): _limit_sections_to_source_breadth(), _project_claims(), Any, BaseModel, model_validator, Synthesize a user-facing answer from verified source text only., Build a minimal JSON-safe input; never forward raw source/search records., Keep answer breadth proportional to the cited source base. A single supporting… (+16 more)

### Community 40 - "ProviderCallError"
Cohesion: 0.20
Nodes (15): intent(), Decide verify-vs-reply with one cheap model call; never streams., ProviderCallError, RuntimeError, A provider attempt failed and the next configured provider may retry., Run an operation in priority order and return its result and provider., run_with_fallback(), main() (+7 more)

### Community 41 - "package.json"
Cohesion: 0.15
Nodes (12): name, private, type, postcss, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+4 more)

### Community 42 - "test_jev_endpoint_maps_gateway_failure_to_502"
Cohesion: 0.36
Nodes (6): test_jev_endpoint_maps_gateway_failure_to_502(), mock_client(), test_jev_endpoint_returns_scored_result(), fake_fetch(), handler(), mock_client()

### Community 43 - "test_free_quota_exhaustion_falls_back_with_an_explicit_notice"
Cohesion: 0.23
Nodes (9): test_configured_free_google_search_is_selected_before_llm_search(), handler(), mock_async_client(), test_free_quota_exhaustion_falls_back_with_an_explicit_notice(), mock_async_client(), test_llm_runtime_ignores_environment_proxy_for_provider_connection(), mock_async_client(), test_runtime_read_stage_uses_youtube_adapter_without_adding_comments_to_source_texts() (+1 more)

### Community 44 - "search_sources"
Cohesion: 0.09
Nodes (29): build_search_query(), AsyncClient, Conservative fallback when extraction did not supply semantic keywords., search_sources(), parametrize, Offline search fixtures, not verified sources., test_aitimes_is_classified_as_korean_news_in_google_results(), test_build_search_query_keeps_entity_and_year_from_forecast_question() (+21 more)

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
Cohesion: 0.22
Nodes (13): Options, validAnswer(), validEvidenceSection(), validProgressCitation(), validProgressClaim(), validProgressClaims(), validProgressSource(), validProgressSources() (+5 more)

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
Cohesion: 0.05
Nodes (47): FactCheckResponse, build_fact_check_result(), build_runtime_workflow(), Validate and assemble the only result shape exposed by the API., Compile five ordered stages and assemble the result after synthesis., The five graph stages, injectable for offline orchestration tests., RuntimeAdapters, encode() (+39 more)

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

### Community 70 - "runtime.py"
Cohesion: 0.10
Nodes (22): build_progress_sources(), _normalize_source(), AsyncClient, Server settings and the assembled four-stage verification workflow., Project internal source state onto the public TypeScript contract., Truncate to a UTF-16 unit budget without splitting astral characters., Search and read evidence, then return Jev's score-only claim result., Expose only source identity and access state before final answer assembly. (+14 more)

### Community 71 - "make_runtime_adapters"
Cohesion: 0.15
Nodes (17): _http_status_from_exception(), make_runtime_adapters(), extract(), page_operation(), search(), synthesize(), operation(), verify() (+9 more)

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

### Community 100 - "Q: JEV 선택이 안 되고 8010에서 Errno 10048이 발생함"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: JEV 선택이 안 되고 8010에서 Errno 10048이 발생함, Source Nodes

### Community 101 - "Q: 지금 레이아웃이 이상해 애니메이션 위치도 이상한곳에 걸쳐지고"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 지금 레이아웃이 이상해 애니메이션 위치도 이상한곳에 걸쳐지고, Source Nodes

### Community 102 - "Q: 지금 jev가 제대로 작동하지 않아"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 지금 jev가 제대로 작동하지 않아, Source Nodes

### Community 103 - "youtube-context.ts"
Cohesion: 0.43
Nodes (6): download(), YoutubeVideoMetadata(), formatYoutubePublishedAt(), formatYoutubeViewCount(), stripYoutubeApiDataForExport(), youtubeThumbnailUrl()

### Community 104 - "Q: 점수 판정이 이상해"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 점수 판정이 이상해, Source Nodes

### Community 106 - "12. API 계약 초안"
Cohesion: 0.29
Nodes (7): start(), 12.1 엔드포인트, 12.2 입력 예시, 12.3 최소 데이터 모델, 12.4 원문 위치 규약, 12.5 오류 분류, 12. API 계약 초안

### Community 107 - "glide-select.tsx"
Cohesion: 0.31
Nodes (8): GlideSelect(), GlideSelectOption, GlideSelectProps, labelText(), nextEnabled(), normalizeOption(), OptionInput, SIZES

### Community 110 - "19. 소개 문구와 데모 안내"
Cohesion: 0.40
Nodes (5): 19. 소개 문구와 데모 안내, 검증 결과 하단 문구, 데모 고지 권장 문구, 서비스 소개, 짧은 소개

### Community 111 - "9. 화면 설계"
Cohesion: 0.40
Nodes (5): 9.1 정보 구조, 9.2 주장 카드, 9.3 요약 지표, 9.4 접근성·반응형, 9. 화면 설계

### Community 114 - "15. QA와 수용 기준"
Cohesion: 0.50
Nodes (4): 15. QA와 수용 기준, 출시 조건, 테스트 케이스, 평가 방법

### Community 115 - "6. 주장 추출과 검증 계획"
Cohesion: 0.50
Nodes (4): 6.1 분류 체계, 6.2 주장 구조, 6.3 검색 계획, 6. 주장 추출과 검증 계획

### Community 116 - "8. 판정 정책"
Cohesion: 0.50
Nodes (4): 8.1 결과 분류, 8.2 겹치는 경우의 결정 규칙, 8.3 근거 충족 규칙, 8. 판정 정책

### Community 118 - "14. 보안·개인정보·이용 조건"
Cohesion: 0.67
Nodes (3): 14. 보안·개인정보·이용 조건, URL과 외부 콘텐츠, 입력·저장

### Community 119 - "4. MVP 범위와 단계별 확장"
Cohesion: 0.67
Nodes (3): 4.1 3일 MVP 필수 범위, 4.2 MVP 이후, 4. MVP 범위와 단계별 확장

## Knowledge Gaps
- **286 isolated node(s):** `input`, `runtime`, `dynamic`, `headers`, `runtime` (+281 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 639 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `agent_status()` (2× useful, score=1.998072925) _(code changed — re-verify)_
- `Backend Environment Keys Configuration` (2× useful, score=1.998072925)
- `Next.js → FastAPI Proxy Route (6-B, app/api/fact-check/route.ts)` (2× useful, score=1.998072925)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_runtime_adapters()` connect `make_runtime_adapters` to `LLMProvider`, `sources.py`, `search_google_free`, `fetch_youtube_data`, `extraction.py`, `extract_claims`, `test_providers.py`, `FactCheckRequest`, `search.py`, `test_jev.py`, `verify_claims`, `test_runtime.py`, `Settings`, `answer_synthesis.py`, `ProviderCallError`, `test_free_quota_exhaustion_falls_back_with_an_explicit_notice`, `search_sources`, `test_runtime_assembly.py`, `runtime.py`, `test_extract_url_only_fetches_page`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `LLMProvider` connect `LLMProvider` to `verify_claims`, `verification.py`, `runtime.py`, `answer_synthesis.py`, `ProviderCallError`, `providers.py`, `search_sources`, `extraction.py`, `extract_claims`, `test_providers.py`, `FactCheckRequest`, `search.py`, `test_verification.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `True or Not 고도화 기획서 v2` connect `True or Not 고도화 기획서 v2` to `12. API 계약 초안`, `19. 소개 문구와 데모 안내`, `9. 화면 설계`, `15. QA와 수용 기준`, `6. 주장 추출과 검증 계획`, `8. 판정 정책`, `14. 보안·개인정보·이용 조건`, `4. MVP 범위와 단계별 확장`, `16. 팀 역할과 3일 실행 계획`, `1. 핵심 방향`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `LLMProvider` (e.g. with `synthesize_answer()` and `extract_claims()`) actually correct?**
  _`LLMProvider` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `make_runtime_adapters()` (e.g. with `FreeSearchUnavailable` and `JevError`) actually correct?**
  _`make_runtime_adapters()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `ProviderCallError` (e.g. with `extract_claims()` and `extract_image_claims()`) actually correct?**
  _`ProviderCallError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `search_sources()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`search_sources()` has 2 INFERRED edges - model-reasoned connections that need verification._