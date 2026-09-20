"""Local FactLens API backed by the assembled LangGraph workflow."""
from typing import Literal

from fastapi import Depends, FastAPI, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from streaming import stream_events
from pydantic import BaseModel

from contracts import AgentStatus, FactCheckResponse
from runtime import build_runtime_workflow, load_settings
from schemas import FactCheckRequest


app = FastAPI(title="FactLens Backend", version="0.1.0")


class HealthStatus(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["factlens-backend"] = "factlens-backend"


@app.get("/health", response_model=HealthStatus)
async def health():
    """Report process liveness, not provider readiness."""
    return HealthStatus()


@app.get("/api/fact-check", response_model=AgentStatus)
async def agent_status(response: Response):
    """Report whether the real four-stage workflow can be constructed."""
    response.headers["Cache-Control"] = "no-store"
    configured = bool(load_settings().api_key.get_secret_value())
    return AgentStatus(
        configured=configured,
        workflowReady=configured,
        engine="langgraph",
        model="gpt-5.6-luna" if configured else None,
        reasoning="max" if configured else None,
        webSearch=configured,
        phase="workflow-ready" if configured else "api-foundation",
    )


def get_workflow():
    """Build the provider-backed graph only when a server-side key is configured."""
    settings = load_settings()
    if not settings.api_key.get_secret_value():
        return None
    return build_runtime_workflow(settings)


@app.post("/api/fact-check", response_model=FactCheckResponse)
async def fact_check(payload: FactCheckRequest, graph=Depends(get_workflow)):
    if graph is None:
        return JSONResponse(
            {"code": "NOT_CONFIGURED", "message": "서버의 OpenAI API 설정이 필요합니다."},
            status_code=503,
            headers={"Cache-Control": "no-store"},
        )
    try:
        state = await graph.ainvoke(payload.model_dump())
        response = FactCheckResponse.model_validate({"result": state.get("result")})
        return JSONResponse(
            response.model_dump(mode="json"),
            headers={"Cache-Control": "no-store"},
        )
    except Exception:
        # Do not expose provider diagnostics, input text, or partial internal state.
        return JSONResponse(
            {"code": "AGENT_FAILED", "message": "검증을 완료하지 못했습니다."},
            status_code=502,
            headers={"Cache-Control": "no-store"},
        )


@app.post("/api/fact-check/stream")
async def fact_check_stream(payload: FactCheckRequest, graph=Depends(get_workflow)):
    if graph is None:
        return JSONResponse({'code':'NOT_CONFIGURED','message':'서버의 OpenAI API 설정이 필요합니다.'}, status_code=503, headers={'Cache-Control':'no-store'})
    return StreamingResponse(stream_events(graph, payload.model_dump()), media_type='application/x-ndjson', headers={'Cache-Control':'no-store','X-Accel-Buffering':'no','X-Content-Type-Options':'nosniff'})


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return JSONResponse(
        {"code": "INVALID_REQUEST", "message": "본문, 확인 요청 길이 및 외부 전송 동의를 확인해 주세요."},
        status_code=422,
        headers={"Cache-Control": "no-store"},
    )
