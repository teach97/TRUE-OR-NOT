"""Provider-neutral requests and ordered LLM fallback policy.

Credentials stay in server-side provider objects. The adapters expose only
structured text and search citations to the stage modules; raw provider
responses never cross the API boundary.
"""

from collections.abc import Awaitable, Callable
from copy import deepcopy
from dataclasses import dataclass
import json
from typing import Any, Literal

import httpx


ProviderKind = Literal["openai", "gemini"]
Reasoning = Literal["max", "high"]
_MAX_RESPONSE_BYTES = 1_000_000
_SEARCH_TIMEOUT_SECONDS = 120


@dataclass(frozen=True, slots=True)
class LLMProvider:
    kind: ProviderKind
    model: str
    reasoning: Reasoning
    api_key: str


class ProviderCallError(RuntimeError):
    """A provider attempt failed and the next configured provider may retry."""


def openai_provider(api_key: str | None) -> LLMProvider:
    return LLMProvider("openai", "gpt-6-luna", "max", api_key or "")


def _secret_value(value: Any) -> str:
    if hasattr(value, "get_secret_value"):
        value = value.get_secret_value()
    return value.strip() if isinstance(value, str) else ""


def configured_providers(settings: Any) -> tuple[LLMProvider, ...]:
    """Return configured providers in the user-requested priority order."""
    openai_key = _secret_value(getattr(settings, "api_key", ""))
    gemini_key = _secret_value(getattr(settings, "gemini_api_key", ""))
    providers: list[LLMProvider] = []
    if gemini_key:
        providers.extend(
            [
                LLMProvider("gemini", "gemini-3.8-flash", "high", gemini_key),
                LLMProvider("gemini", "gemini-3.7-flash", "high", gemini_key),
            ]
        )
    if openai_key:
        providers.append(LLMProvider("openai", "gpt-6-luna", "max", openai_key))
    return tuple(providers)


async def run_with_fallback(
    providers: tuple[LLMProvider, ...],
    operation: Callable[[LLMProvider], Awaitable[Any]],
) -> tuple[Any, LLMProvider]:
    """Run an operation in priority order and return its result and provider."""
    last_error: ProviderCallError | None = None
    for provider in providers:
        try:
            return await operation(provider), provider
        except ProviderCallError as exc:
            last_error = exc
    raise last_error or ProviderCallError("No provider is configured")


def _gemini_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Remove JSON Schema keywords unsupported by Gemini structured output."""
    unsupported = {
        "default",
        "examples",
        "maxLength",
        "minLength",
        "pattern",
        "title",
    }

    def clean(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: clean(item)
                for key, item in value.items()
                if key not in unsupported
            }
        if isinstance(value, list):
            return [clean(item) for item in value]
        return value

    return clean(deepcopy(schema))


def _openai_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize Pydantic schemas for OpenAI strict structured output."""

    def clean(value: Any) -> Any:
        if isinstance(value, dict):
            normalized = {
                key: clean(item)
                for key, item in value.items()
                if key != "default"
            }
            properties = normalized.get("properties")
            if isinstance(properties, dict):
                # OpenAI strict mode does not support optional object keys.
                # Nullable values remain nullable, but every property is required.
                normalized["required"] = list(properties)
            return normalized
        if isinstance(value, list):
            return [clean(item) for item in value]
        return value

    return clean(deepcopy(schema))


def _endpoint_and_headers(provider: LLMProvider) -> tuple[str, dict[str, str]]:
    if provider.kind == "openai":
        return (
            "https://api.openai.com/v1/responses",
            {"Authorization": f"Bearer {provider.api_key}"},
        )
    return (
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        {"x-goog-api-key": provider.api_key},
    )


def _structured_payload(
    provider: LLMProvider,
    *,
    instructions: str,
    input_data: dict[str, Any],
    schema: dict[str, Any],
    max_output_tokens: int,
) -> dict[str, Any]:
    serialized_input = json.dumps(input_data, ensure_ascii=False)
    if provider.kind == "openai":
        return {
            "model": provider.model,
            "reasoning": {"effort": provider.reasoning},
            "store": False,
            "max_output_tokens": max_output_tokens,
            "instructions": instructions,
            "input": serialized_input,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "structured_result",
                    "strict": True,
                    "schema": _openai_schema(schema),
                }
            },
        }
    return {
        "model": provider.model,
        "system_instruction": instructions,
        "input": serialized_input,
        "store": False,
        "generation_config": {
            "max_output_tokens": max_output_tokens,
            "thinking_level": provider.reasoning,
            "thinking_summaries": "none",
        },
        "response_format": {
            "type": "text",
            "mime_type": "application/json",
            "schema": _gemini_schema(schema),
        },
    }


def _search_payload(
    provider: LLMProvider,
    *,
    instructions: str,
    input_data: dict[str, Any],
) -> dict[str, Any]:
    serialized_input = json.dumps(input_data, ensure_ascii=False)
    if provider.kind == "openai":
        return {
            "model": provider.model,
            "reasoning": {"effort": provider.reasoning},
            "store": False,
            "max_output_tokens": 6000,
            "instructions": instructions,
            "input": serialized_input,
            "tools": [{"type": "web_search", "search_context_size": "low"}],
            "tool_choice": "required",
            # Run several targeted search passes so one publisher cannot fill
            # the entire candidate set before the diversity selector sees it.
            "max_tool_calls": 4,
            "include": ["web_search_call.action.sources"],
        }
    return {
        "model": provider.model,
        "system_instruction": instructions,
        "input": serialized_input,
        "store": False,
        "tools": [{"type": "google_search"}],
        "tool_choice": "any",
        "generation_config": {
            "max_output_tokens": 6000,
            "thinking_level": provider.reasoning,
            "thinking_summaries": "none",
        },
    }


def _response_json(response: httpx.Response) -> dict[str, Any]:
    response.raise_for_status()
    if len(response.content) > _MAX_RESPONSE_BYTES:
        raise ProviderCallError("Response too large")
    data = response.json()
    if not isinstance(data, dict):
        raise ProviderCallError("Invalid response")
    if data.get("status") != "completed":
        raise ProviderCallError("Incomplete response")
    return data


def _openai_text(data: dict[str, Any]) -> str:
    parts = [
        part
        for item in data.get("output", [])
        if item.get("type") == "message"
        for part in item.get("content", [])
    ]
    if any(part.get("type") == "refusal" for part in parts):
        raise ProviderCallError("Refusal")
    texts = [part.get("text") for part in parts if part.get("type") == "output_text"]
    if len(texts) != 1 or not isinstance(texts[0], str):
        raise ProviderCallError("Invalid structured response")
    return texts[0]


def _gemini_text(data: dict[str, Any]) -> str:
    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text
    texts: list[str] = []
    for step in data.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for content in step.get("content", []):
            if content.get("type") == "text" and isinstance(content.get("text"), str):
                texts.append(content["text"])
    if len(texts) != 1:
        raise ProviderCallError("Invalid structured response")
    return texts[0]


async def request_structured(
    provider: LLMProvider,
    client: httpx.AsyncClient,
    *,
    instructions: str,
    input_data: dict[str, Any],
    schema: dict[str, Any],
    max_output_tokens: int,
) -> str:
    """Call a provider's structured-output endpoint and return only model text."""
    if not provider.api_key.strip():
        raise ProviderCallError("Missing provider key")
    endpoint, headers = _endpoint_and_headers(provider)
    payload = _structured_payload(
        provider,
        instructions=instructions,
        input_data=input_data,
        schema=schema,
        max_output_tokens=max_output_tokens,
    )
    try:
        response = await client.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=90,
        )
        data = _response_json(response)
        return _openai_text(data) if provider.kind == "openai" else _gemini_text(data)
    except ProviderCallError:
        raise
    except (httpx.HTTPError, TimeoutError, ValueError, KeyError, TypeError) as exc:
        raise ProviderCallError("Provider request failed") from exc


async def request_search(
    provider: LLMProvider,
    client: httpx.AsyncClient,
    *,
    instructions: str,
    input_data: dict[str, Any],
) -> dict[str, Any]:
    """Call a provider's search-grounded endpoint with a bounded response."""
    if not provider.api_key.strip():
        raise ProviderCallError("Missing provider key")
    endpoint, headers = _endpoint_and_headers(provider)
    payload = _search_payload(provider, instructions=instructions, input_data=input_data)
    try:
        async with client.stream(
            "POST",
            endpoint,
            json=payload,
            headers=headers,
            timeout=_SEARCH_TIMEOUT_SECONDS,
            follow_redirects=False,
        ) as response:
            response.raise_for_status()
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > _MAX_RESPONSE_BYTES:
                    raise ProviderCallError("Response too large")
        data = json.loads(body)
        if not isinstance(data, dict) or data.get("status") != "completed":
            raise ProviderCallError("Incomplete search response")
        return data
    except ProviderCallError:
        raise
    except (httpx.HTTPError, TimeoutError, ValueError, KeyError, TypeError) as exc:
        raise ProviderCallError("Provider search failed") from exc


def search_candidates(data: dict[str, Any], provider: LLMProvider) -> list[dict[str, Any]]:
    """Project provider search output to candidate URL annotations."""
    candidates: list[dict[str, Any]] = []
    if provider.kind == "openai":
        calls = [
            item
            for item in data.get("output", [])
            if item.get("type") == "web_search_call" and item.get("status") == "completed"
        ]
        if not calls:
            raise ProviderCallError("Search not completed")
        for item in calls:
            candidates.extend(item.get("action", {}).get("sources", []))
        for item in data.get("output", []):
            if item.get("type") != "message":
                continue
            for part in item.get("content", []):
                if part.get("type") == "refusal":
                    raise ProviderCallError("Refusal")
                candidates.extend(
                    annotation
                    for annotation in part.get("annotations", [])
                    if annotation.get("type") == "url_citation"
                )
        return candidates

    calls = [step for step in data.get("steps", []) if step.get("type") == "google_search_call"]
    if not calls:
        raise ProviderCallError("Google Search was not used")
    for step in data.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for content in step.get("content", []):
            candidates.extend(
                annotation
                for annotation in content.get("annotations", [])
                if annotation.get("type") == "url_citation"
            )
    return candidates
