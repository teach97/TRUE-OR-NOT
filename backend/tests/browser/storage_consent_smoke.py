"""저장 선택 위치와 확정·취소를 검증합니다. 모든 API는 모의 응답으로 처리합니다."""
import json
import os
from urllib.parse import urlparse
from uuid import uuid4

from playwright.sync_api import Error, expect, sync_playwright

BASE = os.environ.get('CONSENT_TEST_URL', 'http://127.0.0.1:3000')
LABEL = '이 브라우저에서 대화 저장'
STAMP = '2026-10-05T00:00:00Z'

with sync_playwright() as runtime:
    browser = runtime.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(viewport={'width': 1400, 'height': 1000})
    writes, provider_posts, rows, saved = [], [], [], []

    def intercept(route):
        request = route.request
        if not request.url.startswith(BASE + '/'):
            route.abort()
            return
        path = urlparse(request.url).path
        if not path.startswith('/api/'):
            route.continue_()
            return
        if path.startswith('/api/conversations'):
            if request.method == 'GET':
                value = {'items': rows, 'nextCursor': None}
            else:
                body = request.post_data_json
                assert body['storageConsent'] is True
                writes.append((path, body))
                if path.endswith('/session'):
                    value = {'sessionAvailable': True}
                elif path == '/api/conversations':
                    value = {'id': str(uuid4()), 'title': body['title'], 'createdAt': STAMP, 'updatedAt': STAMP}
                    rows.append(value)
                elif path.endswith('/messages'):
                    value = {'id': str(uuid4()), 'sequence': len(saved) + 1, 'createdAt': STAMP,
                             'requestId': body['requestId'], 'role': body['role'], 'content': body['content'],
                             'status': body['status'], 'snapshot': body.get('snapshot')}
                    saved.append(value)
                else:
                    raise AssertionError(f'Unexpected storage request: {path}')
        elif request.method == 'GET':
            value = {'configured': True, 'jevConfigured': True, 'model': 'gpt-6-luna',
                     'modelOptions': [{'id': 'gpt-6-luna', 'configured': True}]}
        else:
            body = request.post_data_json
            assert path == '/api/intent' and body['consent'] is True
            provider_posts.append(body)
            value = {'action': 'reply', 'reply': '합성 저장 시험 답변입니다.', 'focus': None}
        route.fulfill(content_type='application/json', body=json.dumps(value))

    context.route('**/*', intercept)
    page = context.new_page()

    def send(text):
        page.get_by_label('확인할 원문', exact=True).fill(text)
        page.get_by_role('button', name='팩트 검증 시작', exact=True).click()

    def settings():
        page.locator('.page-footer').get_by_role('button', name='대화 저장 설정', exact=True).click()
        return page.get_by_role('dialog', name='대화 저장 설정', exact=True)

    try:
        # 같은 꺼짐 값을 확정해도 진행 중인 기록 조회를 취소하지 않아야 합니다.
        for kind in ['external', 'storage']:
            slow = context.new_page()
            slow.add_init_script("localStorage.removeItem('ton_external_consent')")
            held = []
            slow.route('**/api/conversations', lambda route: held.append(route))
            slow.goto(BASE, wait_until='domcontentloaded')
            if kind == 'external':
                slow.get_by_role('button', name='외부 전송 안내', exact=True).click()
                slow_dialog = slow.get_by_role('dialog', name='외부 서비스 전송 동의', exact=True)
                slow_dialog.get_by_role('button', name='동의하고 시작', exact=True).click()
            else:
                slow.locator('.page-footer').get_by_role('button', name='대화 저장 설정', exact=True).click()
                slow_dialog = slow.get_by_role('dialog', name='대화 저장 설정', exact=True)
                slow_dialog.get_by_role('button', name='설정 저장', exact=True).click()
            assert held
            delayed_history = {'items': [{'id': str(uuid4()), 'title': '지연된 기존 대화',
                                          'createdAt': STAMP, 'updatedAt': STAMP}], 'nextCursor': None}
            for held_route in held:
                try:
                    held_route.fulfill(content_type='application/json', body=json.dumps(delayed_history))
                except Error:
                    pass  # 개발 모드의 최초 effect 정리에서 취소한 요청은 다시 응답할 수 없습니다.
            expect(slow.locator('.sidebar .conversation-history')).to_contain_text('지연된 기존 대화')
            slow.evaluate("localStorage.removeItem('ton_external_consent')")
            slow.close()
        page.goto(BASE, wait_until='networkidle')
        for history in page.locator('.conversation-history').all():
            expect(history.get_by_label(LABEL)).to_have_count(0)
            expect(history.get_by_text('저장·개인정보 안내', exact=True)).to_have_count(0)
        send('저장 선택을 시험합니다.')
        first = page.get_by_role('dialog', name='외부 서비스 전송 동의', exact=True)
        expect(first).to_be_visible()
        expect(first.get_by_label(LABEL)).not_to_be_checked()
        first.get_by_label(LABEL).check()
        assert writes == [] and provider_posts == []
        first.get_by_role('button', name='동의하지 않음', exact=True).click()
        assert page.evaluate("localStorage.getItem('ton_storage_consent')") is None
        expect(page.get_by_label('확인할 원문', exact=True)).to_have_value('저장 선택을 시험합니다.')
        setting = settings()
        expect(setting.get_by_label(LABEL)).not_to_be_checked()
        setting.get_by_role('button', name='취소', exact=True).click()
        send('저장 없이 시험합니다.')
        first.get_by_role('button', name='동의하고 시작', exact=True).click()
        expect(page.locator('.chat-thread')).to_contain_text('합성 저장 시험 답변입니다.')
        assert writes == []

        setting = settings()
        setting.get_by_label(LABEL).check()
        setting.get_by_role('button', name='대화상자 닫기', exact=True).click()
        assert page.evaluate("localStorage.getItem('ton_storage_consent')") is None
        setting = settings()
        expect(setting.get_by_label(LABEL)).not_to_be_checked()
        setting.get_by_label(LABEL).check()
        setting.get_by_role('button', name='설정 저장', exact=True).click()
        assert writes == [], '저장 설정을 켜는 것만으로 과거 메시지를 저장하지 않습니다.'
        send('선택 이후 저장할 메시지입니다.')
        expect(page.locator('.sidebar .conversation-history li')).to_have_count(1)
        expect(page.locator('.chat-thread')).to_contain_text('합성 저장 시험 답변입니다.')
        page.wait_for_function('!document.querySelector(".chat-loader-row")')
        for _ in range(100):
            if len(saved) == 2:
                break
            page.wait_for_timeout(20)
        assert len(saved) == 2 and saved[0]['content'] == '선택 이후 저장할 메시지입니다.'
        assert [item['role'] for item in saved] == ['user', 'assistant']
        before = len(writes)
        setting = settings()
        expect(setting.get_by_label(LABEL)).to_be_checked()
        setting.get_by_label(LABEL).uncheck()
        setting.get_by_role('button', name='취소', exact=True).click()
        setting = settings()
        expect(setting.get_by_label(LABEL)).to_be_checked()
        setting.get_by_label(LABEL).uncheck()
        setting.get_by_role('button', name='설정 저장', exact=True).click()
        send('저장 해제 이후 메시지입니다.')
        expect(page.locator('.chat-thread')).to_contain_text('저장 해제 이후 메시지입니다.')
        expect(page.locator('.chat-loader-row')).not_to_be_visible()
        assert len(writes) == before
        expect(page.locator('.sidebar .conversation-history li')).to_have_count(1)

        # 외부 전송 동의가 이미 있어도 저장 설정을 독립적으로 변경할 수 있습니다.
        page.get_by_role('button', name='외부 전송 동의 철회', exact=True).click()
        saved_before_first = len(saved)
        send('최초 창에서 저장을 선택합니다.')
        first.get_by_label(LABEL).check()
        first.get_by_role('button', name='동의하고 시작', exact=True).click()
        expect(page.locator('.chat-loader-row')).not_to_be_visible()
        for _ in range(100):
            if len(saved) == saved_before_first + 2:
                break
            page.wait_for_timeout(20)
        assert [(item['role'], item['content']) for item in saved[saved_before_first:]] == [
            ('user', '최초 창에서 저장을 선택합니다.'), ('assistant', '합성 저장 시험 답변입니다.'),
        ], '최초 창의 저장 선택은 보류한 요청을 재제출하기 전에 적용해야 합니다.'
        setting = settings()
        expect(setting.get_by_label(LABEL)).to_be_checked()
        setting.get_by_role('button', name='취소', exact=True).click()

        policy = page.locator('.page-footer').get_by_role('link', name='개인정보 처리방침', exact=True)
        expect(policy).to_have_attribute('href', '/privacy#conversation-storage')
        with context.expect_page() as opened:
            policy.click()
        notice = opened.value
        notice.wait_for_load_state('networkidle')
        section = notice.locator('#conversation-storage')
        expect(section).to_be_visible()
        expect(section).to_contain_text('쿠키 삭제·만료')
        expect(section).to_contain_text('자동 삭제')
        expect(section).to_contain_text('대화 저장 설정')
        notice.close()
        page.set_viewport_size({'width': 390, 'height': 844})
        setting = settings()
        expect(setting.get_by_label(LABEL)).to_be_checked()
        assert setting.evaluate('element => {const b=element.getBoundingClientRect(); return b.left>=0 && b.right<=innerWidth && element.scrollWidth<=element.clientWidth;}')
        setting.get_by_role('button', name='취소', exact=True).click()
        page.reload(wait_until='networkidle')
        setting = settings()
        expect(setting.get_by_label(LABEL)).to_be_checked()
        setting.get_by_role('button', name='취소', exact=True).click()
        saved_before_reload = len(saved)
        send('새로고침 이후에도 저장합니다.')
        expect(page.locator('.chat-loader-row')).not_to_be_visible()
        for _ in range(100):
            if len(saved) == saved_before_reload + 2:
                break
            page.wait_for_timeout(20)
        assert [(item['role'], item['content']) for item in saved[saved_before_reload:]] == [
            ('user', '새로고침 이후에도 저장합니다.'), ('assistant', '합성 저장 시험 답변입니다.'),
        ]
        setting = settings()
        setting.get_by_label(LABEL).uncheck()
        setting.get_by_role('button', name='취소', exact=True).click()
        page.reload(wait_until='networkidle')
        setting = settings()
        expect(setting.get_by_label(LABEL)).to_be_checked()
        setting.get_by_label(LABEL).uncheck()
        setting.get_by_role('button', name='설정 저장', exact=True).click()
        page.reload(wait_until='networkidle')
        setting = settings()
        expect(setting.get_by_label(LABEL)).not_to_be_checked()
        setting.get_by_role('button', name='취소', exact=True).click()
        writes_before_disabled = len(writes)
        send('새로고침 이후 저장을 끈 상태입니다.')
        expect(page.locator('.chat-loader-row')).not_to_be_visible()
        assert len(writes) == writes_before_disabled

        setting = settings()
        setting.get_by_label(LABEL).check()
        setting.get_by_role('button', name='설정 저장', exact=True).click()
        other = context.new_page()
        other.goto(BASE, wait_until='networkidle')
        other.locator('.page-footer').get_by_role('button', name='대화 저장 설정', exact=True).click()
        other_setting = other.get_by_role('dialog', name='대화 저장 설정', exact=True)
        expect(other_setting.get_by_label(LABEL)).to_be_checked()
        other_setting.get_by_label(LABEL).uncheck()
        other_setting.get_by_role('button', name='설정 저장', exact=True).click()
        writes_before_tab = len(writes)
        send('다른 탭에서 저장을 껐습니다.')
        expect(page.locator('.chat-loader-row')).not_to_be_visible()
        assert len(writes) == writes_before_tab
        setting = settings()
        expect(setting.get_by_label(LABEL)).not_to_be_checked()
        setting.get_by_label(LABEL).check()
        setting.get_by_role('button', name='설정 저장', exact=True).click()
        other.evaluate('localStorage.clear()')
        expect(page.get_by_role('button', name='외부 전송 안내', exact=True)).to_be_visible()
        setting = settings()
        expect(setting.get_by_label(LABEL)).not_to_be_checked()
        setting.get_by_role('button', name='취소', exact=True).click()
        other.evaluate("localStorage.setItem('ton_storage_consent', 'old-policy')")
        page.reload(wait_until='networkidle')
        setting = settings()
        expect(setting.get_by_label(LABEL)).not_to_be_checked()
        setting.get_by_role('button', name='취소', exact=True).click()
        # 저장 해제 기록을 지우지 못한 경고는 확정 직후에도 화면에 남아야 합니다.
        setting = settings()
        setting.get_by_label(LABEL).check()
        setting.get_by_role('button', name='설정 저장', exact=True).click()
        page.evaluate("() => {Storage.prototype.removeItem = function() {throw new DOMException('blocked', 'SecurityError');};}")
        setting = settings()
        setting.get_by_label(LABEL).uncheck()
        setting.get_by_role('button', name='설정 저장', exact=True).click()
        expect(setting).not_to_be_visible()
        expect(page.locator('p[role="alert"]')).to_contain_text('현재 화면에서만 적용')
        page.reload(wait_until='networkidle')
        setting = settings()
        expect(setting.get_by_label(LABEL)).to_be_checked()
        setting.get_by_label(LABEL).uncheck()
        setting.get_by_role('button', name='설정 저장', exact=True).click()
        expect(page.locator('p[role="alert"]')).not_to_be_visible()
        page.reload(wait_until='networkidle')
        setting = settings()
        expect(setting.get_by_label(LABEL)).not_to_be_checked()
        setting.get_by_role('button', name='취소', exact=True).click()
        other.close()

        page.add_init_script("Object.defineProperty(window, 'localStorage', {get() {throw new DOMException('blocked', 'SecurityError');}})")
        page.reload(wait_until='networkidle')
        setting = settings()
        expect(setting.get_by_label(LABEL)).not_to_be_checked()
        setting.get_by_label(LABEL).check()
        setting.get_by_role('button', name='설정 저장', exact=True).click()
        expect(page.locator('p[role="alert"]')).to_contain_text('현재 화면에서만 적용')
        setting = settings()
        expect(setting.get_by_label(LABEL)).to_be_checked()
        expect(setting.get_by_role('status')).to_contain_text('현재 화면에서만 적용')
        setting.get_by_role('button', name='취소', exact=True).click()
        page.reload(wait_until='networkidle')
        setting = settings()
        expect(setting.get_by_label(LABEL)).not_to_be_checked()
        print({'storageConsentPassed': True, 'realProviderCalls': 0, 'realDBCalls': 0,
               'checks': ['sidebar removal', 'default off', 'reject', 'close', 'confirm', 'future only',
                          'cancel preserves', 'disable preserves history', 'first dialog opt-in',
                          'footer policy anchor', 'mobile settings', 'reload preserves consent',
                          'unchanged external consent preserves slow history', 'unchanged storage preserves slow history',
                          'save after reload', 'cancel preserves persisted choice', 'disabled choice survives reload',
                          'same-browser new tab', 'cross-tab disable', 'site data clear', 'old receipt rejected',
                          'failed revoke warning remains visible and recovers',
                          'blocked storage warning and page-only fallback']})
    finally:
        context.close()
        browser.close()
