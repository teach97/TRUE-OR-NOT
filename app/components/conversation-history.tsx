'use client';
import type {ConversationStorage} from './conversation-storage';
export default function ConversationHistory({storage,onNew,onSelect,onDelete}:{storage:ConversationStorage;onNew:()=>void;onSelect:(id:string)=>void;onDelete:(id:string)=>void}){
  return <section className="conversation-history" aria-label="저장된 대화">
    <button type="button" className="conversation-new" onClick={onNew}>＋ 새 대화</button>
    {storage.error&&<div className="conversation-error" role="alert"><p>답변은 유지됩니다. 대화 저장·불러오기에 실패했습니다.</p>{storage.pending.length>0&&<button type="button" onClick={()=>void storage.retrySave()}>저장만 재시도</button>}{storage.error==='SESSION_INVALID'&&<button type="button" onClick={()=>{if(window.confirm('기존 익명 세션을 복구할 수 없습니다. 새 세션을 시작하면 이전 기록에 접근할 수 없습니다. 계속하시겠습니까?')){onNew();void storage.newSession();}}}>새 세션 시작</button>}</div>}
    <ul>{storage.items.map(item=><li key={item.id} className={storage.active===item.id?'is-active':''}><button type="button" title={item.title} onClick={()=>onSelect(item.id)}>{item.title}</button><button type="button" aria-label={`${item.title} 대화 삭제`} onClick={()=>{if(window.confirm(`‘${item.title}’ 대화를 삭제하시겠습니까? 삭제한 대화는 복구할 수 없습니다.`))onDelete(item.id);}}>삭제</button></li>)}</ul>
    {!storage.items.length&&<p className="conversation-empty">저장된 대화가 없습니다.</p>}
    {storage.nextCursor&&<button type="button" onClick={()=>void storage.refresh(true)}>대화 더 보기</button>}
  </section>;
}
