// @ts-ignore -- explicit extension also supports Node 24's native TypeScript test runner.
import { limitedText, runAgent, validateRequest } from '../../lib/server/agent.ts';
import type { AgentStatus, FactCheckRequest } from '../../lib/fact-check-contract';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
const headers = {'Cache-Control':'no-store'};
// Process-local concurrency cap is not a public-service rate limiter.
let active = 0;
export async function GET() {
  const status: AgentStatus = {configured:Boolean(process.env.OPENAI_API_KEY),model:'gpt-5.6-luna',reasoning:'max',webSearch:true};
  return Response.json(status,{headers});
}
function error(status: number, code: string, message: string) {
  return Response.json({code,message},{status,headers});
}
export async function POST(req: Request) {
  const url=new URL(req.url);
  // No paid unauthenticated deployment: production is disabled. Run development bound to loopback,
  // not 0.0.0.0. Host/Origin checks alone cannot authenticate arbitrary non-browser remote clients.
  if(process.env.NODE_ENV==='production' || !['localhost','127.0.0.1','[::1]'].includes(url.hostname) ||
    req.headers.get('origin')!==url.origin || req.headers.has('forwarded') || req.headers.has('x-forwarded-for') ||
    (req.headers.get('sec-fetch-site') && !['same-origin','none'].includes(req.headers.get('sec-fetch-site')!))) {
    return error(403,'LOCAL_ONLY','로컬 개발 환경의 동일 출처 요청만 허용됩니다.');
  }
  if(req.headers.get('content-type')?.split(';')[0].trim()!=='application/json')return error(400,'INVALID_REQUEST','JSON 입력이 필요합니다.');
  let input:FactCheckRequest;
  try {
    const signal=AbortSignal.any([req.signal,AbortSignal.timeout(5000)]);
    if(Number(req.headers.get('content-length'))>80000)throw new Error('BODY_TOO_LARGE');
    input=validateRequest(JSON.parse(await limitedText(new Response(req.body),80000,signal)));
  } catch {return error(400,'INVALID_REQUEST','본문, 확인 요청 길이 및 외부 전송 동의를 확인해 주세요.');}
  const key=process.env.OPENAI_API_KEY;
  if(!key)return error(503,'NOT_CONFIGURED','서버의 OpenAI API 설정이 필요합니다.');
  if(active>=1)return error(429,'BUSY','진행 중인 검증이 있습니다. 완료 후 다시 시도해 주세요.');
  if(req.signal.aborted)return error(400,'CANCELLED','요청이 취소되었습니다.');
  active++;
  const controller=new AbortController();
  let closed=false,released=false;
  const release=()=>{if(!released){released=true;active--;req.signal.removeEventListener('abort',abort);}};
  const abort=()=>controller.abort();
  req.signal.addEventListener('abort',abort,{once:true});
  const encoder=new TextEncoder();
  const stream=new ReadableStream<Uint8Array>({
    async start(sink) {
      try {
        for await(const event of runAgent(input,key,controller.signal)) {
          if(closed||controller.signal.aborted)break;
          sink.enqueue(encoder.encode(`${JSON.stringify(event)}\n`));
        }
      } catch {
        if(!closed&&!controller.signal.aborted)sink.enqueue(encoder.encode(`${JSON.stringify({type:'error',code:'AGENT_FAILED',message:'검증을 완료하지 못했습니다.'})}\n`));
      } finally {if(!closed){closed=true;sink.close();}release();}
    },
    cancel() {closed=true;controller.abort();release();}
  });
  return new Response(stream,{headers:{...headers,'Content-Type':'application/x-ndjson; charset=utf-8','X-Accel-Buffering':'no','X-Content-Type-Options':'nosniff'}});
}
