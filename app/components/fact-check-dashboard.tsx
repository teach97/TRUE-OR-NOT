"use client";

import { AnimatePresence, MotionConfig, motion, useReducedMotion } from 'motion/react';
import { useEffect, useReducer, useRef, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import GlassSurface from './react-bits/GlassSurface';
import { initialState, transition } from './demo-state';
import type { Claim } from './demo-state';
import type { FactCheckResult } from '../lib/fact-check-contract';
import { FactCheckError, readFactCheckStream, safeSourceUrl } from './fact-check-client';
import { DEMO_FOCUS, DEMO_TEXT, demoPreview, documents } from './demo-fixture';
import ScrambleText from './scramble-text';
import FloatingLinesBackground from './floating-lines-background';

type IconName = 'lens' | 'grid' | 'book' | 'arrow' | 'file' | 'link' | 'close' | 'download' | 'plus' | 'shield' | 'check' | 'reset' | 'sliders';
function Icon({name, size = 18}: {name: IconName; size?: number}) {
  const paths: Record<IconName, ReactNode> = {
    lens: <><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5M8 10.5h5M10.5 8v5"/></>,
    grid: <><rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><rect x="14" y="14" width="6" height="6" rx="1"/></>,
    book: <><path d="M12 5v15M12 5C8 2 4 4 3 4v15c3-1 6-1 9 1 3-2 6-2 9-1V4c-3-1-6-1-9 1Z"/></>,
    arrow: <path d="M4 12h16m-6-6 6 6-6 6"/>, file: <><path d="M14 3H5v18h14V8Zm0 0v5h5M8 12h8M8 16h5"/></>,
    link: <><path d="m10 13 4-4M8 15l-2 2a3 3 0 0 1-4-4l5-5a3 3 0 0 1 4 0M13 16a3 3 0 0 0 4 0l5-5a3 3 0 0 0-4-4l-2 2"/></>,
    close: <path d="m6 6 12 12M6 18 18 6"/>, download: <path d="M12 3v12m-4-4 4 4 4-4M4 17v4h16v-4"/>,
    plus: <path d="M12 5v14M5 12h14"/>, shield: <><path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-6"/></>,
    check: <path d="m5 12 4 4L19 6"/>, reset: <><path d="M3 5v5h5M3 10a9 9 0 1 1 1 8"/></>,
    sliders: <><path d="M4 6h5M15 6h5M4 12h9M19 12h1M4 18h2M12 18h8"/><circle cx="12" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="9" cy="18" r="2"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}
function Badge({claim}: {claim: Claim}) { return <span className={`badge ${claim.tone}`}><span aria-hidden="true">{claim.tone === 'cyan' ? '✓' : claim.tone === 'amber' ? '!' : '—'}</span>{claim.verdict || '판정하지 않음'}</span>; }
function Modal({open, title, onClose, children}: {open: boolean; title: string; onClose: () => void; children: ReactNode}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    if (open && !ref.current?.open) ref.current?.showModal();
    else if (!open && ref.current?.open) ref.current.close();
  }, [open]);
  return <dialog ref={ref} className="dialog" aria-labelledby="dialog-heading" onClose={onClose} onClick={e => {if (e.target === e.currentTarget) onClose();}}>
    <div className="dialog-head"><span className="eyebrow">팩트렌즈 · 근거 워크스페이스</span><button className="icon-button" onClick={onClose} aria-label="대화상자 닫기"><Icon name="close"/></button></div>
    <h2 id="dialog-heading">{title}</h2>{children}<button className="secondary-button dialog-done" onClick={onClose}>확인했습니다</button>
  </dialog>;
}
type GlassSettings = {
  distortionScale: number;
  displace: number;
  saturation: number;
  backgroundOpacity: number;
  borderRadius: number;
};
const defaultGlassSettings: GlassSettings = {
  distortionScale: -180, displace: 0.5, saturation: 1.6, backgroundOpacity: 0.3, borderRadius: 18,
};
const glassSettingsStorageKey = 'factlens.glass-surface-settings.v1';
function parseGlassSettings(raw: string | null): GlassSettings {
  try {
    const parsed = JSON.parse(raw || '{}') as Partial<GlassSettings>;
    const number = (value: unknown, min: number, max: number, fallback: number) => typeof value === 'number' && Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : fallback;
    return {
      distortionScale: number(parsed.distortionScale, -300, 0, defaultGlassSettings.distortionScale),
      displace: number(parsed.displace, 0, 5, defaultGlassSettings.displace),
      saturation: number(parsed.saturation, 0.8, 2, defaultGlassSettings.saturation),
      backgroundOpacity: number(parsed.backgroundOpacity, 0, 0.8, defaultGlassSettings.backgroundOpacity),
      borderRadius: number(parsed.borderRadius, 8, 32, defaultGlassSettings.borderRadius),
    };
  } catch { return {...defaultGlassSettings}; }
}
type GlassNumericKey = keyof GlassSettings;
type GlassControl = {key: GlassNumericKey; label: string; min: number; max: number; step: number; precision: number; percent?: boolean};
const glassControls: GlassControl[] = [
  {key: 'distortionScale', label: '굴절 변위 (distortionScale)', min: -300, max: 0, step: 1, precision: 0},
  {key: 'displace', label: '출력 블러 (displace)', min: 0, max: 5, step: 0.1, precision: 1},
  {key: 'saturation', label: '색상 채도', min: 0.8, max: 2, step: 0.05, precision: 2},
  {key: 'backgroundOpacity', label: '배경 불투명도', min: 0, max: 0.8, step: 0.01, precision: 0, percent: true},
  {key: 'borderRadius', label: '모서리 반경', min: 8, max: 32, step: 1, precision: 0},
];

const glassLabEnabled = process.env.NODE_ENV !== 'production' || process.env.NEXT_PUBLIC_GLASS_LAB === 'true';

function LabRange({id, label, value, min, max, step, precision, format, onChange}: {id: string; label: string; value: number; min: number; max: number; step: number; precision: number; format?: (value: number) => string; onChange: (value: number) => void}) {
  return <label className="glass-control" htmlFor={id}><span>{label}</span><output>{format ? format(value) : value.toFixed(precision)}</output><input id={id} type="range" min={min} max={max} step={step} value={value} onChange={event => onChange(Number(event.currentTarget.value))} aria-label={label}/></label>;
}

type GlassPanelProps = {
  as?: 'div' | 'section' | 'article';
  className?: string;
  children: ReactNode;
  glass: GlassSettings;
  enabled?: boolean;
  'aria-labelledby'?: string;
};

function GlassPanel({as = 'div', className = '', children, glass, enabled = true, 'aria-labelledby': labelledBy}: GlassPanelProps) {
  const Element = as;
  if (!enabled) return <Element className={`glass-panel-host glass-disabled ${className}`} aria-labelledby={labelledBy}>{children}</Element>;
  return <Element className={`glass-panel-host ${className}`} aria-labelledby={labelledBy}>
    <GlassSurface className="factlens-glass" {...glass} width="100%" height="auto" style={{colorScheme: 'dark'}}>
      {children}
    </GlassSurface>
  </Element>;
}

export default function FactCheckDashboard() {
  const reduce = useReducedMotion();
  const [state, dispatch] = useReducer(transition, initialState);
  const [draft, setDraft] = useState('');
  const [focus, setFocus] = useState('');
  const [url, setUrl] = useState('');
  const [mode, setMode] = useState<'text' | 'url'>('text');
  const [sample, setSample] = useState(false);
  const [mobileTab, setMobileTab] = useState('results');
  const [dialog, setDialog] = useState<string | null>(null);
  const [notice, setNotice] = useState('');
  const [glass, setGlass] = useState<GlassSettings>(defaultGlassSettings);
  const [glassStorageReady, setGlassStorageReady] = useState(false);
  const [glassLabOpen, setGlassLabOpen] = useState(false);
  const [glassEnabled, setGlassEnabled] = useState(true);
  const request = useRef<AbortController | null>(null);
  const generation = useRef(0);
  const [consent, setConsent] = useState(false);
  const [configured, setConfigured] = useState<boolean | null>(null);
  const [configError, setConfigError] = useState(false);
  const [liveResult, setLiveResult] = useState<FactCheckResult | null>(null);
  const editor = useRef<HTMLTextAreaElement>(null);
  const snapshot = state.snapshot;
  const selected = snapshot?.claims.find(c => c.id === state.selectedId);
  const sourceDocs = snapshot?.demo && selected ? documents.filter(d => selected.evidenceIds.includes(d.id)) : [];
  const activeDocument = documents.find(d => d.id === dialog);
  const busy = state.status === 'loading';
  const configurationHelp = '서버 설정이 필요합니다. 프로젝트의 .env.local에 OPENAI_API_KEY를 설정한 뒤 서버를 다시 시작해 주세요. 키를 화면이나 채팅에 입력하지 마세요.';
  const serviceLabel = configured === true ? 'API 키 설정됨 · 접근 미확인' : configured === false ? 'API 키 미설정' : configError ? '설정 확인 실패' : '서버 설정 확인 중';
  useEffect(() => {
    const controller = new AbortController();
    fetch('/api/fact-check', {signal: controller.signal, cache: 'no-store'})
      .then(async response => {if (!response.ok) throw new Error(); const status = await response.json(); if (typeof status.configured !== 'boolean') throw new Error(); if (!controller.signal.aborted) setConfigured(status.configured);})
      .catch(() => {if (!controller.signal.aborted) setConfigError(true);});
    return () => {controller.abort(); generation.current++; request.current?.abort();};
  }, []);
  useEffect(() => {
    try {
      setGlass(parseGlassSettings(window.localStorage.getItem(glassSettingsStorageKey)));
    } catch { /* 브라우저 저장소가 차단된 환경에서는 기본값으로 실행합니다. */ }
    setGlassStorageReady(true);
  }, []);
  useEffect(() => {
    if (!glassStorageReady) return;
    try { window.localStorage.setItem(glassSettingsStorageKey, JSON.stringify(glass)); }
    catch { /* 저장소 용량·권한 오류가 UI를 중단시키지 않도록 무시합니다. */ }
  }, [glass, glassStorageReady]);
  function stop() {generation.current++; request.current?.abort(); request.current = null;}
  function loadSample() {
    stop(); setLiveResult(null); dispatch({type: 'cancel'}); dispatch({type: 'load', snapshot: demoPreview});
    setDraft(DEMO_TEXT); setFocus(DEMO_FOCUS); setMode('text'); setSample(true); setConsent(false);
    setNotice('가상의 행사 예시를 불러왔습니다. 외부 전송 없이 예시 문서를 비교합니다.');
  }
  function reset() {
    stop(); setLiveResult(null); setConsent(false); dispatch({type: 'reset'}); setDraft(''); setFocus(''); setUrl(''); setSample(false); setMode('text');
    setNotice('새 문서를 시작합니다. 원문을 붙여넣어 주세요.'); editor.current?.focus();
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || request.current) return;
    if (mode === 'url') {setNotice('URL 수집은 아직 연결되지 않았습니다. 본문을 복사해 텍스트 탭에 붙여넣어 주세요.'); return;}
    if (!draft.trim()) {setNotice('검증할 원문을 입력해 주세요.'); return;}
    if (draft.length > 12000 || focus.length > 500) {setNotice('원문은 12,000자, 확인 요청은 500자 이내로 입력해 주세요.'); return;}
    if (sample) {dispatch({type: 'load', snapshot: {...demoPreview, focus}}); setNotice('합성 예시입니다. 실제 검증 요청은 전송하지 않았습니다.'); return;}
    if (configured === false) {setNotice(configurationHelp); return;}
    if (!consent) {setNotice('외부 전송과 유료 검증 안내를 확인하고 동의해 주세요.'); return;}
    stop();
    const controller = new AbortController(); request.current = controller;
    const current = generation.current;
    const submitted = {text: draft, focus, consent: true as const};
    setLiveResult(null); dispatch({type: 'reset'}); dispatch({type: 'start'});
    setNotice('검증 요청을 서버로 전송하고 있습니다. gpt-5.6-luna · max');
    try {
      const response = await fetch('/api/fact-check', {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify(submitted), signal:controller.signal});
      const result = await readFactCheckStream(response, {signal:controller.signal, onStage:event => {if (generation.current === current) setNotice(event.message);}});
      if (generation.current !== current || controller.signal.aborted) return;
      if (result.text !== submitted.text || result.focus !== submitted.focus) throw new Error('제출한 원문과 검증 결과가 일치하지 않습니다. 다시 시도해 주세요.');
      setLiveResult(result); dispatch({type:'load', snapshot:result}); setMobileTab('results');
      setNotice(result.claims.length ? '검증이 완료되었습니다. 출처와 남은 불확실성을 함께 확인해 주세요.' : '검증 가능한 주장을 찾지 못했습니다. 결과의 경고를 확인해 주세요.');
    } catch (error) {
      if (generation.current !== current || controller.signal.aborted) return;
      dispatch({type:'cancel'});
      if (error instanceof FactCheckError && /CONFIG|KEY_MISSING/i.test(error.code)) {setConfigured(false); setNotice(configurationHelp);}
      else setNotice(error instanceof Error ? `검증 실패: ${error.message} 다시 시도하실 수 있습니다.` : '검증 요청에 실패했습니다. 네트워크를 확인하고 다시 시도해 주세요.');
    } finally {if (generation.current === current) request.current = null;}
  }
  function download() {
    if (!snapshot) return;
    const content = snapshot.demo ? {title: 'FactLens 합성 예시', disclaimer: '실제 검증 결과가 아닙니다.', ...snapshot, documents} : {title: 'FactLens 검증 결과', disclaimer: 'AI 검증에는 오류가 있을 수 있습니다. 원출처를 확인해 주세요.', ...liveResult};
    const blobUrl = URL.createObjectURL(new Blob([JSON.stringify(content, null, 2)], {type: 'application/json;charset=utf-8'}));
    const link = document.createElement('a'); link.href = blobUrl; link.download = snapshot.demo ? 'factlens-demo.json' : 'factlens-result.json'; link.click();
    setTimeout(() => URL.revokeObjectURL(blobUrl), 1000); setNotice(snapshot.demo ? '합성 예시 JSON 다운로드를 요청했습니다.' : '원문·출처·불확실성을 포함한 검증 JSON 다운로드를 요청했습니다.');
  }
  const select = (id: string) => dispatch({type: 'select', id});
  const original = snapshot && (() => {
    const chunks: ReactNode[] = []; let cursor = 0;
    snapshot.claims.forEach((claim, i) => {
      chunks.push(snapshot.text.slice(cursor, claim.start));
      chunks.push(<button key={claim.id} className={`sentence ${claim.id === state.selectedId ? 'selected' : ''}`} aria-pressed={claim.id === state.selectedId} onClick={() => select(claim.id)}><span className="sentence-number">0{i + 1}</span>{claim.quote}</button>);
      cursor = claim.end;
    });
    chunks.push(snapshot.text.slice(cursor)); return chunks;
  })();
  function updateGlass(key: GlassNumericKey, value: number) {
    setGlass(previous => ({...previous, [key]: value}));
  }
  return <MotionConfig reducedMotion="user"><div className="app-shell" id="top" data-glass-enabled={glassEnabled}>
    <FloatingLinesBackground />
    <a className="skip-link" href="#workspace-main">본문으로 건너뛰기</a>
    <aside className="sidebar">
      <a className="brand" href="#top" aria-label="팩트렌즈 홈"><span className="brand-symbol"><Icon name="lens" size={25}/></span><span><ScrambleText>FactLens</ScrambleText><small>팩트렌즈</small></span></a>
      <div className="workspace-label"><span className="workspace-avatar">F</span><div>나의 워크스페이스<small>텍스트 검증 · 예시 체험</small></div></div>
      <p className="nav-caption">워크스페이스</p>
      <nav aria-label="주요 메뉴"><a className="nav-item active" href="#review"><Icon name="grid"/>근거 워크스페이스<span className="nav-indicator"/></a><button className="nav-item" onClick={reset}><Icon name="plus"/>새 문서 시작</button><button className="nav-item" onClick={() => setDialog('guide')}><Icon name="book"/>검증 가이드</button></nav>
      <div className="sidebar-bottom"><div className="principle-card"><Icon name="shield"/><strong>결론보다, 근거를 먼저.</strong><p>확인된 내용과 아직 모르는 내용을 나란히 살펴보세요.</p><button onClick={() => setDialog('guide')}>우리의 검증 원칙 <Icon name="arrow" size={15}/></button></div><div className="local-status"><span/>{serviceLabel}</div><p className="sidebar-foot">FACTLENS / EVIDENCE WORKSPACE</p></div>
    </aside>
    <div className="main-shell">
      <header className="topbar"><div className="breadcrumb"><span className="mobile-brand">FactLens</span></div><div className="topbar-actions"><button className="text-button" aria-label="사용 가이드" onClick={() => setDialog('guide')}><Icon name="book"/><span>사용 가이드</span></button>{glassLabEnabled && <button type="button" aria-label="UI 조정" className={`text-button glass-lab-trigger ${glassLabOpen ? 'is-active' : ''}`} aria-expanded={glassLabOpen} aria-controls="glass-lab" onClick={() => setGlassLabOpen(open => !open)}><Icon name="sliders"/><span>UI 조정</span></button>}<span className="profile-mark" aria-label="로컬 워크스페이스">F</span></div></header>
      <main id="workspace-main" className="page-content">
        <GlassPanel as="section" className="composer" aria-labelledby="composer-heading" glass={glass} enabled={glassEnabled}>
          <div className="section-heading"><div><span className="step-label">01 / 문서 입력</span><h2 id="composer-heading"><ScrambleText>어떤 내용을 확인하고 싶으세요?</ScrambleText></h2></div><button className="text-button" aria-label="초기화" onClick={reset}><Icon name="reset" size={16}/><span>초기화</span></button></div>
          <form onSubmit={submit}>
            <div className="input-mode" role="group" aria-label="입력 방식"><button type="button" aria-pressed={mode === 'text'} onClick={() => setMode('text')}><Icon name="file" size={16}/>텍스트 입력</button><button type="button" aria-pressed={mode === 'url'} onClick={() => setMode('url')}><Icon name="link" size={16}/>URL 입력<span className="soon-label">준비 중</span></button></div>
            {mode === 'text' ? <div className="editor-wrap"><label htmlFor="document-text">확인할 원문 {sample && <span className="inline-demo">· 합성 예시</span>}</label><textarea ref={editor} id="document-text" value={draft} onChange={e => {setDraft(e.target.value); setSample(false);}} placeholder="기사, 댓글, 궁금한 문장을 붙여넣어 주세요." rows={3} maxLength={12000} onKeyDown={e => {if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {e.preventDefault(); e.currentTarget.form?.requestSubmit();}}}/><span className="character-count">{draft.length.toLocaleString()} / 12,000</span></div> : <div className="url-wrap"><label htmlFor="document-url">확인할 페이지 주소</label><input id="document-url" type="url" value={url} onChange={e => setUrl(e.target.value)} placeholder="https://…"/><p>URL 수집은 아직 연결되지 않았습니다. 원문을 복사해 <button type="button" className="inline-link" onClick={() => setMode('text')}>텍스트로 붙여넣어 주세요.</button></p></div>}
            <div className="focus-row"><label htmlFor="focus-request"><Icon name="lens" size={16}/>확인 요청 <span>선택</span></label><input id="focus-request" value={focus} maxLength={500} onChange={e => setFocus(e.target.value)} placeholder="예: 행사 일정과 무료 참여 조건이 궁금해요."/></div>
            <div className="focus-note"><div><p>gpt-5.6-luna · reasoning max · 웹 검색 사용. 유료 요청이며 시간이 걸릴 수 있습니다.</p>{!sample && <label><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} disabled={busy}/> 원문과 확인 요청을 서버·OpenAI에 보내고 웹 검색에 사용하는 데 동의합니다. 민감한 정보는 제외해 주세요.</label>}<p>{configured === false ? configurationHelp : serviceLabel}</p></div></div><div className="composer-bottom"><p><Icon name="shield" size={15}/>{sample ? '합성 예시는 외부로 전송하지 않습니다.' : '동의한 검증 요청만 외부로 전송합니다.'}</p><div className="submit-actions">{busy && <button type="button" className="secondary-button" onClick={() => {stop(); dispatch({type: 'cancel'}); setNotice('검증 요청을 취소했습니다. 이미 전송된 요청에는 비용이 발생할 수 있습니다.');}}>취소</button>}<button className="primary-button" disabled={busy || mode === 'url' || !draft.trim()}>{busy ? '검증 진행 중' : sample ? '예시 다시 보기' : '팩트 검증 시작'}<Icon name="arrow" size={17}/></button></div></div>
          </form>
          <div className="sample-row"><span>예시로 둘러보기</span><button onClick={loadSample}><span className="sample-dot"/>가상 도시의 문화 행사<Icon name="arrow" size={14}/></button><span className="sample-explainer">일정 · 참여 조건 · 예측</span></div>
        </GlassPanel>
        <div className="notice-line" role="status" aria-live="polite">{notice || (configured === false ? configurationHelp : '원문을 입력해 실제 검증을 시작하거나, 합성 예시를 선택해 둘러보세요.')}</div>
        <section id="review" className="review-section" aria-labelledby="review-heading">
          <div className="review-heading"><div><span className="step-label">02 / 원문과 근거</span><h2 id="review-heading"><ScrambleText>흩어진 근거를, 한눈에.</ScrambleText></h2></div><button className="secondary-button export-button" disabled={!snapshot || busy} onClick={download}><Icon name="download" size={16}/><span>{snapshot?.demo ? '예시 내보내기' : '결과 내보내기'}</span></button></div>
          {snapshot ? <>
            <div className="review-meta"><span className="document-title"><Icon name="file" size={16}/>{snapshot.demo ? '가을빛 축제 안내 · 합성 예시' : '직접 입력한 문서 · 실제 검증'}</span><div><span>후보 <b>{snapshot.claims.length}</b></span><span>{snapshot.demo ? '예시 문서' : '수집 출처'} <b>{snapshot.demo ? documents.length : liveResult?.sources.length ?? 0}</b></span><span>원자료 그룹 <b>{snapshot.demo ? new Set(documents.map(d => d.group)).size : '관계별 확인'}</b></span></div></div>
            <div className="mobile-tabs" role="group" aria-label="검토 화면 선택">{[['original','원문'],['results','결과'],['sources','출처']].map(([value, label]) => <button key={value} aria-pressed={mobileTab === value} onClick={() => setMobileTab(value)}>{label}</button>)}</div>
            <div className={`review-body mobile-${mobileTab}`}>
              <div className="claim-selector" aria-label="주장 후보 선택">{snapshot.claims.map((claim, index) => <motion.button key={claim.id} layout={!reduce} className={`claim-card ${selected?.id === claim.id ? 'is-selected' : ''}`} aria-pressed={selected?.id === claim.id} onClick={() => select(claim.id)}><div className="claim-card-top"><span>주장 0{index + 1}</span><Badge claim={claim}/></div><strong>{claim.quote}</strong><span className="claim-card-bottom">{selected?.id === claim.id ? '선택한 주장' : '근거 살펴보기'}<Icon name={selected?.id === claim.id ? 'check' : 'arrow'} size={15}/></span></motion.button>)}</div>
              <GlassPanel as="article" className="original-panel" glass={glass} enabled={glassEnabled}><div className="panel-top"><h3><Icon name="file" size={17}/>원문 읽기</h3><span>{snapshot.demo ? '합성 문서' : '제출한 원문'}</span></div><div className="original-content"><span className="article-kicker">{snapshot.demo ? '문화 · 행사 / 가상의 사례' : '제출 원문 / OpenAI · 웹 검색 검증'}</span><h3>{snapshot.demo ? '달빛시 가을빛 축제,\n알아두면 좋은 세 가지' : '직접 입력한 원문'}</h3><p className="article-byline">{snapshot.demo ? '팩트렌즈 예시 편집실 · 실제 기사 아님' : '검증 요청 시점의 원문을 보존했습니다.'}</p><div className="original-text">{original}</div><div className="highlight-legend"><span/>노란 강조는 선택한 문장입니다. 판정 색상이 아닙니다.</div>{snapshot.focus && <div className="focus-note"><Icon name="lens" size={17}/><div><strong>확인하고 싶은 내용</strong><p>{snapshot.focus}</p><small>{snapshot.demo ? '예시의 비교 범위를 보여드립니다.' : '이 요청을 검증의 참고 범위로 전달했습니다.'}</small></div></div>}</div><div className="original-footer"><Icon name="shield" size={15}/>{snapshot.demo ? '실제 인물·지역·사건과 무관한 합성 예시입니다.' : '원문에서 추출한 최대 3개의 주장을 검증합니다.'}</div></GlassPanel>
              {selected && snapshot.demo && <GlassPanel className="evidence-panel" glass={glass} enabled={glassEnabled}><div className="panel-top"><h3><Icon name="lens" size={18}/>주장별 근거</h3><span>{snapshot.demo ? '예시 비교' : '백엔드 미연결'}</span></div><AnimatePresence mode="wait" initial={false}><motion.div className="detail-content" key={selected.id} initial={reduce ? false : {opacity: 0, y: 4}} animate={{opacity: 1, y: 0}} exit={{opacity: 0}} transition={{duration: reduce ? 0 : 0.16}}><div className="result-overview"><span className="article-kicker">선택한 주장 · {snapshot.demo ? '예시 판정' : '문장 후보'}</span><h3>{selected.quote}</h3><Badge claim={selected}/><p>{selected.summary}</p></div><div className="source-content"><div className="source-heading"><h4>근거 문서 비교</h4><span>{sourceDocs.length}개 예시 문서</span></div>{sourceDocs.length ? <><div className="comparison-note"><span className="group-symbol">A</span><p><strong>같은 원자료를 공유합니다.</strong><br/>문서 2개가 독립적인 근거 2개를 뜻하지 않습니다.</p></div>{sourceDocs.map((doc, i) => <button className="source-card" key={doc.id} onClick={() => setDialog(doc.id)}><div className="source-card-top"><span className="source-index">0{i + 1}</span><span className="source-kind">{doc.relation} · 예시</span><Icon name="arrow" size={16}/></div><strong>{doc.title}</strong><span className="source-publisher">{doc.publisher} · {doc.date}</span><blockquote>“{selected.id === 'claim-1' ? (doc.id === 'doc-1' ? '가을빛 축제는 10월 12일부터 14일까지 달빛공원에서 진행합니다.' : '행사는 10월 12일부터 14일까지 열립니다.') : (doc.id === 'doc-1' ? '공예 체험은 사전 예약이 필요하며 재료비 5,000원이 있습니다.' : '공예 체험은 별도 예약과 재료비가 필요합니다.')}”</blockquote><span className="source-footer">원자료 그룹 A <span>예시 문서 전문 보기</span></span></button>)}<p className="evidence-caution">인용 표현은 아래 문서 전문에서 확인해 주세요. 모든 문서는 시연용으로 작성되었습니다.</p></> : <div className="empty-evidence"><Icon name="file" size={27}/><h4>{snapshot.demo ? '비교할 근거가 없습니다' : '아직 검증하지 않았습니다'}</h4><p>{snapshot.demo ? '미래 전망을 현재 사실로 확정하지 않습니다. 예시 문서에도 방문객 추정 근거는 없습니다.' : '현재는 문장을 나누어 보여드리는 로컬 미리보기입니다. 검색·판정 API가 연결되기 전까지 출처와 판정을 생성하지 않습니다.'}</p></div>}</div></motion.div></AnimatePresence></GlassPanel>}
              {!snapshot.demo && liveResult && <GlassPanel className="evidence-panel" glass={glass} enabled={glassEnabled}>
                <div className="panel-top"><h3><Icon name="lens" size={18}/>주장별 근거</h3><span>수집된 원문 비교</span></div>
                <div className="detail-content">
                  {selected && <>
                    <div className="result-overview"><h3>{selected.quote}</h3><Badge claim={selected}/><p>{selected.summary}</p></div>
                    <div className="source-content"><h4>근거 문서 비교</h4>
                      {liveResult.evidence.filter(e => e.claimId === selected.id && selected.evidenceIds.includes(e.id)).map(e => {
                        const source = liveResult.sources.find(s => s.id === e.sourceId);
                        const href = source && safeSourceUrl(source.url);
                        return <div className="source-card" key={e.id}>
                          <span className="source-kind">{e.relation === 'supports' ? '지지 근거' : e.relation === 'contradicts' ? '반박 근거' : '맥락 근거'}</span>
                          {href ? <a href={href} target="_blank" rel="noopener noreferrer">{source?.title}</a> : <strong>{source?.title || '출처 확인 불가'}</strong>}
                          <p className="source-publisher">{source?.publisher} · {source?.publishedAt || '발행일 미확인'}</p>
                          <blockquote>“{e.quote}”</blockquote>
                          <p>{e.quoteVerified ? '원문 인용 일치 확인' : '인용 일치 미확인'} · 출처 독립성은 별도 확인이 필요합니다.</p>
                        </div>;
                      })}
                      {!selected.evidenceIds.length && <div className="empty-evidence"><h4>비교할 근거가 없습니다</h4><p>근거 부족은 거짓을 뜻하지 않습니다.</p></div>}
                      {(() => {const claim = liveResult.claims.find(c => c.id === selected.id); return claim && <>
                        <h4>확인된 내용</h4><ul>{claim.confirmed.map((text, i) => <li key={i}>{text}</li>)}</ul>
                        <h4>남은 불확실성</h4><ul>{claim.unresolved.map((text, i) => <li key={i}>{text}</li>)}</ul>
                        <h4>주장별 주의사항</h4><ul>{claim.warnings.map((text, i) => <li key={i}>{text}</li>)}</ul>
                      </>;})()}
                    </div>
                  </>}
                  <div className="source-content"><h4>검증 한계</h4><ul>{liveResult.warnings.map((text, i) => <li key={i}>{text}</li>)}</ul></div>
                </div>
              </GlassPanel>}
             </div>
          </> : <GlassPanel className="empty-workspace" glass={glass} enabled={glassEnabled}><Icon name="lens" size={34}/><h3>첫 번째 문서를 기다리고 있습니다.</h3><p>원문을 붙여넣거나 예시를 불러와 근거 비교 화면을 둘러보세요.</p><button className="secondary-button" onClick={loadSample}>예시 불러오기<Icon name="arrow"/></button></GlassPanel>}
        </section>
        <footer className="page-footer"><span><span className="footer-mark">F</span>FactLens <span className="footer-divider">/</span>판단을 대신하지 않고, 근거를 연결합니다.</span><button className="text-button" onClick={() => setDialog('guide')}>검증 원칙<Icon name="arrow" size={15}/></button></footer>
      </main>
      {glassLabEnabled && <AnimatePresence>
        {glassLabOpen && <motion.aside id="glass-lab" className="glass-lab" aria-label="UI 컴포넌트 조정" initial={reduce ? false : {opacity: 0, x: 18, scale: 0.98}} animate={{opacity: 1, x: 0, scale: 1}} exit={reduce ? undefined : {opacity: 0, x: 18, scale: 0.98}} transition={{duration: reduce ? 0 : 0.18}}>
          <div className="glass-lab-head"><div><span className="glass-lab-kicker"><Icon name="sliders" size={13}/>DEV TOOL</span><h2>UI Component Lab</h2><p>GlassSurface 설정을 브라우저에서 조정합니다.</p></div><button type="button" className="icon-button" onClick={() => setGlassLabOpen(false)} aria-label="UI 조정 닫기"><Icon name="close" size={17}/></button></div>
          <div className="glass-lab-scroll">
            <section className="glass-lab-section" aria-labelledby="glass-section-heading"><div className="glass-section-title"><h3 id="glass-section-heading">React Bits GlassSurface</h3><span>5개 설정</span></div><div className="glass-controls">{glassControls.map(control => <LabRange key={control.key} id={`glass-${control.key}`} label={control.label} value={glass[control.key]} min={control.min} max={control.max} step={control.step} precision={control.precision} format={control.percent ? value => `${Math.round(value * 100)}%` : undefined} onChange={value => updateGlass(control.key, value)}/>)}</div></section>
          </div>
          <div className="glass-lab-foot"><span><span className="live-dot"/>브라우저에 저장됨</span><div className="glass-lab-actions"><button type="button" className={`text-button glass-toggle ${glassEnabled ? 'is-active' : ''}`} aria-pressed={glassEnabled} onClick={() => setGlassEnabled(value => !value)}>{glassEnabled ? '리퀴드 글라스 끄기' : '리퀴드 글라스 켜기'}</button><button type="button" className="text-button" onClick={() => setGlass(defaultGlassSettings)}>글래스 기본값</button></div></div>
        </motion.aside>}
      </AnimatePresence>}
    </div>
    <Modal open={dialog !== null} title={activeDocument?.title || (dialog === 'guide' ? '근거를 읽는 세 가지 원칙' : '실제 검증과 합성 예시 안내')} onClose={() => setDialog(null)}>{activeDocument ? <><p className="dialog-notice">합성 예시 문서 · 외부 출처 링크가 아닙니다.</p><dl className="document-metadata"><dt>작성 주체</dt><dd>{activeDocument.publisher}</dd><dt>설정 날짜</dt><dd>{activeDocument.date}</dd><dt>원자료 관계</dt><dd>그룹 {activeDocument.group} · {activeDocument.relation}</dd></dl><div className="document-fulltext">{activeDocument.text}</div></> : dialog === 'guide' ? <ol className="guide-list"><li><span>01</span><div><h3>주장을 작게 나누세요.</h3><p>누가, 언제, 어디서, 어떤 조건으로 한 말인지 원문과 함께 확인하세요.</p></div></li><li><span>02</span><div><h3>출처의 수보다 관계를 보세요.</h3><p>같은 발표를 옮긴 여러 문서는 하나의 원자료를 공유할 수 있습니다.</p></div></li><li><span>03</span><div><h3>모르는 것은 남겨 두세요.</h3><p>근거가 없다고 거짓은 아닙니다. 의견과 미래 예측을 확정된 사실처럼 판정하지 않습니다.</p></div></li></ol> : <div className="about-copy"><p>달빛시와 가을빛 축제는 가상의 사례입니다. 모든 예시 문서와 판정은 인터페이스를 설명하기 위해 작성했습니다.</p><p>동의 후 검증을 시작하면 원문과 확인 요청이 서버와 OpenAI에 전달되며 웹 검색을 사용합니다. gpt-5.6-luna · max 유료 요청입니다. URL 수집은 지원하지 않습니다. 예시는 외부로 전송하지 않습니다.</p><p>이 화면은 작업 이력을 저장하지 않으며 새로고침하면 사라집니다. 외부 서비스의 데이터 처리는 해당 서비스 정책을 따릅니다. 내보내기에는 원문이 포함되고 합성 예시와 실제 결과가 구분됩니다.</p></div>}</Modal>
  </div></MotionConfig>;
}
