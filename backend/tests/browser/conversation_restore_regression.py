import json
import uuid
from playwright.sync_api import sync_playwright,expect

base='http://127.0.0.1:3017'
with sync_playwright() as runtime:
    browser=runtime.chromium.launch(channel='chrome',headless=True)
    context=browser.new_context(viewport={'width':1400,'height':1000})
    page=context.new_page();ids=[]
    headers={'origin':base}
    try:
        page.goto(base,wait_until='networkidle')
        assert context.request.post(base+'/api/conversations/session',headers=headers,data={'storageConsent':True}).status==200
        for title in ('Synthetic thread A','Synthetic thread B'):
            value=context.request.post(base+'/api/conversations',headers=headers,data={'storageConsent':True,'createRequestId':str(uuid.uuid4()),'title':title}).json();ids.append(value['id'])
        snapshot={'text':'Synthetic original A','focus':'','checkedAt':'2026-10-04T01:00:00Z','model':'jev-latest','reasoning':'max','scoreMode':'jev','claims':[{'id':'c1','quote':'Synthetic original A','start':0,'end':20,'kind':'fact','factScore':50,'scoreBand':'neutral','scoreLabel':'중립','verdictCode':'insufficient_evidence','verdict':'중립','tone':'normal','summary':'합성 결과입니다.','confirmed':[],'unresolved':[],'warnings':[],'evidenceIds':[]}],'sources':[],'evidence':[],'warnings':[],'answer':{'status':'insufficient_evidence','overview':None,'sections':[],'conclusion':None,'model':None,'reasoning':None}}
        snapshot['claims'][0]['tone']='neutral'
        assert context.request.post(base+'/api/conversations/'+ids[0]+'/messages',headers=headers,data={'storageConsent':True,'requestId':str(uuid.uuid4()),'role':'assistant','content':'Synthetic answer','status':'completed','snapshot':snapshot}).status==200
        page.reload(wait_until='networkidle')
        history=page.locator('.sidebar .conversation-history')
        history.get_by_role('button',name='Synthetic thread A',exact=True).click()
        expect(page.locator('.chat-thread')).to_contain_text('과거 검증 결과',timeout=15000)
        expect(page.locator('.chat-thread .jev-score-value')).to_contain_text('50')
        page.route('**/api/conversations/'+ids[1],lambda route:route.fulfill(status=503,content_type='application/json',body='{"code":"STORAGE_UNAVAILABLE"}'))
        history.get_by_role('button',name='Synthetic thread B',exact=True).click()
        expect(history.locator('.conversation-error')).to_be_visible(timeout=15000)
        captures=[]
        def gate(route):
            captures.append(route.request.post_data_json)
            route.fulfill(status=200,content_type='application/json',body=json.dumps({'action':'reply','reply':'합성 응답','focus':None}))
        page.route('**/api/intent',gate)
        editor=page.get_by_label('확인할 원문',exact=True);editor.fill('근거는?');editor.press('Enter')
        expect(page.locator('.chat-thread')).to_contain_text('합성 응답',timeout=15000)
        assert captures[0]['context']['previousText'] is None,'Previous conversation context leaked after failed restore'
        print({'switchRegressionPassed':True,'jevRestorePassed':True,'realProviderCalls':0})
    finally:
        for identifier in ids:context.request.delete(base+'/api/conversations/'+identifier,headers=headers)
        context.close();browser.close()
