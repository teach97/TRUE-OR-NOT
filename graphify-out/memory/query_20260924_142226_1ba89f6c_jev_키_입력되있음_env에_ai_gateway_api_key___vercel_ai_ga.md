---
type: "query"
date: "2026-09-24T14:22:26.669021+00:00"
question: "jev 키 입력되있음 env에 AI_GATEWAY_API_KEY=; Vercel AI Gateway Jev"
contributor: "graphify"
outcome: "corrected"
correction: "AI_GATEWAY_API_KEY is the correct Vercel AI Gateway credential for Jev in this project; the live backend process, not the .env value, is stale."
source_nodes: ["Settings", "load_settings()", "fact_check_jev()", "evaluate_claims_jev()"]
---

# Q: jev 키 입력되있음 env에 AI_GATEWAY_API_KEY=; Vercel AI Gateway Jev

## Answer

This repository uses the Vercel AI Gateway model typesafe-ai/jev and the correct key is AI_GATEWAY_API_KEY. backend/.env contains a non-empty value without exposing it, and TestClient against current source reports jevConfigured=true. The live backend on port 8010 omits jevConfigured and its OpenAPI schema lacks /api/fact-check/jev, so that running backend process is stale; restart it from backend using .venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8010, then refresh the frontend.

## Outcome

- Signal: corrected
- Correction: AI_GATEWAY_API_KEY is the correct Vercel AI Gateway credential for Jev in this project; the live backend process, not the .env value, is stale.

## Source Nodes

- Settings
- load_settings()
- fact_check_jev()
- evaluate_claims_jev()