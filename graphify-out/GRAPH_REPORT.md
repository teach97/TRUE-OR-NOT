# Graph Report - my-app  (2026-09-24)

## Corpus Check
- 59 files · ~91,941 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1358 nodes · 2730 edges · 112 communities (85 shown, 27 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 274 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Answer Contracts
- Public Source Fetching
- Free Search Adapter
- Execution Boundary Tests
- Source Fetch Fixtures
- Cancellation Probe Harness
- Composer Text Components
- YouTube Offline Tests
- Backend Entry Points
- Chat Intent Routing
- Answer Synthesis Stage
- Recovery Probe Scripts
- Search Query Pipeline
- Claim Extraction Flow
- Demo Fixture Content
- Vector Wordmark Renderer
- Fact-Check Type Contract
- Provider Transports
- Stream Progress Events
- Answer Synthesis Tests
- Client Stream Reader
- Server Request Validation
- Candidate URL Discovery
- Graph Stage Tests
- TypeScript Compiler Config
- Intent Gate API
- Result Assembly Contract
- API Status Tests
- Source Error Tests
- Fact-Check API Route
- Reply Citation UI
- Lattice Loading UI
- Search Query Builder
- Attachment Test Suite
- Source Security Tests
- Test Module References
- Search Image Payloads
- Fallback Error Chain
- Backend Design Docs
- Runtime Workflow Graph
- Runtime Adapters
- App Layout Pages
- Grounded Answer Tests
- Page Claim Extraction
- Request Schema Models
- Package Dependencies
- Public Source Reader
- Provider Configuration
- Free Search Tests
- Extraction Graph Tests
- Synthesis Provider Tests
- Floating Lines Visual
- Lines Background Boundary
- Scramble Text Effect
- Result Assembly Details
- Router Mode Guides
- Welcome Home Routes
- Synthesis Citation Rules
- Type Definition Packages
- Router App Bootstrap
- Forecast Synthesis Tests
- Light Logo Assets
- Next Brand Assets
- Client Stream Tests
- YouTube Context Helpers
- Sidebar Line Controls
- Globe Icon Assets
- Probe Test Scripts
- Router Build Config
- Insufficient Answer Path
- Runtime Dependencies
- Package Scripts
- File Icon Assets
- Cancellation Probe Scripts
- Intent API Route
- Dark Logo Assets
- ESLint Configuration
- Next Generated Types
- Window Icon Assets
- Workspace Design Docs
- Declarative Mode Docs
- RSC Boundary Docs
- Exception Status Helper
- Agent Architecture Docs
- Vercel Brand Assets
- Agent Rule Pointers
- Router Mode Concepts
- Answer Contract Concepts
- Synthesis Plan Docs
- Verification Pipeline Concepts
- Shared Contract Concepts
- Trust Verdict Models
- Floating Lines Docs
- PostCSS Configuration
- Light Logo Branding
- HTTP Get Route
- HTTP Post Route
- UI Design Direction
- UI Verification Record
- Planning Document
- Next Brand Logo
- Backend Service
- FactLens Workspace
- Snapshot 13:08
- Snapshot 13:11
- Snapshot 13:12
- Snapshot 13:14
- Globe Container Parts
- Globe Icon Asset
- Globe Layout Grid
- Frontend Readme Concepts
- Frontend Stack Concepts

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 67 edges
2. `ProviderCallError` - 45 edges
3. `make_runtime_adapters()` - 44 edges
4. `search_sources()` - 41 edges
5. `Settings` - 39 edges
6. `synthesize_answer()` - 34 edges
7. `extract_claims()` - 29 edges
8. `ground_judgments()` - 28 edges
9. `search_google_free()` - 27 edges
10. `verify_claims()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `Dashboard demo-state fixture shader implementation and checks` --conceptually_related_to--> `Next.js breaking changes guide and verification cleanup`  [INFERRED]
  docs/True or Not-UI-verification.md → AGENTS.md
- `test_request_rejects_unknown_model_preference()` --uses--> `FactCheckRequest`  [INFERRED]
  backend/tests/test_api.py → backend/schemas.py
- `test_request_accepts_blank_text_only_with_image()` --uses--> `FactCheckRequest`  [INFERRED]
  backend/tests/test_attachments.py → backend/schemas.py
- `test_request_rejects_bad_link_and_image()` --uses--> `FactCheckRequest`  [INFERRED]
  backend/tests/test_attachments.py → backend/schemas.py
- `test_request_rejects_blank_text_without_image()` --uses--> `FactCheckRequest`  [INFERRED]
  backend/tests/test_attachments.py → backend/schemas.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Fact-check request pipeline** — readme_fact_check_proxy, docs_true_or_not_agent_architecture_pipeline [EXTRACTED 1.00]
- **Grounded answer synthesis vertical slice** — docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_answer_contract, docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_synthesis_stage [EXTRACTED 1.00]
- **Elements that form the document file icon** — public_file_document_file_icon, public_file_document_outline, public_file_folded_corner, public_file_text_lines [EXTRACTED 1.00]
- **React Router mode selection** — agents_skills_react_router_skill_react_router_modes, agents_skills_react_router_skill_framework_mode_detection, agents_skills_react_router_skill_data_mode_detection, agents_skills_react_router_skill_declarative_mode_detection [EXTRACTED 1.00]
- **logo_light_composition** — logo_light_red_accent, logo_light_dark_dots, logo_light_wordmark [INFERRED 0.85]
- **public_globe_composition** — public_globe_globe_path, public_globe_clip_path, public_globe_wireframe [INFERRED 0.85]
- **public_next_composition** — public_next_n_mark, public_next_main_letterforms, public_next_js_suffix [INFERRED 0.85]

## Communities (112 total, 27 thin omitted)

### Community 0 - "Answer Contracts"
Cohesion: 0.06
Nodes (68): FactClaim, model_validator, default_fact_score(), normalize_fact_score(), Evidence-grounded public score policy for fact-check claims., Return the public band for an inclusive 0–100 score., Preserve the model's reasoned score, clamped only to the 0-100 range. The…, Supply a compatible score when an older result omits the new field. (+60 more)

### Community 1 - "Public Source Fetching"
Cohesion: 0.06
Nodes (24): AbstractResolver, aiohttp, aiohttp_abc, checked_url(), _generic_title(), html_sections(), html_title(), _is_japanese_page_text() (+16 more)

### Community 2 - "Free Search Adapter"
Cohesion: 0.09
Nodes (32): FreeSearchUnavailable, _json_response(), AsyncClient, Optional SerpApi Google organic discovery, restricted to a free account., Safe failure code for the optional, free-only search path., Use only an account confirmed to be on the free plan with quota left., search_google_free(), main() (+24 more)

### Community 3 - "Execution Boundary Tests"
Cohesion: 0.08
Nodes (19): test_workflow_preserves_link_and_image_state_keys(), parametrize, Real LangGraph via HTTP boundary; adapters contain offline fixtures only., test_graph_failure_returns_safe_error(), stage(), test_invalid_http_input_is_safe_and_never_runs_graph(), test_post_rejects_malformed_result_contract(), test_post_runs_graph_and_returns_only_result() (+11 more)

### Community 4 - "Source Fetch Fixtures"
Cohesion: 0.08
Nodes (22): parametrize, Deterministic HTTP response fixtures; resolver safety tested separately., Response, run(), Session, test_low_reach_youtube_source_is_dropped_from_results(), youtube_reader(), test_read_follows_same_origin_meta_refresh() (+14 more)

### Community 5 - "Cancellation Probe Harness"
Cohesion: 0.10
Nodes (26): blocking_extract(), cancellation_state(), InstrumentedGraph, get, Explicit integration-test entry point ONLY; never imported by main/runtime. No…, record(), os, pathlib (+18 more)

### Community 6 - "Composer Text Components"
Cohesion: 0.08
Nodes (18): BlurText(), CountUpProps, safeSourceUrl(), ChatMessage, ChatProgress, firstUrl(), IconName, PanelProps (+10 more)

### Community 7 - "YouTube Offline Tests"
Cohesion: 0.12
Nodes (25): Offline YouTube Data API contract tests; no Google credentials or traffic., test_comments_unavailable_keeps_video_title_without_exposing_provider_error(), run(), test_fetches_official_video_title_and_bounded_plain_text_comments(), handler(), run(), test_ignores_malformed_youtube_metadata_without_rejecting_comments(), run() (+17 more)

### Community 8 - "Backend Entry Points"
Cohesion: 0.09
Nodes (29): agent_status(), _code_revision(), fact_check(), fact_check_stream(), get_workflow(), health(), HealthStatus, intent() (+21 more)

### Community 9 - "Chat Intent Routing"
Cohesion: 0.12
Nodes (22): ChatIntent, CLAIM_PATTERNS, classifyChatInput(), describeHistory(), EARLY_META, FOLLOW_UP_PATTERNS, HELP_PATTERNS, isFollowUpText() (+14 more)

### Community 10 - "Answer Synthesis Stage"
Cohesion: 0.13
Nodes (23): eligible_sources(), _project_claims(), Any, Synthesize a user-facing answer from verified source text only., Build a minimal JSON-safe input; never forward raw source/search records., Project at most six verified non-YouTube texts into a provider-safe shape., _string_value(), _synthesis_input() (+15 more)

### Community 11 - "Recovery Probe Scripts"
Cohesion: 0.15
Nodes (22): FactCheckResult, get, post, TEST ONLY deterministic recovery app. Never imported by runtime/main., recover(), status(), verify(), grounded_answer() (+14 more)

### Community 12 - "Search Query Pipeline"
Cohesion: 0.12
Nodes (20): AsyncClient, search_sources(), search(), test_prediction_claims_are_searched_with_primary_query_in_provider_order(), run(), test_search_collects_deduplicated_candidates_without_evidence(), run(), test_search_keeps_completed_sources_when_response_has_nonterminal_search_item() (+12 more)

### Community 13 - "Claim Extraction Flow"
Cohesion: 0.14
Nodes (19): extract_claims(), Return a LangGraph state update; callers own the client and credential., parametrize, Offline provider transport fixtures, never real model responses., test_extractor_drops_invented_claim_without_fabricating_source_text(), run(), test_extractor_keeps_forecast_and_returns_search_keywords_separately(), handler() (+11 more)

### Community 14 - "Demo Fixture Content"
Cohesion: 0.13
Nodes (19): base, DEMO_FOCUS, DEMO_TEXT, demoPreview, documents, results, Action, Claim (+11 more)

### Community 15 - "Vector Wordmark Renderer"
Cohesion: 0.17
Nodes (21): Atlas, buildAtlas(), clamp(), compile(), FontSpec, fontString(), fract(), HANDLE_DEFAULTS (+13 more)

### Community 16 - "Fact-Check Type Contract"
Cohesion: 0.10
Nodes (19): AgentStage, AgentStatus, AnswerSection, AttachedImage, FACT_CHECK_MODEL, FACT_CHECK_REASONING, FactClaim, FactEvidence (+11 more)

### Community 17 - "Provider Transports"
Cohesion: 0.16
Nodes (22): _endpoint_and_headers(), _gemini_schema(), clean(), _gemini_text(), _openai_schema(), clean(), _openai_text(), Any (+14 more)

### Community 18 - "Stream Progress Events"
Cohesion: 0.12
Nodes (16): FactCheckResponse, encode(), NDJSON boundary: only stage labels and validated final results are public., Propagate cancellation and close the graph iterator on every exit path., stream_events(), parametrize, test_stream_emits_candidate_sources_and_grounded_preview_before_final_result(), collect() (+8 more)

### Community 19 - "Answer Synthesis Tests"
Cohesion: 0.19
Nodes (20): completed_response(), draft(), multi_section_draft(), parametrize, Offline tests for source-bounded, citation-grounded answer synthesis., state_with_source(), test_invalid_citation_from_first_provider_retries_and_uses_next_provider_metadata(), handler() (+12 more)

### Community 20 - "Client Stream Reader"
Cohesion: 0.16
Nodes (18): FactCheckError, Options, readFactCheckStream(), line(), validAnswer(), validEvidenceSection(), validProgressCitation(), validProgressClaim() (+10 more)

### Community 21 - "Server Request Validation"
Cohesion: 0.16
Nodes (17): canonical(), extractClaims(), extractionSchema, format(), groundJudgments(), JsonObject, Judgment, judgmentSchema (+9 more)

### Community 22 - "Candidate URL Discovery"
Cohesion: 0.18
Nodes (18): candidate_url(), is_japanese_candidate(), is_unreliable_candidate(), _normalized_host(), origin_group_for_url(), _project_candidates(), Candidate discovery only; pending sources and snippets are not evidence. URL…, Return a conservative publisher group used to avoid duplicate origins. (+10 more)

### Community 23 - "Graph Stage Tests"
Cohesion: 0.16
Nodes (9): run(), extract(), test_real_graph_carries_free_search_fallback_notice_to_later_stages(), extract(), read(), synthesize(), verify(), test_runtime_graph_assembles_valid_final_result_after_five_stages() (+1 more)

### Community 24 - "TypeScript Compiler Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 25 - "Intent Gate API"
Cohesion: 0.16
Nodes (14): asyncio, classify_intent(), IntentDecision, Any, AsyncClient, BaseModel, Cheap intent gate: verify with the pipeline or answer conversationally., Return a verify/reply decision; invalid model output is a retryable failure. (+6 more)

### Community 26 - "Result Assembly Contract"
Cohesion: 0.19
Nodes (17): AgentStatus, AnswerBlock, AnswerCitation, AnswerSection, _ContractModel, FactCheckAnswer, FactCheckProgressCitation, FactCheckProgressClaim (+9 more)

### Community 27 - "API Status Tests"
Cohesion: 0.14
Nodes (14): BaseModel, Settings, Offline API boundary checks; no provider calls., test_health_and_status_do_not_claim_provider_readiness(), test_request_preserves_original_text(), test_request_rejects_unknown_model_preference(), test_status_reports_gemini_fallback_when_openai_is_missing(), test_status_reports_gpt6_luna_when_only_openai_is_configured() (+6 more)

### Community 28 - "Source Error Tests"
Cohesion: 0.14
Nodes (13): parametrize, Offline failure, safety and empty-result tests., test_candidates_filter_unsafe_urls_and_limit_results(), run(), test_completed_empty_search_is_not_a_verdict(), run(), test_nonfacts_skip_network(), run() (+5 more)

### Community 29 - "Fact-Check API Route"
Cohesion: 0.18
Nodes (11): backend(), dynamic, error(), GET(), headers, MODEL_OPTIONS, POST(), runtime (+3 more)

### Community 30 - "Reply Citation UI"
Cohesion: 0.15
Nodes (15): AnswerBlockView(), AnswerOverview(), AnswerCitationDisplay, AnswerCitationDisplayState, AssistantReply, composeAssistantReply(), createAnswerCitationDisplayState(), presentAnswerCitations() (+7 more)

### Community 31 - "Lattice Loading UI"
Cohesion: 0.16
Nodes (14): DEFAULT_PATTERN, formatElapsed(), GridSize, LatticeLoader(), LatticeLoaderProps, LoaderStatus, LoaderStyle, MARKS (+6 more)

### Community 32 - "Search Query Builder"
Cohesion: 0.16
Nodes (14): read(), youtube_reader(), build_search_query(), Classify a URL for display and diversity selection, not truth scoring., Conservative fallback when extraction did not supply semantic keywords., source_type_for_url(), parametrize, Offline search fixtures, not verified sources. (+6 more)

### Community 33 - "Attachment Test Suite"
Cohesion: 0.13
Nodes (9): Link and image attachment paths; no external traffic (all transports mocked)., test_extract_image_claims_replaces_state_text(), test_extract_page_claims_replaces_state_text(), test_extract_url_only_fetches_page(), test_read_prepends_link_seed_without_network(), test_request_accepts_blank_text_only_with_image(), test_request_rejects_bad_link_and_image(), test_request_rejects_blank_text_without_image() (+1 more)

### Community 34 - "Source Security Tests"
Cohesion: 0.22
Nodes (14): module(), parametrize, Public-source security tests; no external traffic., test_html_excludes_noncontent(), test_html_excludes_video_and_custom_player_elements(), test_html_extracts_article_text_without_navigation_or_player_chrome(), test_html_fallback_still_excludes_menu_and_player_without_article_markers(), test_html_preserves_paragraph_breaks_for_readable_source_text() (+6 more)

### Community 35 - "Test Module References"
Cohesion: 0.21
Nodes (8): ref_node_assert, ref_node_fs, ref_node_test, ref_node_url, observations, responses, observations, responses

### Community 36 - "Search Image Payloads"
Cohesion: 0.24
Nodes (13): LLMProvider, Project provider search output to candidate URL annotations., search_candidates(), test_structured_image_payload_shapes(), handler(), run(), decision_response(), Intent gate tests; no external traffic (all transports mocked). (+5 more)

### Community 37 - "Fallback Error Chain"
Cohesion: 0.23
Nodes (13): ProviderCallError, A provider attempt failed and the next configured provider may retry., Run an operation in priority order and return its result and provider., run_with_fallback(), main(), call(), test_provider_fallback_logs_model_stage_and_status_without_secrets(), fail_extraction() (+5 more)

### Community 38 - "Backend Design Docs"
Cohesion: 0.16
Nodes (14): Backend Environment Keys Configuration, FactLens Backend Fact-check API, Search Verification Flow Max 3 Claims 6 Sources, Fact-check Streaming Endpoint, Five Stage Search Improvement Pipeline, Free Google Organic Search via SerpApi, Multi-LLM Fallback Priority Order, Duplicate Link and Japanese Search Result Correction (+6 more)

### Community 39 - "Runtime Workflow Graph"
Cohesion: 0.20
Nodes (9): build_runtime_workflow(), Compile five ordered stages and assemble the result after synthesis., The five graph stages, injectable for offline orchestration tests., RuntimeAdapters, test_forecast_keywords_reach_search_through_graph_without_leaking_into_result(), handler(), graph(), Offline streaming tests; fixtures do not represent real verification. (+1 more)

### Community 40 - "Runtime Adapters"
Cohesion: 0.23
Nodes (13): make_runtime_adapters(), extract(), page_operation(), search(), synthesize(), operation(), verify(), with_client() (+5 more)

### Community 41 - "App Layout Pages"
Cohesion: 0.15
Nodes (6): app_globals, metadata, metadata, metadata, nextConfig, next

### Community 42 - "Grounded Answer Tests"
Cohesion: 0.27
Nodes (13): AsyncClient, Generate and validate a grounded answer, leaving provider retries to runtime., synthesize_answer(), run(), run(), run(), run(), run() (+5 more)

### Community 43 - "Page Claim Extraction"
Cohesion: 0.22
Nodes (12): extract_image_claims(), extract_page_claims(), ExtractedClaim, Extraction, ImageObservation, _project_extracted_claims(), AsyncClient, BaseModel (+4 more)

### Community 44 - "Request Schema Models"
Cohesion: 0.21
Nodes (8): FactCheckRequest, ImageAttachment, BaseModel, model_validator, parametrize, test_request_rejects_invalid_input(), test_request_requires_all_contract_fields(), field_validator

### Community 45 - "Package Dependencies"
Cohesion: 0.15
Nodes (12): name, private, type, postcss, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+4 more)

### Community 46 - "Public Source Reader"
Cohesion: 0.26
Nodes (10): Address, fetchPublicText(), htmlToText(), publicAddress(), resolvePublicUrl(), Resolver, ref_node_dns, ref_node_http (+2 more)

### Community 47 - "Provider Configuration"
Cohesion: 0.24
Nodes (11): configured_providers(), providers_for_preference(), Return configured providers in the user-requested priority order., Return the automatic chain or exactly one explicitly selected model., _secret_value(), Provider priority and fallback policy tests; no network traffic., test_configured_provider_chain_is_ordered_and_skips_missing_keys(), test_explicit_provider_preference_pins_one_configured_model() (+3 more)

### Community 48 - "Free Search Tests"
Cohesion: 0.23
Nodes (9): test_configured_free_google_search_is_selected_before_llm_search(), handler(), mock_async_client(), test_free_quota_exhaustion_falls_back_with_an_explicit_notice(), mock_async_client(), test_llm_runtime_ignores_environment_proxy_for_provider_connection(), mock_async_client(), test_runtime_read_stage_uses_youtube_adapter_without_adding_comments_to_source_texts() (+1 more)

### Community 49 - "Extraction Graph Tests"
Cohesion: 0.20
Nodes (9): build_extraction_graph(), Stage, End after extraction; do not simulate search, sources, or judgments., Isolated settings and extraction graph tests; no paid API calls., test_extraction_graph_ends_without_fabricating_verdict(), test_serpapi_key_is_server_only_and_redacted(), test_settings_load_file_without_exposing_key(), test_youtube_api_key_is_loaded_from_server_environment_and_redacted() (+1 more)

### Community 50 - "Synthesis Provider Tests"
Cohesion: 0.22
Nodes (9): source(), test_eligible_sources_excludes_unverified_empty_and_youtube_and_bounds_text(), test_all_synthesis_providers_failing_preserves_verified_result(), failing_provider(), mock_client(), read(), search(), read() (+1 more)

### Community 51 - "Floating Lines Visual"
Cohesion: 0.22
Nodes (9): DEFAULT_BOTTOM_WAVE_POSITION, DEFAULT_ENABLED_WAVES, DEFAULT_LINE_COUNT, DEFAULT_LINE_DISTANCE, FloatingLines(), FloatingLinesProps, hexToVec3(), WavePosition (+1 more)

### Community 52 - "Lines Background Boundary"
Cohesion: 0.20
Nodes (6): BackgroundBoundary, FloatingLines, floatingLinesCount, floatingLinesDistance, floatingLinesGradient, floatingLinesWaves

### Community 53 - "Scramble Text Effect"
Cohesion: 0.36
Nodes (9): getRevealOrder(), randomCharacter(), randomizeText(), ScrambleRun, ScrambleText(), resetVisual(), startRun(), writeVisual() (+1 more)

### Community 54 - "Result Assembly Details"
Cohesion: 0.27
Nodes (9): build_fact_check_result(), _normalize_source(), Project internal source state onto the public TypeScript contract., Validate and assemble the only result shape exposed by the API., _result_warnings(), Runtime assembly tests; explicit adapters keep the five-node graph offline., test_final_result_warns_when_free_google_search_was_unavailable(), test_result_exposes_youtube_comments_only_as_context_not_verified_content() (+1 more)

### Community 55 - "Router Mode Guides"
Cohesion: 0.22
Nodes (9): Data Loading with Loaders and Actions, Data Router Shape, Forms Fetchers and Pending UI, Middleware Sessions and Auth, Framework Rendering Strategy, Framework Route Modules, Framework Type Safety with Generated Route Types, Data Mode Detection Signals (+1 more)

### Community 56 - "Welcome Home Routes"
Cohesion: 0.25
Nodes (5): app_welcome_logo_dark, app_welcome_logo_light, resources, Welcome(), ref_types_home

### Community 57 - "Synthesis Citation Rules"
Cohesion: 0.22
Nodes (8): _limit_sections_to_source_breadth(), BaseModel, model_validator, Keep answer breadth proportional to the cited source base. A single supporting…, Require every citation to resolve to an exact substring of supplied text., Provider-owned answer fields; server-owned model metadata is excluded., SynthesisDraft, _validate_answer_grounding()

### Community 58 - "Type Definition Packages"
Cohesion: 0.22
Nodes (9): devDependencies, postcss, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom, @types/three (+1 more)

### Community 59 - "Router App Bootstrap"
Cohesion: 0.25
Nodes (3): app_app, ref_react_router, ref_types_root

### Community 60 - "Forecast Synthesis Tests"
Cohesion: 0.29
Nodes (4): test_forecast_synthesis_preserves_prediction_and_citations(), mock_client(), provider_response(), search()

### Community 61 - "Light Logo Assets"
Cohesion: 0.29
Nodes (8): Dark circular dots, logo-light.svg, Logo icon mark, Light theme variant, Red accent path, SVG root 1080x174, Welcome page branding, Wordmark letter paths

### Community 62 - "Next Brand Assets"
Cohesion: 0.32
Nodes (8): Default template branding, next.svg, .js suffix glyphs, EXT letter paths, Monochrome variant, N letter path, SVG root 394x80, Next.js wordmark

### Community 63 - "Client Stream Tests"
Cohesion: 0.29
Nodes (3): insufficientAnswer, result, verifiedSource

### Community 64 - "YouTube Context Helpers"
Cohesion: 0.52
Nodes (5): YoutubeVideoMetadata(), formatYoutubePublishedAt(), formatYoutubeViewCount(), stripYoutubeApiDataForExport(), youtubeThumbnailUrl()

### Community 65 - "Sidebar Line Controls"
Cohesion: 0.29
Nodes (5): Falloff, FALLOFF_CURVES, LineSidebarItem, LineSidebarProps, LineSidebarStyle

### Community 66 - "Globe Icon Assets"
Cohesion: 0.33
Nodes (7): Clip path definition, Default template icon, globe.svg, Globe wireframe path, Monochrome gray variant, SVG root 16x16, Globe wireframe motif

### Community 67 - "Probe Test Scripts"
Cohesion: 0.29
Nodes (3): errors, observations, responses

### Community 68 - "Router Build Config"
Cohesion: 0.33
Nodes (3): ref_react_router_dev, ref_tailwindcss_vite, ref_vite

### Community 69 - "Insufficient Answer Path"
Cohesion: 0.40
Nodes (6): insufficient_answer(), Return a fixed answer that makes no unsupported assertions., synthesizing(), test_insufficient_answer_is_fixed_and_skips_provider_call(), reject_request(), run()

### Community 70 - "Runtime Dependencies"
Cohesion: 0.33
Nodes (6): dependencies, motion, next, react, react-dom, three

### Community 71 - "Package Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, start, typecheck

### Community 72 - "File Icon Assets"
Cohesion: 0.40
Nodes (5): Document File Icon, Document Page Outline, Folded Corner, Gray Fill Style, Text Content Lines

### Community 73 - "Cancellation Probe Scripts"
Cohesion: 0.50
Nodes (4): observations, responses, state(), waitCounts()

### Community 74 - "Intent API Route"
Cohesion: 0.83
Nodes (3): backend(), error(), POST()

### Community 75 - "Dark Logo Assets"
Cohesion: 0.50
Nodes (4): Dark Background Variant Purpose for Welcome Page, Geometric Icon Mark with Red Accent and White Nodes, Dark Mode Logo SVG, React Router Wordmark in White

### Community 76 - "ESLint Configuration"
Cohesion: 0.50
Nodes (3): eslintConfig, ref_eslint, ref_eslint_config_next

### Community 77 - "Next Generated Types"
Cohesion: 0.50
Nodes (3): next_dev_types_root_params_d, next_dev_types_routes_d, NOTE: This file should not be edited

### Community 78 - "Window Icon Assets"
Cohesion: 0.50
Nodes (4): Minimal Window Chrome Icon Purpose for UI, Three Circular Window Control Dots in Title Bar, Window Frame Outline with Rounded Bottom Corners, Browser Window Icon SVG in Gray

### Community 79 - "Workspace Design Docs"
Cohesion: 0.67
Nodes (3): Next.js breaking changes guide and verification cleanup, Premium research workspace dark glass design, Dashboard demo-state fixture shader implementation and checks

### Community 80 - "Declarative Mode Docs"
Cohesion: 0.67
Nodes (3): Declarative Router Shape, Declarative Mode Boundary, Declarative Mode Detection Signals

### Community 81 - "RSC Boundary Docs"
Cohesion: 0.67
Nodes (3): RSC Client Server Boundaries, RSC Route Module Differences, RSC Detection Signals

### Community 82 - "Exception Status Helper"
Cohesion: 0.67
Nodes (3): _http_status_from_exception(), Return only an upstream HTTP status from an exception chain., BaseException

### Community 83 - "Agent Architecture Docs"
Cohesion: 0.67
Nodes (3): True or Not agent architecture, Gemini Interactions API docs citation, GPT-6 Luna model docs citation

### Community 84 - "Vercel Brand Assets"
Cohesion: 0.67
Nodes (3): Vercel Brand Mark Purpose for Deployment Branding, White Filled Triangle Mark viewBox 1155x1000, Vercel Triangle Logo SVG in White

## Knowledge Gaps
- **212 isolated node(s):** `CountUpProps`, `Address`, `Resolver`, `Action`, `State` (+207 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 541 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMProvider` connect `Search Image Payloads` to `Search Query Builder`, `Attachment Test Suite`, `Answer Contracts`, `Fallback Error Chain`, `Insufficient Answer Path`, `Answer Synthesis Stage`, `Page Claim Extraction`, `Grounded Answer Tests`, `Claim Extraction Flow`, `Search Query Pipeline`, `Provider Configuration`, `Provider Transports`, `Answer Synthesis Tests`, `Candidate URL Discovery`, `Intent Gate API`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `make_runtime_adapters()` connect `Runtime Adapters` to `Answer Contracts`, `Public Source Fetching`, `YouTube Offline Tests`, `Answer Synthesis Stage`, `Search Query Pipeline`, `Claim Extraction Flow`, `Candidate URL Discovery`, `API Status Tests`, `Search Query Builder`, `Attachment Test Suite`, `Fallback Error Chain`, `Runtime Workflow Graph`, `Grounded Answer Tests`, `Page Claim Extraction`, `Provider Configuration`, `Free Search Tests`, `Extraction Graph Tests`, `Synthesis Provider Tests`, `Result Assembly Details`, `Forecast Synthesis Tests`, `Insufficient Answer Path`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `build_workflow()` connect `Execution Boundary Tests` to `Attachment Test Suite`, `Public Source Fetching`, `Cancellation Probe Harness`, `Runtime Workflow Graph`, `Answer Synthesis Stage`, `Recovery Probe Scripts`, `Result Assembly Details`, `Graph Stage Tests`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `LLMProvider` (e.g. with `synthesize_answer()` and `extract_claims()`) actually correct?**
  _`LLMProvider` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `ProviderCallError` (e.g. with `extract_claims()` and `extract_image_claims()`) actually correct?**
  _`ProviderCallError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `make_runtime_adapters()` (e.g. with `extract()` and `read()`) actually correct?**
  _`make_runtime_adapters()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `search_sources()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`search_sources()` has 2 INFERRED edges - model-reasoned connections that need verification._