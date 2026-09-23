# Graph Report - TRUE-OR-NOT + grounded-answer-synthesis  (2026-09-23)

## Corpus Check
- Merged snapshot: the existing main-graph snapshot plus the grounded-answer-synthesis worktree. The worktree contributes its 87-file code graph and semantic extraction for HANDOFF.md and the worktree plan; unchanged documents and images are carried forward from the main snapshot, not re-extracted. Any pre-existing main-graph coverage gaps are unchanged. The main-root Graphify scan excludes .worktrees.

## Summary
- 2066 nodes · 3848 edges · 154 communities (112 shown, 42 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 301 edges (avg confidence: 0.88)
- Token cost: 0 Graphify API tokens; host-agent semantic extraction usage is not metered.

## Community Hubs (Navigation)
- YouTube HTTP Retrieval
- Offline Verification Tests
- Demo Fixture Content
- Runtime Workflow Graph
- Fact-Check Request Client
- Assistant Reply Composition
- Provider Configuration
- Client Claim Extraction
- Streaming Response Protocol
- Animated Count-Up UI
- Lattice Loading Component
- Fact-Check Stream Parser
- Client Cancellation Tests
- Async Cancellation Tests
- Claim Verification Client
- Public Source Fetching
- Floating Lines Defaults
- Background Error Boundary
- Sidebar Line Controls
- Fact-Check API Route
- API Contract Models
- Claim Extraction
- Health Status Endpoints
- Extraction Workflow
- YouTube API Tests
- Cancellation Probe Scripts
- Backend Workflow Factory
- App Layout and Entry
- Public URL Classification
- Fact-Check Result Assembly
- React Router Brand Assets
- Workflow Execution Tests
- React Router App Bootstrap
- Fact-Check API Operations
- TypeScript Compiler Settings
- Package Scripts and Metadata
- Build Tool Dependencies
- Vite Toolchain Configuration
- Next.js Package Dependencies
- Project Command Scripts
- ESLint Configuration
- Next.js Generated Types
- PostCSS Configuration
- Backend Package Metadata
- Document File Icon
- Globe Icon Asset
- Next.js Wordmark
- Vercel Brand Mark
- Window Icon Asset
- FactLens Requirements
- Evidence Synthesis Design
- Verification System Docs
- Fact-Check Architecture
- FactLens Workspace Controls
- FactLens Empty-State Workspace
- FactLens Workspace Variant A
- FactLens Workspace Variant B
- FactLens Workspace Variant C
- FactLens Workspace Variant D
- GlassSurface Developer Panel
- Next.js Migration References
- Animation Dependency Cleanup
- Router Navigation Concepts
- React Bits Documentation
- Visual Effects Components
- Evidence Results Panel
- React Router Logo Assets
- Evidence Comparison Principles
- AI Provider Model Catalog
- Provider Fallback Chain
- Backend Startup Progress
- Backend Startup Failure
- Verification Check Progress
- Verification Check Failure
- Workspace Setup Status
- Next.js Agent Instructions
- Router Data-Mode Guides
- React Router Emblem
- Forecast Claim Verdict
- Server Component Boundaries
- Browser Verification Cleanup
- Empty Evidence State
- Example Claim Loader
- Evidence-First Product Principle
- GlassSurface UI Component
- Repository Guidance Files
- Forecast Claim Policy
- Verdict Classification Taxonomy
- Static Shader Fallback
- Mobile Viewport Accessibility
- Forecast Uncertainty Policy
- Inline Citation Rendering
- Evidence Insufficient Fallback
- Forecast Verdict Handling
- Insufficient Evidence Response
- Evidence-First Fact Checking
- GlassSurface Appearance Settings
- React Server Components
- GlassSurface Background Opacity
- GlassSurface Corner Radius
- GlassSurface Displacement
- GlassSurface Distortion
- GlassSurface Saturation
- Browser Regression Tests
- External Search Consent
- Grounded Synthesis Community 0
- Grounded Synthesis Community 1
- Grounded Synthesis Community 12
- Grounded Synthesis Community 13
- Grounded Synthesis Community 15
- Grounded Synthesis Community 18
- Grounded Synthesis Community 19
- Grounded Synthesis Community 2
- Grounded Synthesis Community 21
- Grounded Synthesis Community 22
- Grounded Synthesis Community 23
- Grounded Synthesis Community 26
- Grounded Synthesis Community 27
- Grounded Synthesis Community 29
- Grounded Synthesis Community 30
- Grounded Synthesis Community 31
- Grounded Synthesis Community 38
- Grounded Synthesis Community 4
- Grounded Synthesis Community 40
- Grounded Synthesis Community 5
- Grounded Synthesis Community 7
- Grounded Synthesis Community 8
- Grounded Synthesis Community 11
- Grounded Synthesis Community 14
- Grounded Synthesis Community 17
- Grounded Synthesis Community 20
- Grounded Synthesis Community 24
- Grounded Synthesis Community 28
- Grounded Synthesis Community 3
- Grounded Synthesis Community 32
- Grounded Synthesis Community 33
- Grounded Synthesis Community 34
- Grounded Synthesis Community 35
- Grounded Synthesis Community 6
- Grounded Synthesis Community 9
- Grounded Synthesis Community 16
- Grounded Synthesis Community 25
- Grounded Synthesis Community 36
- Grounded Synthesis Community 41
- Grounded Synthesis Community 42
- Grounded Synthesis Community 43
- Grounded Synthesis Community 44
- Grounded Synthesis Community 45
- Grounded Synthesis Community 46
- Grounded Synthesis Community 48
- Grounded Synthesis Community 10
- Grounded Synthesis Community 47

## God Nodes (most connected - your core abstractions)
1. `search_sources()` - 42 edges
2. `search_sources()` - 42 edges
3. `LLMProvider` - 41 edges
4. `ProviderCallError` - 33 edges
5. `make_runtime_adapters()` - 30 edges
6. `LLMProvider` - 29 edges
7. `extract_claims()` - 28 edges
8. `extract_claims()` - 28 edges
9. `ground_judgments()` - 27 edges
10. `verify_claims()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `verify()` --uses--> `FactCheckResult`  [INFERRED]
  backend/tests/recovery_probe_app.py → backend/contracts.py
- `verify()` --uses--> `FactCheckResult`  [INFERRED]
  grounded-answer-synthesis/backend/tests/recovery_probe_app.py → grounded-answer-synthesis/backend/contracts.py
- `Implemented fifth-stage grounded answer synthesis` --semantically_similar_to--> `Fifth LangGraph synthesis stage`  [INFERRED] [semantically similar]
  grounded-answer-synthesis/HANDOFF.md → grounded-answer-synthesis/docs/superpowers/plans/2026-09-23-grounded-answer-synthesis.md
- `test_openai_structured_schema_requires_defaulted_properties_too()` --uses--> `JudgmentResponse`  [INFERRED]
  backend/tests/test_providers.py → backend/verification.py
- `extract_claims()` --uses--> `FactCheckRequest`  [INFERRED]
  backend/extraction.py → backend/schemas.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Visible elements that form the logo composition** — app_welcome_logo_light_react_wordmark, app_welcome_logo_light_router_wordmark, app_welcome_logo_light_abstract_emblem [EXTRACTED 1.00]
- **GlassSurface settings shown in UI Component Lab** — c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_ui_component_lab, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_react_bits_glasssurface, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_distortion_scale_setting, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_displace_setting, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_saturation_setting, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_background_opacity_setting, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_corner_radius_setting [EXTRACTED 1.00]
- **Traceable claim evidence model** — docs_factlens_________v2_claim_level_verification, docs_factlens_________v2_verified_source_evidence, docs_factlens_________v2_source_independence, docs_factlens_________v2_seven_verdict_taxonomy [EXTRACTED 1.00]
- **Grounded synthesis answer flow** — docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_synthesis_stage, docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_verified_source_text, docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_exact_quote_grounding, docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_inline_citation_renderer [EXTRACTED 1.00]
- **Four-stage verification workflow** — handoff_claim_extraction, handoff_search_candidate_processing, handoff_source_body_extraction, handoff_claim_verification [EXTRACTED 1.00]
- **Inputs and consent for a web-assisted fact check** — output_playwright_ui_up_180_source_input, output_playwright_ui_up_180_verification_request, output_playwright_ui_up_180_model_search_disclosure, output_playwright_ui_up_180_external_search_consent [EXTRACTED 1.00]
- **Source-to-Evidence Fact-Checking Workflow** — output_playwright_ui_up_0_source_text_input, output_playwright_ui_up_0_verification_request_field, output_playwright_ui_up_0_external_processing_consent, output_playwright_ui_up_0_start_fact_check_button, output_playwright_ui_up_0_evidence_panel_empty_state [INFERRED 0.85]
- **Grounded synthesis vertical feature** — grounded-answer-synthesis::docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_grounded_answer_synthesis, grounded-answer-synthesis::docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_structured_answer_contract, grounded-answer-synthesis::docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_ndjson_synthesis_progress, grounded-answer-synthesis::docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_structured_inline_citation_renderer [EXTRACTED 1.00]

## Communities (154 total, 42 thin omitted)

### Community 0 - "YouTube HTTP Retrieval"
Cohesion: 0.05
Nodes (34): PublicResolver, SourceReadResult, _TextParser, _TitleParser, read(), youtube_reader(), candidate_url(), _select_diverse_sources() (+26 more)

### Community 1 - "Offline Verification Tests"
Cohesion: 0.09
Nodes (50): Judgment, JudgmentEvidence, JudgmentResponse, _ValidatedEvidence, html_text(), claim(), test_context_mismatch_is_reported_as_missing_context(), test_date_or_context_mismatch_cannot_support_a_claim() (+42 more)

### Community 10 - "Demo Fixture Content"
Cohesion: 0.11
Nodes (17): Action, Claim, Preview, State, ChatMessage, IconName, PanelProps, createPreview() (+9 more)

### Community 15 - "Runtime Workflow Graph"
Cohesion: 0.15
Nodes (15): RuntimeAdapters, build_runtime_workflow(), test_forecast_keywords_reach_search_through_graph_without_leaking_into_result(), handler(), run(), extract(), read(), search() (+7 more)

### Community 16 - "Fact-Check Request Client"
Cohesion: 0.15
Nodes (17): Settings, FactCheckRequest, fact_check(), fact_check_stream(), test_health_and_status_do_not_claim_provider_readiness(), test_request_preserves_original_text(), test_request_rejects_invalid_input(), test_request_requires_all_contract_fields() (+9 more)

### Community 17 - "Assistant Reply Composition"
Cohesion: 0.12
Nodes (17): AssistantReply, ReplyResult, AgentEvent, AgentStage, AgentStatus, FactCheckResult, FactClaim, FactEvidence (+9 more)

### Community 2 - "Provider Configuration"
Cohesion: 0.09
Nodes (49): LLMProvider, ProviderCallError, configured_providers(), _endpoint_and_headers(), _gemini_schema(), clean(), _gemini_text(), openai_provider() (+41 more)

### Community 21 - "Client Claim Extraction"
Cohesion: 0.18
Nodes (15): JsonObject, Judgment, Schema, canonical(), extractClaims(), format(), outputJson(), providerSources() (+7 more)

### Community 23 - "Streaming Response Protocol"
Cohesion: 0.15
Nodes (13): FactCheckResponse, encode(), stream_events(), test_stream_errors_are_safe(), run(), test_task_cancellation_reaches_graph_cleanup(), run(), consume() (+5 more)

### Community 24 - "Animated Count-Up UI"
Cohesion: 0.21
Nodes (13): CountUpProps, ScrambleRun, ScrambleTextProps, CountUp(), getRevealOrder(), randomCharacter(), randomizeText(), ScrambleText() (+5 more)

### Community 25 - "Lattice Loading Component"
Cohesion: 0.16
Nodes (14): GridSize, LatticeLoaderProps, LoaderStatus, LoaderStyle, Pattern, PatternInput, PatternName, formatElapsed() (+6 more)

### Community 26 - "Fact-Check Stream Parser"
Cohesion: 0.21
Nodes (11): FactCheckError, readFactCheckStream(), line(), safeSourceUrl(), FactCheckDashboard(), addMessage(), loadSample(), reset() (+3 more)

### Community 27 - "Client Cancellation Tests"
Cohesion: 0.20
Nodes (6): FactSource, download(), stripYoutubeApiDataForExport(), result, ref_node_assert, ref_node_test

### Community 28 - "Async Cancellation Tests"
Cohesion: 0.14
Nodes (10): InstrumentedGraph, blocking_extract(), cancellation_state(), record(), get, Explicit integration-test entry point ONLY; never imported by main/runtime. No…, Read-node integration preserves source text for later citation verification., asyncio (+2 more)

### Community 32 - "Claim Verification Client"
Cohesion: 0.35
Nodes (9): Options, validResult(), TrustIndex(), normalizeFactScore(), scoreBand(), scoreLabel(), groundJudgments(), FACT_SCORE_BANDS (+1 more)

### Community 33 - "Public Source Fetching"
Cohesion: 0.26
Nodes (10): Address, Resolver, fetchPublicText(), htmlToText(), publicAddress(), resolvePublicUrl(), ref_node_dns, ref_node_http (+2 more)

### Community 34 - "Floating Lines Defaults"
Cohesion: 0.22
Nodes (9): FloatingLinesProps, WavePosition, FloatingLines(), hexToVec3(), DEFAULT_BOTTOM_WAVE_POSITION, DEFAULT_ENABLED_WAVES, DEFAULT_LINE_COUNT, DEFAULT_LINE_DISTANCE (+1 more)

### Community 35 - "Background Error Boundary"
Cohesion: 0.20
Nodes (7): BackgroundBoundary, FloatingLinesBackground(), FloatingLines, floatingLinesCount, floatingLinesDistance, floatingLinesGradient, floatingLinesWaves

### Community 48 - "Sidebar Line Controls"
Cohesion: 0.29
Nodes (6): Falloff, LineSidebarItem, LineSidebarProps, LineSidebarStyle, LineSidebar(), FALLOFF_CURVES

### Community 5 - "Fact-Check API Route"
Cohesion: 0.07
Nodes (24): FactCheckRequest, backend(), error(), GET(), POST(), limitedText(), validateRequest(), state() (+16 more)

### Community 6 - "API Contract Models"
Cohesion: 0.10
Nodes (29): AgentStatus, _ContractModel, FactCheckResult, FactClaim, FactEvidence, FactSource, default_fact_score(), normalize_fact_score() (+21 more)

### Community 8 - "Claim Extraction"
Cohesion: 0.09
Nodes (23): ExtractedClaim, Extraction, FactCheckState, invalid_request(), verify(), BaseModel, exception_handler, TypedDict (+15 more)

### Community 9 - "Health Status Endpoints"
Cohesion: 0.08
Nodes (20): HealthStatus, Response, Session, agent_status(), health(), run(), test_read_node_attempts_sources_sequentially_even_after_failure(), reader() (+12 more)

### Community 11 - "Extraction Workflow"
Cohesion: 0.13
Nodes (20): extract_claims(), test_extractor_drops_invented_claim_without_fabricating_source_text(), run(), test_extractor_keeps_forecast_and_returns_search_keywords_separately(), handler(), run(), test_extractor_keeps_valid_claims_when_one_model_quote_is_not_in_source(), run() (+12 more)

### Community 12 - "YouTube API Tests"
Cohesion: 0.15
Nodes (19): test_comments_unavailable_keeps_video_title_without_exposing_provider_error(), run(), test_fetches_official_video_title_and_bounded_plain_text_comments(), handler(), run(), test_missing_key_or_invalid_video_url_makes_no_api_request(), run(), test_oversized_api_payload_is_treated_as_unavailable() (+11 more)

### Community 14 - "Cancellation Probe Scripts"
Cohesion: 0.16
Nodes (19): free_port(), ready(), run(), free_port(), port_closed(), ready(), run(), stop_owned() (+11 more)

### Community 22 - "Backend Workflow Factory"
Cohesion: 0.15
Nodes (15): get_workflow(), build_extraction_graph(), load_settings(), test_extraction_graph_ends_without_fabricating_verdict(), test_runtime_read_stage_uses_youtube_adapter_without_adding_comments_to_source_texts(), handler(), mock_async_client(), test_settings_load_file_without_exposing_key() (+7 more)

### Community 29 - "App Layout and Entry"
Cohesion: 0.15
Nodes (6): metadata, metadata, metadata, nextConfig, next, app_globals

### Community 3 - "Public URL Classification"
Cohesion: 0.07
Nodes (39): build_search_query(), _normalized_host(), origin_group_for_url(), search_sources(), source_type_for_url(), test_candidates_filter_unsafe_urls_and_limit_results(), run(), test_completed_empty_search_is_not_a_verdict() (+31 more)

### Community 36 - "Fact-Check Result Assembly"
Cohesion: 0.24
Nodes (9): build_fact_check_result(), verifying(), _normalize_source(), _result_warnings(), test_result_exposes_youtube_comments_only_as_context_not_verified_content(), test_result_reports_provider_used_by_the_final_stage(), Project internal source state onto the public TypeScript contract., Validate and assemble the only result shape exposed by the API. (+1 more)

### Community 38 - "React Router Brand Assets"
Cohesion: 0.25
Nodes (5): Welcome(), resources, app_welcome_logo_dark, app_welcome_logo_light, ref_types_home

### Community 4 - "Workflow Execution Tests"
Cohesion: 0.06
Nodes (31): test_graph_failure_returns_safe_error(), stage(), test_invalid_http_input_is_safe_and_never_runs_graph(), test_post_rejects_malformed_result_contract(), test_post_runs_graph_and_returns_only_result(), module(), test_html_excludes_noncontent(), test_html_excludes_video_and_custom_player_elements() (+23 more)

### Community 45 - "React Router App Bootstrap"
Cohesion: 0.25
Nodes (3): app_app, ref_react_router, ref_types_root

### Community 58 - "Fact-Check API Operations"
Cohesion: 0.50
Nodes (4): recover(), status(), get, post

### Community 20 - "TypeScript Compiler Settings"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 31 - "Package Scripts and Metadata"
Cohesion: 0.15
Nodes (12): name, private, type, postcss, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+4 more)

### Community 39 - "Build Tool Dependencies"
Cohesion: 0.22
Nodes (9): devDependencies, postcss, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom, @types/three (+1 more)

### Community 51 - "Vite Toolchain Configuration"
Cohesion: 0.33
Nodes (3): ref_react_router_dev, ref_tailwindcss_vite, ref_vite

### Community 52 - "Next.js Package Dependencies"
Cohesion: 0.33
Nodes (6): dependencies, motion, next, react, react-dom, three

### Community 56 - "Project Command Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, start, typecheck

### Community 61 - "ESLint Configuration"
Cohesion: 0.50
Nodes (3): eslintConfig, ref_eslint, ref_eslint_config_next

### Community 63 - "Next.js Generated Types"
Cohesion: 0.50
Nodes (3): NOTE: This file should not be edited, next_dev_types_root_params_d, next_dev_types_routes_d

### Community 13 - "FactLens Requirements"
Cohesion: 0.09
Nodes (23): Claim Extraction and Selection, True or Not, URL Fetch Security, User Privacy Notice, Verified Source Evidence, Dark Glass UI, Claim Evidence Selection Sync, Direct Input Without Verdict (+15 more)

### Community 18 - "Evidence Synthesis Design"
Cohesion: 0.11
Nodes (19): Answer Provider Metadata, Exact Quote Grounding, Five-stage Workflow, Synthesis Stage, Verified Source Text, Answer Block, Answer Citation, Answer Section (+11 more)

### Community 19 - "Verification System Docs"
Cohesion: 0.11
Nodes (19): Claim Extraction, Claim Verification, FactLens Verification System, FastAPI Backend, Google Search Rank Limitation, Grounded Citation, LangGraph Workflow, Public YouTube Comments (+11 more)

### Community 30 - "Fact-Check Architecture"
Cohesion: 0.15
Nodes (13): Claim Extraction Stage, Claim Verification Stage, Exact Citation Grounding, Fact Check Workflow, Source Reading Stage, Structured Fact Check Contract, Web Search Stage, Agent Architecture Design (+5 more)

### Community 37 - "FactLens Workspace Controls"
Cohesion: 0.20
Nodes (10): Evidence comparison section (section 02, awaiting a document), Checkbox consent to send the source and verification request to the server/OpenAI for web search, Fact-check request form (section 01), FactLens fact-checking workspace, GlassSurface appearance controls: distortion −10, displacement 0.5, saturation 1.60, background opacity 30%, blur radius 18, Processing disclosure: gpt-5.6-luna reasoning max and web search, which may take time, Example document: virtual city's cultural event, Source entry by pasted text or URL (+2 more)

### Community 40 - "FactLens Empty-State Workspace"
Cohesion: 0.25
Nodes (8): Document Input Stage, Evidence Comparison Workspace, FactLens, Text Input Mode, URL Input Mode, Virtual City Cultural Event Example, FactLens Workspace Snapshot, Evidence-first Principle

### Community 41 - "FactLens Workspace Variant A"
Cohesion: 0.25
Nodes (8): Document Input Stage, Evidence Comparison Workspace, FactLens, Text Input Mode, URL Input Mode, Virtual City Cultural Event Example, FactLens Workspace Snapshot, Evidence-first Principle

### Community 42 - "FactLens Workspace Variant B"
Cohesion: 0.25
Nodes (8): Document Input Stage, Evidence Comparison Workspace, FactLens, Text Input Mode, URL Input Mode, Virtual City Cultural Event Example, FactLens Workspace Snapshot, Evidence-first Principle

### Community 43 - "FactLens Workspace Variant C"
Cohesion: 0.25
Nodes (8): Document Input Stage, Evidence Comparison Workspace, FactLens, Text Input Mode, URL Input Mode, Virtual City Cultural Event Example, FactLens Workspace Snapshot, Evidence-first Principle

### Community 44 - "FactLens Workspace Variant D"
Cohesion: 0.25
Nodes (8): Document Input Stage, Evidence Comparison Workspace, FactLens, Text Input Mode, URL Input Mode, Virtual City Cultural Event Example, FactLens Workspace Snapshot, Evidence-first Principle

### Community 46 - "GlassSurface Developer Panel"
Cohesion: 0.29
Nodes (8): Claim request field (확인 요청), Claim verification workspace (근거 워크스페이스), Model and web-search notice (gpt-5.6-luna · reasoning max · 웹 검색 사용), Original text field (확인할 원문), Start fact-checking button (팩트 검증 시작), Text input mode (텍스트 입력), URL input mode (URL 입력), Consent option for sending the original text and claim request to the server/OpenAI for web search

### Community 47 - "Next.js Migration References"
Cohesion: 0.25
Nodes (8): Next.js App Router, Next.js Project Scripts, Production Build Output, React Router Rollback References, Tailwind CSS, TypeScript, Visual Effects Dependencies, Project README

### Community 49 - "Animation Dependency Cleanup"
Cohesion: 0.29
Nodes (7): animejs, Dependency Cleanup, particles-gl, ParticlesLogo, tweakpane, UI Dependency Audit, Unused Direct Dependency Rationale

### Community 50 - "Router Navigation Concepts"
Cohesion: 0.33
Nodes (6): Action Functions, Fetchers, Loader Functions, Route Objects, Search Params, Nested Routes

### Community 53 - "React Bits Documentation"
Cohesion: 0.40
Nodes (5): Backgrounds Category, Floating Lines Component, React Bits Documentation, React Bits Pro, React Bits Page Snapshot

### Community 54 - "Visual Effects Components"
Cohesion: 0.40
Nodes (5): FactCheckDashboard, FloatingLinesBackground, Liquid Glass Panels, Motion, Three.js

### Community 55 - "Evidence Results Panel"
Cohesion: 0.40
Nodes (5): Evidence Results Panel (Empty State), Source Text Input Panel, Start Fact Check Button, URL Input Tab, Verification Request Field

### Community 57 - "React Router Logo Assets"
Cohesion: 0.50
Nodes (4): REACT wordmark, Router wordmark, Red-and-black abstract emblem, REACT Router logo

### Community 59 - "Evidence Comparison Principles"
Cohesion: 0.50
Nodes (4): Evidence Comparison Workspace, Original Source Grouping, Demo Disclosure Policy, Source Independence

### Community 60 - "AI Provider Model Catalog"
Cohesion: 0.50
Nodes (4): Gemini 3.7 Flash, Gemini 3.8 Flash, GPT-6 Luna, Provider Fallback Chain

### Community 62 - "Provider Fallback Chain"
Cohesion: 0.50
Nodes (4): Gemini 3.7 Flash, Gemini 3.8 Flash, GPT-6 Luna, Provider Fallback Chain

### Community 64 - "Backend Startup Progress"
Cohesion: 0.67
Nodes (3): Server setup check in progress, Verification Start Control, External Transmission Consent

### Community 65 - "Backend Startup Failure"
Cohesion: 0.67
Nodes (3): Server setup check failed, Verification Start Control, External Transmission Consent

### Community 66 - "Verification Check Progress"
Cohesion: 0.67
Nodes (3): Server setup check in progress, Verification Start Control, External Transmission Consent

### Community 67 - "Verification Check Failure"
Cohesion: 0.67
Nodes (3): Server setup check failed, Verification Start Control, External Transmission Consent

### Community 68 - "Workspace Setup Status"
Cohesion: 0.67
Nodes (3): Server setup check in progress, Verification Start Control, External Transmission Consent

### Community 69 - "Next.js Agent Instructions"
Cohesion: 0.67
Nodes (3): Installed Next.js Documentation, Next.js Agent Guidance, Project Agent Rules

### Community 7 - "Router Data-Mode Guides"
Cohesion: 0.07
Nodes (35): Data Router, RouterProvider, BrowserRouter, Outlet, Route Parameters, Routes and Route Components, App Routes Configuration, Framework Loaders and Actions (+27 more)

### Community 70 - "React Router Emblem"
Cohesion: 0.67
Nodes (3): Red branching emblem with three white circular marks, REACT Router wordmark, React Router logo

### Community 71 - "Forecast Claim Verdict"
Cohesion: 0.67
Nodes (3): Forecast Claim, Not Checkable Verdict, Forecast-answer synthesis pending

### Community 105 - "Grounded Synthesis Community 0"
Cohesion: 0.06
Nodes (73): LLMProvider, ProviderCallError, eligible_sources(), insufficient_answer(), synthesize_answer(), _endpoint_and_headers(), _gemini_schema(), clean() (+65 more)

### Community 106 - "Grounded Synthesis Community 1"
Cohesion: 0.05
Nodes (51): RuntimeAdapters, Settings, build_fact_check_result(), build_runtime_workflow(), _normalize_source(), _result_warnings(), main(), source() (+43 more)

### Community 117 - "Grounded Synthesis Community 12"
Cohesion: 0.11
Nodes (20): AssistantReply, ReplyResult, ResolvedAnswerCitation, AgentStage, AgentStatus, AnswerCitation, AnswerSection, FactCheckAnswer (+12 more)

### Community 118 - "Grounded Synthesis Community 13"
Cohesion: 0.11
Nodes (13): Response, Session, run(), test_read_node_attempts_sources_sequentially_even_after_failure(), reader(), test_read_node_records_failure_without_inventing_text(), test_read_node_uses_page_title_when_search_only_provided_a_host(), test_reads_html_and_tracks_final_url() (+5 more)

### Community 120 - "Grounded Synthesis Community 15"
Cohesion: 0.18
Nodes (15): JsonObject, Judgment, Schema, canonical(), extractClaims(), format(), outputJson(), providerSources() (+7 more)

### Community 123 - "Grounded Synthesis Community 18"
Cohesion: 0.18
Nodes (10): FactCheckRequest, backend(), GET(), POST(), limitedText(), validateRequest(), dynamic, headers (+2 more)

### Community 124 - "Grounded Synthesis Community 19"
Cohesion: 0.24
Nodes (13): Options, AgentEvent, AnswerBlock, createPreview(), validAnswer(), validResult(), TrustIndex(), normalizeFactScore() (+5 more)

### Community 107 - "Grounded Synthesis Community 2"
Cohesion: 0.06
Nodes (53): SynthesisDraft, AgentStatus, AnswerBlock, AnswerCitation, AnswerSection, _ContractModel, FactCheckAnswer, FactCheckResponse (+45 more)

### Community 126 - "Grounded Synthesis Community 21"
Cohesion: 0.16
Nodes (14): GridSize, LatticeLoaderProps, LoaderStatus, LoaderStyle, Pattern, PatternInput, PatternName, formatElapsed() (+6 more)

### Community 127 - "Grounded Synthesis Community 22"
Cohesion: 0.22
Nodes (11): FactCheckError, readFactCheckStream(), line(), FactCheckDashboard(), addMessage(), loadSample(), reset(), stop() (+3 more)

### Community 128 - "Grounded Synthesis Community 23"
Cohesion: 0.22
Nodes (10): HealthStatus, agent_status(), health(), invalid_request(), BaseModel, get, exception_handler, Local True or Not API backed by the assembled LangGraph workflow. (+2 more)

### Community 131 - "Grounded Synthesis Community 26"
Cohesion: 0.18
Nodes (8): Falloff, LineSidebarItem, LineSidebarProps, LineSidebarStyle, LineSidebar(), FALLOFF_CURVES, metadata, react

### Community 132 - "Grounded Synthesis Community 27"
Cohesion: 0.46
Nodes (6): Address, Resolver, fetchPublicText(), htmlToText(), publicAddress(), resolvePublicUrl()

### Community 134 - "Grounded Synthesis Community 29"
Cohesion: 0.22
Nodes (9): FloatingLinesProps, WavePosition, FloatingLines(), hexToVec3(), DEFAULT_BOTTOM_WAVE_POSITION, DEFAULT_ENABLED_WAVES, DEFAULT_LINE_COUNT, DEFAULT_LINE_DISTANCE (+1 more)

### Community 135 - "Grounded Synthesis Community 30"
Cohesion: 0.20
Nodes (7): BackgroundBoundary, FloatingLinesBackground(), FloatingLines, floatingLinesCount, floatingLinesDistance, floatingLinesGradient, floatingLinesWaves

### Community 136 - "Grounded Synthesis Community 31"
Cohesion: 0.36
Nodes (9): ScrambleRun, ScrambleTextProps, getRevealOrder(), randomCharacter(), randomizeText(), ScrambleText(), resetVisual(), startRun() (+1 more)

### Community 143 - "Grounded Synthesis Community 38"
Cohesion: 0.32
Nodes (6): FactCheckRequest, fact_check(), fact_check_stream(), post, BaseModel, field_validator

### Community 109 - "Grounded Synthesis Community 4"
Cohesion: 0.09
Nodes (50): Judgment, JudgmentEvidence, JudgmentResponse, _ValidatedEvidence, html_text(), claim(), test_context_mismatch_is_reported_as_missing_context(), test_date_or_context_mismatch_cannot_support_a_claim() (+42 more)

### Community 145 - "Grounded Synthesis Community 40"
Cohesion: 0.40
Nodes (5): ExtractedClaim, Extraction, openai_provider(), BaseModel, Server-only claim extraction. No search, judgment, or fallback output.

### Community 110 - "Grounded Synthesis Community 5"
Cohesion: 0.07
Nodes (20): PublicResolver, SourceReadResult, _TextParser, _TitleParser, candidate_url(), checked_url(), fetch_public_text(), _generic_title() (+12 more)

### Community 112 - "Grounded Synthesis Community 7"
Cohesion: 0.10
Nodes (17): InstrumentedGraph, blocking_extract(), cancellation_state(), record(), free_port(), ready(), run(), free_port() (+9 more)

### Community 113 - "Grounded Synthesis Community 8"
Cohesion: 0.09
Nodes (20): CountUpProps, Action, Claim, Preview, State, ChatMessage, IconName, PanelProps (+12 more)

### Community 116 - "Grounded Synthesis Community 11"
Cohesion: 0.13
Nodes (20): extract_claims(), test_extractor_drops_invented_claim_without_fabricating_source_text(), run(), test_extractor_keeps_forecast_and_returns_search_keywords_separately(), handler(), run(), test_extractor_keeps_valid_claims_when_one_model_quote_is_not_in_source(), run() (+12 more)

### Community 119 - "Grounded Synthesis Community 14"
Cohesion: 0.11
Nodes (12): error(), state(), waitCounts(), observations, responses, observations, responses, observations (+4 more)

### Community 122 - "Grounded Synthesis Community 17"
Cohesion: 0.15
Nodes (15): get_workflow(), build_extraction_graph(), load_settings(), test_extraction_graph_ends_without_fabricating_verdict(), test_runtime_read_stage_uses_youtube_adapter_without_adding_comments_to_source_texts(), handler(), mock_async_client(), test_settings_load_file_without_exposing_key() (+7 more)

### Community 125 - "Grounded Synthesis Community 20"
Cohesion: 0.13
Nodes (8): safeSourceUrl(), AnswerBlockView(), resolveAnswerCitationSource(), insufficientAnswer, result, verifiedSource, answer, source

### Community 129 - "Grounded Synthesis Community 24"
Cohesion: 0.18
Nodes (10): encode(), stream_events(), test_stream_errors_are_safe(), run(), test_task_cancellation_reaches_graph_cleanup(), run(), consume(), parametrize (+2 more)

### Community 133 - "Grounded Synthesis Community 28"
Cohesion: 0.22
Nodes (6): _http_status_from_exception(), BaseException, Server settings and the assembled four-stage verification workflow., Return only an upstream HTTP status from an exception chain., Request boundary compatible with the existing TypeScript request fields., Safe diagnostics for failed provider fallbacks.

### Community 108 - "Grounded Synthesis Community 3"
Cohesion: 0.06
Nodes (44): build_search_query(), _normalized_host(), origin_group_for_url(), search_sources(), _select_diverse_sources(), _source_identity(), source_type_for_url(), test_candidates_filter_unsafe_urls_and_limit_results() (+36 more)

### Community 137 - "Grounded Synthesis Community 32"
Cohesion: 0.47
Nodes (4): configured_providers(), _secret_value(), Provider-neutral requests and ordered LLM fallback policy. Credentials stay in…, Return configured providers in the user-requested priority order.

### Community 138 - "Grounded Synthesis Community 33"
Cohesion: 0.22
Nodes (6): recover(), status(), verify(), get, post, TEST ONLY deterministic recovery app. Never imported by runtime/main.

### Community 139 - "Grounded Synthesis Community 34"
Cohesion: 0.22
Nodes (4): metadata, metadata, nextConfig, next

### Community 111 - "Grounded Synthesis Community 6"
Cohesion: 0.06
Nodes (28): test_graph_failure_returns_safe_error(), stage(), test_invalid_http_input_is_safe_and_never_runs_graph(), test_post_rejects_malformed_result_contract(), test_post_runs_graph_and_returns_only_result(), module(), test_html_excludes_noncontent(), test_html_excludes_video_and_custom_player_elements() (+20 more)

### Community 114 - "Grounded Synthesis Community 9"
Cohesion: 0.14
Nodes (21): read(), youtube_reader(), test_comments_unavailable_keeps_video_title_without_exposing_provider_error(), run(), test_fetches_official_video_title_and_bounded_plain_text_comments(), handler(), run(), test_missing_key_or_invalid_video_url_makes_no_api_request() (+13 more)

### Community 121 - "Grounded Synthesis Community 16"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 130 - "Grounded Synthesis Community 25"
Cohesion: 0.15
Nodes (12): name, private, type, postcss, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+4 more)

### Community 141 - "Grounded Synthesis Community 36"
Cohesion: 0.22
Nodes (9): devDependencies, postcss, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom, @types/three (+1 more)

### Community 146 - "Grounded Synthesis Community 41"
Cohesion: 0.33
Nodes (6): dependencies, motion, next, react, react-dom, three

### Community 148 - "Grounded Synthesis Community 43"
Cohesion: 0.40
Nodes (5): scripts, build, dev, start, typecheck

### Community 115 - "Grounded Synthesis Community 10"
Cohesion: 0.08
Nodes (28): Grounded answer synthesis, Client validation of answer shape, bounds, and citation sources, Eligible source projection: verified, non-YouTube source text, Exact source-body citation grounding, Fifth LangGraph synthesis stage, insufficient_answer() fallback, Ordered synthesizing progress in NDJSON stream, Offline AGI forecast synthesis regression (+20 more)

## Knowledge Gaps
- **412 isolated node(s):** `Action`, `State`, `ChatMessage`, `IconName`, `PanelProps` (+407 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 887 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **42 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_workflow()` connect `Workflow Execution Tests` to `YouTube HTTP Retrieval`, `Claim Extraction`, `Async Cancellation Tests`, `Runtime Workflow Graph`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `next` connect `App Layout and Entry` to `Background Error Boundary`, `Fact-Check API Route`, `Package Scripts and Metadata`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `search_sources()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`search_sources()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `search_sources()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`search_sources()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `LLMProvider` (e.g. with `synthesize_answer()` and `extract_claims()`) actually correct?**
  _`LLMProvider` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ProviderCallError` (e.g. with `extract_claims()` and `search_sources()`) actually correct?**
  _`ProviderCallError` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Action`, `State`, `ChatMessage` to the rest of the system?**
  _412 weakly-connected nodes found - possible documentation gaps or missing edges._

## Merge provenance
- The main graph was retained as-is; this merge did not perform a full main-corpus re-extraction.
- Main-project node IDs and source paths were retained; worktree nodes use the `grounded-answer-synthesis/` source namespace.
- The worktree is a snapshot of branch `feat/grounded-answer-synthesis`, including its current uncommitted files.
- A normal `graphify extract .` from the main root skips `.worktrees`; refresh the worktree graph and merge it again after branch changes.
