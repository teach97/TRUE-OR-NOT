# Graph Report - my-app  (2026-09-24)

## Corpus Check
- 135 files · ~92,118 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1411 nodes · 2812 edges · 100 communities (74 shown, 26 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 300 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Answer Contracts
- Answer Synthesis Tests
- Answer Contracts
- Search Query Pipeline
- Public Source Fetching
- Execution Boundary Tests
- Verification Pipeline Concepts
- Free Search Adapter
- Composer Text Components
- Source Fetch Fixtures
- Cancellation Probe Harness
- Backend Entry Points
- Provider Transports
- YouTube Offline Tests
- Test Module References
- Page Claim Extraction
- Chat Intent Routing
- Claim Extraction Flow
- Demo Fixture Content
- Server Request Validation
- Stream Progress Events
- Vector Wordmark Renderer
- Client Stream Reader
- Request Schema Models
- Search Image Payloads
- Candidate URL Discovery
- TypeScript Compiler Config
- Fact-Check Type Contract
- API Status Tests
- Fact-Check API Route
- Reply Citation UI
- Lattice Loading UI
- Next Brand Assets
- Fallback Error Chain
- Source Security Tests
- Backend Design Docs
- Runtime Adapters
- Graph Stage Tests
- App Layout Pages
- Extraction Graph Tests
- Runtime Workflow Graph
- Package Dependencies
- Public Source Reader
- Free Search Tests
- Synthesis Provider Tests
- Floating Lines Visual
- Lines Background Boundary
- Scramble Text Effect
- Result Assembly Details
- Router Mode Guides
- Welcome Home Routes
- Type Definition Packages
- Router App Bootstrap
- Forecast Synthesis Tests
- Light Logo Assets
- Sidebar Line Controls
- Globe Icon Assets
- Router Build Config
- Runtime Dependencies
- Package Scripts
- File Icon Assets
- Intent API Route
- Dark Logo Assets
- API Status Tests
- ESLint Configuration
- Next Generated Types
- Window Icon Assets
- Workspace Design Docs
- Declarative Mode Docs
- RSC Boundary Docs
- Exception Status Helper
- Attachment Test Suite
- Agent Architecture Docs
- Globe Icon Asset
- Vercel Brand Assets
- Agent Rule Pointers
- Router Mode Concepts
- Answer Contract Concepts
- Synthesis Plan Docs
- Shared Contract Concepts
- Floating Lines Docs
- PostCSS Configuration
- Trust Verdict Models
- UI Design Direction
- UI Verification Record
- Trust Verdict Models
- Planning Document
- Backend Entry Points
- Next Brand Logo
- Backend Service
- FactLens Workspace
- Snapshot 13:08
- Snapshot 13:11
- Snapshot 13:12
- Snapshot 13:14
- Backend Entry Points
- Globe Container Parts
- Globe Layout Grid
- Frontend Readme Concepts
- Frontend Stack Concepts

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
- `Next.js Wordmark Logo` --semantically_similar_to--> `Path-Drawn Brand Wordmark`  [INFERRED] [semantically similar]
  public/next.svg → app/welcome/logo-light.svg
- `Backend Model Fallback Order (Gemini 3.8 Flash → Gemini 3.7 Flash → GPT-6 Luna)` --semantically_similar_to--> `LLM Fallback Chain (Gemini 3.8 Flash → Gemini 3.7 Flash → GPT-6 Luna)`  [INFERRED] [semantically similar]
  backend/README.md → HANDOFF.md
- `Backend Search & Verification Flow` --semantically_similar_to--> `Four-Node LangGraph Runtime (extracting→searching→reading→verifying)`  [INFERRED] [semantically similar]
  backend/README.md → HANDOFF.md
- `True or Not Interactive Fact-Check Workspace (empty state)` --conceptually_related_to--> `7-Stage Fact-Check Implementation Roadmap`  [INFERRED]
  .playwright-cli/page-2026-09-24T01-03-06-200Z.yml → HANDOFF.md
- `Verification Response Format Error State (검증 응답 형식 오류)` --conceptually_related_to--> `Citation Verification & Judgment Rules (5-C, ground_judgments)`  [INFERRED]
  .playwright-cli/page-2026-09-24T01-05-41-775Z.yml → HANDOFF.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **logo_light_composition** — logo_light_red_accent, logo_light_dark_dots, logo_light_wordmark [INFERRED 0.85]
- **public_globe_composition** — public_globe_globe_path, public_globe_clip_path, public_globe_wireframe [INFERRED 0.85]
- **public_next_composition** — public_next_n_mark, public_next_main_letterforms, public_next_js_suffix [INFERRED 0.85]
- **React Router mode selection** — agents_skills_react_router_skill_react_router_modes, agents_skills_react_router_skill_framework_mode_detection, agents_skills_react_router_skill_data_mode_detection, agents_skills_react_router_skill_declarative_mode_detection [EXTRACTED 1.00]
- **Fact-check request pipeline** — readme_fact_check_proxy, backend_readme_factlens_backend, docs_true_or_not_agent_architecture_pipeline [EXTRACTED 1.00]
- **Grounded answer synthesis vertical slice** — docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_answer_contract, docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_synthesis_stage [EXTRACTED 1.00]
- **Elements that form the document file icon** — public_file_document_file_icon, public_file_document_outline, public_file_folded_corner, public_file_text_lines [EXTRACTED 1.00]
- **Four-Stage Fact-Check Pipeline (extracting → searching → reading → verifying)** — handoff_extraction_adapter, handoff_search_connector, handoff_source_fetcher, handoff_verification_rules [EXTRACTED 1.00]
- **True or Not Workspace States (empty → error → result)** — _playwright_cli_page_2026_09_24t01_03_06_200z_true_or_not_workspace, _playwright_cli_page_2026_09_24t01_05_41_775z_true_or_not_workspace, _playwright_cli_page_2026_09_24t01_08_40_011z_true_or_not_workspace [INFERRED 0.75]
- **Answer Model Fallback Chain Agreed Across UI, HANDOFF, and README** — _playwright_cli_page_2026_09_24t01_03_06_200z_model_fallback_selector, handoff_llm_fallback_chain, backend_readme_model_fallback [INFERRED 0.95]
- **Light Logo Composition (Emblem + Wordmark)** — app_welcome_logo_light_logo, app_welcome_logo_light_emblem, app_welcome_logo_light_wordmark [EXTRACTED 1.00]
- **Next.js Wordmark Letterform Group** — public_next_wordmark, public_next_nglyph, public_next_textglyphs [EXTRACTED 1.00]
- **Globe Icon Composition** — public_globe_svg_globe_icon, public_globe_outerring, public_globe_gridlines [EXTRACTED 1.00]

## Communities (100 total, 26 thin omitted)

### Community 0 - "Answer Contracts"
Cohesion: 0.06
Nodes (55): AgentStatus, AnswerBlock, AnswerCitation, AnswerSection, _ContractModel, FactCheckAnswer, FactCheckProgressCitation, FactCheckProgressClaim (+47 more)

### Community 1 - "Answer Synthesis Tests"
Cohesion: 0.07
Nodes (58): eligible_sources(), insufficient_answer(), _limit_sections_to_source_breadth(), _project_claims(), Any, AsyncClient, BaseModel, model_validator (+50 more)

### Community 2 - "Answer Contracts"
Cohesion: 0.08
Nodes (52): html_text(), claim(), Offline citation-grounding and judgment tests; no provider traffic., test_context_mismatch_is_reported_as_missing_context(), test_date_or_context_mismatch_cannot_support_a_claim(), test_ground_judgments_accepts_a_verified_contiguous_quote(), test_ground_judgments_accepts_a_verified_quote_for_an_unclear_checkable_claim(), test_ground_judgments_attaches_only_the_matching_section_not_the_whole_page() (+44 more)

### Community 3 - "Search Query Pipeline"
Cohesion: 0.06
Nodes (41): build_search_query(), AsyncClient, Conservative fallback when extraction did not supply semantic keywords., search_sources(), parametrize, test_candidates_filter_unsafe_urls_and_limit_results(), run(), test_completed_empty_search_is_not_a_verdict() (+33 more)

### Community 4 - "Public Source Fetching"
Cohesion: 0.06
Nodes (26): AbstractResolver, aiohttp, aiohttp_abc, checked_url(), _generic_title(), html_sections(), html_title(), _is_japanese_page_text() (+18 more)

### Community 5 - "Execution Boundary Tests"
Cohesion: 0.05
Nodes (28): get, post, TEST ONLY deterministic recovery app. Never imported by runtime/main., recover(), status(), verify(), test_workflow_preserves_link_and_image_state_keys(), parametrize (+20 more)

### Community 6 - "Verification Pipeline Concepts"
Cohesion: 0.06
Nodes (45): Document Input Panel (원문 입력 + 확인 요청), Evidence-First Verification Principle (결론보다, 근거를 먼저), FactLens (팩트렌즈) Brand, FactLens Evidence Workspace (09-21, settings check failed), Synthetic Example Documents (가상 도시의 문화 행사), FactLens Evidence Workspace (09-21, server check pending), External Transmission & YouTube Data API Consent, Answer Model Fallback Selector (Gemini 3.8 Flash → Gemini 3.7 Flash → GPT-6 Luna Max) (+37 more)

### Community 7 - "Free Search Adapter"
Cohesion: 0.09
Nodes (32): FreeSearchUnavailable, _json_response(), AsyncClient, Optional SerpApi Google organic discovery, restricted to a free account., Safe failure code for the optional, free-only search path., Use only an account confirmed to be on the free plan with quota left., search_google_free(), main() (+24 more)

### Community 8 - "Composer Text Components"
Cohesion: 0.08
Nodes (25): BlurText(), CountUp(), CountUpProps, DonutChart(), safeSourceUrl(), ChatMessage, ChatProgress, firstUrl() (+17 more)

### Community 9 - "Source Fetch Fixtures"
Cohesion: 0.08
Nodes (22): parametrize, Deterministic HTTP response fixtures; resolver safety tested separately., Response, run(), Session, test_low_reach_youtube_source_is_dropped_from_results(), youtube_reader(), test_read_follows_same_origin_meta_refresh() (+14 more)

### Community 10 - "Cancellation Probe Harness"
Cohesion: 0.10
Nodes (26): blocking_extract(), cancellation_state(), InstrumentedGraph, get, Explicit integration-test entry point ONLY; never imported by main/runtime. No…, record(), os, pathlib (+18 more)

### Community 11 - "Backend Entry Points"
Cohesion: 0.09
Nodes (32): classify_intent(), Any, AsyncClient, Return a verify/reply decision; invalid model output is a retryable failure., agent_status(), _code_revision(), fact_check(), fact_check_stream() (+24 more)

### Community 12 - "Provider Transports"
Cohesion: 0.14
Nodes (30): _endpoint_and_headers(), _gemini_schema(), _gemini_text(), LLMProvider, _openai_schema(), _openai_text(), Any, AsyncClient (+22 more)

### Community 13 - "YouTube Offline Tests"
Cohesion: 0.11
Nodes (26): youtube_reader(), Offline YouTube Data API contract tests; no Google credentials or traffic., test_comments_unavailable_keeps_video_title_without_exposing_provider_error(), run(), test_fetches_official_video_title_and_bounded_plain_text_comments(), handler(), run(), test_ignores_malformed_youtube_metadata_without_rejecting_comments() (+18 more)

### Community 14 - "Test Module References"
Cohesion: 0.08
Nodes (18): insufficientAnswer, result, verifiedSource, ref_node_assert, ref_node_fs, ref_node_test, ref_node_url, observations (+10 more)

### Community 15 - "Page Claim Extraction"
Cohesion: 0.11
Nodes (26): extract_image_claims(), extract_page_claims(), ExtractedClaim, Extraction, ImageObservation, _project_extracted_claims(), AsyncClient, BaseModel (+18 more)

### Community 16 - "Chat Intent Routing"
Cohesion: 0.12
Nodes (22): ChatIntent, CLAIM_PATTERNS, classifyChatInput(), describeHistory(), EARLY_META, FOLLOW_UP_PATTERNS, HELP_PATTERNS, isFollowUpText() (+14 more)

### Community 17 - "Claim Extraction Flow"
Cohesion: 0.14
Nodes (19): extract_claims(), Return a LangGraph state update; callers own the client and credential., parametrize, Offline provider transport fixtures, never real model responses., test_extractor_drops_invented_claim_without_fabricating_source_text(), run(), test_extractor_keeps_forecast_and_returns_search_keywords_separately(), handler() (+11 more)

### Community 18 - "Demo Fixture Content"
Cohesion: 0.14
Nodes (20): base, DEMO_FOCUS, DEMO_TEXT, demoPreview, documents, results, Action, Claim (+12 more)

### Community 19 - "Server Request Validation"
Cohesion: 0.13
Nodes (20): AttachedImage, FactClaim, FactEvidence, VerdictCode, canonical(), extractClaims(), extractionSchema, format() (+12 more)

### Community 20 - "Stream Progress Events"
Cohesion: 0.12
Nodes (15): Propagate cancellation and close the graph iterator on every exit path., stream_events(), graph(), parametrize, Offline streaming tests; fixtures do not represent real verification., test_stream_emits_candidate_sources_and_grounded_preview_before_final_result(), collect(), test_stream_endpoint_emits_ordered_stages_and_valid_result() (+7 more)

### Community 21 - "Vector Wordmark Renderer"
Cohesion: 0.17
Nodes (21): Atlas, buildAtlas(), clamp(), compile(), FontSpec, fontString(), fract(), HANDLE_DEFAULTS (+13 more)

### Community 22 - "Client Stream Reader"
Cohesion: 0.15
Nodes (19): FactCheckError, Options, readFactCheckStream(), line(), validAnswer(), validEvidenceSection(), validProgressCitation(), validProgressClaim() (+11 more)

### Community 23 - "Request Schema Models"
Cohesion: 0.12
Nodes (13): FactCheckRequest, ImageAttachment, BaseModel, model_validator, test_request_preserves_original_text(), Link and image attachment paths; no external traffic (all transports mocked)., test_extract_image_claims_replaces_state_text(), test_extract_page_claims_replaces_state_text() (+5 more)

### Community 24 - "Search Image Payloads"
Cohesion: 0.13
Nodes (17): asyncio, providers_for_preference(), Return the automatic chain or exactly one explicitly selected model., decision_response(), Intent gate tests; no external traffic (all transports mocked)., test_intent_reply_requires_text(), run_empty(), run_reply() (+9 more)

### Community 25 - "Candidate URL Discovery"
Cohesion: 0.18
Nodes (19): read(), candidate_url(), is_japanese_candidate(), is_unreliable_candidate(), _normalized_host(), origin_group_for_url(), _project_candidates(), Candidate discovery only; pending sources and snippets are not evidence. URL… (+11 more)

### Community 26 - "TypeScript Compiler Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 27 - "Fact-Check Type Contract"
Cohesion: 0.12
Nodes (15): AgentStage, AgentStatus, AnswerSection, FACT_CHECK_MODEL, FACT_CHECK_REASONING, FactSource, MODEL_OPTIONS, ModelId (+7 more)

### Community 28 - "API Status Tests"
Cohesion: 0.14
Nodes (14): BaseModel, Settings, parametrize, Offline API boundary checks; no provider calls., test_health_and_status_do_not_claim_provider_readiness(), test_request_rejects_invalid_input(), test_request_rejects_unknown_model_preference(), test_request_requires_all_contract_fields() (+6 more)

### Community 29 - "Fact-Check API Route"
Cohesion: 0.18
Nodes (11): backend(), dynamic, error(), GET(), headers, MODEL_OPTIONS, POST(), runtime (+3 more)

### Community 30 - "Reply Citation UI"
Cohesion: 0.15
Nodes (15): AnswerBlockView(), AnswerOverview(), AnswerCitationDisplay, AnswerCitationDisplayState, AssistantReply, composeAssistantReply(), createAnswerCitationDisplayState(), presentAnswerCitations() (+7 more)

### Community 31 - "Lattice Loading UI"
Cohesion: 0.16
Nodes (14): DEFAULT_PATTERN, formatElapsed(), GridSize, LatticeLoader(), LatticeLoaderProps, LoaderStatus, LoaderStyle, MARKS (+6 more)

### Community 32 - "Next Brand Assets"
Cohesion: 0.17
Nodes (15): Geometric Brand Emblem (Red & Black Circles), Light Theme Variant (Dark Glyphs on Light Background), logo-light.svg light-mode branding logo, Path-Drawn Brand Wordmark, Next.js Framework Brand, Default template branding, next.svg, .js suffix glyphs (+7 more)

### Community 33 - "Fallback Error Chain"
Cohesion: 0.23
Nodes (13): ProviderCallError, A provider attempt failed and the next configured provider may retry., Run an operation in priority order and return its result and provider., run_with_fallback(), main(), call(), test_provider_fallback_logs_model_stage_and_status_without_secrets(), fail_extraction() (+5 more)

### Community 34 - "Source Security Tests"
Cohesion: 0.22
Nodes (14): module(), parametrize, Public-source security tests; no external traffic., test_html_excludes_noncontent(), test_html_excludes_video_and_custom_player_elements(), test_html_extracts_article_text_without_navigation_or_player_chrome(), test_html_fallback_still_excludes_menu_and_player_without_article_markers(), test_html_preserves_paragraph_breaks_for_readable_source_text() (+6 more)

### Community 35 - "Backend Design Docs"
Cohesion: 0.16
Nodes (14): Backend Environment Keys Configuration, FactLens Backend Fact-check API, Search Verification Flow Max 3 Claims 6 Sources, Fact-check Streaming Endpoint, Five Stage Search Improvement Pipeline, Free Google Organic Search via SerpApi, Multi-LLM Fallback Priority Order, Duplicate Link and Japanese Search Result Correction (+6 more)

### Community 36 - "Runtime Adapters"
Cohesion: 0.23
Nodes (13): make_runtime_adapters(), extract(), page_operation(), search(), synthesize(), operation(), verify(), with_client() (+5 more)

### Community 37 - "Graph Stage Tests"
Cohesion: 0.19
Nodes (6): test_real_graph_carries_free_search_fallback_notice_to_later_stages(), extract(), synthesize(), verify(), test_runtime_graph_assembles_valid_final_result_after_five_stages(), test_synthesis_stage_failure_does_not_return_intermediate_result()

### Community 38 - "App Layout Pages"
Cohesion: 0.15
Nodes (6): app_globals, metadata, metadata, metadata, nextConfig, next

### Community 39 - "Extraction Graph Tests"
Cohesion: 0.21
Nodes (11): build_extraction_graph(), load_settings(), Stage, End after extraction; do not simulate search, sources, or judgments., Read the backend-local file without mutating process environment., Isolated settings and extraction graph tests; no paid API calls., test_extraction_graph_ends_without_fabricating_verdict(), test_serpapi_key_is_server_only_and_redacted() (+3 more)

### Community 40 - "Runtime Workflow Graph"
Cohesion: 0.21
Nodes (10): build_runtime_workflow(), Compile five ordered stages and assemble the result after synthesis., The five graph stages, injectable for offline orchestration tests., RuntimeAdapters, test_forecast_keywords_reach_search_through_graph_without_leaking_into_result(), handler(), run(), extract() (+2 more)

### Community 41 - "Package Dependencies"
Cohesion: 0.15
Nodes (12): name, private, type, postcss, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+4 more)

### Community 42 - "Public Source Reader"
Cohesion: 0.26
Nodes (10): Address, fetchPublicText(), htmlToText(), publicAddress(), resolvePublicUrl(), Resolver, ref_node_dns, ref_node_http (+2 more)

### Community 43 - "Free Search Tests"
Cohesion: 0.23
Nodes (9): test_configured_free_google_search_is_selected_before_llm_search(), handler(), mock_async_client(), test_free_quota_exhaustion_falls_back_with_an_explicit_notice(), mock_async_client(), test_llm_runtime_ignores_environment_proxy_for_provider_connection(), mock_async_client(), test_runtime_read_stage_uses_youtube_adapter_without_adding_comments_to_source_texts() (+1 more)

### Community 44 - "Synthesis Provider Tests"
Cohesion: 0.22
Nodes (9): source(), test_all_synthesis_providers_failing_preserves_verified_result(), failing_provider(), mock_client(), read(), search(), read(), read() (+1 more)

### Community 45 - "Floating Lines Visual"
Cohesion: 0.22
Nodes (9): DEFAULT_BOTTOM_WAVE_POSITION, DEFAULT_ENABLED_WAVES, DEFAULT_LINE_COUNT, DEFAULT_LINE_DISTANCE, FloatingLines(), FloatingLinesProps, hexToVec3(), WavePosition (+1 more)

### Community 46 - "Lines Background Boundary"
Cohesion: 0.20
Nodes (7): BackgroundBoundary, FloatingLines, FloatingLinesBackground(), floatingLinesCount, floatingLinesDistance, floatingLinesGradient, floatingLinesWaves

### Community 47 - "Scramble Text Effect"
Cohesion: 0.36
Nodes (9): getRevealOrder(), randomCharacter(), randomizeText(), ScrambleRun, ScrambleText(), resetVisual(), startRun(), writeVisual() (+1 more)

### Community 48 - "Result Assembly Details"
Cohesion: 0.27
Nodes (9): build_fact_check_result(), _normalize_source(), Project internal source state onto the public TypeScript contract., Validate and assemble the only result shape exposed by the API., _result_warnings(), Runtime assembly tests; explicit adapters keep the five-node graph offline., test_final_result_warns_when_free_google_search_was_unavailable(), test_result_exposes_youtube_comments_only_as_context_not_verified_content() (+1 more)

### Community 49 - "Router Mode Guides"
Cohesion: 0.22
Nodes (9): Data Loading with Loaders and Actions, Data Router Shape, Forms Fetchers and Pending UI, Middleware Sessions and Auth, Framework Rendering Strategy, Framework Route Modules, Framework Type Safety with Generated Route Types, Data Mode Detection Signals (+1 more)

### Community 50 - "Welcome Home Routes"
Cohesion: 0.25
Nodes (5): app_welcome_logo_dark, app_welcome_logo_light, resources, Welcome(), ref_types_home

### Community 51 - "Type Definition Packages"
Cohesion: 0.22
Nodes (9): devDependencies, postcss, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom, @types/three (+1 more)

### Community 52 - "Router App Bootstrap"
Cohesion: 0.25
Nodes (3): app_app, ref_react_router, ref_types_root

### Community 53 - "Forecast Synthesis Tests"
Cohesion: 0.29
Nodes (4): test_forecast_synthesis_preserves_prediction_and_citations(), mock_client(), provider_response(), search()

### Community 54 - "Light Logo Assets"
Cohesion: 0.29
Nodes (8): Dark circular dots, logo-light.svg, Logo icon mark, Light theme variant, Red accent path, SVG root 1080x174, Welcome page branding, Wordmark letter paths

### Community 55 - "Sidebar Line Controls"
Cohesion: 0.29
Nodes (6): Falloff, FALLOFF_CURVES, LineSidebar(), LineSidebarItem, LineSidebarProps, LineSidebarStyle

### Community 56 - "Globe Icon Assets"
Cohesion: 0.33
Nodes (7): Clip path definition, Default template icon, globe.svg, Globe wireframe path, Monochrome gray variant, SVG root 16x16, Globe wireframe motif

### Community 57 - "Router Build Config"
Cohesion: 0.33
Nodes (3): ref_react_router_dev, ref_tailwindcss_vite, ref_vite

### Community 58 - "Runtime Dependencies"
Cohesion: 0.33
Nodes (6): dependencies, motion, next, react, react-dom, three

### Community 59 - "Package Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, start, typecheck

### Community 60 - "File Icon Assets"
Cohesion: 0.40
Nodes (5): Document File Icon, Document Page Outline, Folded Corner, Gray Fill Style, Text Content Lines

### Community 61 - "Intent API Route"
Cohesion: 0.83
Nodes (3): backend(), error(), POST()

### Community 62 - "Dark Logo Assets"
Cohesion: 0.50
Nodes (4): Dark Background Variant Purpose for Welcome Page, Geometric Icon Mark with Red Accent and White Nodes, Dark Mode Logo SVG, React Router Wordmark in White

### Community 63 - "API Status Tests"
Cohesion: 0.50
Nodes (3): test_runtime_stage_keeps_explicit_provider_selection_pinned_after_failure(), test_runtime_stage_retries_next_provider_after_adapter_failure(), fake_extract()

### Community 64 - "ESLint Configuration"
Cohesion: 0.50
Nodes (3): eslintConfig, ref_eslint, ref_eslint_config_next

### Community 65 - "Next Generated Types"
Cohesion: 0.50
Nodes (3): next_dev_types_root_params_d, next_dev_types_routes_d, NOTE: This file should not be edited

### Community 66 - "Window Icon Assets"
Cohesion: 0.50
Nodes (4): Minimal Window Chrome Icon Purpose for UI, Three Circular Window Control Dots in Title Bar, Window Frame Outline with Rounded Bottom Corners, Browser Window Icon SVG in Gray

### Community 67 - "Workspace Design Docs"
Cohesion: 0.67
Nodes (3): Next.js breaking changes guide and verification cleanup, Premium research workspace dark glass design, Dashboard demo-state fixture shader implementation and checks

### Community 68 - "Declarative Mode Docs"
Cohesion: 0.67
Nodes (3): Declarative Router Shape, Declarative Mode Boundary, Declarative Mode Detection Signals

### Community 69 - "RSC Boundary Docs"
Cohesion: 0.67
Nodes (3): RSC Client Server Boundaries, RSC Route Module Differences, RSC Detection Signals

### Community 70 - "Exception Status Helper"
Cohesion: 0.67
Nodes (3): _http_status_from_exception(), Return only an upstream HTTP status from an exception chain., BaseException

### Community 72 - "Agent Architecture Docs"
Cohesion: 0.67
Nodes (3): True or Not agent architecture, Gemini Interactions API docs citation, GPT-6 Luna model docs citation

### Community 73 - "Globe Icon Asset"
Cohesion: 0.67
Nodes (3): Globe Grid Lines (Meridians & Parallels), Globe Outer Ring, Globe Icon 16x16

### Community 74 - "Vercel Brand Assets"
Cohesion: 0.67
Nodes (3): Vercel Brand Mark Purpose for Deployment Branding, White Filled Triangle Mark viewBox 1155x1000, Vercel Triangle Logo SVG in White

## Knowledge Gaps
- **223 isolated node(s):** `MVP F01-F11 and claim-centered product principles`, `Seven verdict codes mostly_supported to contradicted`, `True or Not advanced planning v2`, `runtime`, `dynamic` (+218 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 552 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMProvider` connect `Provider Transports` to `Answer Synthesis Tests`, `Fallback Error Chain`, `Search Query Pipeline`, `Answer Contracts`, `Backend Entry Points`, `Page Claim Extraction`, `Claim Extraction Flow`, `Request Schema Models`, `Search Image Payloads`, `Candidate URL Discovery`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `make_runtime_adapters()` connect `Runtime Adapters` to `Answer Synthesis Tests`, `Answer Contracts`, `Search Query Pipeline`, `Public Source Fetching`, `Free Search Adapter`, `YouTube Offline Tests`, `Page Claim Extraction`, `Claim Extraction Flow`, `Request Schema Models`, `Search Image Payloads`, `Candidate URL Discovery`, `API Status Tests`, `Fallback Error Chain`, `Extraction Graph Tests`, `Runtime Workflow Graph`, `Free Search Tests`, `Synthesis Provider Tests`, `Result Assembly Details`, `Forecast Synthesis Tests`, `API Status Tests`, `Attachment Test Suite`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `ProviderCallError` connect `Fallback Error Chain` to `Answer Synthesis Tests`, `Answer Contracts`, `Search Query Pipeline`, `Runtime Adapters`, `Backend Entry Points`, `Provider Transports`, `Page Claim Extraction`, `Claim Extraction Flow`, `Search Image Payloads`, `Candidate URL Discovery`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `LLMProvider` (e.g. with `synthesize_answer()` and `extract_claims()`) actually correct?**
  _`LLMProvider` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `make_runtime_adapters()` (e.g. with `FreeSearchUnavailable` and `extract()`) actually correct?**
  _`make_runtime_adapters()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `ProviderCallError` (e.g. with `extract_claims()` and `extract_image_claims()`) actually correct?**
  _`ProviderCallError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `search_sources()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`search_sources()` has 2 INFERRED edges - model-reasoned connections that need verification._