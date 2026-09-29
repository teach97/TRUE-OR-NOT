function backend(path: string) {
  const base = new URL(process.env.FACTLENS_BACKEND_URL || 'http://127.0.0.1:8010');
  if (base.protocol !== 'http:' || !['127.0.0.1','[::1]'].includes(base.hostname) || base.username || base.password || base.pathname !== '/' || base.search || base.hash) throw new Error('INVALID_BACKEND');
  return new URL(path, base).href;
}
function error(status: number, code: string, message: string) {
  return Response.json({code,message},{status,headers:{'Cache-Control':'no-store'}});
}
export async function POST(req: Request) {
  const url=new URL(req.url);
  const forwardedFor = req.headers.get('x-forwarded-for');
  const unsafeForwarding = forwardedFor !== null && !['127.0.0.1','::1','::ffff:127.0.0.1'].includes(forwardedFor);
  const host = req.headers.get('host') ?? '';
  const localHost = /^(localhost|127\.0\.0\.1|\[::1\])(?::[1-9][0-9]{0,4})?$/.test(host);
  const unsafeForwardedAuthority =
    (req.headers.has('x-forwarded-host') && req.headers.get('x-forwarded-host') !== host) ||
    (req.headers.has('x-forwarded-proto') && req.headers.get('x-forwarded-proto') !== 'http') ||
    (req.headers.has('x-forwarded-port') && req.headers.get('x-forwarded-port') !== (host.match(/:([0-9]+)$/)?.[1] ?? '80'));
  if(process.env.NODE_ENV==='production' || url.protocol!=='http:' || !['localhost','127.0.0.1','[::1]'].includes(url.hostname) || !localHost ||
    req.headers.get('origin')!==`http://${host}` || req.headers.has('forwarded') || unsafeForwarding || unsafeForwardedAuthority ||
    (req.headers.get('sec-fetch-site') && !['same-origin','none'].includes(req.headers.get('sec-fetch-site')!))) {
    return error(403,'LOCAL_ONLY','로컬 개발 환경의 동일 출처 요청만 허용됩니다.');
  }
  if(req.headers.get('content-type')?.split(';')[0].trim()!=='application/json')return error(400,'INVALID_REQUEST','JSON 입력이 필요합니다.');
  let body: unknown;
  try {
    if(Number(req.headers.get('content-length'))>20000)throw new Error('BODY_TOO_LARGE');
    const text = await req.text();
    if (text.length > 20000) throw new Error('BODY_TOO_LARGE');
    body=JSON.parse(text);
  }catch{return error(400,'INVALID_REQUEST','의도 파악 입력을 확인해 주세요.');}
  if(req.signal.aborted)return error(400,'CANCELLED','요청이 취소되었습니다.');
  try {
    const signal=AbortSignal.any([req.signal,AbortSignal.timeout(25000)]);
    const upstream=await fetch(backend('/api/intent'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal,redirect:'error',cache:'no-store'});
    if(!upstream.ok){await upstream.body?.cancel();return error(503,'INTENT_FAILED','의도 파악에 실패했습니다.');}
    const value=await upstream.json();
    if(!value || (value.action!=='verify'&&value.action!=='reply'))throw new Error('PROTOCOL');
    return Response.json({action:value.action,reply:value.reply??null,focus:value.focus??null},{headers:{'Cache-Control':'no-store'}});
  }catch{return error(503,'INTENT_FAILED','의도 파악에 실패했습니다.');}
}
