---
type: "query"
date: "2026-10-05T12:47:50.549502+00:00"
question: "Measure True or Not backend latency with model and reasoning settings held fixed"
contributor: "graphify"
outcome: "useful"
source_nodes: ["build_runtime_workflow()", "stream_events()", "request_structured()", "runtime.py"]
---

# Q: Measure True or Not backend latency with model and reasoning settings held fixed

## Answer

One live run on 42f7d61: intent 2447.70ms, extract 2681.99ms, Tavily search 1896.73ms, read 3977.78ms, verify 22509.13ms, synthesis 64960.68ms. Preview at 33529.44ms; total 98490.83ms ending MODEL_FAILED. Four structured LLM calls, one search and three general-web read attempts, no recovery or model fallback. Final HTTP200 ended length with completion_tokens=16000 and was rejected as incomplete. Verify+synthesis account for 88.8 percent. Model and reasoning level are fixed constraints, not causes or optimization variables. No production change; browser/proxy/DB and read substeps unmeasured. See docs/qa/실행기록/2026-10-05-지연측정.md.

## Outcome

- Signal: useful

## Source Nodes

- build_runtime_workflow()
- stream_events()
- request_structured()
- runtime.py