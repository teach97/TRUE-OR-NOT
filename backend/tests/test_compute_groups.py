"""Deterministic arithmetic and shared-origin grouping; no network calls."""


def test_extract_numbers_skips_years_and_parses_commas():
    from compute import extract_numbers

    assert extract_numbers("2024년 매출 12,500원") == [12500.0]
    assert extract_numbers("3.5% 상승") == [3.5]
    assert extract_numbers("숫자 없음") == []
    assert extract_numbers("") == []


def test_percent_change_guards_zero_and_types():
    from compute import percent_change

    assert percent_change(100, 130) == 30.0
    assert percent_change(200, 100) == -50.0
    assert percent_change(0, 10) is None
    assert percent_change("a", 10) is None


def test_claim_computations_pairs_adjacent_numbers():
    from compute import claim_computations

    assert claim_computations("매출이 100에서 130으로 늘었다") == [
        {"expression": "100→130", "percent": 30.0}]
    assert claim_computations("주장 하나") == []
    assert len(claim_computations("1 2 3 4 5 6 7 8")) == 3


def test_shared_passage_groups_copied_sources():
    from search import apply_shared_origin_groups, group_by_shared_quotes

    passage = "동일한 보도자료 문장입니다. " * 6
    sources = [
        {"id": "s1", "originGroupId": "a.com"},
        {"id": "s2", "originGroupId": "b.org"},
        {"id": "s3", "originGroupId": "c.net"},
    ]
    texts = {
        "s1": "서론 " + passage + "결론",
        "s2": "다른 서론 " + passage + "다른 결론",
        "s3": "완전히 다른 내용의 기사 본문입니다. 겹치는 구절이 없습니다.",
    }
    mapping = group_by_shared_quotes(sources, texts)
    assert mapping["s1"] == mapping["s2"]
    assert "s3" not in mapping
    regrouped = apply_shared_origin_groups(sources, texts)
    assert regrouped[0]["originGroupId"] == mapping["s1"]
    assert regrouped[2]["originGroupId"] == "c.net"


def test_independence_warning_drops_when_group_confirmed():
    from runtime import _result_warnings

    plain = [{"sourceType": "웹"}]
    assert any("독립성" in warning for warning in _result_warnings(plain))
    grouped = [
        {"sourceType": "웹", "originGroupId": "shared-1"},
        {"sourceType": "웹", "originGroupId": "shared-1"},
    ]
    assert not any("독립성" in warning for warning in _result_warnings(grouped))


def test_verify_input_carries_computed_values():
    import asyncio
    import json

    import httpx

    from verification import verify_claims

    text = "매출이 100에서 130으로 늘었다."
    state = {
        "text": text,
        "focus": "",
        "claims": [{"id": "c1", "quote": text, "start": 0,
                    "end": len(text.encode("utf-16-le")) // 2, "kind": "fact"}],
        "sources": [{"id": "s1", "url": "https://example.org/report",
                     "accessStatus": "verified"}],
        "sourceTexts": {"s1": text + " 추가 원문 내용입니다."},
    }
    seen = {}

    def handler(request):
        body = json.loads(request.content)
        seen["input"] = json.loads(body["input"])
        return httpx.Response(200, json={
            "status": "completed",
            "output": [{
                "type": "message",
                "content": [{
                    "type": "output_text",
                    "text": json.dumps({"claims": [{
                        "claimId": "c1",
                        "verdictCode": "insufficient_evidence",
                        "factScore": 50,
                        "summary": "근거가 부족합니다.",
                        "confirmed": [],
                        "unresolved": [],
                        "evidence": [],
                    }]}),
                }],
            }],
        })

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await verify_claims(state, api_key="test-only", client=client)

    asyncio.run(run())
    assert seen["input"]["computed"]["c1"] == [{"expression": "100→130", "percent": 30.0}]
