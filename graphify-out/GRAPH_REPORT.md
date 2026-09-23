# Graph Report - TRUE-OR-NOT  (2026-09-23)

## Corpus Check
- 115 files · ~156,388 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 5, .css 4, .log 3)

## Summary
- 1138 nodes · 1875 edges · 105 communities (72 shown, 33 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 123 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- YouTube HTTP Retrieval
- Offline Verification Tests
- Provider Configuration
- Public URL Classification
- Workflow Execution Tests
- Fact-Check API Route
- API Contract Models
- Router Data-Mode Guides
- Claim Extraction
- Health Status Endpoints
- Demo Fixture Content
- Extraction Workflow
- YouTube API Tests
- FactLens Requirements
- Cancellation Probe Scripts
- Runtime Workflow Graph
- Fact-Check Request Client
- Assistant Reply Composition
- Evidence Synthesis Design
- Verification System Docs
- TypeScript Compiler Settings
- Client Claim Extraction
- Backend Workflow Factory
- Streaming Response Protocol
- Animated Count-Up UI
- Lattice Loading Component
- Fact-Check Stream Parser
- Client Cancellation Tests
- Async Cancellation Tests
- App Layout and Entry
- Fact-Check Architecture
- Package Scripts and Metadata
- Claim Verification Client
- Public Source Fetching
- Floating Lines Defaults
- Background Error Boundary
- Fact-Check Result Assembly
- FactLens Workspace Controls
- React Router Brand Assets
- Build Tool Dependencies
- FactLens Empty-State Workspace
- FactLens Workspace Variant A
- FactLens Workspace Variant B
- FactLens Workspace Variant C
- FactLens Workspace Variant D
- React Router App Bootstrap
- GlassSurface Developer Panel
- Next.js Migration References
- Sidebar Line Controls
- Animation Dependency Cleanup
- Router Navigation Concepts
- Vite Toolchain Configuration
- Next.js Package Dependencies
- React Bits Documentation
- Visual Effects Components
- Evidence Results Panel
- Project Command Scripts
- React Router Logo Assets
- Fact-Check API Operations
- Evidence Comparison Principles
- AI Provider Model Catalog
- ESLint Configuration
- Provider Fallback Chain
- Next.js Generated Types
- Backend Startup Progress
- Backend Startup Failure
- Verification Check Progress
- Verification Check Failure
- Workspace Setup Status
- Next.js Agent Instructions
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
- PostCSS Configuration
- React Server Components
- GlassSurface Background Opacity
- GlassSurface Corner Radius
- GlassSurface Displacement
- GlassSurface Distortion
- GlassSurface Saturation
- Browser Regression Tests
- External Search Consent
- Backend Package Metadata
- Document File Icon
- Globe Icon Asset
- Next.js Wordmark
- Vercel Brand Mark
- Window Icon Asset

## God Nodes (most connected - your core abstractions)
1. `search_sources()` - 42 edges
2. `LLMProvider` - 29 edges
3. `extract_claims()` - 28 edges
4. `ground_judgments()` - 27 edges
5. `verify_claims()` - 27 edges
6. `ProviderCallError` - 24 edges
7. `make_runtime_adapters()` - 22 edges
8. `Settings` - 21 edges
9. `claim()` - 19 edges
10. `build_workflow()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `verify()` --uses--> `FactCheckResult`  [INFERRED]
  backend/tests/recovery_probe_app.py → backend/contracts.py
- `FactCheckDashboard()` --indirect_call--> `transition()`  [INFERRED]
  app/components/fact-check-dashboard.tsx → app/components/demo-state.ts
- `build_fact_check_result()` --uses--> `FactCheckResult`  [INFERRED]
  backend/runtime.py → backend/contracts.py
- `fact_check()` --uses--> `FactCheckResponse`  [INFERRED]
  backend/main.py → backend/contracts.py
- `test_final_contract_accepts_frontend_shape_and_wrapper()` --uses--> `FactCheckResponse`  [INFERRED]
  backend/tests/test_contracts.py → backend/contracts.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Four-stage verification workflow** — handoff_claim_extraction, handoff_search_candidate_processing, handoff_source_body_extraction, handoff_claim_verification [EXTRACTED 1.00]
- **Traceable claim evidence model** — docs_factlens_________v2_claim_level_verification, docs_factlens_________v2_verified_source_evidence, docs_factlens_________v2_source_independence, docs_factlens_________v2_seven_verdict_taxonomy [EXTRACTED 1.00]
- **Grounded synthesis answer flow** — docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_synthesis_stage, docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_verified_source_text, docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_exact_quote_grounding, docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_inline_citation_renderer [EXTRACTED 1.00]
- **Visible elements that form the logo composition** — app_welcome_logo_light_react_wordmark, app_welcome_logo_light_router_wordmark, app_welcome_logo_light_abstract_emblem [EXTRACTED 1.00]
- **Source-to-Evidence Fact-Checking Workflow** — output_playwright_ui_up_0_source_text_input, output_playwright_ui_up_0_verification_request_field, output_playwright_ui_up_0_external_processing_consent, output_playwright_ui_up_0_start_fact_check_button, output_playwright_ui_up_0_evidence_panel_empty_state [INFERRED 0.85]
- **Inputs and consent for a web-assisted fact check** — output_playwright_ui_up_180_source_input, output_playwright_ui_up_180_verification_request, output_playwright_ui_up_180_model_search_disclosure, output_playwright_ui_up_180_external_search_consent [EXTRACTED 1.00]
- **GlassSurface settings shown in UI Component Lab** — c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_ui_component_lab, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_react_bits_glasssurface, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_distortion_scale_setting, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_displace_setting, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_saturation_setting, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_background_opacity_setting, c_users_playdata_desktop______true_or_not_output_playwright_ui_up_20_corner_radius_setting [EXTRACTED 1.00]

## Communities (105 total, 33 thin omitted)

### Community 0 - "YouTube HTTP Retrieval"
Cohesion: 0.05
Nodes (34): AbstractResolver, aiohttp, aiohttp_abc, read(), youtube_reader(), candidate_url(), Candidate discovery only; pending sources and snippets are not evidence. URL…, Preserve provider order with a strict site cap, not a Google rank claim. (+26 more)

### Community 1 - "Offline Verification Tests"
Cohesion: 0.09
Nodes (50): html_text(), claim(), Offline citation-grounding and judgment tests; no provider traffic., test_context_mismatch_is_reported_as_missing_context(), test_date_or_context_mismatch_cannot_support_a_claim(), test_ground_judgments_accepts_a_verified_contiguous_quote(), test_ground_judgments_accepts_a_verified_quote_for_an_unclear_checkable_claim(), test_ground_judgments_keeps_korean_translation_for_english_quote() (+42 more)

### Community 2 - "Provider Configuration"
Cohesion: 0.09
Nodes (49): configured_providers(), _endpoint_and_headers(), _gemini_schema(), clean(), _gemini_text(), LLMProvider, openai_provider(), _openai_schema() (+41 more)

### Community 3 - "Public URL Classification"
Cohesion: 0.07
Nodes (39): build_search_query(), _normalized_host(), origin_group_for_url(), AsyncClient, Classify a URL for display and diversity selection, not truth scoring., Return a conservative publisher group used to avoid duplicate origins., Conservative fallback when extraction did not supply semantic keywords., search_sources() (+31 more)

### Community 4 - "Workflow Execution Tests"
Cohesion: 0.06
Nodes (31): parametrize, Real LangGraph via HTTP boundary; adapters contain offline fixtures only., test_graph_failure_returns_safe_error(), stage(), test_invalid_http_input_is_safe_and_never_runs_graph(), test_post_rejects_malformed_result_contract(), test_post_runs_graph_and_returns_only_result(), module() (+23 more)

### Community 5 - "Fact-Check API Route"
Cohesion: 0.07
Nodes (24): backend(), dynamic, error(), GET(), headers, POST(), runtime, FactCheckRequest (+16 more)

### Community 6 - "API Contract Models"
Cohesion: 0.10
Nodes (29): AgentStatus, _ContractModel, FactCheckResult, FactClaim, FactEvidence, FactSource, BaseModel, Validated Python representation of the public True or Not result contract. (+21 more)

### Community 7 - "Router Data-Mode Guides"
Cohesion: 0.07
Nodes (35): Data Mode, Data Mode Reference, Data Router, RouterProvider, BrowserRouter, Declarative Data API Boundary, Declarative Mode, Declarative Mode Reference (+27 more)

### Community 8 - "Claim Extraction"
Cohesion: 0.09
Nodes (23): ExtractedClaim, Extraction, BaseModel, Server-only claim extraction. No search, judgment, or fallback output., invalid_request(), Local True or Not API backed by the assembled LangGraph workflow., Server settings and the assembled four-stage verification workflow., Request boundary compatible with the existing TypeScript request fields. (+15 more)

### Community 9 - "Health Status Endpoints"
Cohesion: 0.08
Nodes (20): agent_status(), health(), HealthStatus, BaseModel, get, Report process liveness, not provider readiness., Report whether the real four-stage workflow can be constructed., parametrize (+12 more)

### Community 10 - "Demo Fixture Content"
Cohesion: 0.11
Nodes (17): base, DEMO_FOCUS, DEMO_TEXT, demoPreview, documents, results, Action, Claim (+9 more)

### Community 11 - "Extraction Workflow"
Cohesion: 0.13
Nodes (20): extract_claims(), AsyncClient, Return a LangGraph state update; callers own the client and credential., parametrize, Offline provider transport fixtures, never real model responses., test_extractor_drops_invented_claim_without_fabricating_source_text(), run(), test_extractor_keeps_forecast_and_returns_search_keywords_separately() (+12 more)

### Community 12 - "YouTube API Tests"
Cohesion: 0.15
Nodes (19): Offline YouTube Data API contract tests; no Google credentials or traffic., test_comments_unavailable_keeps_video_title_without_exposing_provider_error(), run(), test_fetches_official_video_title_and_bounded_plain_text_comments(), handler(), run(), test_missing_key_or_invalid_video_url_makes_no_api_request(), run() (+11 more)

### Community 13 - "FactLens Requirements"
Cohesion: 0.09
Nodes (23): Claim Extraction and Selection, Claim-level Verification, Direct Evidence Requirement, Evidence Traceability Principle, FactLens Product Requirements Proposal, True or Not, URL Fetch Security, User Privacy Notice (+15 more)

### Community 14 - "Cancellation Probe Scripts"
Cohesion: 0.16
Nodes (19): os, pathlib, free_port(), Run from repo: backend/.venv/Scripts/python.exe scripts/probe-cancellation.py…, ready(), run(), free_port(), port_closed() (+11 more)

### Community 15 - "Runtime Workflow Graph"
Cohesion: 0.15
Nodes (15): build_runtime_workflow(), Compile extracting → searching → reading → verifying with final assembly., The four graph stages, injectable for offline orchestration tests., RuntimeAdapters, test_forecast_keywords_reach_search_through_graph_without_leaking_into_result(), handler(), run(), extract() (+7 more)

### Community 16 - "Fact-Check Request Client"
Cohesion: 0.15
Nodes (17): fact_check(), fact_check_stream(), post, BaseModel, Settings, FactCheckRequest, BaseModel, parametrize (+9 more)

### Community 17 - "Assistant Reply Composition"
Cohesion: 0.12
Nodes (17): AssistantReply, composeAssistantReply(), joinDetails(), ReplyResult, AgentEvent, AgentStage, AgentStatus, FACT_CHECK_MODEL (+9 more)

### Community 18 - "Evidence Synthesis Design"
Cohesion: 0.11
Nodes (19): Answer Provider Metadata, Exact Quote Grounding, Five-stage Workflow, Grounded Answer Synthesis, Grounded Answer Synthesis Plan, Synthesis Stage, Verified Source Text, YouTube Data Exclusion (+11 more)

### Community 19 - "Verification System Docs"
Cohesion: 0.11
Nodes (19): Claim Extraction, Claim Verification, FactLens Handoff, FactLens Verification System, FastAPI Backend, Google Search Rank Limitation, Grounded Citation, LangGraph Workflow (+11 more)

### Community 20 - "TypeScript Compiler Settings"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 21 - "Client Claim Extraction"
Cohesion: 0.18
Nodes (15): canonical(), extractClaims(), extractionSchema, format(), JsonObject, Judgment, judgmentSchema, labels (+7 more)

### Community 22 - "Backend Workflow Factory"
Cohesion: 0.15
Nodes (15): get_workflow(), Build the provider-backed graph only when a server-side key is configured., build_extraction_graph(), load_settings(), Stage, End after extraction; do not simulate search, sources, or judgments., Read the backend-local file without mutating process environment., Isolated settings and extraction graph tests; no paid API calls. (+7 more)

### Community 23 - "Streaming Response Protocol"
Cohesion: 0.15
Nodes (13): FactCheckResponse, encode(), NDJSON boundary: only stage labels and validated final results are public., Propagate cancellation and close the graph iterator on every exit path., stream_events(), parametrize, test_stream_errors_are_safe(), run() (+5 more)

### Community 24 - "Animated Count-Up UI"
Cohesion: 0.21
Nodes (13): CountUp(), CountUpProps, getRevealOrder(), randomCharacter(), randomizeText(), ScrambleRun, ScrambleText(), resetVisual() (+5 more)

### Community 25 - "Lattice Loading Component"
Cohesion: 0.16
Nodes (14): DEFAULT_PATTERN, formatElapsed(), GridSize, LatticeLoader(), LatticeLoaderProps, LoaderStatus, LoaderStyle, MARKS (+6 more)

### Community 26 - "Fact-Check Stream Parser"
Cohesion: 0.21
Nodes (11): FactCheckError, readFactCheckStream(), line(), safeSourceUrl(), FactCheckDashboard(), addMessage(), loadSample(), reset() (+3 more)

### Community 27 - "Client Cancellation Tests"
Cohesion: 0.20
Nodes (6): result, download(), FactSource, stripYoutubeApiDataForExport(), ref_node_assert, ref_node_test

### Community 28 - "Async Cancellation Tests"
Cohesion: 0.16
Nodes (9): asyncio, blocking_extract(), cancellation_state(), InstrumentedGraph, get, Explicit integration-test entry point ONLY; never imported by main/runtime. No…, record(), Read-node integration preserves source text for later citation verification. (+1 more)

### Community 29 - "App Layout and Entry"
Cohesion: 0.15
Nodes (6): app_globals, metadata, metadata, metadata, nextConfig, next

### Community 30 - "Fact-Check Architecture"
Cohesion: 0.15
Nodes (13): Agent Architecture Design, Claim Extraction Stage, Claim Verification Stage, Exact Citation Grounding, Fact Check Workflow, Local Development Boundary, No Persistent Answer Storage, Server Credential Boundary (+5 more)

### Community 31 - "Package Scripts and Metadata"
Cohesion: 0.15
Nodes (12): name, private, type, postcss, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+4 more)

### Community 32 - "Claim Verification Client"
Cohesion: 0.35
Nodes (9): Options, validResult(), TrustIndex(), FACT_SCORE_BANDS, FACT_SCORE_LABELS, normalizeFactScore(), scoreBand(), scoreLabel() (+1 more)

### Community 33 - "Public Source Fetching"
Cohesion: 0.26
Nodes (10): Address, fetchPublicText(), htmlToText(), publicAddress(), resolvePublicUrl(), Resolver, ref_node_dns, ref_node_http (+2 more)

### Community 34 - "Floating Lines Defaults"
Cohesion: 0.22
Nodes (9): DEFAULT_BOTTOM_WAVE_POSITION, DEFAULT_ENABLED_WAVES, DEFAULT_LINE_COUNT, DEFAULT_LINE_DISTANCE, FloatingLines(), FloatingLinesProps, hexToVec3(), WavePosition (+1 more)

### Community 35 - "Background Error Boundary"
Cohesion: 0.20
Nodes (7): BackgroundBoundary, FloatingLines, FloatingLinesBackground(), floatingLinesCount, floatingLinesDistance, floatingLinesGradient, floatingLinesWaves

### Community 36 - "Fact-Check Result Assembly"
Cohesion: 0.24
Nodes (9): build_fact_check_result(), verifying(), _normalize_source(), Project internal source state onto the public TypeScript contract., Validate and assemble the only result shape exposed by the API., _result_warnings(), Runtime assembly tests; fake adapters keep the four-node graph offline., test_result_exposes_youtube_comments_only_as_context_not_verified_content() (+1 more)

### Community 37 - "FactLens Workspace Controls"
Cohesion: 0.20
Nodes (10): Evidence comparison section (section 02, awaiting a document), Checkbox consent to send the source and verification request to the server/OpenAI for web search, Fact-check request form (section 01), FactLens fact-checking workspace, GlassSurface appearance controls: distortion −10, displacement 0.5, saturation 1.60, background opacity 30%, blur radius 18, Processing disclosure: gpt-5.6-luna reasoning max and web search, which may take time, Example document: virtual city's cultural event, Source entry by pasted text or URL (+2 more)

### Community 38 - "React Router Brand Assets"
Cohesion: 0.25
Nodes (5): app_welcome_logo_dark, app_welcome_logo_light, resources, Welcome(), ref_types_home

### Community 39 - "Build Tool Dependencies"
Cohesion: 0.22
Nodes (9): devDependencies, postcss, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom, @types/three (+1 more)

### Community 40 - "FactLens Empty-State Workspace"
Cohesion: 0.25
Nodes (8): Document Input Stage, Evidence Comparison Workspace, Evidence-first Principle, FactLens, FactLens Workspace Snapshot, Text Input Mode, URL Input Mode, Virtual City Cultural Event Example

### Community 41 - "FactLens Workspace Variant A"
Cohesion: 0.25
Nodes (8): Document Input Stage, Evidence Comparison Workspace, Evidence-first Principle, FactLens, FactLens Workspace Snapshot, Text Input Mode, URL Input Mode, Virtual City Cultural Event Example

### Community 42 - "FactLens Workspace Variant B"
Cohesion: 0.25
Nodes (8): Document Input Stage, Evidence Comparison Workspace, Evidence-first Principle, FactLens, FactLens Workspace Snapshot, Text Input Mode, URL Input Mode, Virtual City Cultural Event Example

### Community 43 - "FactLens Workspace Variant C"
Cohesion: 0.25
Nodes (8): Document Input Stage, Evidence Comparison Workspace, Evidence-first Principle, FactLens, FactLens Workspace Snapshot, Text Input Mode, URL Input Mode, Virtual City Cultural Event Example

### Community 44 - "FactLens Workspace Variant D"
Cohesion: 0.25
Nodes (8): Document Input Stage, Evidence Comparison Workspace, Evidence-first Principle, FactLens, FactLens Workspace Snapshot, Text Input Mode, URL Input Mode, Virtual City Cultural Event Example

### Community 45 - "React Router App Bootstrap"
Cohesion: 0.25
Nodes (3): app_app, ref_react_router, ref_types_root

### Community 46 - "GlassSurface Developer Panel"
Cohesion: 0.29
Nodes (8): Claim request field (확인 요청), Claim verification workspace (근거 워크스페이스), Model and web-search notice (gpt-5.6-luna · reasoning max · 웹 검색 사용), Original text field (확인할 원문), Start fact-checking button (팩트 검증 시작), Text input mode (텍스트 입력), URL input mode (URL 입력), Consent option for sending the original text and claim request to the server/OpenAI for web search

### Community 47 - "Next.js Migration References"
Cohesion: 0.25
Nodes (8): Next.js App Router, Next.js Project Scripts, Production Build Output, Project README, React Router Rollback References, Tailwind CSS, TypeScript, Visual Effects Dependencies

### Community 48 - "Sidebar Line Controls"
Cohesion: 0.29
Nodes (6): Falloff, FALLOFF_CURVES, LineSidebar(), LineSidebarItem, LineSidebarProps, LineSidebarStyle

### Community 49 - "Animation Dependency Cleanup"
Cohesion: 0.29
Nodes (7): animejs, Dependency Cleanup, particles-gl, ParticlesLogo, tweakpane, UI Dependency Audit, Unused Direct Dependency Rationale

### Community 50 - "Router Navigation Concepts"
Cohesion: 0.33
Nodes (6): Action Functions, Fetchers, Loader Functions, Nested Routes, Route Objects, Search Params

### Community 51 - "Vite Toolchain Configuration"
Cohesion: 0.33
Nodes (3): ref_react_router_dev, ref_tailwindcss_vite, ref_vite

### Community 52 - "Next.js Package Dependencies"
Cohesion: 0.33
Nodes (6): dependencies, motion, next, react, react-dom, three

### Community 53 - "React Bits Documentation"
Cohesion: 0.40
Nodes (5): Backgrounds Category, Floating Lines Component, React Bits Documentation, React Bits Page Snapshot, React Bits Pro

### Community 54 - "Visual Effects Components"
Cohesion: 0.40
Nodes (5): FactCheckDashboard, FloatingLinesBackground, Liquid Glass Panels, Motion, Three.js

### Community 55 - "Evidence Results Panel"
Cohesion: 0.40
Nodes (5): Evidence Results Panel (Empty State), Source Text Input Panel, Start Fact Check Button, URL Input Tab, Verification Request Field

### Community 56 - "Project Command Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, start, typecheck

### Community 57 - "React Router Logo Assets"
Cohesion: 0.50
Nodes (4): Red-and-black abstract emblem, REACT Router logo, REACT wordmark, Router wordmark

### Community 58 - "Fact-Check API Operations"
Cohesion: 0.50
Nodes (4): get, post, recover(), status()

### Community 59 - "Evidence Comparison Principles"
Cohesion: 0.50
Nodes (4): Demo Disclosure Policy, Evidence Comparison Workspace, Original Source Grouping, Source Independence

### Community 60 - "AI Provider Model Catalog"
Cohesion: 0.50
Nodes (4): Gemini 3.7 Flash, Gemini 3.8 Flash, GPT-6 Luna, Provider Fallback Chain

### Community 61 - "ESLint Configuration"
Cohesion: 0.50
Nodes (3): eslintConfig, ref_eslint, ref_eslint_config_next

### Community 62 - "Provider Fallback Chain"
Cohesion: 0.50
Nodes (4): Gemini 3.7 Flash, Gemini 3.8 Flash, GPT-6 Luna, Provider Fallback Chain

### Community 63 - "Next.js Generated Types"
Cohesion: 0.50
Nodes (3): next_dev_types_root_params_d, next_dev_types_routes_d, NOTE: This file should not be edited

### Community 64 - "Backend Startup Progress"
Cohesion: 0.67
Nodes (3): External Transmission Consent, Server setup check in progress, Verification Start Control

### Community 65 - "Backend Startup Failure"
Cohesion: 0.67
Nodes (3): External Transmission Consent, Server setup check failed, Verification Start Control

### Community 66 - "Verification Check Progress"
Cohesion: 0.67
Nodes (3): External Transmission Consent, Server setup check in progress, Verification Start Control

### Community 67 - "Verification Check Failure"
Cohesion: 0.67
Nodes (3): External Transmission Consent, Server setup check failed, Verification Start Control

### Community 68 - "Workspace Setup Status"
Cohesion: 0.67
Nodes (3): External Transmission Consent, Server setup check in progress, Verification Start Control

### Community 69 - "Next.js Agent Instructions"
Cohesion: 0.67
Nodes (3): Installed Next.js Documentation, Next.js Agent Guidance, Project Agent Rules

### Community 70 - "React Router Emblem"
Cohesion: 0.67
Nodes (3): Red branching emblem with three white circular marks, React Router logo, REACT Router wordmark

### Community 71 - "Forecast Claim Verdict"
Cohesion: 0.67
Nodes (3): Forecast Claim, Forecast-answer synthesis pending, Not Checkable Verdict

## Knowledge Gaps
- **273 isolated node(s):** `runtime`, `dynamic`, `headers`, `CountUpProps`, `base` (+268 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 537 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `search_sources()` connect `Public URL Classification` to `YouTube HTTP Retrieval`, `Provider Configuration`, `Fact-Check Result Assembly`, `Claim Extraction`, `Runtime Workflow Graph`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `extract_claims()` connect `Extraction Workflow` to `Provider Configuration`, `Fact-Check Result Assembly`, `Claim Extraction`, `Runtime Workflow Graph`, `Fact-Check Request Client`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `fetch_youtube_data()` connect `YouTube API Tests` to `Claim Extraction`, `YouTube HTTP Retrieval`, `Provider Configuration`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `search_sources()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`search_sources()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `LLMProvider` (e.g. with `extract_claims()` and `search_sources()`) actually correct?**
  _`LLMProvider` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `extract_claims()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`extract_claims()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `verify_claims()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`verify_claims()` has 2 INFERRED edges - model-reasoned connections that need verification._

## Graph Health Check

[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 1082
unverified_code_nodes: 0
raw_edges: 2009
valid_candidate_edges: 1792
missing_endpoint_edges: 0
dangling_endpoint_edges: 172
external_reference_edges: 45
self_loop_edges: 6
exact_duplicate_edges: 0
directed_unique_endpoint_pairs: 1668
directed_same_endpoint_collapsed_edges: 124
undirected_unique_endpoint_pairs: 1668
undirected_same_endpoint_collapsed_edges: 124
same_endpoint_group_count: 124
relation_variant_groups: 115
source_file_variant_groups: 0
source_location_variant_groups: 9
context_variant_groups: 0
post_build_graph_type: Graph
post_build_edges: 1875
producer_suppression_sites: 12
producer_suppression_examples:
  - L1349 seen_ids arity=unknown
  - L1882 seen_ids arity=unknown
  - L1884 seen_doc_refs arity=unknown
  - L2254 seen_ids arity=unknown
  - L2401 seen_ids arity=unknown
  - L3127 seen_keys arity=unknown
  - L3296 seen_keys arity=unknown
  - L5370 seen_ids arity=unknown
examples:
  - app_components_demo_fixture -> app_components_demo_state edges=2 relations=['imports_from'] locations=['L1', 'L2'] contexts=['import']
  - app_components_demo_state -> app_lib_fact_score edges=2 relations=['imports_from'] locations=['L2', 'L3'] contexts=['import']
  - app_components_fact_check_client_test -> app_components_fact_check_client_test_response edges=2 relations=['calls', 'contains'] locations=['L12', 'L6'] contexts=['', 'call']
  - app_components_fact_check_client_readfactcheckstream -> app_components_fact_check_client_readfactcheckstream_line edges=2 relations=['calls', 'contains'] locations=['L35', 'L52'] contexts=['', 'call']
  - app_components_fact_check_dashboard -> ref_react edges=2 relations=['imports_from'] locations=['L4', 'L5'] contexts=['import']
note: normal graph.json is post-build; raw producer loss must be measured earlier.

> Token tracking note: delegated semantic-extraction results did not include measured token usage. The 0 input/output counts above are placeholders, not a claim that semantic extraction used zero tokens.

## Token Reduction Benchmark

> Estimate from Graphify's built-in sample queries; this is not measured model usage.

- Corpus: 156,388 words, approximately 208,517 baseline tokens.
- Graph: 1,138 nodes and 1,875 edges.
- Average query context: approximately 7,450 tokens.
- Estimated reduction: 28.0× per sample query.
- Sample-query estimates:
  - `what is the main entry point`: ~4,321 tokens; ~48.3× reduction.
  - `how are errors handled`: ~15,507 tokens; ~13.4× reduction.
  - `what connects the data layer to the api`: ~7,664 tokens; ~27.2× reduction.
  - `what are the core abstractions`: ~2,311 tokens; ~90.2× reduction.
