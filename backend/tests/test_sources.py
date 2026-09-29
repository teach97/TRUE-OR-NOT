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


def test_html_extracts_article_text_without_navigation_or_player_chrome():
    html = '''
        <header>사이트 머리글</header>
        <nav>홈 최신글 카테고리</nav>
        <main>
          <h1>AGI 2030 전망</h1>
          <aside>추천 기사 다른 글</aside>
          <article>
            <div class="article-body">
              <p>연구진은 2030년까지 범용 인공지능이 실현될 가능성을 검토했다.</p>
              <div id="video-player"><button>재생</button><span>00:00 / 12:00</span></div>
              <p>전문가들은 정의와 평가 기준에 따라 전망이 달라진다고 설명했다.</p>
            </div>
          </article>
        </main>
        <footer>개인정보 처리방침</footer>
    '''

    assert module().html_text(html) == (
        'AGI 2030 전망\n\n연구진은 2030년까지 범용 인공지능이 실현될 가능성을 검토했다.\n\n'
        '전문가들은 정의와 평가 기준에 따라 전망이 달라진다고 설명했다.'
    )


def test_html_preserves_paragraph_breaks_for_readable_source_text():
    assert module().html_text(
        '<article><p>첫 번째 문단이다.</p><p>두 번째 문단이다.</p></article>'
    ) == '첫 번째 문단이다.\n\n두 번째 문단이다.'
    assert module().html_text('<p>첫 줄<br>둘째 줄</p>') == '첫 줄\n둘째 줄'
    assert module().html_text('<div>위 내용</div><div>아래 내용</div>') == '위 내용\n\n아래 내용'


def test_html_fallback_still_excludes_menu_and_player_without_article_markers():
    html = '''
        <body>
          <div class="site-menu">전체 메뉴 로그인</div>
          <p>보고서는 공개된 실험 결과와 한계를 함께 설명한다.</p>
          <div class="video-player">재생 음소거 전체 화면</div>
        </body>
    '''

    assert module().html_text(html) == '보고서는 공개된 실험 결과와 한계를 함께 설명한다.'


def test_html_excludes_video_and_custom_player_elements():
    html = '''
        <article>
          <p>기사는 AGI 전망의 근거와 반대 의견을 설명한다.</p>
          <video controls>동영상 형식을 지원하지 않습니다.</video>
          <ytd-player>재생 일시중지 자막 설정</ytd-player>
        </article>
    '''

    assert module().html_text(html) == '기사는 AGI 전망의 근거와 반대 의견을 설명한다.'


def test_html_skips_table_of_contents_and_extracts_only_each_heading_body():
    html = '''
        <div id="toc">
          <span>목차 전용 안내</span>
          <a href="#s-4">4. 텔러린 앱</a>
          <a href="#s-5">5. 자선 활동</a>
        </div>
        <article class="article-content">
          <h2 id="s-4">4. 텔러린 앱</h2>
          <p>텔러린 앱은 여러 기능을 통합해 제공하는 서비스입니다.</p>
          <h3>서비스 구조</h3>
          <p>사용자는 앱에서 메시지와 일정을 관리할 수 있습니다.</p>
          <h2 id="s-5">5. 자선 활동</h2>
          <p>별도 단락은 텔러린 앱 설명에 포함되면 안 됩니다.</p>
        </article>
    '''

    text = module().html_text(html)
    sections = module().html_sections(html)
    app_section = next(section for section in sections if section['title'] == '4. 텔러린 앱')

    assert text.count('4. 텔러린 앱') == 1
    assert '목차 전용' not in text
    assert '별도 단락' in text
    assert '텔러린 앱은 여러 기능을 통합해 제공하는 서비스입니다.' in app_section['text']
    assert '서비스 구조' in app_section['text']
    assert '사용자는 앱에서 메시지와 일정을 관리할 수 있습니다.' in app_section['text']
    assert '별도 단락' not in app_section['text']
