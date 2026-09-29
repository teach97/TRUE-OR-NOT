import asyncio
import json

import httpx

from providers import (
    ProviderCallError,
    configured_providers,
    request_structured,
    run_with_fallback,
)
from runtime import load_settings


async def main():
    providers = configured_providers(load_settings())
    if not providers:
        raise SystemExit("LLM provider is not configured.")

    # The preceding smoke run already made a real request to the first provider
    # and confirmed it fails; start here at the first actual fallback candidate.
    fallback_providers = providers[1:]
    if not fallback_providers:
        raise SystemExit("1순위 외에 설정된 폴백 제공자가 없어.")
    print("폴백 시험 순서: " + " → ".join(provider.model for provider in fallback_providers))
    schema = {
        "type": "object",
        "properties": {"reply": {"type": "string"}},
        "required": ["reply"],
        "additionalProperties": False,
    }

    async with httpx.AsyncClient() as client:
        async def call(provider):
            try:
                async with asyncio.timeout(25):
                    output = await request_structured(
                        provider,
                        client,
                        instructions="Reply briefly in Korean to the user's message.",
                        input_data={"message": "하이"},
                        schema=schema,
                        max_output_tokens=32,
                    )
                try:
                    result = json.loads(output)
                except (json.JSONDecodeError, TypeError) as exc:
                    raise ProviderCallError("Invalid smoke-test reply") from exc
                reply = result.get("reply") if isinstance(result, dict) else None
                if not isinstance(reply, str) or not reply.strip():
                    raise ProviderCallError("Empty smoke-test reply")
                return reply.strip()
            except TimeoutError:
                print(f"{provider.model}: 25초 시간 초과, 다음 제공자로 폴백")
                raise ProviderCallError("Smoke-test timeout") from None
            except ProviderCallError as exc:
                cause = exc.__cause__
                status = getattr(getattr(cause, "response", None), "status_code", None)
                detail = f"HTTP {status}" if isinstance(status, int) else type(cause or exc).__name__
                print(f"{provider.model}: 호출 실패 ({detail}), 다음 제공자로 폴백")
                raise

        try:
            reply, provider = await run_with_fallback(fallback_providers, call)
        except ProviderCallError:
            print("모든 설정된 제공자의 호출이 실패했어.")
            raise SystemExit(1) from None

    print(f"성공 모델: {provider.model}")
    print(f"응답: {reply}")


if __name__ == "__main__":
    asyncio.run(main())
