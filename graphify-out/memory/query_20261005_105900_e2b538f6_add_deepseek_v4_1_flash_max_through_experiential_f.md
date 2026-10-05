---
type: "query"
date: "2026-10-05T10:59:00.656047+00:00"
question: "Add DeepSeek V4.1 Flash MAX through Experiential first in the existing LLM fallback chain"
contributor: "graphify"
outcome: "useful"
source_nodes: ["providers.py", "runtime.py", "run_with_fallback()"]
---

# Q: Add DeepSeek V4.1 Flash MAX through Experiential first in the existing LLM fallback chain

## Answer

Expanded graph vocabulary: provider model fallback. Verified backend/providers.py central routing, backend/runtime.py stage fallback, schemas and TypeScript model contracts. DeepSeek uses the Experiential Chat Completions endpoint and server-only EXPLABS_API_KEY; existing OpenAI/Gemini request payloads and native search tools remain separate. Synthetic gateway request succeeded once; full offline and browser tests remain separate evidence in docs/qa.

## Outcome

- Signal: useful

## Source Nodes

- providers.py
- runtime.py
- run_with_fallback()