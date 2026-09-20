// TEST ONLY: real process outage controlled by the Python owner via scratch IPC.
import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const {chromium}=await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
const base=process.env.PROBE_FRONTEND, backend=process.env.PROBE_BACKEND, dir=process.env.PROBE_EVIDENCE_DIR;
const browser=await chromium.launch({headless:true,channel:'chrome'});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const responses=[],observations=[];
async function control(action) {
  await writeFile(`${dir}/${action}.request`,'TEST ONLY');
  const deadline=Date.now()+30000;
  while(Date.now()<deadline) {
    try {return JSON.parse(await readFile(`${dir}/${action}.done`,'utf8'));}
    catch(error) {if(error.code!=='ENOENT') throw error;}
    await new Promise(resolve=>setTimeout(resolve,50));
  }
  throw new Error(`Process owner did not acknowledge ${action}`);
}
try {
  page.on('response',r=>{if(r.url()===`${base}/api/fact-check` && r.request().method()==='POST') responses.push(r.status());});
  await page.goto(base,{waitUntil:'networkidle',timeout:120000});
  const documentToken=await page.evaluate(()=>window.__restartProbeToken=crypto.randomUUID());
  const input=page.locator('#document-text:visible');
  const text='TEST ONLY first claim | TEST ONLY second claim';
  await input.fill(text);
  await page.locator('input[type=checkbox]:visible').check();
  const start=page.getByRole('button',{name:'팩트 검증 시작',exact:true});
  const stopped=await control('stop');
  assert.equal(stopped.portClosed,true);
  observations.push({case:'actual_process_stopped',...stopped});
  // Two immediate UI attempts while down also prove the failed fetch releases BUSY.
  for(let attempt=0;attempt<2;attempt++) {
    const responsePromise=page.waitForResponse(r=>r.url()===`${base}/api/fact-check` && r.request().method()==='POST');
    await start.click();
    const response=await responsePromise;
    assert.equal(response.status(),503);
    assert.deepEqual(await response.json(),{code:'BACKEND_UNAVAILABLE',message:'검증 백엔드에 연결할 수 없습니다.'});
    await page.getByRole('status').filter({hasText:'검증 실패: 검증 백엔드에 연결할 수 없습니다.'}).waitFor();
    assert.equal(await start.isEnabled(),true);
    assert.equal(await page.getByRole('button',{name:'결과 내보내기'}).isEnabled(),false);
    assert.equal(await page.locator('.claim-card').count(),0);
    assert.ok(!(await page.locator('body').innerText()).includes('TEST ONLY summary'));
    observations.push({case:'connection_error_no_verdict',attempt,notice:await page.getByRole('status').innerText()});
  }
  await page.screenshot({path:`${dir}/network-error.png`,fullPage:true});
  const restarted=await control('restart');
  assert.notEqual(restarted.pid,stopped.pid);
  observations.push({case:'actual_process_restarted',...restarted});
  const fixture=await (await fetch(`${backend}/__test__/recover`,{method:'POST'})).json();
  assert.equal(fixture.testOnly,true);
  assert.deepEqual(fixture.attempts,[]);
  // No reload, status refresh, new context or replacement page between failure/retry.
  for(let attempt=0;attempt<2;attempt++) {
    await start.click();
    await page.getByRole('status').filter({hasText:'검증이 완료되었습니다'}).waitFor();
    assert.equal(await page.getByRole('button',{name:'결과 내보내기'}).isEnabled(),true);
    const state=await (await fetch(`${backend}/__test__/recovery`)).json();
    assert.deepEqual(state.attempts,Array(attempt+1).fill('success'));
    observations.push({case:'same_page_retry_success',attempt,backend:state});
  }
  assert.equal(await page.evaluate(()=>window.__restartProbeToken),documentToken);
  assert.equal(await input.inputValue(),text);
  assert.equal(await page.locator('input[type=checkbox]:visible').isChecked(),true);
  assert.deepEqual(responses,[503,503,200,200]);
  await page.screenshot({path:`${dir}/restart-success.png`,fullPage:true});
  await browser.close();
  console.log(JSON.stringify({passed:true,bundler:'webpack',browserClosed:true,sameDocument:true,responses,observations},null,2));
} catch(error) {
  await page.screenshot({path:`${dir}/failed-assertion.png`,fullPage:true});
  await writeFile(`${dir}/failed-dom.txt`,await page.locator('body').innerText());
  console.error(JSON.stringify({passed:false,error:String(error),responses,observations},null,2));
  process.exitCode=1;
} finally {await browser.close();}
