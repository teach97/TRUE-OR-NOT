import { lookup } from 'node:dns/promises';
import { isIP } from 'node:net';
import { request as httpsRequest } from 'node:https';
import { request as httpRequest } from 'node:http';

type Address = {address:string;family:number};
type Resolver = (host:string) => Promise<Address[]>;
const resolver: Resolver = host => lookup(host,{all:true,verbatim:true});
/** Conservative global-unicast allowlist: never permit mapped/tunnel/reserved addresses. */
export function publicAddress(ip: string): boolean {
  if (isIP(ip) === 4) {
    const [a,b,c] = ip.split('.').map(Number);
    return !(a===0 || a===10 || a===127 || a>=224 || (a===100 && b>=64 && b<=127) ||
      (a===169 && b===254) || (a===172 && b>=16 && b<=31) ||
      (a===192 && (b===168 || (b===0 && (c===0 || c===2)) || (b===88 && c===99))) ||
      (a===198 && (b===18 || b===19 || (b===51 && c===100))) || (a===203 && b===0 && c===113));
  }
  if (isIP(ip) !== 6) return false;
  const normalized = new URL(`http://[${ip}]/`).hostname.slice(1,-1).toLowerCase();
  return /^[23]/.test(normalized) && !normalized.startsWith('2002:') && !normalized.startsWith('3fff:') &&
    !normalized.startsWith('2001:db8:') && !/^2001:(?:[0-9a-f]{1,2}|1[0-9a-f]{2}):/.test(normalized);
}
export async function resolvePublicUrl(raw: string, resolve: Resolver = resolver) {
  const url = new URL(raw);
  if (!['http:','https:'].includes(url.protocol) || url.username || url.password || url.port || raw.length>2048) throw new Error('UNSAFE_SOURCE');
  const host = url.hostname.replace(/^\[|\]$/g,'');
  if (host==='localhost' || host.endsWith('.localhost') || host.endsWith('.local') || !host.includes('.') && !isIP(host)) throw new Error('UNSAFE_SOURCE');
  const addresses = isIP(host) ? [{address:host,family:isIP(host)}] : await resolve(host);
  if (!addresses.length || addresses.some(a=>!publicAddress(a.address))) throw new Error('UNSAFE_SOURCE');
  url.hash=''; return {url,address:addresses[0]};
}
export function htmlToText(html: string): string {
  // Deliberately a conservative text extractor, not a DOM renderer. Never execute page content.
  return html.replace(/<!--[\s\S]*?-->/g,' ').replace(/<(script|style|noscript|template)\b[^>]*>[\s\S]*?<\/\1\s*>/gi,' ')
    .replace(/<[^>]*>/g,' ').replace(/&(#x[0-9a-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi,(_,entity:string)=>{
      const named:Record<string,string>={amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' '};
      if (entity[0]!=='#') return named[entity.toLowerCase()] ?? ' ';
      const n=entity[1].toLowerCase()==='x'?parseInt(entity.slice(2),16):parseInt(entity.slice(1),10);
      return n>0 && n<=0x10ffff && !(n>=0xd800&&n<=0xdfff)?String.fromCodePoint(n):' ';
    }).replace(/\s+/g,' ').trim();
}
export async function fetchPublicText(raw: string, signal: AbortSignal): Promise<string> {
  const timeout = AbortSignal.timeout(8000);
  const combined = AbortSignal.any([signal,timeout]);
  // Race covers DNS stalls as well; socket work receives the same signal.
  return await new Promise<string>((resolve,reject)=>{
    const abort=()=>reject(new Error('SOURCE_ABORTED'));
    combined.addEventListener('abort',abort,{once:true});
    const run=async()=>{
      let next=raw;
      for(let redirects=0;redirects<=2;redirects++) {
        combined.throwIfAborted();
        const target=await resolvePublicUrl(next);
        combined.throwIfAborted();
        const result=await new Promise<{location?:string;text?:string}>((resolveResponse,rejectResponse)=>{
          const transport=target.url.protocol==='https:'?httpsRequest:httpRequest;
          const req=transport(target.url,{
            signal:combined, agent:false, headers:{'User-Agent':'TrueOrNot/1.0 (source verification)','Accept':'text/html,text/plain','Accept-Encoding':'identity'},
            // Pin the validated DNS answer; never resolve a second time at connection time.
            lookup:(_hostname,options,callback)=>{
              if (options.all) callback(null,[target.address]);
              else callback(null,target.address.address,target.address.family);
            }
          },res=>{
            const status=res.statusCode ?? 0;
            if ([301,302,303,307,308].includes(status)) { const location=res.headers.location; res.destroy(); location?resolveResponse({location}):rejectResponse(new Error('SOURCE_REDIRECT')); return; }
            const type=(res.headers['content-type']??'').split(';')[0].trim().toLowerCase();
            if (status!==200 || !['text/html','text/plain'].includes(type) || (res.headers['content-encoding'] && res.headers['content-encoding']!=='identity')) { res.destroy(); rejectResponse(new Error('SOURCE_UNAVAILABLE')); return; }
            const chunks:Buffer[]=[]; let size=0;
            res.on('data',(chunk:Buffer)=>{size+=chunk.length;if(size>512000) res.destroy(new Error('SOURCE_TOO_LARGE'));else chunks.push(chunk);});
            res.on('error',rejectResponse);
            res.on('end',()=>{const body=Buffer.concat(chunks).toString('utf8');resolveResponse({text:(type==='text/html'?htmlToText(body):body.replace(/\s+/g,' ').trim()).slice(0,18000)});});
          });
          req.on('error',rejectResponse); req.end();
        });
        if(result.text!==undefined) return result.text;
        next=new URL(result.location!,target.url).href;
      }
      throw new Error('SOURCE_REDIRECT_LIMIT');
    };
    run().then(resolve,reject).finally(()=>combined.removeEventListener('abort',abort));
  });
}
