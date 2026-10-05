"""Deterministic, exact source excerpts; no model or source-text mutation."""
import re


_CONTEXT = 450
_FALLBACK_LIMIT = 6_000
_STOP_WORDS = {"the", "are", "was", "were", "has", "have", "does", "did", "not",
               "and", "for", "this", "that", "with", "from", "will", "can"}


def _quote_matches(body: str, quote: str):
    words = quote.split()
    if not words:
        return iter(())
    return re.finditer(r"\s+".join(re.escape(word) for word in words), body)


def quote_span(body: str, quote: str) -> tuple[int, int] | None:
    """Locate the same whitespace-normalized quote accepted by verification."""
    match = next(_quote_matches(body, quote), None)
    return (match.start(), match.end()) if match else None


def claim_queries(state: dict, claims: list[dict]) -> list[str]:
    """Prefer existing extracted keywords; never add a keyword-generation call."""
    queries = state.get("searchQueries", {})
    if not isinstance(queries, dict):
        queries = {}
    return [queries.get(claim.get("id")) or claim.get("quote", "") for claim in claims]


def select_passages(body: str, queries: list[str], quotes: list[str] | None = None) -> dict:
    """Keep all matching windows, or use the old prefix when selection is broad.

    Exact quotes retain their full windows even when collectively over budget.
    Context selection is lexical, not proof of complete semantic coverage.
    """
    quotes = quotes or []
    anchors = [(match.start(), match.end()) for quote in quotes for match in _quote_matches(body, quote)]
    selection = "quote_context" if anchors else "related_context"
    if not anchors and len(body) <= 1_200:
        return {"selection": "complete", "passages": [{"start": 0, "end": len(body), "text": body}]}
    if not anchors:
        terms = {term for query in queries if isinstance(query, str)
                 for term in re.findall(r"[a-z][a-z0-9_-]{2,}|[가-힣]{2,}", query.lower())
                 if term not in _STOP_WORDS}
        for term in terms:
            pattern = re.escape(term)
            if term.isascii():
                pattern = r"(?<![a-z0-9_])" + pattern + r"(?![a-z0-9_])"
            anchors.extend((match.start(), match.end()) for match in re.finditer(pattern, body, re.IGNORECASE))

    ranges: list[list[int]] = []
    for start, end in sorted(anchors):
        start, end = max(0, start - _CONTEXT), min(len(body), end + _CONTEXT)
        if ranges and start <= ranges[-1][1]:
            ranges[-1][1] = max(ranges[-1][1], end)
        else:
            ranges.append([start, end])
    if not ranges or (not quotes and sum(end - start for start, end in ranges) > _FALLBACK_LIMIT):
        ranges = [[0, min(len(body), _FALLBACK_LIMIT)]]
        selection = "fallback"
    return {"selection": selection,
            "passages": [{"start": start, "end": end, "text": body[start:end]} for start, end in ranges]}
