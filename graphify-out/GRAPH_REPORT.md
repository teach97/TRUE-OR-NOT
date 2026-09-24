# Graph Report - my-app  (2026-09-24)

## Corpus Check
- 119 files · ~92,142 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: (none) 5, .log 4, .css 4)

## Summary
- 1462 nodes · 2869 edges · 122 communities (96 shown, 26 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 301 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f8eaf11e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- contracts.py
- LLMProvider
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
- providers.py
- fetch_youtube_data
- ref_node_assert
- extraction.py
- FactCheckDashboard
- extract_claims
- demo-state.ts
- agent.ts
- stream_events
- vector-wordmark.tsx
- fact-check-client.ts
- FactCheckRequest
- test_intent.py
- search.py
- compilerOptions
- fact-check-contract.ts
- Settings
- fact-check/route.ts
- fact-check-reply.ts
- lattice-loader.tsx
- Next.js Wordmark Logo
- ProviderCallError
- answer_synthesis.py
- Backend Environment Keys Configuration
- make_runtime_adapters
- test_runtime_graph_assembles_valid_final_result_after_five_stages
- next
- test_runtime.py
- run
- package.json
- public-source.ts
- test_free_quota_exhaustion_falls_back_with_an_explicit_notice
- test_all_synthesis_providers_failing_preserves_verified_result
- floating-lines.tsx
- floating-lines-background.tsx
- scramble-text.tsx
- test_runtime_assembly.py
- Framework Route Modules
- home.tsx
- devDependencies
- root.tsx
- test_forecast_synthesis_preserves_prediction_and_citations
- SVG root 1080x174
- build_runtime_workflow
- globe.svg
- ref_react_router_dev
- dependencies
- scripts
- Document File Icon
- intent/route.ts
- Dark Mode Logo SVG
- handler
- eslint.config.mjs
- next-env.d.ts
- Browser Window Icon SVG in Gray
- Dashboard demo-state fixture shader implementation and checks
- Declarative Router Shape
- RSC Route Module Differences
- runtime.py
- test_attachments.py
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
- google_serp.py
- Globe Components and Clip Container
- Globe Layout and Meridian Grid
- FactLens frontend README
- FactLens frontend Next.js App Router TypeScript Tailwind
- cancellation_probe_app.py
- asyncio
- recovery_probe_app.py
- youtube-context.ts
- _TitleParser
- fact-check-client.test.mjs
- 12. API 계약 초안
- test_graph_keeps_source_texts_for_verification
- probe-stage7.mjs
- build_search_query
- 19. 소개 문구와 데모 안내
- 9. 화면 설계
- probe-cancellation.mjs
- test_account_guard_never_starts_a_search_without_confirmed_free_quota
- 15. QA와 수용 기준
- 6. 주장 추출과 검증 계획
- 8. 판정 정책
- test_structured_image_payload_shapes
- 14. 보안·개인정보·이용 조건
- 4. MVP 범위와 단계별 확장
- 16. 팀 역할과 3일 실행 계획
- 1. 핵심 방향

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 67 edges
2. `make_runtime_adapters()` - 46 edges
3. `ProviderCallError` - 45 edges
4. `search_sources()` - 41 edges
5. `Settings` - 39 edges
6. `synthesize_answer()` - 34 edges
7. `search_google_free()` - 30 edges
8. `extract_claims()` - 29 edges
9. `ground_judgments()` - 28 edges
10. `verify_claims()` - 27 edges

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

## Communities (122 total, 26 thin omitted)

### Community 0 - "contracts.py"
Cohesion: 0.22
Nodes (15): AgentStatus, AnswerBlock, AnswerCitation, AnswerSection, _ContractModel, FactCheckAnswer, FactCheckProgressCitation, FactCheckProgressClaim (+7 more)

### Community 1 - "LLMProvider"
Cohesion: 0.15
Nodes (37): AsyncClient, Generate and validate a grounded answer, leaving provider retries to runtime., synthesize_answer(), LLMProvider, completed_response(), draft(), multi_section_draft(), parametrize (+29 more)

### Community 2 - "verification.py"
Cohesion: 0.06
Nodes (67): FactClaim, model_validator, default_fact_score(), normalize_fact_score(), Evidence-grounded public score policy for fact-check claims., Return the public band for an inclusive 0–100 score., Preserve the model's reasoned score, clamped only to the 0-100 range. The…, Supply a compatible score when an older result omits the new field. (+59 more)

### Community 3 - "search_sources"
Cohesion: 0.13
Nodes (19): AsyncClient, search_sources(), parametrize, Offline failure, safety and empty-result tests., test_candidates_filter_unsafe_urls_and_limit_results(), run(), test_completed_empty_search_is_not_a_verdict(), run() (+11 more)

### Community 4 - "sources.py"
Cohesion: 0.13
Nodes (17): AbstractResolver, aiohttp, aiohttp_abc, checked_url(), _generic_title(), html_title(), _is_japanese_page_text(), public_ip() (+9 more)

### Community 5 - "build_workflow"
Cohesion: 0.06
Nodes (36): FactCheckResult, test_workflow_preserves_link_and_image_state_keys(), grounded_answer(), parametrize, Final Python contract tests; no provider calls., result_payload(), test_evidence_may_expose_only_a_bounded_matching_article_section(), test_final_contract_accepts_frontend_shape_and_wrapper() (+28 more)

### Community 6 - "Four-Node LangGraph Runtime (extracting→searching→reading→verifying)"
Cohesion: 0.06
Nodes (45): Document Input Panel (원문 입력 + 확인 요청), Evidence-First Verification Principle (결론보다, 근거를 먼저), FactLens (팩트렌즈) Brand, FactLens Evidence Workspace (09-21, settings check failed), Synthetic Example Documents (가상 도시의 문화 행사), FactLens Evidence Workspace (09-21, server check pending), External Transmission & YouTube Data API Consent, Answer Model Fallback Selector (Gemini 3.8 Flash → Gemini 3.7 Flash → GPT-6 Luna Max) (+37 more)

### Community 7 - "search_google_free"
Cohesion: 0.14
Nodes (17): Use only an account confirmed to be on the free plan with quota left., search_google_free(), test_actual_free_plan_label_allows_a_zero_price_search(), run(), test_completed_google_search_without_organic_results_returns_no_sources(), run(), test_each_distinct_claim_query_gets_its_own_ranked_search_when_free_quota_covers_all(), run() (+9 more)

### Community 8 - "fact-check-dashboard.tsx"
Cohesion: 0.07
Nodes (21): BlurText(), CountUp(), CountUpProps, DonutChart(), ChatMessage, ChatProgress, IconName, PanelProps (+13 more)

### Community 9 - "test_source_fetch.py"
Cohesion: 0.06
Nodes (24): html_sections(), _TextParser, parametrize, Deterministic HTTP response fixtures; resolver safety tested separately., Response, run(), Session, test_low_reach_youtube_source_is_dropped_from_results() (+16 more)

### Community 10 - "probe-recovery.py"
Cohesion: 0.09
Nodes (33): module(), parametrize, Public-source security tests; no external traffic., test_html_excludes_noncontent(), test_html_excludes_video_and_custom_player_elements(), test_html_extracts_article_text_without_navigation_or_player_chrome(), test_html_fallback_still_excludes_menu_and_player_without_article_markers(), test_html_preserves_paragraph_breaks_for_readable_source_text() (+25 more)

### Community 11 - "main.py"
Cohesion: 0.12
Nodes (20): _code_revision(), fact_check(), fact_check_stream(), health(), HealthStatus, IntentClaim, IntentContext, IntentRequest (+12 more)

### Community 12 - "providers.py"
Cohesion: 0.15
Nodes (27): _endpoint_and_headers(), _gemini_schema(), clean(), _gemini_text(), _openai_schema(), clean(), _openai_text(), Any (+19 more)

### Community 13 - "fetch_youtube_data"
Cohesion: 0.12
Nodes (25): Offline YouTube Data API contract tests; no Google credentials or traffic., test_comments_unavailable_keeps_video_title_without_exposing_provider_error(), run(), test_fetches_official_video_title_and_bounded_plain_text_comments(), handler(), run(), test_ignores_malformed_youtube_metadata_without_rejecting_comments(), run() (+17 more)

### Community 14 - "ref_node_assert"
Cohesion: 0.21
Nodes (8): ref_node_assert, ref_node_fs, ref_node_test, ref_node_url, observations, responses, observations, responses

### Community 15 - "extraction.py"
Cohesion: 0.22
Nodes (13): extract_image_claims(), extract_page_claims(), ExtractedClaim, Extraction, ImageObservation, _project_extracted_claims(), AsyncClient, BaseModel (+5 more)

### Community 16 - "FactCheckDashboard"
Cohesion: 0.12
Nodes (21): ChatIntent, CLAIM_PATTERNS, classifyChatInput(), describeHistory(), EARLY_META, FOLLOW_UP_PATTERNS, HELP_PATTERNS, isFollowUpText() (+13 more)

### Community 17 - "extract_claims"
Cohesion: 0.14
Nodes (19): extract_claims(), Return a LangGraph state update; callers own the client and credential., parametrize, Offline provider transport fixtures, never real model responses., test_extractor_drops_invented_claim_without_fabricating_source_text(), run(), test_extractor_keeps_forecast_and_returns_search_keywords_separately(), handler() (+11 more)

### Community 18 - "demo-state.ts"
Cohesion: 0.13
Nodes (21): base, DEMO_FOCUS, DEMO_TEXT, demoPreview, documents, results, Action, Claim (+13 more)

### Community 19 - "agent.ts"
Cohesion: 0.14
Nodes (19): AttachedImage, FactEvidence, VerdictCode, canonical(), extractClaims(), extractionSchema, format(), JsonObject (+11 more)

### Community 20 - "stream_events"
Cohesion: 0.13
Nodes (16): build_progress_preview(), build_progress_sources(), Expose only source identity and access state before final answer assembly., Build an early, strictly projected claim summary from validated evidence., encode(), NDJSON boundary: only stage labels and validated final results are public., Propagate cancellation and close the graph iterator on every exit path., stream_events() (+8 more)

### Community 21 - "vector-wordmark.tsx"
Cohesion: 0.17
Nodes (21): Atlas, buildAtlas(), clamp(), compile(), FontSpec, fontString(), fract(), HANDLE_DEFAULTS (+13 more)

### Community 22 - "fact-check-client.ts"
Cohesion: 0.19
Nodes (16): FactCheckError, Options, readFactCheckStream(), line(), validAnswer(), validEvidenceSection(), validProgressCitation(), validProgressClaim() (+8 more)

### Community 23 - "FactCheckRequest"
Cohesion: 0.24
Nodes (6): FactCheckRequest, ImageAttachment, BaseModel, model_validator, test_request_preserves_original_text(), field_validator

### Community 24 - "test_intent.py"
Cohesion: 0.28
Nodes (8): decision_response(), Intent gate tests; no external traffic (all transports mocked)., test_intent_endpoint_rejects_bad_payloads_and_reports_unconfigured(), test_intent_reply_requires_text(), run_empty(), run_reply(), test_intent_verify_passes_focus_through(), run()

### Community 25 - "search.py"
Cohesion: 0.12
Nodes (27): read(), youtube_reader(), candidate_url(), is_japanese_candidate(), is_unreliable_candidate(), _normalized_host(), origin_group_for_url(), _project_candidates() (+19 more)

### Community 26 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 27 - "fact-check-contract.ts"
Cohesion: 0.10
Nodes (18): AgentEvent, AgentStage, AgentStatus, AnswerSection, FACT_CHECK_MODEL, FACT_CHECK_REASONING, FactClaim, FactSource (+10 more)

### Community 28 - "Settings"
Cohesion: 0.18
Nodes (12): BaseModel, Settings, parametrize, Offline API boundary checks; no provider calls., test_health_and_status_do_not_claim_provider_readiness(), test_request_rejects_invalid_input(), test_request_rejects_unknown_model_preference(), test_request_requires_all_contract_fields() (+4 more)

### Community 29 - "fact-check/route.ts"
Cohesion: 0.19
Nodes (11): backend(), dynamic, error(), GET(), headers, MODEL_OPTIONS, POST(), runtime (+3 more)

### Community 30 - "fact-check-reply.ts"
Cohesion: 0.12
Nodes (20): safeSourceUrl(), AnswerBlockView(), AnswerOverview(), firstUrl(), ProgressReply(), ProgressSourceList(), YoutubeThumbnail(), AnswerCitationDisplay (+12 more)

### Community 31 - "lattice-loader.tsx"
Cohesion: 0.16
Nodes (14): DEFAULT_PATTERN, formatElapsed(), GridSize, LatticeLoader(), LatticeLoaderProps, LoaderStatus, LoaderStyle, MARKS (+6 more)

### Community 32 - "Next.js Wordmark Logo"
Cohesion: 0.17
Nodes (15): Geometric Brand Emblem (Red & Black Circles), Light Theme Variant (Dark Glyphs on Light Background), logo-light.svg light-mode branding logo, Path-Drawn Brand Wordmark, Next.js Framework Brand, Default template branding, next.svg, .js suffix glyphs (+7 more)

### Community 33 - "ProviderCallError"
Cohesion: 0.12
Nodes (22): classify_intent(), IntentDecision, Any, AsyncClient, BaseModel, Cheap intent gate: verify with the pipeline or answer conversationally., Return a verify/reply decision; invalid model output is a retryable failure., intent() (+14 more)

### Community 34 - "answer_synthesis.py"
Cohesion: 0.13
Nodes (19): eligible_sources(), _limit_sections_to_source_breadth(), _project_claims(), Any, BaseModel, model_validator, Synthesize a user-facing answer from verified source text only., Build a minimal JSON-safe input; never forward raw source/search records. (+11 more)

### Community 35 - "Backend Environment Keys Configuration"
Cohesion: 0.16
Nodes (14): Backend Environment Keys Configuration, FactLens Backend Fact-check API, Search Verification Flow Max 3 Claims 6 Sources, Fact-check Streaming Endpoint, Five Stage Search Improvement Pipeline, Free Google Organic Search via SerpApi, Multi-LLM Fallback Priority Order, Duplicate Link and Japanese Search Result Correction (+6 more)

### Community 36 - "make_runtime_adapters"
Cohesion: 0.10
Nodes (29): agent_status(), Report whether the real four-stage workflow can be constructed., configured_model_options(), configured_providers(), providers_for_preference(), Return configured providers in the user-requested priority order., Return the automatic chain or exactly one explicitly selected model., make_runtime_adapters() (+21 more)

### Community 37 - "test_runtime_graph_assembles_valid_final_result_after_five_stages"
Cohesion: 0.19
Nodes (8): test_real_graph_carries_free_search_fallback_notice_to_later_stages(), extract(), read(), search(), synthesize(), verify(), test_runtime_graph_assembles_valid_final_result_after_five_stages(), test_synthesis_stage_failure_does_not_return_intermediate_result()

### Community 38 - "next"
Cohesion: 0.15
Nodes (6): app_globals, metadata, metadata, metadata, nextConfig, next

### Community 39 - "test_runtime.py"
Cohesion: 0.21
Nodes (11): build_extraction_graph(), load_settings(), Stage, End after extraction; do not simulate search, sources, or judgments., Read the backend-local file without mutating process environment., Isolated settings and extraction graph tests; no paid API calls., test_extraction_graph_ends_without_fabricating_verdict(), test_serpapi_key_is_server_only_and_redacted() (+3 more)

### Community 40 - "run"
Cohesion: 0.29
Nodes (6): test_forecast_keywords_reach_search_through_graph_without_leaking_into_result(), handler(), run(), extract(), search(), verify()

### Community 41 - "package.json"
Cohesion: 0.15
Nodes (12): name, private, type, postcss, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+4 more)

### Community 42 - "public-source.ts"
Cohesion: 0.26
Nodes (10): Address, fetchPublicText(), htmlToText(), publicAddress(), resolvePublicUrl(), Resolver, ref_node_dns, ref_node_http (+2 more)

### Community 43 - "test_free_quota_exhaustion_falls_back_with_an_explicit_notice"
Cohesion: 0.23
Nodes (9): test_configured_free_google_search_is_selected_before_llm_search(), handler(), mock_async_client(), test_free_quota_exhaustion_falls_back_with_an_explicit_notice(), mock_async_client(), test_llm_runtime_ignores_environment_proxy_for_provider_connection(), mock_async_client(), test_runtime_read_stage_uses_youtube_adapter_without_adding_comments_to_source_texts() (+1 more)

### Community 44 - "test_all_synthesis_providers_failing_preserves_verified_result"
Cohesion: 0.22
Nodes (9): source(), test_eligible_sources_excludes_unverified_empty_and_youtube_and_bounds_text(), test_all_synthesis_providers_failing_preserves_verified_result(), failing_provider(), mock_client(), read(), search(), read() (+1 more)

### Community 45 - "floating-lines.tsx"
Cohesion: 0.22
Nodes (9): DEFAULT_BOTTOM_WAVE_POSITION, DEFAULT_ENABLED_WAVES, DEFAULT_LINE_COUNT, DEFAULT_LINE_DISTANCE, FloatingLines(), FloatingLinesProps, hexToVec3(), WavePosition (+1 more)

### Community 46 - "floating-lines-background.tsx"
Cohesion: 0.20
Nodes (7): BackgroundBoundary, FloatingLines, FloatingLinesBackground(), floatingLinesCount, floatingLinesDistance, floatingLinesGradient, floatingLinesWaves

### Community 47 - "scramble-text.tsx"
Cohesion: 0.36
Nodes (9): getRevealOrder(), randomCharacter(), randomizeText(), ScrambleRun, ScrambleText(), resetVisual(), startRun(), writeVisual() (+1 more)

### Community 48 - "test_runtime_assembly.py"
Cohesion: 0.20
Nodes (13): insufficient_answer(), Return a fixed answer that makes no unsupported assertions., FactCheckResponse, build_fact_check_result(), synthesizing(), _normalize_source(), Project internal source state onto the public TypeScript contract., Validate and assemble the only result shape exposed by the API. (+5 more)

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

### Community 53 - "test_forecast_synthesis_preserves_prediction_and_citations"
Cohesion: 0.33
Nodes (3): test_forecast_synthesis_preserves_prediction_and_citations(), mock_client(), provider_response()

### Community 54 - "SVG root 1080x174"
Cohesion: 0.29
Nodes (8): Dark circular dots, logo-light.svg, Logo icon mark, Light theme variant, Red accent path, SVG root 1080x174, Welcome page branding, Wordmark letter paths

### Community 55 - "build_runtime_workflow"
Cohesion: 0.14
Nodes (12): get_workflow(), Build the provider-backed graph only when a server-side key is configured., build_runtime_workflow(), Compile five ordered stages and assemble the result after synthesis., The five graph stages, injectable for offline orchestration tests., RuntimeAdapters, graph(), parametrize (+4 more)

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

### Community 63 - "handler"
Cohesion: 0.12
Nodes (13): test_prediction_claims_are_searched_with_primary_query_in_provider_order(), run(), test_search_collects_deduplicated_candidates_without_evidence(), run(), test_search_keeps_completed_sources_when_response_has_nonterminal_search_item(), run(), test_search_preserves_candidate_order_and_strict_duplicate_limits(), handler() (+5 more)

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
Cohesion: 0.17
Nodes (12): _http_status_from_exception(), Server settings and the assembled four-stage verification workflow., Return only an upstream HTTP status from an exception chain., Request boundary compatible with the existing TypeScript request fields., Provider-independent graph. All real service adapters must be supplied…, BaseException, collections_abc, dotenv (+4 more)

### Community 71 - "test_attachments.py"
Cohesion: 0.13
Nodes (9): Link and image attachment paths; no external traffic (all transports mocked)., test_extract_image_claims_replaces_state_text(), test_extract_page_claims_replaces_state_text(), test_extract_url_only_fetches_page(), test_read_prepends_link_seed_without_network(), test_request_accepts_blank_text_only_with_image(), test_request_rejects_bad_link_and_image(), test_request_rejects_blank_text_without_image() (+1 more)

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

### Community 95 - "google_serp.py"
Cohesion: 0.24
Nodes (9): FreeSearchUnavailable, _json_response(), AsyncClient, Optional SerpApi Google organic discovery, restricted to a free account., Safe failure code for the optional, free-only search path., main(), One-query live check for the optional free-only Google search adapter., Exception (+1 more)

### Community 100 - "cancellation_probe_app.py"
Cohesion: 0.22
Nodes (7): blocking_extract(), cancellation_state(), InstrumentedGraph, get, Explicit integration-test entry point ONLY; never imported by main/runtime. No…, record(), time

### Community 101 - "asyncio"
Cohesion: 0.22
Nodes (7): asyncio, Offline contract tests for the optional, free-only Google organic adapter., test_malformed_search_metadata_is_safely_classified_as_unavailable(), run(), Safe diagnostics for failed provider fallbacks., httpx, logging

### Community 102 - "recovery_probe_app.py"
Cohesion: 0.22
Nodes (6): get, post, TEST ONLY deterministic recovery app. Never imported by runtime/main., recover(), status(), verify()

### Community 103 - "youtube-context.ts"
Cohesion: 0.43
Nodes (6): download(), YoutubeVideoMetadata(), formatYoutubePublishedAt(), formatYoutubeViewCount(), stripYoutubeApiDataForExport(), youtubeThumbnailUrl()

### Community 105 - "fact-check-client.test.mjs"
Cohesion: 0.29
Nodes (3): insufficientAnswer, result, verifiedSource

### Community 106 - "12. API 계약 초안"
Cohesion: 0.29
Nodes (7): start(), 12.1 엔드포인트, 12.2 입력 예시, 12.3 최소 데이터 모델, 12.4 원문 위치 규약, 12.5 오류 분류, 12. API 계약 초안

### Community 107 - "test_graph_keeps_source_texts_for_verification"
Cohesion: 0.33
Nodes (3): test_graph_keeps_source_texts_for_verification(), read(), reader()

### Community 108 - "probe-stage7.mjs"
Cohesion: 0.29
Nodes (3): errors, observations, responses

### Community 109 - "build_search_query"
Cohesion: 0.40
Nodes (5): build_search_query(), Conservative fallback when extraction did not supply semantic keywords., parametrize, test_build_search_query_keeps_entity_and_year_from_forecast_question(), test_query_fallback_preserves_negation_names_and_numbers()

### Community 110 - "19. 소개 문구와 데모 안내"
Cohesion: 0.40
Nodes (5): 19. 소개 문구와 데모 안내, 검증 결과 하단 문구, 데모 고지 권장 문구, 서비스 소개, 짧은 소개

### Community 111 - "9. 화면 설계"
Cohesion: 0.40
Nodes (5): 9.1 정보 구조, 9.2 주장 카드, 9.3 요약 지표, 9.4 접근성·반응형, 9. 화면 설계

### Community 112 - "probe-cancellation.mjs"
Cohesion: 0.50
Nodes (4): observations, responses, state(), waitCounts()

### Community 113 - "test_account_guard_never_starts_a_search_without_confirmed_free_quota"
Cohesion: 0.50
Nodes (3): parametrize, test_account_guard_never_starts_a_search_without_confirmed_free_quota(), run()

### Community 114 - "15. QA와 수용 기준"
Cohesion: 0.50
Nodes (4): 15. QA와 수용 기준, 출시 조건, 테스트 케이스, 평가 방법

### Community 115 - "6. 주장 추출과 검증 계획"
Cohesion: 0.50
Nodes (4): 6.1 분류 체계, 6.2 주장 구조, 6.3 검색 계획, 6. 주장 추출과 검증 계획

### Community 116 - "8. 판정 정책"
Cohesion: 0.50
Nodes (4): 8.1 결과 분류, 8.2 겹치는 경우의 결정 규칙, 8.3 근거 충족 규칙, 8. 판정 정책

### Community 117 - "test_structured_image_payload_shapes"
Cohesion: 1.00
Nodes (3): test_structured_image_payload_shapes(), handler(), run()

### Community 118 - "14. 보안·개인정보·이용 조건"
Cohesion: 0.67
Nodes (3): 14. 보안·개인정보·이용 조건, URL과 외부 콘텐츠, 입력·저장

### Community 119 - "4. MVP 범위와 단계별 확장"
Cohesion: 0.67
Nodes (3): 4.1 3일 MVP 필수 범위, 4.2 MVP 이후, 4. MVP 범위와 단계별 확장

## Knowledge Gaps
- **260 isolated node(s):** `runtime`, `dynamic`, `headers`, `MODEL_OPTIONS`, `ChatIntent` (+255 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 586 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_runtime_adapters()` connect `make_runtime_adapters` to `LLMProvider`, `verification.py`, `search_sources`, `sources.py`, `search_google_free`, `fetch_youtube_data`, `extraction.py`, `extract_claims`, `search.py`, `Settings`, `ProviderCallError`, `answer_synthesis.py`, `test_runtime.py`, `test_free_quota_exhaustion_falls_back_with_an_explicit_notice`, `test_all_synthesis_providers_failing_preserves_verified_result`, `test_runtime_assembly.py`, `test_forecast_synthesis_preserves_prediction_and_citations`, `build_runtime_workflow`, `runtime.py`, `test_attachments.py`, `google_serp.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `search_google_free()` connect `search_google_free` to `make_runtime_adapters`, `asyncio`, `runtime.py`, `build_search_query`, `test_account_guard_never_starts_a_search_without_confirmed_free_quota`, `search.py`, `google_serp.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `LLMProvider` connect `LLMProvider` to `ProviderCallError`, `answer_synthesis.py`, `search_sources`, `make_runtime_adapters`, `verification.py`, `test_attachments.py`, `providers.py`, `extraction.py`, `extract_claims`, `test_structured_image_payload_shapes`, `test_intent.py`, `search.py`, `handler`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `LLMProvider` (e.g. with `synthesize_answer()` and `extract_claims()`) actually correct?**
  _`LLMProvider` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `make_runtime_adapters()` (e.g. with `FreeSearchUnavailable` and `extract()`) actually correct?**
  _`make_runtime_adapters()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `ProviderCallError` (e.g. with `extract_claims()` and `extract_image_claims()`) actually correct?**
  _`ProviderCallError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `search_sources()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`search_sources()` has 2 INFERRED edges - model-reasoned connections that need verification._