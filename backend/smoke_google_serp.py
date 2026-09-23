"""One-query live check for the optional free-only Google search adapter."""
import asyncio

import httpx

from google_serp import FreeSearchUnavailable, search_google_free
from runtime import load_settings


async def main() -> int:
    key = load_settings().serpapi_api_key.get_secret_value()
    if not key:
        print("serpapi_configured=false")
        return 1

    state = {
        "consent": True,
        "claims": [{"id": "c1", "kind": "prediction", "quote": "AGI는 2030년 안에 오나?"}],
        "searchQueries": {"c1": "AGI 2030년"},
    }
    try:
        async with httpx.AsyncClient(timeout=20.0, trust_env=False) as client:
            result = await asyncio.wait_for(
                search_google_free(state, api_key=key, client=client), timeout=45.0,
            )
    except FreeSearchUnavailable as exc:
        print(f"free_google_search={exc}")
        return 1
    except TimeoutError:
        print("free_google_search=timeout")
        return 1

    sources = result["sources"]
    print(f"free_google_search=success source_count={len(sources)}")
    for source in sources:
        print(f"rank={source['candidateOrder']} publisher={source['publisher']} title={source['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
