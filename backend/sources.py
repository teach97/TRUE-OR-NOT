"""Bounded public-source reader. TLS validation stays enabled; no credentials."""
import asyncio
import ipaddress
import re
import socket
from html.parser import HTMLParser
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit
from search import candidate_url

import aiohttp
from aiohttp.abc import AbstractResolver


def public_ip(raw):
    try:
        ip = ipaddress.ip_address(raw)
        if not ip.is_global or ip.is_multicast or ip.is_reserved:
            return False
        if ip.version == 6:
            return ip in ipaddress.ip_network('2000::/3') and not any(ip in ipaddress.ip_network(n) for n in ('2001::/23','2002::/16','3fff::/20'))
        return not any(ip in ipaddress.ip_network(n) for n in ('192.0.0.0/24','192.88.99.0/24'))
    except ValueError:
        return False


class PublicResolver(AbstractResolver):
    async def resolve(self, host, port=0, family=socket.AF_UNSPEC):
        answers = await asyncio.get_running_loop().getaddrinfo(host, port, family=family, type=socket.SOCK_STREAM)
        if not answers or any(not public_ip(a[4][0]) for a in answers):
            raise ValueError('UNSAFE_SOURCE')
        # Connector connects directly to these numeric addresses, without re-resolving.
        return [dict(hostname=host, host=a[4][0], port=port, family=a[0], proto=a[2], flags=socket.AI_NUMERICHOST) for a in answers]

    async def close(self):
        pass


class _TextParser(HTMLParser):
    _HIDDEN_TAGS = {
        'head', 'script', 'style', 'noscript', 'template', 'svg', 'nav',
        'header', 'footer', 'aside', 'button', 'input', 'select', 'option',
        'textarea', 'form', 'dialog', 'iframe', 'video', 'audio',
    }
    _VOID_TAGS = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr',
    }
    _CONTENT_HINTS = {
        'article-body', 'articlebody', 'article-content', 'articlecontent',
        'story-body', 'storybody', 'story-content', 'storycontent',
        'post-body', 'postbody', 'post-content', 'postcontent',
        'entry-content', 'entrycontent', 'news-body', 'newsbody',
        'news-content', 'newscontent', 'main-content', 'maincontent',
        'content-body', 'contentbody',
    }
    _UI_HINTS = {
        'nav', 'navigation', 'navbar', 'menu', 'sidebar', 'toolbar', 'player',
        'playlist', 'related', 'recommend', 'recommended', 'cookie', 'consent',
        'advert', 'advertisement', 'ad-container', 'promo', 'promotion',
        'share-tool', 'share-tools',
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.fallback_parts = []
        self.content_parts = []

    @staticmethod
    def _normalized_token(value):
        value = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', value)
        return re.sub(r'[^a-zA-Z0-9]+', '-', value).strip('-').lower()

    @classmethod
    def _is_content_root(cls, tag, attrs):
        if tag in {'main', 'article'} or attrs.get('role', '').lower() == 'main':
            return True
        if attrs.get('itemprop', '').lower() == 'articlebody':
            return True
        for name in ('id', 'class'):
            tokens = attrs.get(name, '').split()
            if any(cls._normalized_token(token) in cls._CONTENT_HINTS for token in tokens):
                return True
        return False

    @classmethod
    def _is_ui(cls, tag, attrs):
        role = attrs.get('role', '').lower()
        normalized_tag = cls._normalized_token(tag)
        if (
            tag in cls._HIDDEN_TAGS
            or 'player' in normalized_tag.split('-')
            or role in {
                'navigation', 'banner', 'complementary', 'contentinfo', 'search',
                'dialog', 'menu', 'toolbar',
            }
        ):
            return True
        if (
            'hidden' in attrs
            or 'inert' in attrs
            or attrs.get('aria-hidden', '').lower() == 'true'
        ):
            return True
        for name in ('id', 'class', 'aria-label'):
            tokens = attrs.get(name, '').split()
            for token in tokens:
                normalized = cls._normalized_token(token)
                pieces = set(normalized.split('-'))
                if normalized in cls._UI_HINTS or pieces.intersection(cls._UI_HINTS):
                    return True
        return False

    def handle_starttag(self, tag, attrs):
        attributes = {name.lower(): value or '' for name, value in attrs}
        parent = self.stack[-1] if self.stack else {'excluded': False, 'content': False}
        excluded = parent['excluded'] or self._is_ui(tag, attributes)
        content = not excluded and (parent['content'] or self._is_content_root(tag, attributes))
        if not excluded:
            self.fallback_parts.append(' ')
            if content:
                self.content_parts.append(' ')
        if tag not in self._VOID_TAGS:
            self.stack.append({'tag': tag, 'excluded': excluded, 'content': content})

    def handle_endtag(self, tag):
        match = next((i for i in range(len(self.stack) - 1, -1, -1)
                      if self.stack[i]['tag'] == tag), None)
        if match is None:
            return
        frame = self.stack[match]
        if not frame['excluded']:
            self.fallback_parts.append(' ')
            if frame['content']:
                self.content_parts.append(' ')
        del self.stack[match:]

    def handle_data(self, data):
        if self.stack and self.stack[-1]['excluded']:
            return
        self.fallback_parts.append(data)
        if self.stack and self.stack[-1]['content']:
            self.content_parts.append(data)

    @staticmethod
    def _normalize(parts):
        return ' '.join(' '.join(parts).split())

    def text(self):
        content = self._normalize(self.content_parts)
        return content or self._normalize(self.fallback_parts)


class _TitleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.parts.append(data)


def html_text(raw):
    parser = _TextParser()
    parser.feed(raw)
    return parser.text()


def html_title(raw):
    parser = _TitleParser()
    parser.feed(raw)
    return ' '.join(' '.join(parser.parts).split())[:300]


class SourceReadResult:
    """Reader result with optional metadata and backwards-compatible unpacking."""

    __slots__ = ('text', 'url', 'title')

    def __init__(self, text, url, title=''):
        self.text = text
        self.url = url
        self.title = title

    def __iter__(self):
        # Existing test and custom readers unpack only (text, url).
        yield self.text
        yield self.url


def checked_url(raw):
    url = candidate_url(raw)
    if url is None:
        raise ValueError('UNSAFE_SOURCE')
    host = urlsplit(url).hostname
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return url
    if not public_ip(str(ip)):
        raise ValueError('UNSAFE_SOURCE')
    return url


async def _read_url(session, raw, *, include_title=False):
    current = raw
    for attempt in range(3):
        current = checked_url(current)
        async with session.get(current, allow_redirects=False) as response:
            if response.status in {301, 302, 303, 307, 308}:
                location = response.headers.get('Location')
                if not location:
                    raise ValueError('SOURCE_REDIRECT')
                current = urljoin(current, location)
                continue
            media = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
            encoding = response.headers.get('Content-Encoding', 'identity').lower()
            if response.status != 200 or media not in {'text/html', 'text/plain'} or encoding != 'identity':
                raise ValueError('SOURCE_UNAVAILABLE')
            body = bytearray()
            async for chunk in response.content.iter_chunked(16384):
                if len(body) + len(chunk) > 512000:
                    raise ValueError('SOURCE_TOO_LARGE')
                body.extend(chunk)
            decoded = body.decode('utf-8', errors='replace')
            title = html_title(decoded) if media == 'text/html' else ''
            text = html_text(decoded) if media == 'text/html' else ' '.join(decoded.split())
            if not text:
                raise ValueError('SOURCE_EMPTY')
            if include_title:
                return SourceReadResult(text[:18000], current, title)
            return text[:18000], current
    raise ValueError('SOURCE_REDIRECT_LIMIT')


async def fetch_public_text(raw):
    # One deadline includes DNS, TLS, redirects, and reads. No proxy or cookie state.
    async with asyncio.timeout(8):
        connector = aiohttp.TCPConnector(resolver=PublicResolver(), use_dns_cache=False, force_close=True)
        async with aiohttp.ClientSession(connector=connector, trust_env=False,
                cookie_jar=aiohttp.DummyCookieJar(), auto_decompress=False,
                timeout=aiohttp.ClientTimeout(total=8), headers={
                    'User-Agent':'TrueOrNot/1.0 (source verification)',
                    'Accept':'text/html,text/plain', 'Accept-Encoding':'identity'}) as session:
            return await _read_url(session, raw, include_title=True)


def _generic_title(title, raw_url):
    if not isinstance(title, str) or not title.strip():
        return True
    host = (urlsplit(raw_url).hostname or '').lower().removeprefix('www.')
    normalized = title.strip().lower().rstrip('/')
    return normalized in {host, f'www.{host}', 'source', 'untitled'}


async def read_sources(state, *, reader=fetch_public_text):
    sources, texts = [], {}
    for source in state['sources'][:6]:
        item = {**source, 'accessStatus':'unavailable', 'retrievedAt':datetime.now(timezone.utc).isoformat()}
        try:
            result = await reader(source['url'])
            if isinstance(result, SourceReadResult):
                text, final_url, page_title = result.text, result.url, result.title
            else:
                text, final_url = result
                page_title = ''
            if not text.strip():
                raise ValueError('SOURCE_EMPTY')
            if page_title and _generic_title(item.get('title'), source['url']):
                item['title'] = page_title
            item.update(accessStatus='verified', resolvedUrl=final_url)
            texts[source['id']] = text
        except (ValueError, OSError, aiohttp.ClientError, TimeoutError):
            pass
        sources.append(item)
    return {'sources':sources, 'sourceTexts':texts}

