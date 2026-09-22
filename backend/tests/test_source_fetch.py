"""Deterministic HTTP response fixtures; resolver safety tested separately."""
import asyncio
import pytest
import sources


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
