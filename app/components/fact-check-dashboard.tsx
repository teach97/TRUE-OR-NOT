"use client";

import { AnimatePresence, MotionConfig, motion, useReducedMotion } from 'motion/react';
import { useEffect, useReducer, useRef, useState } from 'react';
import type { CSSProperties, FormEvent, ReactNode } from 'react';
import { initialState, transition } from './demo-state';
import type { Claim } from './demo-state';
import { MODEL_OPTIONS } from '../lib/fact-check-contract';
import type { AnswerBlock, FactCheckAnswer, FactCheckResult, FactSource, ModelOption, ModelPreference } from '../lib/fact-check-contract';
import { sourceDiscoveryLabel } from '../lib/source-discovery';
import { scoreBand, scoreLabel } from '../lib/fact-score';
import { stripYoutubeApiDataForExport } from '../lib/youtube-context';
import { FactCheckError, readFactCheckStream, safeSourceUrl } from './fact-check-client';
import { answerCitationAnchorId, composeAssistantReply, createAnswerCitationDisplayState, presentAnswerCitations } from './fact-check-reply';
import { DEMO_FOCUS, DEMO_TEXT, demoPreview, documents } from './demo-fixture';
import ScrambleText from './scramble-text';
import FloatingLinesBackground from './floating-lines-background';
import LineSidebar from './line-sidebar';
import CountUp from './count-up';
import LatticeLoader from './lattice-loader';

type IconName = 'lens' | 'grid' | 'book' | 'arrow' | 'file' | 'link' | 'close' | 'download' | 'plus' | 'shield' | 'check' | 'reset';

function Icon({name, size = 18}: {name: IconName; size?: number}) {
  const paths: Record<IconName, ReactNode> = {
    lens: <><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5M8 10.5h5M10.5 8v5"/></>,
    grid: <><rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><rect x="14" y="14" width="6" height="6" rx="1"/></>,
    book: <><path d="M12 5v15M12 5C8 2 4 4 3 4v15c3-1 6-1 9 1 3-2 6-2 9-1V4c-3-1-6-1-9 1Z"/></>,
    arrow: <path d="M4 12h16m-6-6 6 6-6 6"/>,
    file: <><path d="M14 3H5v18h14V8Zm0 0v5h5M8 12h8M8 16h5"/></>,
    link: <><path d="m10 13 4-4M8 15l-2 2a3 3 0 0 1-4-4l5-5a3 3 0 0 1 4 0M13 16a3 3 0 0 0 4 0l5-5a3 3 0 0 0-4-4l-2 2"/></>,
    close: <path d="m6 6 12 12M6 18 18 6"/>,
    download: <path d="M12 3v12m-4-4 4 4 4-4M4 17v4h16v-4"/>,
    plus: <path d="M12 5v14M5 12h14"/>,
    shield: <><path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-6"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
    reset: <><path d="M3 5v5h5M3 10a9 9 0 1 1 1 8"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

function Badge({claim}: {claim: Claim}) {
  const mark = claim.scoreBand === 'verified' ? '✓' : claim.scoreBand === 'false' ? '×' : '!';
  return <span className={`badge score-${claim.scoreBand}`}><span aria-hidden="true">{mark}</span>{claim.scoreLabel}</span>;
}

function FactScore({claim}: {claim: Pick<Claim, 'id' | 'factScore' | 'scoreBand' | 'scoreLabel'>}) {
  return <div className="fact-score" data-score-band={claim.scoreBand} data-testid="fact-score" aria-label={`${claim.scoreLabel}, ${claim.factScore}점`}>
    <div className="fact-score-heading"><span>팩트 점수</span><span>0-100</span></div>
    <div className="fact-score-value"><CountUp key={`${claim.id}-${claim.factScore}`} from={0} to={claim.factScore} duration={1.1} separator=","/><span>점</span></div>
    <strong>{claim.scoreLabel}</strong>
  </div>;
}

function hasEnglishText(value: string) {
  return /[A-Za-z]/.test(value);
}

function YoutubeCommentContext({source}: {source: FactSource}) {
  if (source.sourceType !== '유튜브') return null;
  const statusText = source.youtubeDataStatus === 'collected'
    ? source.youtubeComments.length ? '수집 완료' : '댓글 없음'
    : source.youtubeDataStatus === 'not_configured'
      ? 'API 키 미설정'
      : '댓글 조회 불가';
  return <details className="youtube-comment-context">
    <summary><span>공개 댓글 {source.youtubeComments.length}개 · 의견 맥락</span><span>{statusText}</span></summary>
    <p className="source-caption">최대 10개의 공개 댓글입니다. 대표 의견을 뜻하지 않으며 AI 판정과 인용 근거에 사용하지 않습니다.</p>
    {source.youtubeDataStatus === 'collected' && source.youtubeComments.length
      ? <ol>{source.youtubeComments.map((comment, index) => <li key={`${source.id}-${index}`}>{comment}</li>)}</ol>
      : <p className="youtube-empty">{source.youtubeDataStatus === 'not_configured'
        ? 'backend/.env에 YOUTUBE_API_KEY를 설정하면 공개 댓글을 조회할 수 있습니다.'
        : source.youtubeDataStatus === 'collected'
          ? '표시할 공개 댓글이 없습니다.'
          : '댓글이 비활성화되었거나 API에서 가져오지 못했습니다.'}</p>}
  </details>;
}

function TrustIndex({score, claimCount, sourceCount, evidenceCount, warningCount}: {score: number | null; claimCount: number; sourceCount: number; evidenceCount: number; warningCount: number}) {
  const band = score === null ? 'neutral' : scoreBand(score);
  const ringStyle = score === null ? undefined : ({'--trust-score': `${score}%`} as CSSProperties);
  return <div className={`trust-index ${score === null ? 'is-empty' : ''}`} data-score-band={band}>
    <div className="trust-index-head">
      <div><span className="metric-label">종합 신뢰지수</span><h3>근거가 확인된 정도</h3></div>
      {score !== null && <span className={`score-label score-${band}`}>{scoreLabel(score)}</span>}
    </div>
    <div className="trust-index-main">
      <div className="trust-ring" style={ringStyle} aria-label={score === null ? '검증 대기 중' : `종합 신뢰지수 ${score}점`}>
        <div className="trust-ring-inner">{score === null ? <span className="trust-empty">대기</span> : <><CountUp key={`trust-${score}`} from={0} to={score} duration={1.2}/><small>/ 100</small></>}</div>
      </div>
      <div className="trust-copy">
        <strong>{score === null ? '검증을 시작하면 지수가 표시됩니다.' : '주장별 점수의 평균입니다.'}</strong>
        <p>{score === null ? '원문을 보내면 주장, 출처, 인용을 한 화면에서 연결해 볼 수 있습니다.' : '출처의 개수만으로 점수를 올리지 않고, 확인된 인용과 남은 불확실성을 함께 반영합니다.'}</p>
      </div>
    </div>
    <div className="dashboard-stats" aria-label="검증 요약">
      <div><span>검증 주장</span><strong>{claimCount}</strong></div>
      <div><span>검토 출처</span><strong>{sourceCount}</strong></div>
      <div><span>연결 근거</span><strong>{evidenceCount}</strong></div>
      <div><span>확인 필요</span><strong>{warningCount}</strong></div>
    </div>
  </div>;
}

type ChatMessage = {id: string; role: 'assistant' | 'user'; text?: string; answer?: FactCheckAnswer; sources?: FactSource[]; meta?: string; tone?: 'normal' | 'error'};
const WELCOME_MESSAGE: ChatMessage = {id: 'welcome', role: 'assistant', text: '확인하고 싶은 주장이나 원문을 보내줘. 문장을 나누고, 직접 확인할 수 있는 출처와 인용을 연결해볼게.'};

function Modal({open, title, onClose, children}: {open: boolean; title: string; onClose: () => void; children: ReactNode}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    if (open && !ref.current?.open) ref.current?.showModal();
    else if (!open && ref.current?.open) ref.current.close();
  }, [open]);
  return <dialog ref={ref} className="dialog" aria-labelledby="dialog-heading" onClose={onClose} onClick={event => {if (event.target === event.currentTarget) onClose();}}>
    <div className="dialog-head"><span className="eyebrow">True or Not · 근거 워크스페이스</span><button className="icon-button" onClick={onClose} aria-label="대화상자 닫기"><Icon name="close"/></button></div>
    <h2 id="dialog-heading">{title}</h2>{children}<button className="secondary-button dialog-done" onClick={onClose}>확인했습니다</button>
  </dialog>;
}

type PanelProps = {as?: 'div' | 'section' | 'article'; className?: string; children: ReactNode; 'aria-labelledby'?: string};
function Panel({as = 'div', className = '', children, 'aria-labelledby': labelledBy}: PanelProps) {
  const Element = as;
  return <Element className={`panel-host ${className}`} aria-labelledby={labelledBy}>{children}</Element>;
}

function AnswerBlockView({block, sources, citationState, messageId}: {block: AnswerBlock; sources: FactSource[]; citationState: ReturnType<typeof createAnswerCitationDisplayState>; messageId: string}) {
  const citations = presentAnswerCitations(block.citations, sources, citationState);
  return <div className="answer-block">
    <p className="answer-block-text">{block.text}</p>
    {citations.length > 0 && <ul className="answer-citations" aria-label="답변 근거 출처">
      {citations.map(({citation, number, source, href, linkTarget}) => <li key={citation.sourceId}>
          {linkTarget === 'external' && source && href
            ? <a id={answerCitationAnchorId(messageId, number)} className="answer-citation-chip" href={href} target="_blank" rel="noopener noreferrer" title={citation.quote} aria-label={`출처 ${number}: ${source.publisher}, ${source.title}. 새 탭에서 원문 열기`}>
                <span className="answer-citation-index">[{number}]</span><span>{source.publisher} · {source.title}</span><span aria-hidden="true">↗</span>
              </a>
            : linkTarget === 'reference' && source
              ? <a className="answer-citation-reference" href={`#${answerCitationAnchorId(messageId, number)}`} title={`${source.publisher} · ${source.title}`} aria-label={`출처 ${number} 다시 참조`}>
                  <span className="answer-citation-index">[{number}]</span>
                </a>
              : <span className="answer-citation-chip is-unavailable" aria-label={`출처 ${number}: 확인된 원문 연결 없음`}>
                <span className="answer-citation-index">[{number}]</span><span>확인된 원문 연결 없음</span>
              </span>}
        </li>)}
    </ul>}
  </div>;
}

function AnswerOverview({answer, sources, messageId}: {answer: FactCheckAnswer; sources: FactSource[]; messageId: string}) {
  const citationState = createAnswerCitationDisplayState(sources);
  return <section className="ai-answer" aria-label="AI 개요">
    <div className="ai-answer-heading"><span className="answer-spark" aria-hidden="true">✦</span><h3>AI 개요</h3></div>
    {answer.status === 'insufficient_evidence'
      ? <p className="answer-insufficient" role="note">확인된 원문 근거가 부족해 AI 개요를 만들지 않았어. 아래 출처 목록과 주장별 판정에서 확인 가능한 내용을 살펴봐.</p>
      : <>
          {answer.overview && <div className="answer-overview-block"><AnswerBlockView block={answer.overview} sources={sources} citationState={citationState} messageId={messageId}/></div>}
          {answer.sections.map((section, sectionIndex) => <section className={`answer-section answer-section--${section.kind}`} key={`${section.kind}-${sectionIndex}`} aria-label={section.title}>
            <h4>{section.title}</h4>
            <ul className="answer-section-items">{section.items.map((item, itemIndex) => <li key={itemIndex}><AnswerBlockView block={item} sources={sources} citationState={citationState} messageId={messageId}/></li>)}</ul>
          </section>)}
          {answer.conclusion && <section className="answer-conclusion" aria-label="정리">
            <h4>정리</h4><AnswerBlockView block={answer.conclusion} sources={sources} citationState={citationState} messageId={messageId}/>
          </section>}
        </>}
  </section>;
}

export default function FactCheckDashboard() {
  const reduce = useReducedMotion();
  const [state, dispatch] = useReducer(transition, initialState);
  const [draft, setDraft] = useState('');
  const [focus, setFocus] = useState('');
  const [sample, setSample] = useState(false);
  const [mobileTab, setMobileTab] = useState('results');
  const [dialog, setDialog] = useState<string | null>(null);
  const [notice, setNotice] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const request = useRef<AbortController | null>(null);
  const generation = useRef(0);
  const messageCounter = useRef(0);
  const [consent, setConsent] = useState(false);
  const [configured, setConfigured] = useState<boolean | null>(null);
  const [configuredModel, setConfiguredModel] = useState<string | null>(null);
  const [modelOptions, setModelOptions] = useState<ModelOption[]>([]);
  const [modelPreference, setModelPreference] = useState<ModelPreference>('auto');
  const [configError, setConfigError] = useState(false);
  const [liveResult, setLiveResult] = useState<FactCheckResult | null>(null);
  const editor = useRef<HTMLTextAreaElement>(null);
  const snapshot = state.snapshot;
  const selected = snapshot?.claims.find(claim => claim.id === state.selectedId);
  const sourceDocs = snapshot?.demo && selected ? documents.filter(document => selected.evidenceIds.includes(document.id)) : [];
  const activeDocument = documents.find(document => document.id === dialog);
  const busy = state.status === 'loading';
  const configurationHelp = '서버 설정이 필요합니다. backend/.env에 OPENAI_API_KEY 또는 GEMINI_API_KEY를 설정한 뒤 서버를 다시 시작해 주세요. 키를 화면이나 채팅에 입력하지 마세요.';
  const serviceLabel = configured === true ? 'LLM fallback 설정됨 · 접근 미확인' : configured === false ? 'LLM 키 미설정' : configError ? '설정 확인 실패' : '서버 설정 확인 중';
  const modelLabel = MODEL_OPTIONS.find(model => model.id === configuredModel)?.label
    ?? (configured === false ? '모델 미설정' : '모델 확인 중');
  const fallbackOrder = modelOptions.filter(model => model.configured).map(model => model.label).join(' → ');
  const trustScore = snapshot?.claims.length ? Math.round(snapshot.claims.reduce((total, claim) => total + claim.factScore, 0) / snapshot.claims.length) : null;
  const sourceCount = snapshot ? snapshot.demo ? documents.length : liveResult?.sources.length ?? 0 : 0;
  const evidenceCount = snapshot ? snapshot.demo ? snapshot.claims.reduce((total, claim) => total + claim.evidenceIds.length, 0) : liveResult?.evidence.length ?? 0 : 0;
  const warningCount = snapshot ? snapshot.demo ? snapshot.claims.filter(claim => claim.scoreBand !== 'verified').length : liveResult?.warnings.length ?? 0 : 0;
  const selectedEvidence = selected && liveResult ? liveResult.evidence.filter(evidence => evidence.claimId === selected.id && selected.evidenceIds.includes(evidence.id)) : [];
  const selectedLiveClaim = selected && liveResult ? liveResult.claims.find(claim => claim.id === selected.id) : null;
  const youtubeSources = liveResult?.sources.filter(source => source.sourceType === '유튜브') ?? [];
  const otherSources = liveResult?.sources.filter(source => source.sourceType !== '유튜브') ?? [];

  useEffect(() => {
    const controller = new AbortController();
    fetch('/api/fact-check', {signal: controller.signal, cache: 'no-store'})
      .then(async response => {
        if (!response.ok) throw new Error();
        const status = await response.json();
        if (typeof status.configured !== 'boolean' || !Array.isArray(status.modelOptions)) throw new Error();
        const options: ModelOption[] = MODEL_OPTIONS.map(model => {
          const option = status.modelOptions.find((candidate: unknown) => candidate && typeof candidate === 'object' && 'id' in candidate && candidate.id === model.id);
          if (!option || typeof option.configured !== 'boolean') throw new Error();
          return {...model, configured: option.configured};
        });
        if (!controller.signal.aborted) {
          setConfigured(status.configured);
          setConfiguredModel(typeof status.model === 'string' ? status.model : null);
          setModelOptions(options);
        }
      })
      .catch(() => {if (!controller.signal.aborted) setConfigError(true);});
    return () => {controller.abort(); generation.current++; request.current?.abort();};
  }, []);

  function addMessage(message: Omit<ChatMessage, 'id'>) {
    setMessages(current => [...current, {...message, id: `message-${messageCounter.current++}`}]);
  }

  function stop() {
    generation.current++;
    request.current?.abort();
    request.current = null;
  }

  function loadSample() {
    stop();
    setLiveResult(null);
    dispatch({type: 'cancel'});
    dispatch({type: 'load', snapshot: demoPreview});
    setDraft(DEMO_TEXT);
    setFocus(DEMO_FOCUS);
    setSample(true);
    setConsent(false);
    setMessages([
      WELCOME_MESSAGE,
      {id: 'sample-user', role: 'user', text: DEMO_TEXT, meta: `확인 요청: ${DEMO_FOCUS}`},
      {id: 'sample-assistant', role: 'assistant', text: '합성 예시를 준비했어. 아래 대시보드에서 주장별 점수와 같은 원자료를 공유하는 출처를 확인해봐.', meta: '외부 전송 없음'},
    ]);
    setNotice('가상의 행사 예시를 불러왔습니다. 외부 전송 없이 예시 문서를 비교합니다.');
  }

  function reset() {
    stop();
    setLiveResult(null);
    setConsent(false);
    dispatch({type: 'reset'});
    setDraft('');
    setFocus('');
    setSample(false);
    setMessages([WELCOME_MESSAGE]);
    setNotice('');
    editor.current?.focus();
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || request.current) return;
    if (!draft.trim()) {setNotice('검증할 원문을 입력해 주세요.'); return;}
    if (draft.length > 12000 || focus.length > 500) {setNotice('원문은 12,000자, 확인 요청은 500자 이내로 입력해 주세요.'); return;}
    if (sample) {dispatch({type: 'load', snapshot: {...demoPreview, focus}}); setNotice('합성 예시입니다. 실제 검증 요청은 전송하지 않았습니다.'); return;}
    if (configured === false) {setNotice(configurationHelp); return;}
    if (!consent) {setNotice('외부 전송과 유료 검증 안내를 확인하고 동의해 주세요.'); return;}

    stop();
    const controller = new AbortController();
    request.current = controller;
    const current = generation.current;
    const submitted = {text: draft, focus, consent: true as const, modelPreference};
    addMessage({role: 'user', text: draft, meta: focus ? `확인 요청: ${focus}` : undefined});
    setLiveResult(null);
    dispatch({type: 'reset'});
    dispatch({type: 'start'});
    setNotice('검증 요청을 서버로 전송하고 있습니다.');
    try {
      const response = await fetch('/api/fact-check', {method: 'POST', headers: {'content-type': 'application/json'}, body: JSON.stringify(submitted), signal: controller.signal});
      const result = await readFactCheckStream(response, {signal: controller.signal, onStage: stage => {if (generation.current === current) setNotice(stage.message);}});
      if (generation.current !== current || controller.signal.aborted) return;
      if (result.text !== submitted.text || result.focus !== submitted.focus) throw new Error('제출한 원문과 검증 결과가 일치하지 않습니다. 다시 시도해 주세요.');
      setLiveResult(result);
      dispatch({type: 'load', snapshot: result});
      setMobileTab('results');
      setNotice(result.claims.length ? '검증이 완료되었습니다. 아래에서 출처와 남은 불확실성을 확인해 주세요.' : '검증 가능한 주장을 찾지 못했습니다. 결과의 경고를 확인해 주세요.');
      const reply = composeAssistantReply(result);
      addMessage({role: 'assistant', ...reply});
    } catch (error) {
      if (generation.current !== current || controller.signal.aborted) return;
      dispatch({type: 'cancel'});
      const message = error instanceof FactCheckError && /CONFIG|KEY_MISSING/i.test(error.code) ? configurationHelp : error instanceof Error ? `검증 실패: ${error.message} 다시 시도하실 수 있습니다.` : '검증 요청에 실패했습니다. 네트워크를 확인하고 다시 시도해 주세요.';
      if (error instanceof FactCheckError && /CONFIG|KEY_MISSING/i.test(error.code)) setConfigured(false);
      setNotice(message);
      addMessage({role: 'assistant', text: message, tone: 'error'});
    } finally {
      if (generation.current === current) request.current = null;
    }
  }

  function download() {
    if (!snapshot) return;
    const exportResult = liveResult ? {...liveResult, sources: stripYoutubeApiDataForExport(liveResult.sources)} : liveResult;
    const content = snapshot.demo ? {title: 'True or Not 합성 예시', disclaimer: '실제 검증 결과가 아닙니다.', ...snapshot, documents} : {title: 'True or Not 검증 결과', disclaimer: 'AI 검증에는 오류가 있을 수 있습니다. 원출처를 확인해 주세요.', ...exportResult};
    const blobUrl = URL.createObjectURL(new Blob([JSON.stringify(content, null, 2)], {type: 'application/json;charset=utf-8'}));
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = snapshot.demo ? 'true-or-not-demo.json' : 'true-or-not-result.json';
    link.click();
    setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
    setNotice(snapshot.demo ? '합성 예시 JSON 다운로드를 요청했습니다.' : '원문·출처·불확실성을 포함한 검증 JSON 다운로드를 요청했습니다.');
  }

  const select = (id: string) => dispatch({type: 'select', id});
  const original = snapshot && (() => {
    const chunks: ReactNode[] = [];
    let cursor = 0;
    snapshot.claims.forEach((claim, index) => {
      chunks.push(snapshot.text.slice(cursor, claim.start));
      chunks.push(<button key={claim.id} className={`sentence ${claim.id === state.selectedId ? 'selected' : ''}`} aria-pressed={claim.id === state.selectedId} onClick={() => select(claim.id)}><span className="sentence-number">{String(index + 1).padStart(2, '0')}</span>{claim.quote}</button>);
      cursor = claim.end;
    });
    chunks.push(snapshot.text.slice(cursor));
    return chunks;
  })();

  return <MotionConfig reducedMotion="user"><div className="app-shell" id="top">
    <FloatingLinesBackground />
    <a className="skip-link" href="#workspace-main">본문으로 건너뛰기</a>
    <aside className="sidebar">
      <a className="brand" href="#top" aria-label="True or Not 홈"><span className="brand-symbol"><Icon name="lens" size={25}/></span><span><ScrambleText>True or Not</ScrambleText><small>TRUE OR NOT</small></span></a>
      <div className="workspace-label"><span className="workspace-avatar">F</span><div>나의 워크스페이스<small>대화형 팩트체크</small></div></div>
      <p className="nav-caption">워크스페이스</p>
      <LineSidebar
        className="workspace-nav"
        ariaLabel="주요 메뉴"
        items={[
          {label: '대화 시작', icon: <Icon name="plus"/>},
          {label: '검증 대시보드', icon: <Icon name="grid"/>},
          {label: '검증 원칙', icon: <Icon name="book"/>},
        ]}
        defaultActive={0}
        onItemClick={index => {
          if (index === 0) document.getElementById('top')?.scrollIntoView({behavior: reduce ? 'auto' : 'smooth', block: 'start'});
          if (index === 1) document.getElementById('review')?.scrollIntoView({behavior: reduce ? 'auto' : 'smooth', block: 'start'});
          if (index === 2) setDialog('guide');
        }}
      />
      <div className="sidebar-bottom"><div className="principle-card"><Icon name="shield"/><strong>결론보다, 근거를 먼저.</strong><p>확인된 내용과 아직 모르는 내용을 함께 살펴보세요.</p><button onClick={() => setDialog('guide')}>검증 원칙 보기 <Icon name="arrow" size={15}/></button></div><div className="local-status"><span/>{serviceLabel}</div><p className="sidebar-foot">TRUE OR NOT / EVIDENCE WORKSPACE</p></div>
    </aside>
    <div className="main-shell">
      <header className="topbar"><div className="breadcrumb"><span className="mobile-brand">True or Not</span><strong>대화형 팩트체크</strong></div><div className="topbar-actions"><button className="text-button" aria-label="사용 가이드" onClick={() => setDialog('guide')}><Icon name="book"/><span>사용 가이드</span></button><span className="profile-mark" aria-label="로컬 워크스페이스">F</span></div></header>
      <main id="workspace-main" className="page-content">
        <section className="composer panel-host chat-hero" aria-labelledby="chat-heading">
          <div className="chat-intro"><span className="chat-kicker"><Icon name="shield" size={15}/>근거를 연결하는 대화</span><h1 id="chat-heading">무엇을 확인해볼까요?</h1><p>주장이나 원문을 보내면, 확인된 사실과 남은 불확실성을 출처와 함께 보여줄게.</p></div>
          <div className="chat-thread" aria-live="polite">
            {messages.map(message => <motion.div key={message.id} className={`chat-message ${message.role === 'user' ? 'is-user' : 'is-assistant'} ${message.answer ? 'has-answer' : ''} ${message.tone === 'error' ? 'is-error' : ''}`} initial={reduce ? false : {opacity: 0, y: 10}} animate={{opacity: 1, y: 0}} transition={{duration: reduce ? 0 : .22}}>
              {message.role === 'assistant' && <span className="chat-avatar"><Icon name="lens" size={16}/></span>}
              <div className={`chat-bubble ${message.answer ? 'chat-bubble--answer' : ''}`}>
                {message.answer ? <AnswerOverview answer={message.answer} sources={message.sources ?? []} messageId={message.id}/> : message.text ? <p>{message.text}</p> : null}
                {message.meta && <small>{message.meta}</small>}
              </div>
            </motion.div>)}
            {busy && <div className="chat-message is-assistant chat-message--loading" data-testid="verification-loading"><span className="chat-avatar"><Icon name="lens" size={16}/></span><div className="chat-bubble"><div className="chat-loader-row"><LatticeLoader label="검증 중" doneLabel="검증 완료" errorLabel="검증 실패" pattern="orbit" grid={3} shape="round" cellSize={7} gap={3} fontSize={12} step={75} idleOpacity={0.15} glow color="#ffffff" showTimer/><span>{notice || '근거를 모으고 사실 여부를 대조하고 있습니다.'}</span></div></div></div>}
          </div>
          <form className="chat-form" onSubmit={submit}>
            <div className="chat-input-shell">
              <label className="sr-only" htmlFor="document-text">확인할 원문</label>
              <textarea ref={editor} id="document-text" value={draft} onChange={event => {setDraft(event.target.value); if (sample) {setSample(false); setMessages([WELCOME_MESSAGE]);}}} placeholder="확인하고 싶은 주장이나 원문을 입력해 주세요." rows={3} maxLength={12000} onKeyDown={event => {if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {event.preventDefault(); event.currentTarget.form?.requestSubmit();}}}/>
              <div className="chat-input-meta"><span>{draft.length.toLocaleString()} / 12,000</span><span>Ctrl + Enter로 보내기</span></div>
              <div className="chat-toolbar">
                <div className="chat-tools"><button type="button" className="chat-tool" onClick={() => setDialog('guide')}><Icon name="plus" size={17}/><span>검증 조건</span></button><span className="chat-tool is-static"><Icon name="link" size={16}/><span>웹 검색</span></span><label className="chat-focus-control" htmlFor="focus-request"><Icon name="lens" size={15}/><span>확인 요청</span><input id="focus-request" value={focus} maxLength={500} onChange={event => setFocus(event.target.value)} placeholder="선택 입력"/></label></div>
                <div className="chat-send-group">
                  <label className="chat-model-control">
                    <span className="sr-only">답변 모델</span>
                    <select id="model-preference" className="chat-model-select" aria-describedby="model-preference-help" value={modelPreference} onChange={event => setModelPreference(event.target.value as ModelPreference)} disabled={busy || configured !== true} title={modelPreference === 'auto' ? `자동 폴백 순서: ${fallbackOrder || modelLabel}` : '선택한 모델만 호출하며 다른 모델로 폴백하지 않습니다.'}>
                      <option value="auto">자동 폴백 · {fallbackOrder || modelLabel}</option>
                      {modelOptions.map(model => <option key={model.id} value={model.id} disabled={!model.configured}>{model.label}{model.configured ? '' : ' · API 키 미설정'}</option>)}
                    </select>
                  </label>
                  <span className="chat-model-policy">{modelPreference === 'auto' ? '순서대로 재시도' : '선택 모델만 사용'}</span>
                  <span id="model-preference-help" className="sr-only">자동은 설정된 Gemini 3.8 Flash, Gemini 3.7 Flash, GPT-6 Luna Max 순서로 시도합니다. 특정 모델을 선택하면 다른 모델로 폴백하지 않습니다.</span>
                  <button type="submit" className="chat-send" disabled={busy || !draft.trim()} aria-label={busy ? '검증 진행 중' : sample ? '예시 다시 보기' : '팩트 검증 시작'}><Icon name="arrow" size={19}/></button>
                </div>
              </div>
            </div>
            <div className="chat-footer"><div>{!sample && <><label className="consent-control"><input type="checkbox" checked={consent} onChange={event => setConsent(event.target.checked)} disabled={busy}/><span>원문·확인 요청의 외부 전송과 검색, YouTube Data API의 영상 제목·공개 댓글(최대 10개) 조회에 동의합니다. 댓글은 판정 근거로 사용하지 않습니다.</span></label><div className="consent-links"><a href="/privacy">개인정보 처리방침</a><a href="/terms">이용약관</a><a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener noreferrer">YouTube 약관</a><a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google 개인정보</a></div></>}{sample && <span className="sample-state"><Icon name="shield" size={14}/>합성 예시는 외부로 전송하지 않습니다.</span>}</div><button type="button" className="sample-chip" onClick={loadSample}>예시로 시작하기 <Icon name="arrow" size={14}/></button></div>
          </form>
          <div className={`chat-status ${busy ? 'is-busy' : ''}`} role="status" aria-live="polite">{busy ? notice || '검증을 진행하고 있습니다.' : notice || (configured === false ? configurationHelp : '원문을 입력하거나 예시로 시작해 근거를 확인해 보세요.')}</div>
        </section>

        <section id="review" className="review-section" aria-labelledby="review-heading">
          <div className="review-heading dashboard-heading"><div><span className="section-kicker">검증 대시보드</span><h2 id="review-heading">판정은 아래에서 근거를 만납니다.</h2><p>주장별 신뢰지수, 확인된 인용, 출처의 관계를 한 흐름으로 살펴보세요.</p></div><button className="secondary-button export-button" disabled={!snapshot || busy} onClick={download}><Icon name="download" size={16}/><span>{snapshot?.demo ? '예시 내보내기' : '결과 내보내기'}</span></button></div>
          {snapshot ? <>
            <div className="dashboard-meta"><span className="document-title"><Icon name={snapshot.demo ? 'book' : 'file'} size={16}/>{snapshot.demo ? '합성 예시 · 외부 전송 없음' : '직접 입력한 원문 · 실제 검증'}</span><div><span>{snapshot.claims.length}개 주장</span><span>{sourceCount}개 출처</span><span>{snapshot.demo ? '시연용 데이터' : liveResult?.checkedAt || '검증 시점 기록됨'}</span></div></div>
            <div className="dashboard-top-grid">
              <Panel className="trust-panel"><TrustIndex score={trustScore} claimCount={snapshot.claims.length} sourceCount={sourceCount} evidenceCount={evidenceCount} warningCount={warningCount}/></Panel>
              <Panel className="claim-panel"><div className="panel-top"><h3><Icon name="grid" size={17}/>주장별 점수</h3><span>선택하면 근거가 바뀝니다</span></div><div className="claim-selector" aria-label="주장 후보 선택">{snapshot.claims.map((claim, index) => <motion.button key={claim.id} layout={!reduce} className={`claim-card ${selected?.id === claim.id ? 'is-selected' : ''}`} aria-pressed={selected?.id === claim.id} onClick={() => select(claim.id)}><div className="claim-card-top"><span>주장 {String(index + 1).padStart(2, '0')}</span><Badge claim={claim}/></div><div className="claim-card-score"><strong>{claim.factScore}</strong><span>점</span></div><p>{claim.quote}</p><span className="claim-card-bottom">{selected?.id === claim.id ? '선택한 주장' : '근거 살펴보기'}<Icon name={selected?.id === claim.id ? 'check' : 'arrow'} size={15}/></span></motion.button>)}</div></Panel>
            </div>
            <div className="mobile-tabs" role="group" aria-label="검토 화면 선택"><button aria-pressed={mobileTab === 'original'} onClick={() => setMobileTab('original')}>원문</button><button aria-pressed={mobileTab === 'results'} onClick={() => setMobileTab('results')}>결과</button><button aria-pressed={mobileTab === 'sources'} onClick={() => setMobileTab('sources')}>출처</button></div>
            <div className={`dashboard-detail-layout mobile-${mobileTab}`}>
              <Panel as="article" className="original-panel"><div className="panel-top"><h3><Icon name="file" size={17}/>원문</h3><span>{snapshot.demo ? '합성 문서' : '제출한 원문'}</span></div><div className="original-content"><span className="article-kicker">{snapshot.demo ? '문화 행사 · 가상의 사례' : '검증 요청 시점의 원문'}</span><h3>{snapshot.demo ? '달빛시 가을빛 축제, 알아두면 좋은 내용' : '검증한 원문'}</h3><p className="article-byline">{snapshot.demo ? 'True or Not 예시 편집실 · 실제 기사 아님' : '원문을 보존한 상태로 주장을 추출했습니다.'}</p><div className="original-text">{original}</div><div className="highlight-legend"><span/>강조된 문장을 선택하면 오른쪽 근거가 바뀝니다.</div>{snapshot.focus && <div className="focus-note"><Icon name="lens" size={17}/><div><strong>확인하고 싶은 내용</strong><p>{snapshot.focus}</p><small>{snapshot.demo ? '예시의 비교 범위를 보여드립니다.' : '검증의 참고 범위로 전달했습니다.'}</small></div></div>}</div><div className="original-footer"><Icon name="shield" size={15}/>{snapshot.demo ? '실제 인물·지역·사건과 무관한 합성 예시입니다.' : '원문에서 추출한 최대 3개의 주장을 검증합니다.'}</div></Panel>
              <Panel className="evidence-panel"><div className="panel-top"><h3><Icon name="lens" size={18}/>선택한 주장과 근거</h3><span>{snapshot.demo ? '예시 비교' : '수집된 원문 비교'}</span></div><AnimatePresence mode="wait" initial={false}><motion.div className="detail-content" key={selected?.id || 'empty'} initial={reduce ? false : {opacity: 0, y: 5}} animate={{opacity: 1, y: 0}} exit={{opacity: 0}} transition={{duration: reduce ? 0 : 0.18}}>{selected ? <>
                <div className="result-overview"><span className="article-kicker">선택한 주장</span><h3>{selected.quote}</h3><FactScore claim={selected}/><Badge claim={selected}/><p>{selected.summary}</p></div>
                <div className="source-content"><div className="source-heading"><h4>근거 출처</h4><span>{snapshot.demo ? `${sourceDocs.length}개 연결` : `${selectedEvidence.length}개 인용 · ${liveResult?.sources.length ?? 0}개 검색`}</span></div>
                  {snapshot.demo ? sourceDocs.length ? <><div className="comparison-note"><span className="group-symbol">A</span><p><strong>같은 원자료를 공유합니다.</strong><br/>출처 2개가 독립적인 근거 2개를 뜻하지 않습니다.</p></div>{sourceDocs.map((source, index) => <button className="source-card" key={source.id} onClick={() => setDialog(source.id)}><div className="source-card-top"><span className="source-index">{String(index + 1).padStart(2, '0')}</span><span className="source-kind">{source.relation} · 예시</span><Icon name="arrow" size={16}/></div><strong>{source.title}</strong><span className="source-publisher">{source.publisher} · {source.date}</span><blockquote>“{selected.id === 'claim-1' ? source.id === 'doc-1' ? '가을빛 축제는 10월 12일부터 14일까지 달빛공원에서 진행합니다.' : '행사는 10월 12일부터 14일까지 열립니다.' : source.id === 'doc-1' ? '공예 체험은 사전 예약이 필요하며 재료비 5,000원이 있습니다.' : '공예 체험은 별도 예약과 재료비가 필요합니다.'}”</blockquote><span className="source-footer">원자료 그룹 A <span>전문 보기</span></span></button>)}<p className="evidence-caution">인용은 시연용 문서 전문에서 확인해 주세요. 실제 검색 결과가 아닙니다.</p></> : <div className="empty-evidence"><Icon name="file" size={27}/><h4>비교할 근거가 없습니다</h4><p>미래 전망을 현재 사실로 확정하지 않습니다. 예시 문서에도 방문객 추정 근거는 없습니다.</p></div> : selectedEvidence.length ? <>{selectedEvidence.map((evidence, index) => {const source = liveResult?.sources.find(item => item.id === evidence.sourceId); const href = source && safeSourceUrl(source.url); return <article className="source-card" key={evidence.id}><div className="source-card-top"><span className="source-index">{String(index + 1).padStart(2, '0')}</span><span className="source-kind">{source?.sourceType || '출처'} · {evidence.relation === 'supports' ? '지지 근거' : evidence.relation === 'contradicts' ? '반박 근거' : '맥락 근거'}</span><span className="source-verified">{evidence.quoteVerified ? '인용 확인' : '확인 필요'}</span></div>{href ? <a className="source-title-link" href={href} target="_blank" rel="noopener noreferrer">{source?.title || '출처 열기'} <Icon name="arrow" size={14}/></a> : <strong>{source?.title || '출처 확인 불가'}</strong>}<span className="source-publisher">{source?.publisher || '발행 기관 미확인'} · {source?.publishedAt || '발행일 미확인'}</span><blockquote>“{evidence.quote}”</blockquote>{hasEnglishText(evidence.quote) && evidence.quoteTranslation ? <div className="source-translation"><span>한국어 번역</span><p>{evidence.quoteTranslation}</p></div> : null}<p className="source-caption">원문 인용 일치 확인 · 출처 독립성은 별도 확인이 필요합니다.</p></article>;})}</> : <div className="empty-evidence"><Icon name="file" size={27}/><h4>비교할 근거가 없습니다</h4><p>근거 부족은 거짓을 뜻하지 않습니다. 확인 가능한 원문이 없다는 의미입니다.</p></div>}
                </div>
                {!snapshot.demo && !selectedEvidence.length && otherSources.length ? <div className="source-candidate-list"><p className="evidence-caution">출처별 검색 경로와 순위를 확인해. Google 자연검색 순위는 그렇게 표시된 출처에만 해당하고, 아직 선택한 주장과 직접 대조된 인용은 아니야.</p>{otherSources.map((source, index) => {const href = safeSourceUrl(source.url); return <article className="source-card" key={source.id}><div className="source-card-top"><span className="source-index">{String(index + 1).padStart(2, '0')}</span><span className="source-kind">{source.sourceType || '검색 출처'}</span><span className="source-verified">{source.accessStatus === 'verified' ? '원문 확인' : '접근 불가'}</span></div>{href ? <a className="source-title-link" href={href} target="_blank" rel="noopener noreferrer">{source.title} <Icon name="arrow" size={14}/></a> : <strong>{source.title}</strong>}<span className="source-publisher">{source.publisher} · {source.publishedAt || '발행일 미확인'}</span><p className="source-caption">{sourceDiscoveryLabel(source)} · 원문 인용이 연결되기 전에는 판정 근거로 사용하지 않습니다.</p></article>;})}</div> : null}
                {!snapshot.demo && youtubeSources.length > 0 ? <section className="youtube-context-list" aria-label="유튜브 영상 제목과 공개 댓글"><div className="source-heading"><h4>유튜브 영상 제목·공개 댓글</h4><span>참고 맥락 · 판정 근거 아님</span></div>{youtubeSources.map(source => {const href = safeSourceUrl(source.url); return <article className="youtube-context-card" key={source.id}>{href ? <a className="source-title-link" href={href} target="_blank" rel="noopener noreferrer">{source.youtubeTitle || source.title} <Icon name="arrow" size={14}/></a> : <strong>{source.youtubeTitle || source.title}</strong>}<YoutubeCommentContext source={source}/></article>;})}</section> : null}
                {!snapshot.demo && selectedLiveClaim && <div className="detail-blocks"><div><h4>확인된 내용</h4>{selectedLiveClaim.confirmed.length ? <ul>{selectedLiveClaim.confirmed.map((text, index) => <li key={index}>{text}</li>)}</ul> : <p>직접 확인된 내용이 없습니다.</p>}</div><div><h4>남은 불확실성</h4>{selectedLiveClaim.unresolved.length ? <ul>{selectedLiveClaim.unresolved.map((text, index) => <li key={index}>{text}</li>)}</ul> : <p>현재 기록된 불확실성이 없습니다.</p>}</div>{selectedLiveClaim.warnings.length > 0 && <div><h4>주장별 주의사항</h4><ul>{selectedLiveClaim.warnings.map((text, index) => <li key={index}>{text}</li>)}</ul></div>}</div>}
              </> : <div className="empty-evidence"><Icon name="lens" size={27}/><h4>주장을 선택해 주세요</h4><p>위의 주장 카드를 선택하면 연결된 출처와 인용이 표시됩니다.</p></div>}</motion.div></AnimatePresence></Panel>
              <Panel className="source-index-panel"><div className="panel-top"><h3><Icon name="book" size={17}/>검토한 출처</h3><span>{sourceCount}개 수집</span></div><div className="source-index-grid">{snapshot.demo ? documents.map((source, index) => <button className="source-index-card" key={source.id} onClick={() => setDialog(source.id)}><span className="source-index-number">{String(index + 1).padStart(2, '0')}</span><span><strong>{source.title}</strong><small>{source.publisher}</small></span><Icon name="arrow" size={15}/></button>) : liveResult?.sources.map((source, index) => {const href = safeSourceUrl(source.url); const sourceLabel = source.sourceType === '유튜브' ? source.youtubeDataStatus === 'collected' ? `공개 댓글 ${source.youtubeComments.length}개` : source.youtubeDataStatus === 'not_configured' ? '댓글 API 미설정' : '댓글 조회 불가' : source.accessStatus === 'verified' ? '원문 확인' : '접근 불가'; const content = <><span className="source-index-number">{String(index + 1).padStart(2, '0')}</span><span><strong>{source.youtubeTitle || source.title}</strong><small>{source.sourceType} · {source.publisher} · {sourceDiscoveryLabel(source)} · {sourceLabel}</small></span><Icon name="arrow" size={15}/></>; return href ? <a className="source-index-card" href={href} target="_blank" rel="noopener noreferrer" key={source.id}>{content}</a> : <div className="source-index-card" key={source.id}>{content}</div>;})}{!sourceCount && <div className="source-index-empty">아직 수집된 출처가 없습니다.</div>}</div></Panel>
            </div>
          </> : <Panel className="dashboard-empty"><div className="empty-orbit"><Icon name="lens" size={31}/></div><h3>검증 결과가 이곳에 쌓입니다.</h3><p>대화창에 원문을 보내면 주장별 신뢰지수와 근거 출처를 연결해 보여드립니다.</p><div className="empty-preview-stats"><span><strong>--</strong><small>신뢰지수</small></span><span><strong>--</strong><small>검토 출처</small></span><span><strong>--</strong><small>연결 근거</small></span></div><button className="secondary-button" onClick={loadSample}>예시 대시보드 보기 <Icon name="arrow"/></button></Panel>}
        </section>
        <footer className="page-footer"><span><span className="footer-mark">F</span>True or Not <span className="footer-divider">/</span>판단을 대신하지 않고, 근거를 연결합니다.</span><button className="text-button" onClick={() => setDialog('guide')}>검증 원칙<Icon name="arrow" size={15}/></button></footer>
      </main>
    </div>
    <Modal open={dialog !== null} title={activeDocument?.title || (dialog === 'guide' ? '근거를 읽는 세 가지 원칙' : '검증 안내')} onClose={() => setDialog(null)}>{activeDocument ? <><p className="dialog-notice">합성 예시 문서 · 외부 출처 링크가 아닙니다.</p><dl className="document-metadata"><dt>작성 주체</dt><dd>{activeDocument.publisher}</dd><dt>설정 날짜</dt><dd>{activeDocument.date}</dd><dt>원자료 관계</dt><dd>그룹 {activeDocument.group} · {activeDocument.relation}</dd></dl><div className="document-fulltext">{activeDocument.text}</div></> : dialog === 'guide' ? <ol className="guide-list"><li><span>01</span><div><h3>주장을 작게 나누세요.</h3><p>누가, 언제, 어디서, 어떤 조건으로 한 말인지 원문과 함께 확인하세요.</p></div></li><li><span>02</span><div><h3>출처의 수보다 관계를 보세요.</h3><p>같은 발표를 옮긴 여러 문서는 하나의 원자료를 공유할 수 있습니다.</p></div></li><li><span>03</span><div><h3>모르는 것은 남겨 두세요.</h3><p>근거가 없다고 거짓은 아닙니다. 의견과 미래 예측을 확정된 사실처럼 판정하지 않습니다.</p></div></li></ol> : <div className="about-copy"><p>동의 후 검증을 시작하면 원문과 확인 요청은 서버, 외부 AI 및 검색 서비스로 전송됩니다. 관련 YouTube 영상 제목과 공개 댓글 최대 10개는 YouTube Data API로 조회할 수 있습니다. 댓글은 LLM 입력 및 판정 근거로 사용하지 않습니다.</p><p>검증 결과와 YouTube 댓글은 현재 화면 메모리에만 유지되며 새로고침하면 사라집니다. YouTube API 제목·댓글은 JSON 내보내기에서 제외됩니다. 자세한 내용은 <a href="/privacy">개인정보 처리방침</a>과 <a href="/terms">이용약관</a>을 확인해 주세요.</p></div>}</Modal>
  </div></MotionConfig>;
}
