import asyncio
import json

import httpx

from providers import configured_providers, request_structured
from runtime import load_settings


async def main():
    providers = configured_providers(load_settings())
    if not providers:
        raise SystemExit("LLM provider is not configured.")

    provider = providers[0]
    schema = {
        "type": "object",
        "properties": {"reply": {"type": "string"}},
        "required": ["reply"],
        "additionalProperties": False,
    }

    try:
        async with httpx.AsyncClient() as client, asyncio.timeout(45):
            output = await request_structured(
                provider,
                client,
                instructions="Reply briefly in Korean to the user's message.",
                input_data={"message": "하이"},
                schema=schema,
                max_output_tokens=32,
            )
        print(f"{provider.model}: {json.loads(output)['reply']}")
    except Exception as exc:
        print(f"{provider.model}: 호출 실패 ({type(exc).__name__})")
        raise SystemExit(1) from None


if __name__ == "__main__":
    asyncio.run(main())
