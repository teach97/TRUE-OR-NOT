"""Public-source security tests; no external traffic."""
import asyncio
import importlib.util
import socket
import pytest


def module():
    assert importlib.util.find_spec("sources") is not None, "Source fetcher missing"
    import sources
    return sources


@pytest.mark.parametrize("ip", ["127.0.0.1", "10.0.0.1", "169.254.169.254", "100.64.0.1", "224.0.0.1", "::1", "::ffff:8.8.8.8", "2002:808:808::1", "2001:db8::1"])
def test_nonpublic_addresses_rejected(ip):
    assert not module().public_ip(ip)


def test_resolver_returns_only_validated_addresses(monkeypatch):
    m = module()
    async def run():
        loop = asyncio.get_running_loop()
        async def lookup(*args, **kwargs):
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))]
        monkeypatch.setattr(loop, "getaddrinfo", lookup)
        resolved = await m.PublicResolver().resolve("example.org", 443)
        assert resolved[0]["host"] == "8.8.8.8"
        async def mixed(*args, **kwargs):
            return await lookup() + [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1",443))]
        monkeypatch.setattr(loop, "getaddrinfo", mixed)
        with pytest.raises(ValueError):
            await m.PublicResolver().resolve("example.org",443)
    asyncio.run(run())


def test_html_excludes_noncontent():
    assert module().html_text('<p>Hello &amp; world</p><script>SECRET</script><style>HIDE</style><template>NO</template>') == 'Hello & world'
