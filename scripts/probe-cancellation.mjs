// Explicit test-only browser probe. Requires PLAYWRIGHT_MODULE (absolute module path).
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const {chromium} = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
const base = process.env.PROBE_FRONTEND;
const backend = process.env.PROBE_BACKEND;
const browser = await chromium.launch({headless:true,channel:'chrome'});
const observations = [];
const responses = [];
async function state() {return (await fetch(`${backend}/__test__/cancellation`)).json();}
async function waitCounts(expected) {
  const deadline = Date.now()+10000;
  let value;
  do {
    value = await state();
    if(Object.entries(expected).every(([k,v])=>value.counts[k]===v)) return value;
    await new Promise(resolve=>setTimeout(resolve,25));
  } while(Date.now()<deadline);
  assert.fail(`cleanup/start deadline: expected ${JSON.stringify(expected)}, observed ${JSON.stringify(value)}`);
}
try {
  const page = await browser.newPage();
  page.on('response',r=>{if(r.url()===`${base}/api/fact-check` && r.request().method()==='POST') responses.push(r.status());});
  await page.goto(base,{waitUntil:'networkidle',timeout:120000});
  const editor=page.locator('#document-text:visible');
  const start=page.getByRole('button',{name:'팩트 검증 시작',exact:true});
  const cancel=page.getByRole('button',{name:/취소|중단/});
  await editor.fill('TEST ONLY: deterministic cancellation probe, no factual verdict.');
  await page.locator('input[type=checkbox]:visible').check();
  await start.click();
  await waitCounts({started:1,adapter_started:1,active:1});
  // A second real same-origin browser request must be rejected while held.
  const busy=await page.evaluate(async()=>{
    const r=await fetch('/api/fact-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({text:'TEST ONLY overlap',focus:'',consent:true})});
    return {status:r.status,body:await r.json()};
  });
  assert.equal(busy.status,429);assert.equal(busy.body.code,'BUSY');
  observations.push({case:'overlap_rejected',...busy});
  await cancel.click();
  // Deliberately NO server polling/sleep before immediate UI retry.
  await start.click();
  const retried=await waitCounts({started:2,finalized:1,adapter_started:2,adapter_finalized:1,adapter_cancelled:1,active:1});
  observations.push({case:'cancel_immediate_retry',...retried});
  // Full document navigation: real Chromium disconnect, not synthetic AbortSignal.
  await page.goto('about:blank');
  const navigated=await waitCounts({started:2,finalized:2,adapter_finalized:2,adapter_cancelled:2,active:0});
  observations.push({case:'navigation_cleanup',...navigated});
  await page.goto(base,{waitUntil:'networkidle',timeout:120000});
  await editor.fill('TEST ONLY: retry after navigation.');
  await page.locator('input[type=checkbox]:visible').check();
  await start.click();
  await waitCounts({started:3,adapter_started:3,active:1});
  await cancel.click();
  const final=await waitCounts({started:3,finalized:3,adapter_finalized:3,adapter_cancelled:3,active:0});
  assert.equal(final.counts.max_active,1);
  assert.deepEqual(responses,[200,429,200,200]);
  observations.push({case:'navigation_retry_and_final_cancel',...final});
  console.log(JSON.stringify({passed:true,bundler:'webpack',responses,observations},null,2));
} catch(error) {
  console.error(JSON.stringify({passed:false,error:String(error),responses,observations,backend:await state()},null,2));
  process.exitCode=1;
} finally {await browser.close();}
