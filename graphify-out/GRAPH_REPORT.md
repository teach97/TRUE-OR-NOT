# Graph Report - my-app  (2026-09-24)

## Corpus Check
- 126 files · ~85,915 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: (none) 5, .log 4, .css 4)

## Summary
- 1232 nodes · 2442 edges · 86 communities (68 shown, 18 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 256 edges (avg confidence: 0.88)
- Token cost: 1,150 input · 620 output

## Community Hubs (Navigation)
- Scoring Policy
- Answer Contracts
- Fact-Check API Route
- Search Query Pipeline
- Backend Entry Points
- Free Search Adapter
- Runtime Fallback Chain
- Cancellation Probe Harness
- Answer Synthesis Stage
- Source Fetch Fixtures
- Dashboard Chat UI
- YouTube Offline Tests
- Client Stream Tests
- Synthesis Provider Tests
- Claim Extraction Flow
- Provider Transports
- Grounded Answer Tests
- Vector Wordmark Renderer
- Execution Boundary Tests
- Public Source Fetching
- Fact-Check Type Contract
- Candidate URL Discovery
- Runtime Workflow Graph
- TypeScript Compiler Config
- Demo State Machine
- Client Stream Reader
- Citation Grounding Rules
- Request Validation Models
- Reply Citation UI
- Stream Progress Events
- Lattice Loading UI
- Source Security Tests
- Result Assembly Contract
- Package Dependencies
- Dashboard Actions
- Sidebar Line Controls
- HTML Content Parser
- Workflow Offline Tests
- Offline Test Suite
- Source Read Models
- Floating Lines Visual
- Lines Background Boundary
- Scramble Text Effect
- Router Mode Guides
- Static Legal Pages
- Welcome Home Routes
- Synthesis Pipeline Concepts
- Type Definition Packages
- Router App Bootstrap
- Demo Fixture Content
- Light Logo Assets
- Next Brand Assets
- Graph Stage Tests
- Forecast Synthesis Tests
- Globe Icon Assets
- Router Build Config
- Runtime Dependencies
- Package Scripts
- File Icon Assets
- Dark Logo Assets
- ESLint Configuration
- Next Generated Types
- Window Icon Assets
- Workspace Design Docs
- Declarative Mode Docs
- RSC Boundary Docs
- Agent Architecture Docs
- Workspace Snapshots
- Vercel Brand Assets
- Agent Rule Pointers
- Router Mode Concepts
- Project Readmes
- Model Fallback Chain
- Synthesis Plan Docs
- Trust Verdict Models
- Handoff Search Docs
- Search Filter Rules
- Floating Lines Docs
- PostCSS Configuration
- UI Design Direction
- UI Verification Record
- Planning Document
- YouTube Metadata Concepts
- Backend Service
- Playwright Snapshot
- Frontend Stack Concepts

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 44 edges
2. `search_sources()` - 41 edges
3. `make_runtime_adapters()` - 38 edges
4. `ProviderCallError` - 36 edges
5. `Settings` - 34 edges
6. `search_google_free()` - 30 edges
7. `extract_claims()` - 28 edges
8. `ground_judgments()` - 28 edges
9. `synthesize_answer()` - 27 edges
10. `verify_claims()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `Verification pipeline extract search read verify synthesize` --conceptually_related_to--> `FactLens backend FastAPI LangGraph claim pipeline`  [INFERRED]
  docs/True or Not-agent-architecture.md → backend/README.md
- `Provider fallback Gemini 3.8 Flash to 3.7 Flash to GPT-6 Luna` --shares_data_with--> `Model priority Gemini 3.8 3.7 GPT-6 Luna 2026-09-23`  [INFERRED]
  backend/README.md → HANDOFF.md
- `Fifth synthesizing LLM stage grounded overview` --conceptually_related_to--> `POST api fact-check stream NDJSON progress`  [INFERRED]
  docs/superpowers/plans/2026-09-23-grounded-answer-synthesis.md → backend/README.md
- `Evidence workspace conversation dashboard AI overview` --conceptually_related_to--> `Verification pipeline extract search read verify synthesize`  [INFERRED]
  .playwright-cli/page-2026-09-24T01-08-40-011Z.yml → docs/True or Not-agent-architecture.md
- `Dashboard demo-state fixture shader implementation and checks` --conceptually_related_to--> `Next.js breaking changes guide and verification cleanup`  [INFERRED]
  docs/True or Not-UI-verification.md → AGENTS.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **React Router mode selection** — agents_skills_react_router_skill_react_router_modes, agents_skills_react_router_skill_framework_mode_detection, agents_skills_react_router_skill_data_mode_detection, agents_skills_react_router_skill_declarative_mode_detection [EXTRACTED 1.00]
- **Evidence-first fact-check flow** — playwright_cli_page_2026_09_21t13_03_00_136z_factlens_workspace, playwright_cli_page_2026_09_24t01_03_06_200z_true_or_not_workspace, playwright_cli_page_2026_09_24t01_05_41_775z_verification_dashboard [INFERRED 0.75]
- **Grounded answer synthesis vertical slice** — docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_answer_contract, docs_superpowers_plans_2026_09_23_grounded_answer_synthesis_synthesis_stage, backend_readme_fact_check_stream [EXTRACTED 1.00]
- **Fact-check request pipeline** — readme_fact_check_proxy, backend_readme_factlens_backend, docs_true_or_not_agent_architecture_pipeline [EXTRACTED 1.00]
- **logo_light_composition** — logo_light_red_accent, logo_light_dark_dots, logo_light_wordmark [INFERRED 0.85]
- **Elements that form the document file icon** — public_file_document_file_icon, public_file_document_outline, public_file_folded_corner, public_file_text_lines [EXTRACTED 1.00]
- **public_globe_composition** — public_globe_globe_path, public_globe_clip_path, public_globe_wireframe [INFERRED 0.85]
- **public_next_composition** — public_next_n_mark, public_next_main_letterforms, public_next_js_suffix [INFERRED 0.85]

## Communities (86 total, 18 thin omitted)

### Community 0 - "Scoring Policy"
Cohesion: 0.06
Nodes (65): default_fact_score(), normalize_fact_score(), Evidence-grounded public score policy for fact-check claims., Return the public band for an inclusive 0–100 score., Keep model scores inside the certainty supported by grounded evidence. A…, Supply a compatible score when an older result omits the new field., score_band(), score_label() (+57 more)

### Community 1 - "Answer Contracts"
Cohesion: 0.06
Nodes (50): BaseModel, model_validator, Provider-owned answer fields; server-owned model metadata is excluded., SynthesisDraft, AgentStatus, AnswerBlock, AnswerCitation, AnswerSection (+42 more)

### Community 2 - "Fact-Check API Route"
Cohesion: 0.06
Nodes (44): backend(), dynamic, error(), GET(), headers, MODEL_OPTIONS, POST(), runtime (+36 more)

### Community 3 - "Search Query Pipeline"
Cohesion: 0.07
Nodes (41): build_search_query(), AsyncClient, Conservative fallback when extraction did not supply semantic keywords., search_sources(), search(), parametrize, Offline failure, safety and empty-result tests., test_candidates_filter_unsafe_urls_and_limit_results() (+33 more)

### Community 4 - "Backend Entry Points"
Cohesion: 0.06
Nodes (41): agent_status(), fact_check(), fact_check_stream(), get_workflow(), health(), HealthStatus, invalid_request(), BaseModel (+33 more)

### Community 5 - "Free Search Adapter"
Cohesion: 0.08
Nodes (31): FreeSearchUnavailable, _json_response(), AsyncClient, Optional SerpApi Google organic discovery, restricted to a free account., Safe failure code for the optional, free-only search path., Use only an account confirmed to be on the free plan with quota left., search_google_free(), main() (+23 more)

### Community 6 - "Runtime Fallback Chain"
Cohesion: 0.09
Nodes (31): insufficient_answer(), Return a fixed answer that makes no unsupported assertions., providers_for_preference(), Return the automatic chain or exactly one explicitly selected model., _structured_payload(), synthesizing(), _http_status_from_exception(), make_runtime_adapters() (+23 more)

### Community 7 - "Cancellation Probe Harness"
Cohesion: 0.10
Nodes (26): blocking_extract(), cancellation_state(), InstrumentedGraph, get, Explicit integration-test entry point ONLY; never imported by main/runtime. No…, record(), os, pathlib (+18 more)

### Community 8 - "Answer Synthesis Stage"
Cohesion: 0.11
Nodes (25): eligible_sources(), _project_claims(), Any, Synthesize a user-facing answer from verified source text only., Build a minimal JSON-safe input; never forward raw source/search records., Project at most six verified non-YouTube texts into a provider-safe shape., _string_value(), _synthesis_input() (+17 more)

### Community 9 - "Source Fetch Fixtures"
Cohesion: 0.09
Nodes (17): parametrize, Deterministic HTTP response fixtures; resolver safety tested separately., Response, run(), Session, test_read_node_attempts_sources_sequentially_even_after_failure(), reader(), test_read_node_deduplicates_distinct_search_urls_that_resolve_to_the_same_page() (+9 more)

### Community 10 - "Dashboard Chat UI"
Cohesion: 0.10
Nodes (18): CountUp(), CountUpProps, safeSourceUrl(), ChatMessage, ChatProgress, IconName, PanelProps, ProgressReply() (+10 more)

### Community 11 - "YouTube Offline Tests"
Cohesion: 0.13
Nodes (23): Offline YouTube Data API contract tests; no Google credentials or traffic., test_comments_unavailable_keeps_video_title_without_exposing_provider_error(), run(), test_fetches_official_video_title_and_bounded_plain_text_comments(), handler(), run(), test_ignores_malformed_youtube_metadata_without_rejecting_comments(), run() (+15 more)

### Community 12 - "Client Stream Tests"
Cohesion: 0.10
Nodes (14): insufficientAnswer, result, verifiedSource, ref_node_assert, ref_node_fs, ref_node_test, ref_node_url, observations (+6 more)

### Community 13 - "Synthesis Provider Tests"
Cohesion: 0.12
Nodes (17): source(), test_eligible_sources_excludes_unverified_empty_and_youtube_and_bounds_text(), test_all_synthesis_providers_failing_preserves_verified_result(), failing_provider(), mock_client(), read(), search(), test_real_graph_carries_free_search_fallback_notice_to_later_stages() (+9 more)

### Community 14 - "Claim Extraction Flow"
Cohesion: 0.12
Nodes (19): extract_claims(), AsyncClient, Return a LangGraph state update; callers own the client and credential., parametrize, test_extractor_drops_invented_claim_without_fabricating_source_text(), run(), test_extractor_keeps_forecast_and_returns_search_keywords_separately(), handler() (+11 more)

### Community 15 - "Provider Transports"
Cohesion: 0.15
Nodes (24): _endpoint_and_headers(), _gemini_schema(), clean(), _gemini_text(), LLMProvider, openai_provider(), _openai_schema(), clean() (+16 more)

### Community 16 - "Grounded Answer Tests"
Cohesion: 0.16
Nodes (23): AsyncClient, Generate and validate a grounded answer, leaving provider retries to runtime., synthesize_answer(), completed_response(), draft(), parametrize, state_with_source(), test_insufficient_answer_is_fixed_and_skips_provider_call() (+15 more)

### Community 17 - "Vector Wordmark Renderer"
Cohesion: 0.17
Nodes (21): Atlas, buildAtlas(), clamp(), compile(), FontSpec, fontString(), fract(), HANDLE_DEFAULTS (+13 more)

### Community 18 - "Execution Boundary Tests"
Cohesion: 0.13
Nodes (14): parametrize, Real LangGraph via HTTP boundary; adapters contain offline fixtures only., test_graph_failure_returns_safe_error(), stage(), test_invalid_http_input_is_safe_and_never_runs_graph(), test_post_rejects_malformed_result_contract(), test_post_runs_graph_and_returns_only_result(), test_updates_stream_uses_five_frontend_stage_names() (+6 more)

### Community 19 - "Public Source Fetching"
Cohesion: 0.15
Nodes (16): AbstractResolver, aiohttp, aiohttp_abc, checked_url(), fetch_public_text(), _generic_title(), html_title(), _is_japanese_page_text() (+8 more)

### Community 20 - "Fact-Check Type Contract"
Cohesion: 0.11
Nodes (17): AgentEvent, AgentStage, AgentStatus, AnswerSection, FACT_CHECK_MODEL, FACT_CHECK_REASONING, FactSource, MODEL_OPTIONS (+9 more)

### Community 21 - "Candidate URL Discovery"
Cohesion: 0.16
Nodes (19): candidate_url(), is_japanese_candidate(), _normalized_host(), origin_group_for_url(), _project_candidates(), Candidate discovery only; pending sources and snippets are not evidence. URL…, Classify a URL for display and diversity selection, not truth scoring., Return a conservative publisher group used to avoid duplicate origins. (+11 more)

### Community 22 - "Runtime Workflow Graph"
Cohesion: 0.15
Nodes (12): build_runtime_workflow(), Compile five ordered stages and assemble the result after synthesis., The five graph stages, injectable for offline orchestration tests., RuntimeAdapters, test_forecast_keywords_reach_search_through_graph_without_leaking_into_result(), handler(), run(), extract() (+4 more)

### Community 23 - "TypeScript Compiler Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "Demo State Machine"
Cohesion: 0.21
Nodes (14): Action, Claim, createPreview(), initialState, State, transition(), TrustIndex(), FACT_SCORE_BANDS (+6 more)

### Community 25 - "Client Stream Reader"
Cohesion: 0.19
Nodes (16): FactCheckError, Options, readFactCheckStream(), line(), validAnswer(), validEvidenceSection(), validProgressCitation(), validProgressClaim() (+8 more)

### Community 26 - "Citation Grounding Rules"
Cohesion: 0.17
Nodes (17): Require every citation to resolve to an exact substring of supplied text., _validate_answer_grounding(), ProviderCallError, A provider attempt failed and the next configured provider may retry., Run an operation in priority order and return its result and provider., run_with_fallback(), main(), call() (+9 more)

### Community 27 - "Request Validation Models"
Cohesion: 0.18
Nodes (15): BaseModel, Settings, FactCheckRequest, BaseModel, parametrize, Offline API boundary checks; no provider calls., test_health_and_status_do_not_claim_provider_readiness(), test_request_preserves_original_text() (+7 more)

### Community 28 - "Reply Citation UI"
Cohesion: 0.15
Nodes (15): AnswerBlockView(), AnswerOverview(), AnswerCitationDisplay, AnswerCitationDisplayState, AssistantReply, createAnswerCitationDisplayState(), presentAnswerCitations(), ReplyResult (+7 more)

### Community 29 - "Stream Progress Events"
Cohesion: 0.15
Nodes (12): Propagate cancellation and close the graph iterator on every exit path., stream_events(), parametrize, test_stream_emits_candidate_sources_and_grounded_preview_before_final_result(), collect(), test_stream_errors_are_safe(), run(), test_stream_explains_that_a_pinned_model_failed_without_exposing_provider_details() (+4 more)

### Community 30 - "Lattice Loading UI"
Cohesion: 0.16
Nodes (14): DEFAULT_PATTERN, formatElapsed(), GridSize, LatticeLoader(), LatticeLoaderProps, LoaderStatus, LoaderStyle, MARKS (+6 more)

### Community 31 - "Source Security Tests"
Cohesion: 0.23
Nodes (13): module(), parametrize, Public-source security tests; no external traffic., test_html_excludes_noncontent(), test_html_excludes_video_and_custom_player_elements(), test_html_extracts_article_text_without_navigation_or_player_chrome(), test_html_fallback_still_excludes_menu_and_player_without_article_markers(), test_html_skips_table_of_contents_and_extracts_only_each_heading_body() (+5 more)

### Community 32 - "Result Assembly Contract"
Cohesion: 0.21
Nodes (11): FactCheckResponse, build_fact_check_result(), _normalize_source(), Project internal source state onto the public TypeScript contract., Validate and assemble the only result shape exposed by the API., _result_warnings(), Runtime assembly tests; explicit adapters keep the five-node graph offline., test_final_result_warns_when_free_google_search_was_unavailable() (+3 more)

### Community 33 - "Package Dependencies"
Cohesion: 0.15
Nodes (12): name, private, type, postcss, react-dom, tailwindcss, @tailwindcss/postcss, @types/node (+4 more)

### Community 34 - "Dashboard Actions"
Cohesion: 0.26
Nodes (10): FactCheckDashboard(), addMessage(), download(), loadSample(), reset(), stop(), submit(), hasEnglishText() (+2 more)

### Community 35 - "Sidebar Line Controls"
Cohesion: 0.17
Nodes (9): Falloff, FALLOFF_CURVES, LineSidebar(), LineSidebarItem, LineSidebarProps, LineSidebarStyle, app_globals, metadata (+1 more)

### Community 37 - "Workflow Offline Tests"
Cohesion: 0.17
Nodes (4): Offline orchestration tests; fixtures are not real fact-check results., test_provider_failure_stops_graph_without_fabricated_result(), test_workflow_runs_stages_in_order_and_passes_state(), importlib_util

### Community 38 - "Offline Test Suite"
Cohesion: 0.31
Nodes (7): asyncio, Offline tests for source-bounded, citation-grounded answer synthesis., Offline provider transport fixtures, never real model responses., Offline contract tests for the optional, free-only Google organic adapter., httpx, json, pytest

### Community 39 - "Source Read Models"
Cohesion: 0.18
Nodes (4): Reader result with optional metadata and backwards-compatible unpacking., SourceReadResult, _TitleParser, HTMLParser

### Community 40 - "Floating Lines Visual"
Cohesion: 0.22
Nodes (9): DEFAULT_BOTTOM_WAVE_POSITION, DEFAULT_ENABLED_WAVES, DEFAULT_LINE_COUNT, DEFAULT_LINE_DISTANCE, FloatingLines(), FloatingLinesProps, hexToVec3(), WavePosition (+1 more)

### Community 41 - "Lines Background Boundary"
Cohesion: 0.20
Nodes (7): BackgroundBoundary, FloatingLines, FloatingLinesBackground(), floatingLinesCount, floatingLinesDistance, floatingLinesGradient, floatingLinesWaves

### Community 42 - "Scramble Text Effect"
Cohesion: 0.36
Nodes (9): getRevealOrder(), randomCharacter(), randomizeText(), ScrambleRun, ScrambleText(), resetVisual(), startRun(), writeVisual() (+1 more)

### Community 43 - "Router Mode Guides"
Cohesion: 0.22
Nodes (9): Data Loading with Loaders and Actions, Data Router Shape, Forms Fetchers and Pending UI, Middleware Sessions and Auth, Framework Rendering Strategy, Framework Route Modules, Framework Type Safety with Generated Route Types, Data Mode Detection Signals (+1 more)

### Community 44 - "Static Legal Pages"
Cohesion: 0.22
Nodes (4): metadata, metadata, nextConfig, next

### Community 45 - "Welcome Home Routes"
Cohesion: 0.25
Nodes (5): app_welcome_logo_dark, app_welcome_logo_light, resources, Welcome(), ref_types_home

### Community 46 - "Synthesis Pipeline Concepts"
Cohesion: 0.22
Nodes (9): POST api fact-check stream NDJSON progress, FactLens backend FastAPI LangGraph claim pipeline, FactCheckAnswer AnswerBlock Citation Section contract, Fifth synthesizing LLM stage grounded overview, Verification pipeline extract search read verify synthesize, Shared contract app lib fact-check-contract.ts, MVP F01-F11 and claim-centered product principles, Evidence workspace conversation dashboard AI overview (+1 more)

### Community 47 - "Type Definition Packages"
Cohesion: 0.22
Nodes (9): devDependencies, postcss, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom, @types/three (+1 more)

### Community 48 - "Router App Bootstrap"
Cohesion: 0.25
Nodes (3): app_app, ref_react_router, ref_types_root

### Community 49 - "Demo Fixture Content"
Cohesion: 0.25
Nodes (7): base, DEMO_FOCUS, DEMO_TEXT, demoPreview, documents, results, Preview

### Community 50 - "Light Logo Assets"
Cohesion: 0.29
Nodes (8): Dark circular dots, logo-light.svg, Logo icon mark, Light theme variant, Red accent path, SVG root 1080x174, Welcome page branding, Wordmark letter paths

### Community 51 - "Next Brand Assets"
Cohesion: 0.32
Nodes (8): Default template branding, next.svg, .js suffix glyphs, EXT letter paths, Monochrome variant, N letter path, SVG root 394x80, Next.js wordmark

### Community 52 - "Graph Stage Tests"
Cohesion: 0.33
Nodes (3): test_graph_keeps_source_texts_for_verification(), read(), reader()

### Community 53 - "Forecast Synthesis Tests"
Cohesion: 0.33
Nodes (3): test_forecast_synthesis_preserves_prediction_and_citations(), mock_client(), provider_response()

### Community 54 - "Globe Icon Assets"
Cohesion: 0.33
Nodes (7): Clip path definition, Default template icon, globe.svg, Globe wireframe path, Monochrome gray variant, SVG root 16x16, Globe wireframe motif

### Community 55 - "Router Build Config"
Cohesion: 0.33
Nodes (3): ref_react_router_dev, ref_tailwindcss_vite, ref_vite

### Community 56 - "Runtime Dependencies"
Cohesion: 0.33
Nodes (6): dependencies, motion, next, react, react-dom, three

### Community 57 - "Package Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, start, typecheck

### Community 58 - "File Icon Assets"
Cohesion: 0.40
Nodes (5): Document File Icon, Document Page Outline, Folded Corner, Gray Fill Style, Text Content Lines

### Community 59 - "Dark Logo Assets"
Cohesion: 0.50
Nodes (4): Dark Background Variant Purpose for Welcome Page, Geometric Icon Mark with Red Accent and White Nodes, Dark Mode Logo SVG, React Router Wordmark in White

### Community 60 - "ESLint Configuration"
Cohesion: 0.50
Nodes (3): eslintConfig, ref_eslint, ref_eslint_config_next

### Community 61 - "Next Generated Types"
Cohesion: 0.50
Nodes (3): next_dev_types_root_params_d, next_dev_types_routes_d, NOTE: This file should not be edited

### Community 62 - "Window Icon Assets"
Cohesion: 0.50
Nodes (4): Minimal Window Chrome Icon Purpose for UI, Three Circular Window Control Dots in Title Bar, Window Frame Outline with Rounded Bottom Corners, Browser Window Icon SVG in Gray

### Community 63 - "Workspace Design Docs"
Cohesion: 0.67
Nodes (3): Next.js breaking changes guide and verification cleanup, Premium research workspace dark glass design, Dashboard demo-state fixture shader implementation and checks

### Community 64 - "Declarative Mode Docs"
Cohesion: 0.67
Nodes (3): Declarative Router Shape, Declarative Mode Boundary, Declarative Mode Detection Signals

### Community 65 - "RSC Boundary Docs"
Cohesion: 0.67
Nodes (3): RSC Client Server Boundaries, RSC Route Module Differences, RSC Detection Signals

### Community 66 - "Agent Architecture Docs"
Cohesion: 0.67
Nodes (3): True or Not agent architecture, Gemini Interactions API docs citation, GPT-6 Luna model docs citation

### Community 67 - "Workspace Snapshots"
Cohesion: 0.67
Nodes (3): FactLens Evidence Workspace, True or Not Conversational Fact-Check Workspace, Verification Dashboard with Trust Index

### Community 68 - "Vercel Brand Assets"
Cohesion: 0.67
Nodes (3): Vercel Brand Mark Purpose for Deployment Branding, White Filled Triangle Mark viewBox 1155x1000, Vercel Triangle Logo SVG in White

## Knowledge Gaps
- **201 isolated node(s):** `runtime`, `dynamic`, `headers`, `MODEL_OPTIONS`, `CountUpProps` (+196 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 500 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_runtime_adapters()` connect `Runtime Fallback Chain` to `Scoring Policy`, `Result Assembly Contract`, `Search Query Pipeline`, `Backend Entry Points`, `Free Search Adapter`, `Answer Synthesis Stage`, `YouTube Offline Tests`, `Synthesis Provider Tests`, `Claim Extraction Flow`, `Grounded Answer Tests`, `Public Source Fetching`, `Forecast Synthesis Tests`, `Runtime Workflow Graph`, `Citation Grounding Rules`, `Request Validation Models`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `LLMProvider` connect `Provider Transports` to `Scoring Policy`, `Search Query Pipeline`, `Backend Entry Points`, `Runtime Fallback Chain`, `Offline Test Suite`, `Answer Synthesis Stage`, `Claim Extraction Flow`, `Grounded Answer Tests`, `Candidate URL Discovery`, `Citation Grounding Rules`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `search_sources()` connect `Search Query Pipeline` to `Result Assembly Contract`, `Runtime Fallback Chain`, `Answer Synthesis Stage`, `Provider Transports`, `Candidate URL Discovery`, `Runtime Workflow Graph`, `Citation Grounding Rules`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `LLMProvider` (e.g. with `synthesize_answer()` and `extract_claims()`) actually correct?**
  _`LLMProvider` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `search_sources()` (e.g. with `LLMProvider` and `ProviderCallError`) actually correct?**
  _`search_sources()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `make_runtime_adapters()` (e.g. with `FreeSearchUnavailable` and `extract()`) actually correct?**
  _`make_runtime_adapters()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ProviderCallError` (e.g. with `extract_claims()` and `search_sources()`) actually correct?**
  _`ProviderCallError` has 5 INFERRED edges - model-reasoned connections that need verification._