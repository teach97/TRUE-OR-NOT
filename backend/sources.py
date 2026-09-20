"""Bounded public-source reader. TLS validation stays enabled; no credentials."""
import asyncio
import ipaddress
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
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'noscript', 'template'}:
            self.hidden.append(tag)

    def handle_endtag(self, tag):
        if self.hidden and self.hidden[-1] == tag:
            self.hidden.pop()
        if not self.hidden:
            self.parts.append(' ')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def html_text(raw):
    parser = _TextParser()
    parser.feed(raw)
    return ' '.join(' '.join(parser.parts).split())


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


async def _read_url(session, raw):
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
            text = html_text(decoded) if media == 'text/html' else ' '.join(decoded.split())
            if not text:
                raise ValueError('SOURCE_EMPTY')
            return text[:18000], current
    raise ValueError('SOURCE_REDIRECT_LIMIT')


async def fetch_public_text(raw):
    # One deadline includes DNS, TLS, redirects, and reads. No proxy or cookie state.
    async with asyncio.timeout(8):
        connector = aiohttp.TCPConnector(resolver=PublicResolver(), use_dns_cache=False, force_close=True)
        async with aiohttp.ClientSession(connector=connector, trust_env=False,
                cookie_jar=aiohttp.DummyCookieJar(), auto_decompress=False,
                timeout=aiohttp.ClientTimeout(total=8), headers={
                    'User-Agent':'FactLens/1.0 (source verification)',
                    'Accept':'text/html,text/plain', 'Accept-Encoding':'identity'}) as session:
            return await _read_url(session, raw)


async def read_sources(state, *, reader=fetch_public_text):
    sources, texts = [], {}
    for source in state['sources'][:6]:
        item = {**source, 'accessStatus':'unavailable', 'retrievedAt':datetime.now(timezone.utc).isoformat()}
        try:
            text, final_url = await reader(source['url'])
            if not text.strip():
                raise ValueError('SOURCE_EMPTY')
            item.update(accessStatus='verified', resolvedUrl=final_url)
            texts[source['id']] = text
        except (ValueError, OSError, aiohttp.ClientError, TimeoutError):
            pass
        sources.append(item)
    return {'sources':sources, 'sourceTexts':texts}

