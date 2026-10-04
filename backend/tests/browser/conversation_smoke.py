from playwright.sync_api import sync_playwright, expect

with sync_playwright() as runtime:
    browser=runtime.chromium.launch(channel='chrome',headless=True)
    context=browser.new_context(viewport={'width':1400,'height':1000})
    page=context.new_page()
    provider_requests=[]
    storage_responses=[]
    page.on('response',lambda response:storage_responses.append({'path':response.url.split('/api/conversations')[-1].split('?')[0],'status':response.status}) if '/api/conversations' in response.url else None)
    page.on('request',lambda request:provider_requests.append(request.url) if any(part in request.url for part in ('/api/intent','/api/fact-check')) and request.method=='POST' else None)
    try:
        page.goto('http://127.0.0.1:3017',wait_until='networkidle')
        history=page.locator('.sidebar .conversation-history')
        consent=history.get_by_label('이 브라우저에서 대화 저장')
        expect(consent).not_to_be_checked()
        consent.check()
        editor=page.get_by_label('확인할 원문',exact=True)
        title='너는 어떤 모델이야?'
        editor.fill(title);editor.press('Enter')
        entry=history.locator('li').filter(has=page.get_by_role('button',name=title,exact=True))
        try:expect(entry).to_have_count(1,timeout=15000)
        except Exception:
            print({'storageResponses':storage_responses,'storageErrorVisible':history.locator('.conversation-error').count(),'chatMessageCount':page.locator('.chat-message').count()})
            raise
        for _ in range(60):
            value=context.request.get('http://127.0.0.1:3017/api/conversations').json()
            identifier=value['items'][0]['id']
            stored=context.request.get('http://127.0.0.1:3017/api/conversations/'+identifier).json()
            if len(stored['messages'])==2:break
            page.wait_for_timeout(100)
        assert len(stored['messages'])==2
        assert stored['messages'][0]['role']=='user' and stored['messages'][1]['role']=='assistant'
        assert not provider_requests
        page.reload(wait_until='networkidle')
        expect(consent).not_to_be_checked()
        history.get_by_role('button',name=title,exact=True).click()
        expect(page.locator('.chat-thread')).to_contain_text('현재 Auto 모드입니다.',timeout=15000)
        consent.check()
        failed={'once':True}
        def fail_once(route):
            if failed['once']:
                failed['once']=False;route.fulfill(status=503,content_type='application/json',body='{"code":"STORAGE_UNAVAILABLE"}')
            else:route.continue_()
        page.route('**/api/conversations/*/messages',fail_once)
        editor.fill(title);editor.press('Enter')
        retry=history.get_by_role('button',name='저장만 재시도')
        expect(retry).to_be_visible(timeout=15000);retry.click()
        expect(retry).not_to_be_visible(timeout=15000)
        for _ in range(60):
            stored=context.request.get('http://127.0.0.1:3017/api/conversations/'+identifier).json()
            if len(stored['messages'])==4:break
            page.wait_for_timeout(100)
        assert len(stored['messages'])==4
        assert not provider_requests
        consent.uncheck();editor.fill(title);editor.press('Enter')
        page.wait_for_timeout(500)
        assert len(context.request.get('http://127.0.0.1:3017/api/conversations/'+identifier).json()['messages'])==4
        page.on('dialog',lambda dialog:dialog.accept())
        history.get_by_role('button',name=title+' 대화 삭제').click()
        expect(history.locator('li')).to_have_count(0,timeout=15000)
        assert context.request.get('http://127.0.0.1:3017/api/conversations/'+identifier).status==404
        page.set_viewport_size({'width':390,'height':844})
        expect(page.locator('.conversation-mobile')).to_be_visible()
        cookies=context.cookies()
        assert all(cookie['httpOnly'] and cookie['sameSite']=='Lax' for cookie in cookies if cookie['name']=='ton_session')
        print({'browserPassed':True,'providerPostRequests':len(provider_requests),'checks':['default off','save','reload','restore','continue','save-only retry','consent off','delete','mobile','HttpOnly']})
    finally:
        context.close();browser.close()
