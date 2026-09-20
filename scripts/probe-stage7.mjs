// Offline final regression: real Chrome -> default Next Turbopack -> test-only FastAPI.
import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const {chromium}=await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
const base=process.env.PROBE_FRONTEND, backend=process.env.PROBE_BACKEND, dir=process.env.PROBE_EVIDENCE_DIR;
const browser=await chromium.launch({headless:true,channel:'chrome'});
const observations=[], responses=[], errors=[];
let current;
async function noOverflow(page, label) {
  const size=await page.evaluate(()=>({viewport:document.documentElement.clientWidth,document:document.documentElement.scrollWidth,body:document.body.scrollWidth}));
  assert.ok(size.document<=size.viewport && size.body<=size.viewport, `${label}: ${JSON.stringify(size)}`);
  observations.push({case:label,...size});
}
async function exportJson(page, name, file) {
  const pending=page.waitForEvent('download');
  await page.getByRole('button',{name,exact:true}).click();
  const download=await pending;
  await download.saveAs(`${dir}/${file}`);
  return JSON.parse(await readFile(`${dir}/${file}`,'utf8'));
}
try {
  assert.equal((await fetch(`${backend}/__test__/recover`,{method:'POST'})).status,200);
  for (const [label,viewport] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]]) {
    const context=await browser.newContext({viewport,reducedMotion:'reduce',isMobile:label==='mobile',hasTouch:label==='mobile'});
    const page=await context.newPage(); current=page;
    page.on('pageerror',e=>errors.push({label,error:String(e)}));
    page.on('response',r=>{if(r.url()===`${base}/api/fact-check`&&r.request().method()==='POST')responses.push({label,status:r.status()});});
    await page.goto(base,{waitUntil:'networkidle',timeout:120000});
    await noOverflow(page,`${label}_initial`);
    await page.locator('#document-text:visible').fill('TEST ONLY first claim | TEST ONLY second claim');
    await page.locator('input[type=checkbox]:visible').check();
    await page.getByRole('button',{name:'팩트 검증 시작',exact:true}).click();
    await page.getByRole('status').filter({hasText:'검증이 완료되었습니다'}).waitFor();
    const cards=page.locator('.claim-card');
    assert.equal(await cards.count(),2);
    await cards.filter({hasText:'TEST ONLY first claim'}).click();
    if(label==='mobile')await page.getByRole('group',{name:'검토 화면 선택'}).getByRole('button',{name:'출처',exact:true}).click();
    const details=page.locator('.evidence-panel .liquid-panel-live:visible');
    await details.getByText('TEST ONLY evidence quotation, not a factual finding.',{exact:false}).waitFor();
    assert.equal(await details.getByRole('link',{name:'TEST ONLY source',exact:true}).getAttribute('href'),'https://example.org/test-only-source');
    assert.ok((await details.innerText()).includes('TEST ONLY uncertainty 0'));
    await noOverflow(page,`${label}_live_evidence`);
    await page.screenshot({path:`${dir}/${label}-result.png`,fullPage:true});
    if(label==='mobile')await page.getByRole('group',{name:'검토 화면 선택'}).getByRole('button',{name:'결과',exact:true}).click();
    await cards.filter({hasText:'TEST ONLY second claim'}).click();
    if(label==='mobile')await page.getByRole('group',{name:'검토 화면 선택'}).getByRole('button',{name:'출처',exact:true}).click();
    assert.ok((await details.innerText()).includes('TEST ONLY uncertainty 1'));
    assert.ok((await details.innerText()).includes('비교할 근거가 없습니다'));
    assert.ok(!(await details.innerText()).includes('TEST ONLY evidence quotation'));
    const result=await exportJson(page,'결과 내보내기',`${label}-result.json`);
    assert.equal(result.demo,false); assert.equal(result.claims.length,2);
    assert.equal(result.evidence[0].claimId,result.claims[0].id);
    assert.equal(result.evidence[0].sourceId,result.sources[0].id);
    assert.equal(result.evidence[0].quoteVerified,true);
    observations.push({case:`${label}_result_selection_export`,claims:result.claims.length,sources:result.sources.length,evidence:result.evidence.length});
    await page.screenshot({path:`${dir}/${label}-second-claim.png`,fullPage:true});
    await context.close();
    // Fresh document: demo has no prior API result or consent state to rely on.
    const demoContext=await browser.newContext({viewport,reducedMotion:'reduce',isMobile:label==='mobile',hasTouch:label==='mobile'});
    const demo=await demoContext.newPage(); current=demo;
    demo.on('pageerror',e=>errors.push({label:`${label}_demo`,error:String(e)}));
    const before=await (await fetch(`${backend}/__test__/recovery`)).json();
    const demoPosts=[];
    demo.on('request',r=>{if(r.method()==='POST' && r.url()===`${base}/api/fact-check`)demoPosts.push(r.url());});
    await demo.goto(base,{waitUntil:'networkidle',timeout:120000});
    await demo.getByRole('button',{name:'가상 도시의 문화 행사'}).click();
    const demoCards=demo.locator('.claim-card');
    assert.equal(await demoCards.count(),3);
    await demoCards.nth(0).click();
    if(label==='mobile')await demo.getByRole('group',{name:'검토 화면 선택'}).getByRole('button',{name:'출처',exact:true}).click();
    const demoDetails=demo.locator('.evidence-panel .liquid-panel-live:visible');
    assert.equal(await demoDetails.locator('.source-card').count(),2);
    await noOverflow(demo,`${label}_demo_evidence`);
    await demo.screenshot({path:`${dir}/${label}-demo.png`,fullPage:true});
    if(label==='mobile')await demo.getByRole('group',{name:'검토 화면 선택'}).getByRole('button',{name:'결과',exact:true}).click();
    await demoCards.nth(2).click();
    if(label==='mobile')await demo.getByRole('group',{name:'검토 화면 선택'}).getByRole('button',{name:'출처',exact:true}).click();
    await demoDetails.getByRole('heading',{name:'비교할 근거가 없습니다'}).waitFor();
    const sample=await exportJson(demo,'예시 내보내기',`${label}-demo.json`);
    assert.equal(sample.demo,true); assert.equal(sample.claims.length,3);
    assert.ok(sample.disclaimer.includes('실제 검증 결과가 아닙니다'));
    assert.ok(!JSON.stringify(sample).includes('TEST ONLY'));
    assert.deepEqual(demoPosts,[]);
    const after=await (await fetch(`${backend}/__test__/recovery`)).json();
    assert.deepEqual(after.attempts,before.attempts);
    observations.push({case:`${label}_independent_demo`,posts:demoPosts,claims:sample.claims.length,backendAttempts:after.attempts.length});
    await demoContext.close();
  }
  assert.deepEqual(responses.map(r=>r.status),[200,200]);
  assert.deepEqual(errors,[]);
  const output={passed:true,bundler:'default Turbopack (scratch root adjusted)',responses,errors,observations};
  await writeFile(`${dir}/browser-evidence.json`,JSON.stringify(output,null,2));
  console.log(JSON.stringify(output,null,2));
} catch(error) {
  if(current&&!current.isClosed()) {
    await current.screenshot({path:`${dir}/failed-assertion.png`,fullPage:true});
    await writeFile(`${dir}/failed-dom.txt`,await current.locator('body').innerText());
  }
  const output={passed:false,error:String(error),stack:error.stack,responses,errors,observations};
  await writeFile(`${dir}/browser-evidence.json`,JSON.stringify(output,null,2));
  console.error(JSON.stringify(output,null,2)); process.exitCode=1;
} finally {await browser.close();}
