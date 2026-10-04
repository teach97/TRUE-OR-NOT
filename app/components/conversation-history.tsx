'use client';
import type {ConversationStorage} from './conversation-storage';
export default function ConversationHistory({storage,onNew,onSelect,onDelete}:{storage:ConversationStorage;onNew:()=>void;onSelect:(id:string)=>void;onDelete:(id:string)=>void}){
  return <section className="conversation-history" aria-label="저장된 대화">
    <button type="button" className="conversation-new" onClick={onNew}>＋ 새 대화</button>
    <label className="conversation-consent"><input type="checkbox" checked={storage.consent} onChange={event=>storage.setConsent(event.target.checked)}/>이 브라우저에서 대화 저장</label>
    <details><summary>저장·개인정보 안내</summary><p>동의 이후 메시지와 최종 검증 결과를 서버 DB에 저장합니다. 로그인 없이 이 브라우저 쿠키로만 복원합니다. 쿠키 삭제·30일 만료 시 기존 기록에 접근할 수 없습니다. 저장을 꺼도 기존 기록은 남으며 아래 삭제 버튼으로 지울 수 있습니다. 시연용 무료 DB는 2026년 11월 3일 만료 예정이며 영구 보관·백업을 보장하지 않습니다.</p></details>
    {storage.error&&<div className="conversation-error" role="alert"><p>답변은 유지됩니다. 대화 저장·불러오기에 실패했습니다.</p>{storage.pending.length>0&&<button type="button" onClick={()=>void storage.retrySave()}>저장만 재시도</button>}{storage.error==='SESSION_INVALID'&&<button type="button" onClick={()=>{if(window.confirm('기존 익명 세션을 복구할 수 없습니다. 새 세션을 시작하면 이전 기록에 접근할 수 없습니다. 계속하시겠습니까?')){onNew();void storage.newSession();}}}>새 세션 시작</button>}</div>}
    <ul>{storage.items.map(item=><li key={item.id} className={storage.active===item.id?'is-active':''}><button type="button" title={item.title} onClick={()=>onSelect(item.id)}>{item.title}</button><button type="button" aria-label={`${item.title} 대화 삭제`} onClick={()=>{if(window.confirm(`‘${item.title}’ 대화를 삭제하시겠습니까? 삭제한 대화는 복구할 수 없습니다.`))onDelete(item.id);}}>삭제</button></li>)}</ul>
    {!storage.items.length&&<p className="conversation-empty">저장된 대화가 없습니다.</p>}
    {storage.nextCursor&&<button type="button" onClick={()=>void storage.refresh(true)}>대화 더 보기</button>}
  </section>;
}
