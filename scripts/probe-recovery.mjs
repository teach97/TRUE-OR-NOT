// TEST ONLY fixtures via real Next proxy/FastAPI; no route interception.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const {chromium} = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
const base=process.env.PROBE_FRONTEND, backend=process.env.PROBE_BACKEND, dir=process.env.PROBE_EVIDENCE_DIR;
const browser=await chromium.launch({headless:true,channel:'chrome'});
const observations=[],responses=[];
const page=await browser.newPage({viewport:{width:1440,height:1000}});
try {
  page.on('response',r=>{if(r.url()===`${base}/api/fact-check` && r.request().method()==='POST') responses.push(r.status());});
  await page.goto(base,{waitUntil:'networkidle',timeout:120000});
  await page.locator('#document-text:visible').fill('TEST ONLY first claim | TEST ONLY second claim');
  await page.locator('input[type=checkbox]:visible').check();
  const start=page.getByRole('button',{name:'팩트 검증 시작',exact:true});
  await start.click();
  await page.getByRole('status').filter({hasText:'검증 실패:'}).waitFor();
  assert.equal(await page.getByRole('button',{name:'결과 내보내기'}).isEnabled(),false);
  assert.equal(await start.isEnabled(),true);
  assert.ok(!(await page.locator('body').innerText()).includes('TEST_ONLY_PRIVATE_DIAGNOSTIC'));
  await page.screenshot({path:`${dir}/failure.png`,fullPage:true});
  observations.push({case:'backend_failure',notice:await page.getByRole('status').innerText()});
  await fetch(`${backend}/__test__/recover`,{method:'POST'});
  assert.equal((await (await fetch(`${backend}/__test__/recovery`)).json()).mode,'success');
  await start.click();
  await page.getByRole('status').filter({hasText:'검증이 완료되었습니다'}).waitFor();
  observations.push({case:'ui_retry_success',backend:await (await fetch(`${backend}/__test__/recovery`)).json()});
  await page.locator('.claim-card').filter({hasText:'TEST ONLY first claim'}).click();
  const details=page.locator('.evidence-panel .liquid-panel-live:visible');
  await details.getByText('TEST ONLY evidence quotation, not a factual finding.',{exact:false}).waitFor({timeout:10000});
  assert.equal(await details.getByRole('link',{name:'TEST ONLY source'}).getAttribute('href'),'https://example.org/test-only-source');
  assert.ok((await details.innerText()).includes('TEST ONLY uncertainty 0'));
  assert.ok((await details.innerText()).includes('TEST ONLY warning 0'));
  await page.screenshot({path:`${dir}/details.png`,fullPage:true});
  observations.push({case:'first_claim_details',text:await details.innerText()});
  await page.locator('.claim-card').filter({hasText:'TEST ONLY second claim'}).click();
  assert.ok((await details.innerText()).includes('TEST ONLY uncertainty 1'));
  assert.ok(!(await details.innerText()).includes('TEST ONLY evidence quotation'));
  assert.ok((await details.innerText()).includes('비교할 근거가 없습니다'));
  observations.push({case:'second_claim_no_evidence',text:await details.innerText()});
  assert.deepEqual(responses,[200,200]);
  console.log(JSON.stringify({passed:true,bundler:'webpack',responses,observations},null,2));
} catch(error) {
  await page.screenshot({path:`${dir}/failed-assertion.png`,fullPage:true});
  await writeFile(`${dir}/failed-dom.txt`,await page.locator('body').innerText());
  console.error(JSON.stringify({passed:false,error:String(error),responses,observations},null,2));
  process.exitCode=1;
} finally {await browser.close();}
