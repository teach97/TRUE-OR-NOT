"""Local True or Not API backed by the assembled LangGraph workflow."""
import subprocess
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from streaming import stream_events
from pydantic import BaseModel

from contracts import AgentStatus, FactCheckResponse
from providers import configured_model_options, configured_providers
from runtime import build_runtime_workflow, load_settings
from schemas import FactCheckRequest


app = FastAPI(title="True or Not Backend", version="0.1.0")


def _code_revision() -> str:
    """Identify the running tree so a stale deployment is visible via /health."""
    try:
        root = Path(__file__).resolve().parent.parent
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root, capture_output=True, text=True, timeout=5,
        )
        revision = head.stdout.strip()
        if head.returncode != 0 or not revision:
            return "unknown"
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root, capture_output=True, text=True, timeout=5,
        )
        if dirty.returncode == 0 and dirty.stdout.strip():
            revision += "-dirty"
        return revision
    except Exception:
        return "unknown"


_CODE_REVISION = _code_revision()


class HealthStatus(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["factlens-backend"] = "factlens-backend"
    revision: str = "unknown"


@app.get("/health", response_model=HealthStatus)
async def health():
    """Report process liveness, not provider readiness."""
    return HealthStatus(revision=_CODE_REVISION)


@app.get("/api/fact-check", response_model=AgentStatus)
async def agent_status(response: Response):
    """Report whether the real four-stage workflow can be constructed."""
    response.headers["Cache-Control"] = "no-store"
    settings = load_settings()
    providers = configured_providers(settings)
    configured = bool(providers)
    primary = providers[0] if providers else None
    return AgentStatus(
        configured=configured,
        workflowReady=configured,
        engine="langgraph",
        model=primary.model if primary else None,
        reasoning=primary.reasoning if primary else None,
        webSearch=configured,
        modelOptions=configured_model_options(settings),
        phase="workflow-ready" if configured else "api-foundation",
    )


def get_workflow():
    """Build the provider-backed graph only when a server-side key is configured."""
    settings = load_settings()
    if not configured_providers(settings):
        return None
    return build_runtime_workflow(settings)


@app.post("/api/fact-check", response_model=FactCheckResponse)
async def fact_check(payload: FactCheckRequest, graph=Depends(get_workflow)):
    if graph is None:
        return JSONResponse(
            {"code": "NOT_CONFIGURED", "message": "서버의 LLM provider 설정이 필요합니다."},
            status_code=503,
            headers={"Cache-Control": "no-store"},
        )
    try:
        state = await graph.ainvoke(payload.model_dump(exclude_defaults=True))
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
        return JSONResponse({'code':'NOT_CONFIGURED','message':'서버의 LLM provider 설정이 필요합니다.'}, status_code=503, headers={'Cache-Control':'no-store'})
    return StreamingResponse(stream_events(graph, payload.model_dump(exclude_defaults=True)), media_type='application/x-ndjson', headers={'Cache-Control':'no-store','X-Accel-Buffering':'no','X-Content-Type-Options':'nosniff'})


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return JSONResponse(
        {"code": "INVALID_REQUEST", "message": "본문, 확인 요청 길이 및 외부 전송 동의를 확인해 주세요."},
        status_code=422,
        headers={"Cache-Control": "no-store"},
    )
