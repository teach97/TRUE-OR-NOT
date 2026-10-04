"""Deterministic arithmetic and shared-origin grouping; no network calls."""

import pytest


def test_extract_numbers_skips_years_and_parses_commas():
    from compute import extract_numbers

    assert extract_numbers("2024년 매출 12,500원") == [12500.0]
    assert extract_numbers("3.5% 상승") == [3.5]
    assert extract_numbers("숫자 없음") == []
    assert extract_numbers("") == []


def test_extract_numbers_preserves_year_like_measurements():
    from compute import extract_numbers

    assert extract_numbers("2024년 가격이 2,000원에서 2,500원으로 올랐다") == [2000.0, 2500.0]
    assert extract_numbers("2024년 직원 2000명") == [2000.0]


def test_percent_change_guards_zero_and_types():
    from compute import percent_change

    assert percent_change(100, 130) == 30.0
    assert percent_change(200, 100) == -50.0
    assert percent_change(0, 10) is None
    assert percent_change("a", 10) is None


def test_claim_computations_limits_explicit_changes():
    from compute import claim_computations

    assert claim_computations("주장 하나") == []
    assert claim_computations("1원→2원, 3원→4원, 5원→6원, 7원→8원") == [
        {"expression": "1→2", "percent": 100.0},
        {"expression": "3→4", "percent": 33.3},
        {"expression": "5→6", "percent": 20.0},
    ]


@pytest.mark.parametrize("quote, expected", [
    ("가격이 2,000원에서 2,500원으로 올랐다", {"expression": "2000→2500", "percent": 25.0}),
    ("매출이 100억 원에서 130억원으로 늘었다", {"expression": "100→130", "percent": 30.0}),
    ("직원 수가 100명에서 130명으로 늘었다", {"expression": "100→130", "percent": 30.0}),
    ("수량 10개→8개", {"expression": "10→8", "percent": -20.0}),
    ("가격 1만원 -> 1.5만 원", {"expression": "1→1.5", "percent": 50.0}),
    ("가격이 2000원→2500원 상승했다", {"expression": "2000→2500", "percent": 25.0}),
    ("수량 10개 -> 8개 감소", {"expression": "10→8", "percent": -20.0}),
])
def test_claim_computations_compares_same_unit_changes(quote, expected):
    from compute import claim_computations

    assert claim_computations(quote) == [expected]


@pytest.mark.parametrize("quote", [
    "매출 100억원, 직원 20명",
    "매출 100억원에서 순이익 130억원으로 바뀌었다",
    "가격 100원에서 130달러로 바뀌었다",
    "가격 10만원에서 100000원으로 바뀌었다",
    "가격은 100원에서 130원까지다",
    "가격은 100원부터 130원까지다",
    "가격 100원, 배송비 130원",
    "매출이 100에서 130으로 늘었다",
    "1 2 3 4 5 6 7 8",
    "2024년에서 2025년으로 넘어갔다",
    "금리가 3%에서 4%로 올랐다",
    "가격이 -100원에서 130원으로 바뀌었다",
    "가격이 1e3원에서 2e3원으로 바뀌었다",
    "가격이 1,2원에서 3원으로 바뀌었다",
    "가격이 0원에서 100원으로 올랐다",
    "가격 100~200원→300원",
    "가격 100~ 200원→300원",
    "가격 1/2원→3원",
    "가격 1/ 2원→3원",
    "가격 - 100원에서 130원으로 바뀌었다",
    "가격 100원→200원~300원",
    "가격 100원→200원 ~ 300원",
    "가격 100원→200원/2",
    "가격 100원→200원 / 2",
    "가격 100원→200원까지",
])
def test_claim_computations_skips_ambiguous_comparisons(quote):
    from compute import claim_computations

    assert claim_computations(quote) == []


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


@pytest.mark.parametrize("text, expected", [
    ("매출이 100억원에서 130억원으로 늘었다.", {"c1": [{"expression": "100→130", "percent": 30.0}]}),
    ("가격이 2000원에서 2500원으로 올랐다.", {"c1": [{"expression": "2000→2500", "percent": 25.0}]}),
    ("매출 100억원, 직원 20명.", {}),
    ("매출이 100에서 130으로 늘었다.", {}),
])
def test_verify_input_carries_only_supported_computed_values(text, expected):
    import asyncio
    import json

    import httpx

    from verification import verify_claims

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
    assert seen["input"]["computed"] == expected
