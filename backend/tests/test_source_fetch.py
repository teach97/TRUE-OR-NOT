"""Deterministic HTTP response fixtures; resolver safety tested separately."""
import asyncio
import pytest
import sources


def test_read_node_attempts_sources_sequentially_even_after_failure():
    events = []

    async def reader(url):
        events.append(("start", url))
        await asyncio.sleep(0)
        events.append(("end", url))
        if url.endswith("/1"):
            raise ValueError("UNAVAILABLE")
        return "Actual source content", url

    candidates = [{"id": f"s{i}", "url": f"https://example.org/{i}"} for i in range(1, 4)]
    state = asyncio.run(sources.read_sources({"sources": candidates}, reader=reader))
    assert events == [(event, source["url"]) for source in candidates for event in ("start", "end")]
    assert [s["id"] for s in state["sources"]] == ["s1", "s2", "s3"]
    assert [s["accessStatus"] for s in state["sources"]] == ["unavailable", "verified", "verified"]


class Response:
    def __init__(self, status=200, headers=None, body=b'<p>Public source text.</p>'):
        self.status = status
        self.headers = headers or {'Content-Type':'text/html'}
        self.content = self
        self.body = body
    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass
    async def iter_chunked(self, size):
        yield self.body


class Session:
    def __init__(self, responses): self.responses, self.urls = list(responses), []
    def get(self, url, **kwargs):
        assert kwargs['allow_redirects'] is False
        self.urls.append(url)
        return self.responses.pop(0)


def run(responses, url='https://example.org/a'):
    assert hasattr(sources, '_read_url'), 'HTTP reader missing'
    session = Session(responses)
    return asyncio.run(sources._read_url(session, url)), session


def test_reads_html_and_tracks_final_url():
    (text, url), session = run([Response(302, {'Location':'/final'}), Response()])
    assert text == 'Public source text.'
    assert url == 'https://example.org/final'
    assert len(session.urls) == 2


@pytest.mark.parametrize('url', ['http://127.0.0.1/', 'http://[::1]/', 'http://169.254.169.254/', 'file:///etc/passwd', 'https://user:pw@example.org/', 'https://example.org:8080/'])
def test_redirect_to_unsafe_address_rejected(url):
    with pytest.raises(ValueError):
        run([Response(302, {'Location':url})])


@pytest.mark.parametrize('response', [Response(403), Response(200, {'Content-Type':'application/pdf'}), Response(200, {'Content-Type':'text/html','Content-Encoding':'gzip'}), Response(body=b'x'*512001), Response(body=b' '), Response(302, {'Location':'/loop'})])
def test_unavailable_and_oversized_content_rejected(response):
    with pytest.raises(ValueError):
        run([response]*4)


def test_read_node_records_failure_without_inventing_text():
    assert hasattr(sources, 'read_sources'), 'Read node missing'
    async def reader(url):
        if url.endswith('/bad'): raise ValueError('UNAVAILABLE')
        return 'Actual source content', url
    state = asyncio.run(sources.read_sources({'sources':[{'id':'s1','url':'https://example.org/good'}, {'id':'s2','url':'https://example.org/bad'}]}, reader=reader))
    assert [s['accessStatus'] for s in state['sources']] == ['verified','unavailable']
    assert state['sourceTexts'] == {'s1':'Actual source content'}


def test_read_node_deduplicates_distinct_search_urls_that_resolve_to_the_same_page():
    async def reader(url):
        return sources.SourceReadResult(
            'Same article text',
            'https://datalab.co.kr/agi/2030',
            'AGI 2030 전망',
        )

    state = asyncio.run(sources.read_sources({
        'sources': [
            {'id': 's1', 'url': 'https://short.example/agi', 'title': '첫 검색 결과'},
            {'id': 's2', 'url': 'https://datalab.co.kr/article?ref=google', 'title': '같은 기사 다른 주소'},
        ],
    }, reader=reader))

    assert [source['id'] for source in state['sources']] == ['s1']
    assert state['sourceTexts'] == {'s1': 'Same article text'}


def test_read_node_skips_japanese_article_body_from_generic_domain():
    async def reader(url):
        return sources.SourceReadResult(
            'これは日本語の記事です。人工知能の予測について解説します。2030年までの展望を紹介します。',
            url,
            'AGI 2030 forecast',
        )

    state = asyncio.run(sources.read_sources({
        'sources': [{'id': 's1', 'url': 'https://example.com/agi', 'title': 'AGI 2030 forecast'}],
    }, reader=reader))

    assert state['sources'] == []
    assert state['sourceTexts'] == {}


def test_read_node_uses_page_title_when_search_only_provided_a_host():
    async def reader(url):
        return sources.SourceReadResult(
            'Actual source content',
            url,
            'Astra research update · Example newsroom',
        )

    state = asyncio.run(sources.read_sources({
        'sources': [{
            'id': 's1',
            'url': 'https://example.org/good',
            'title': 'example.org',
        }],
    }, reader=reader))

    assert state['sources'][0]['title'] == 'Astra research update · Example newsroom'


def test_youtube_comments_are_context_only_and_never_become_source_text():
    async def youtube_reader(url):
        assert url == 'https://www.youtube.com/watch?v=aB_12345678'
        return {
            'title': 'AGI 전망 인터뷰',
            'comments': ['댓글 원문 1', '댓글 원문 2'],
            'status': 'collected',
        }

    state = asyncio.run(sources.read_sources({
        'sources': [{
            'id': 's1',
            'url': 'https://www.youtube.com/watch?v=aB_12345678',
            'title': '검색 결과 제목',
            'sourceType': '유튜브',
        }],
    }, youtube_reader=youtube_reader))

    assert state['sources'][0]['youtubeTitle'] == 'AGI 전망 인터뷰'
    assert state['sources'][0]['youtubeComments'] == ['댓글 원문 1', '댓글 원문 2']
    assert state['sources'][0]['youtubeDataStatus'] == 'collected'
    assert state['sources'][0]['accessStatus'] == 'unavailable'
    assert state['sourceTexts'] == {}


def test_youtube_without_api_reader_is_marked_not_configured():
    state = asyncio.run(sources.read_sources({
        'sources': [{
            'id': 's1',
            'url': 'https://www.youtube.com/watch?v=aB_12345678',
            'title': 'Search title',
            'sourceType': '유튜브',
        }],
    }))

    assert state['sources'][0]['youtubeDataStatus'] == 'not_configured'
    assert state['sources'][0]['youtubeComments'] == []
    assert state['sourceTexts'] == {}
