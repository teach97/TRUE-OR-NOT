"use client";

import { AnimatePresence, MotionConfig, motion, useReducedMotion } from 'motion/react';
import { useEffect, useReducer, useRef, useState } from 'react';
import type { CSSProperties, FormEvent, ReactNode } from 'react';
import { initialState, transition } from './demo-state';
import type { Claim } from './demo-state';
import { MODEL_OPTIONS } from '../lib/fact-check-contract';
import type { AgentStage, AnswerBlock, AttachedImage, FactCheckAnswer, FactCheckRequest, FactCheckResult, FactSource, ModelOption, ModelPreference, ProgressClaim, ProgressSource } from '../lib/fact-check-contract';
import { sourceDiscoveryLabel } from '../lib/source-discovery';
import { scoreBand, scoreLabel } from '../lib/fact-score';
import { formatYoutubePublishedAt, formatYoutubeViewCount, stripYoutubeApiDataForExport, youtubeThumbnailUrl } from '../lib/youtube-context';
import { FactCheckError, readFactCheckStream, safeSourceUrl } from './fact-check-client';
import { composeAssistantReply, createAnswerCitationDisplayState, presentAnswerCitations } from './fact-check-reply';
import { classifyChatInput, describeHistory, isFollowUpText, metaReply } from './chat-intent';
import { DEMO_FOCUS, DEMO_TEXT, demoPreview, documents } from './demo-fixture';
import ScrambleText from './scramble-text';
import FloatingLinesBackground from './floating-lines-background';
import LineSidebar from './line-sidebar';
import CountUp from './count-up';
import LatticeLoader from './lattice-loader';
import BlurText from './blur-text';
import { useSpotlight } from './spotlight';
import VectorWordmark from './vector-wordmark';

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

const YOUTUBE_AVATAR_PALETTES = [
  {background: '#3b3d40', skin: '#c7c7c7', hair: '#242629', shirt: '#77797d'},
  {background: '#303236', skin: '#b8b9bb', hair: '#17191b', shirt: '#62656a'},
  {background: '#45474b', skin: '#d0d0d0', hair: '#303236', shirt: '#85878a'},
  {background: '#35373a', skin: '#c0c1c2', hair: '#202225', shirt: '#707276'},
  {background: '#414347', skin: '#d4d4d4', hair: '#292b2e', shirt: '#66696e'},
  {background: '#2e3033', skin: '#bfc0c1', hair: '#101214', shirt: '#7d7f82'},
];
const YOUTUBE_AVATAR_HAIR = [
  'M10 21c0-8 4-13 10-13s10 5 10 13c-3-3-6-4-10-4s-7 1-10 4Z',
  'M9 22c-1-9 3-14 11-14s12 5 11 14c-2-2-3-5-4-8-4 4-10 6-18 8Z',
  'M9 20c0-8 4-12 11-12 8 0 11 5 11 12l-4-2c-2-4-5-6-8-6s-7 2-9 8Z',
  'M10 21c-1-7 3-13 10-13 8 0 11 5 10 13-3-4-5-6-10-6s-7 2-10 6Z',
  'M9 22c0-9 4-14 11-14 8 0 12 6 11 14-3-2-4-4-5-8-4 4-10 6-17 8Z',
  'M10 21c0-8 4-13 10-13 7 0 10 5 10 13-2-2-5-4-10-4s-8 2-10 4Z',
];

function YoutubeCommentAvatar({sourceId, index}: {sourceId: string; index: number}) {
  let hash = 2166136261;
  const seed = `${sourceId}:${index}`;
  for (let offset = 0; offset < seed.length; offset += 1) hash = Math.imul(hash ^ seed.charCodeAt(offset), 16777619);
  const variant = (hash >>> 0) % YOUTUBE_AVATAR_PALETTES.length;
  const palette = YOUTUBE_AVATAR_PALETTES[variant];
  return <span className="youtube-comment-avatar" aria-hidden="true">
    <svg viewBox="0 0 40 40" focusable="false">
      <circle cx="20" cy="20" r="20" fill={palette.background}/>
      <path d="M3 40c1-8 7-12 17-12s16 4 17 12Z" fill={palette.shirt}/>
      <ellipse cx="20" cy="21" rx="8.7" ry="10.5" fill={palette.skin}/>
      <path d={YOUTUBE_AVATAR_HAIR[variant]} fill={palette.hair}/>
      {variant === 1 || variant === 4 ? <path d="M10 19v11l4 2V20m16-1v12l-4 1V20" fill={palette.hair}/> : null}
      <circle cx="17" cy="22" r=".8" fill="#333538"/>
      <circle cx="23" cy="22" r=".8" fill="#333538"/>
      <path d="M18 26q2 1.5 4 0" fill="none" stroke="#77797b" strokeWidth=".9" strokeLinecap="round"/>
    </svg>
  </span>;
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
    <p className="source-caption">최대 10개의 공개 댓글입니다. 대표 의견을 뜻하지 않으며 AI 판정과 인용 근거에 사용하지 않습니다. 왼쪽 그림은 실제 작성자 사진이 아닌 임의 생성 이미지입니다.</p>
    {source.youtubeDataStatus === 'collected' && source.youtubeComments.length
      ? <ol>{source.youtubeComments.map((comment, index) => <li className="youtube-comment-row" key={`${source.id}-${index}`}><YoutubeCommentAvatar sourceId={source.id} index={index}/><span className="youtube-comment-text">{comment}</span></li>)}</ol>
      : <p className="youtube-empty">{source.youtubeDataStatus === 'not_configured'
        ? 'backend/.env에 YOUTUBE_API_KEY를 설정하면 공개 댓글을 조회할 수 있습니다.'
        : source.youtubeDataStatus === 'collected'
          ? '표시할 공개 댓글이 없습니다.'
          : '댓글이 비활성화되었거나 API에서 가져오지 못했습니다.'}</p>}
  </details>;
}

function YoutubeThumbnail({source}: {source: FactSource}) {
  const [failed, setFailed] = useState(false);
  const thumbnailUrl = youtubeThumbnailUrl(source.url);
  const title = source.youtubeTitle || source.title;
  const image = thumbnailUrl && !failed
    ? <img className="youtube-thumbnail" src={thumbnailUrl} alt="" loading="lazy" decoding="async" referrerPolicy="no-referrer" onError={() => setFailed(true)}/>
    : <span className="youtube-thumbnail-fallback" aria-hidden="true">미리보기 없음</span>;
  const href = safeSourceUrl(source.url);

  return href
    ? <a className="youtube-thumbnail-frame" href={href} target="_blank" rel="noopener noreferrer" aria-label={`${title} 영상 보기`}>{image}</a>
    : <div className="youtube-thumbnail-frame">{image}</div>;
}

function YoutubeVideoMetadata({source}: {source: FactSource}) {
  const publishedAt = formatYoutubePublishedAt(source.youtubePublishedAt);
  const viewCount = formatYoutubeViewCount(source.youtubeViewCount);
  return <div className="youtube-video-metadata" aria-label="유튜브 영상 정보">
    <span><small>채널</small>{source.youtubeChannelTitle || '확인 불가'}</span>
    <span><small>게시일</small>{publishedAt || '확인 불가'}</span>
    <span><small>조회수</small>{viewCount || '확인 불가'}</span>
  </div>;
}

function TrustIndex({score, claimCount, sourceCount, evidenceCount, warningCount}: {score: number | null; claimCount: number; sourceCount: number; evidenceCount: number; warningCount: number}) {
  const band = score === null ? 'neutral' : scoreBand(score);
  const ringStyle = score === null ? undefined : ({'--trust-score': `${score}%`} as CSSProperties);
  return <div className={`trust-index ${score === null ? 'is-empty' : ''}`} data-score-band={band}>
    <div className="trust-index-head">
      <div><span className="metric-label">종합 신뢰지수</span><h3>팩트 점수</h3></div>
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

type ChatProgress = {
  status?: string; statusElapsedSeconds?: number; statusStage?: AgentStage;
  sourcesFound?: ProgressSource[]; sourcesFoundElapsedSeconds?: number;
  sourcesRead?: ProgressSource[]; sourcesReadElapsedSeconds?: number;
  claims?: ProgressClaim[]; claimsElapsedSeconds?: number; completed?: boolean; error?: string;
};
type ChatMessage = {id: string; role: 'assistant' | 'user'; text?: string; answer?: FactCheckAnswer; sources?: FactSource[]; progress?: ChatProgress; meta?: string; tone?: 'normal' | 'error'; imagePreview?: string};
const WELCOME_MESSAGE: ChatMessage = {id: 'welcome', role: 'assistant', text: '확인하고 싶은 주장이나 원문을 보내주세요. 문장을 나누고, 직접 확인할 수 있는 출처와 인용을 연결하겠습니다.'};

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

function AnswerBlockView({block, sources, citationState}: {block: AnswerBlock; sources: FactSource[]; citationState: ReturnType<typeof createAnswerCitationDisplayState>}) {
  const citations = presentAnswerCitations(block.citations, sources, citationState);
  return <div className="answer-block">
    <p className="answer-block-text">{block.text}</p>
    {citations.length > 0 && <ul className="answer-citations" aria-label="답변 근거 출처">
      {citations.map(({number, source, href, linkTarget}, index) => <li key={`${number}-${index}`}>
          {linkTarget === 'external' && source && href
            ? <a className="answer-citation-chip" href={href} target="_blank" rel="noopener noreferrer" title={source.title} aria-label={`출처 ${number}: ${source.title} (${source.publisher}). 새 탭에서 원문 열기`}>
                <span className="answer-citation-index">[{number}]</span><span className="answer-citation-title">{source.title}</span><span aria-hidden="true">↗</span>
              </a>
              : <span className="answer-citation-chip is-unavailable" aria-label={`출처 ${number}: 확인된 원문 연결 없음`}>
                <span className="answer-citation-index">[{number}]</span><span className="answer-citation-title">확인된 원문 링크 없음</span>
              </span>}
        </li>)}
    </ul>}
  </div>;
}

function AnswerOverview({answer, sources}: {answer: FactCheckAnswer; sources: FactSource[]; messageId: string}) {
  const citationState = createAnswerCitationDisplayState(sources);
  return <section className="ai-answer" aria-label="AI 개요">
    <div className="ai-answer-heading"><span className="answer-spark" aria-hidden="true">✦</span><h3><BlurText text="AI 개요"/></h3></div>
    {answer.status === 'insufficient_evidence'
      ? <p className="answer-insufficient" role="note">확인된 원문 근거가 부족해 AI 개요를 만들지 않았어. 아래 출처 목록과 주장별 판정에서 확인 가능한 내용을 살펴봐.</p>
      : <>
          {answer.overview && <div className="answer-overview-block"><AnswerBlockView block={answer.overview} sources={sources} citationState={citationState}/></div>}
          {answer.sections.map((section, sectionIndex) => <section className={`answer-section answer-section--${section.kind}`} key={`${section.kind}-${sectionIndex}`} aria-label={section.title}>
            <h4>{section.title}</h4>
            <ul className="answer-section-items">{section.items.map((item, itemIndex) => <li key={itemIndex}><AnswerBlockView block={item} sources={sources} citationState={citationState}/></li>)}</ul>
          </section>)}
          {answer.conclusion && <section className="answer-conclusion" aria-label="정리">
            <h4>정리</h4><AnswerBlockView block={answer.conclusion} sources={sources} citationState={citationState}/>
          </section>}
        </>}
  </section>;
}

const VERIFY_STAGES: Array<{id: AgentStage; label: string}> = [
  {id: 'extracting', label: '추출'},
  {id: 'searching', label: '검색'},
  {id: 'reading', label: '읽기'},
  {id: 'verifying', label: '검증'},
  {id: 'synthesizing', label: '합성'},
];

function VerifyTimeline({progress}: {progress: ChatProgress}) {
  if (!progress.statusStage && !progress.completed && !progress.error) return null;
  const currentIndex = progress.completed
    ? VERIFY_STAGES.length
    : Math.max(0, VERIFY_STAGES.findIndex(stage => stage.id === progress.statusStage));
  return <ol className="verify-timeline" aria-label="검증 단계 진행">
    {VERIFY_STAGES.map((stage, index) => <li key={stage.id} data-state={index < currentIndex ? 'done' : index === currentIndex ? 'active' : 'todo'}><span className="verify-timeline-dot" aria-hidden="true"/><span>{stage.label}</span></li>)}
  </ol>;
}

function ProgressReply({progress}: {progress: ChatProgress}) {
  const claims = progress.claims;
  const sources = progress.sourcesRead ?? [];
  const sourceNumbers = new Map(sources.map((source, index) => [source.id, index + 1]));
  const heading = claims !== undefined ? '1차 검증 요약' : '검증 진행 상황';
  return <section className="progress-reply" data-testid="progress-reply" aria-label="검증 진행 결과">
    <div className="progress-reply-heading"><span aria-hidden="true">✦</span><h3><BlurText text={heading}/></h3><span className="progress-reply-status">{progress.error ? '중단' : progress.completed ? '완료' : '중간 업데이트'}</span></div>
    <VerifyTimeline progress={progress}/>
    {progress.status && <p className="progress-current-stage" data-testid="progress-stage">
      <span>{progress.status}</span><time>{progress.statusElapsedSeconds ?? 0}초 경과</time>
    </p>}
    {progress.sourcesFound !== undefined && progress.sourcesRead === undefined && <ProgressSourceList title="검색된 출처 후보" sources={progress.sourcesFound} elapsedSeconds={progress.sourcesFoundElapsedSeconds} testId="progress-candidate-source"/>}
    {progress.sourcesRead !== undefined && <ProgressSourceList title="가져온 원문" sources={progress.sourcesRead} elapsedSeconds={progress.sourcesReadElapsedSeconds} testId="progress-read-source"/>}
    {claims !== undefined && (claims.length
      ? <ol className="progress-claim-list">{claims.map(claim => <li className="progress-claim" key={claim.id}>
          <div className="progress-claim-heading"><strong>{claim.quote}</strong><span>{claim.verdict}</span></div>
          <p>{claim.summary}</p>
          {claim.citations.length > 0 && <ul className="progress-citations" aria-label="1차 요약의 확인된 인용">{claim.citations.map((citation, index) => {
            const source = sources.find(item => item.id === citation.sourceId);
            const href = source ? safeSourceUrl(source.url) : null;
            const number = sourceNumbers.get(citation.sourceId) ?? index + 1;
            return <li key={`${claim.id}-${citation.sourceId}-${index}`}>{source && href
              ? <a href={href} target="_blank" rel="noopener noreferrer" title={citation.quote} aria-label={`출처 ${number}: ${source.publisher}, ${source.title}`}>
                  <span>[{number}]</span> {source.title}
                </a>
              : <span className="progress-citation-unavailable">인용 출처 확인 필요</span>}</li>;
          })}</ul>}
        </li>)}</ol>
        : <p className="progress-empty">검증 가능한 주장을 찾지 못했어. 확인할 원문·링크·이미지를 보내주면 검증할게.</p>)}
        {claims !== undefined && progress.claimsElapsedSeconds !== undefined && <small className="progress-milestone-time">1차 요약 · {progress.claimsElapsedSeconds}초</small>}
        {progress.error
          ? <p className="progress-error" role="alert">{progress.error}<br/>위 내용은 최종 답변이 아닌 1차 확인 결과야.</p>
          : <small className="progress-disclaimer">{progress.completed ? '검증 진행 기록이야. 최종 답변은 아래에 이어져.' : '최종 인용 답변을 만드는 중이야. 이 1차 요약은 완성된 답변이 아니야.'}</small>}
        </section>;
        }

        function ProgressSourceList({title, sources, elapsedSeconds, testId}: {title: string; sources: ProgressSource[]; elapsedSeconds?: number; testId: string}) {
        return <div className="progress-source-block" data-testid={`${testId}-group`}>
        <h4>{title}{elapsedSeconds !== undefined && <span className="progress-milestone-time"> · {elapsedSeconds}초</span>}</h4>
        {sources.length > 0
        ? <ul className="progress-source-list">{sources.map((source, index) => {
            const href = safeSourceUrl(source.url);
            const accessLabel = source.accessStatus === 'candidate' ? '검색 후보' : source.accessStatus === 'verified' ? '원문 확인' : '접근 불가';
            return <li className="progress-source" key={source.id} data-testid={testId}>
              <span className="progress-source-index">[{index + 1}]</span>
              <span className="progress-source-copy">{href
                ? <a href={href} target="_blank" rel="noopener noreferrer">{source.title}</a>
                : <strong>{source.title}</strong>}<small>{source.publisher} · {source.sourceType} · {accessLabel}</small></span>
            </li>;
          })}</ul>
        : <p className="progress-empty">이 단계에서 확인된 출처가 없어. 다음 검증 단계를 진행하고 있어.</p>}
        </div>;
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
  const [image, setImage] = useState<{mime: AttachedImage['mime']; data: string; preview: string} | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const [configured, setConfigured] = useState<boolean | null>(null);
  const [configuredModel, setConfiguredModel] = useState<string | null>(null);
  const [modelOptions, setModelOptions] = useState<ModelOption[]>([]);
  const [modelPreference, setModelPreference] = useState<ModelPreference>('auto');
  const [configError, setConfigError] = useState(false);
  const [liveResult, setLiveResult] = useState<FactCheckResult | null>(null);
  const spotlight = useSpotlight<HTMLElement>();
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
    const id = `message-${messageCounter.current++}`;
    setMessages(current => [...current, {...message, id}]);
    return id;
  }

  function stop() {
    generation.current++;
    request.current?.abort();
    request.current = null;
  }

  function firstUrl(text: string): string | null {
    const match = text.match(/https?:\/\/[^\s)\]]+/);
    if (!match) return null;
    return safeSourceUrl(match[0].replace(/[.,;:!?)\]]+$/, ''));
  }

  async function downscaleImage(file: File): Promise<{mime: 'image/jpeg'; data: string; preview: string} | null> {
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {setNotice('JPEG·PNG·WebP 이미지만 보낼 수 있습니다.'); return null;}
    if (file.size > 8_000_000) {setNotice('이미지는 8MB 이하로 보내 주세요.'); return null;}
    const bitmap = await createImageBitmap(file).catch(() => null);
    if (!bitmap) {setNotice('이미지를 읽을 수 없습니다.'); return null;}
    const scale = Math.min(1, 1568 / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement('canvas');
    canvas.width = Math.max(1, Math.round(bitmap.width * scale));
    canvas.height = Math.max(1, Math.round(bitmap.height * scale));
    const context = canvas.getContext('2d');
    if (!context) {bitmap.close(); setNotice('이미지를 읽을 수 없습니다.'); return null;}
    context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    bitmap.close();
    const preview = canvas.toDataURL('image/jpeg', 0.82);
    const data = preview.split(',', 2)[1] ?? '';
    if (!data || data.length > 1500000) {setNotice('이미지가 너무 큽니다. 더 작은 이미지로 보내 주세요.'); return null;}
    return {mime: 'image/jpeg', data, preview};
  }

  const detectedLink = firstUrl(draft);

  type GateDecision = {action: 'verify' | 'reply'; reply: string | null; focus: string | null};
  function gateContext() {
    return {
      previousText: liveResult?.text.slice(0, 2000) ?? null,
      previousClaims: liveResult?.claims.slice(0, 3).map(claim => ({quote: claim.quote.slice(0, 200), verdict: claim.verdict, score: claim.factScore})) ?? [],
      recentUser: messages.filter(message => message.role === 'user' && message.text).slice(-3).map(message => message.text!.slice(0, 200)),
    };
  }
  async function requestGate(text: string, signal: AbortSignal): Promise<GateDecision> {
    const response = await fetch('/api/intent', {method: 'POST', headers: {'content-type': 'application/json'}, body: JSON.stringify({text, context: gateContext()}), signal});
    if (!response.ok) throw new Error('INTENT_FAILED');
    const value = await response.json() as {action?: unknown; reply?: unknown; focus?: unknown};
    if (value?.action !== 'verify' && value?.action !== 'reply') throw new Error('INTENT_FAILED');
    if (value.action === 'reply' && typeof value.reply !== 'string') throw new Error('INTENT_FAILED');
    return {action: value.action, reply: typeof value.reply === 'string' ? value.reply : null, focus: typeof value.focus === 'string' ? value.focus : null};
  }
  const prevHasClaims = (liveResult?.claims.length ?? 0) > 0;
  const continuedThread = !sample && !image && !detectedLink && liveResult !== null && isFollowUpText(draft);
  const followUp = continuedThread && prevHasClaims;

  function loadSample() {
    stop();
    setLiveResult(null);
    dispatch({type: 'cancel'});
    dispatch({type: 'load', snapshot: demoPreview});
    setDraft(DEMO_TEXT);
    setFocus(DEMO_FOCUS);
    setSample(true);
    setImage(null);
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
    setImage(null);
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
    if (!draft.trim() && !image) {setNotice('검증할 원문이나 이미지를 입력해 주세요.'); return;}
    if (draft.length > 12000 || focus.length > 500) {setNotice('원문은 12,000자, 확인 요청은 500자 이내로 입력해 주세요.'); return;}
    if (sample) {dispatch({type: 'load', snapshot: {...demoPreview, focus}}); setNotice('합성 예시입니다. 실제 검증 요청은 전송하지 않았습니다.'); return;}

    stop();
    const controller = new AbortController();
    request.current = controller;
    addMessage({role: 'user', text: followUp ? draft.trim() : draft, meta: continuedThread ? '이전 검증에 이어서 확인' : focus ? `확인 요청: ${focus}` : undefined, ...(image ? {imagePreview: image.preview} : {})});
    setDraft('');
    setImage(null);
    const current = generation.current;
    const startedAt = performance.now();
    const elapsedSeconds = () => Math.floor((performance.now() - startedAt) / 1000);
    let progressMessageId: string | null = null;
    const release = () => {if (request.current === controller) request.current = null;};
    const updateProgressMessage = (patch: Partial<ChatProgress>) => {
      if (generation.current !== current) return;
      if (progressMessageId === null) {
        progressMessageId = `message-${messageCounter.current++}`;
        setMessages(messages => [...messages, {
          id: progressMessageId!, role: 'assistant', progress: patch,
        }]);
        return;
      }
      setMessages(messages => messages.map(message => message.id === progressMessageId
        ? {...message, progress: {...message.progress, ...patch}}
        : message));
    };
    let gate: GateDecision | null = null;
    if (!image && !detectedLink && draft.trim().length <= 120) {
      try {
        gate = await requestGate(draft.trim(), controller.signal);
      } catch { gate = null; }
      if (generation.current !== current || controller.signal.aborted) {release(); return;}
    }
    if (gate?.action === 'reply' && gate.reply) {
      addMessage({role: 'assistant', text: gate.reply});
      setDraft(''); setImage(null); release();
      return;
    }
    const gateFocus = gate?.action === 'verify' ? (gate.focus || '') : '';
    if (!gate) {
      const fallback = classifyChatInput(draft, {hasPrevious: !sample && liveResult !== null, hasAttachment: !!(image || detectedLink)});
      if (fallback.kind === 'meta') {
        addMessage({role: 'assistant', text: fallback.topic === 'history' ? describeHistory(messages, liveResult, DEMO_TEXT) : metaReply(fallback.topic)});
        setDraft(''); setImage(null); release();
        return;
      }
      if (fallback.kind === 'followup' && !prevHasClaims) {
        addMessage({role: 'assistant', text: '이전 검증에서 검증 가능한 주장을 못 찾았어. 확인할 원문·링크·이미지를 보내주면 바로 검증할게.'});
        setDraft(''); release();
        return;
      }
    }
    if (configured === false) {setNotice(configurationHelp); release(); return;}
    const effectiveText = followUp && liveResult ? liveResult.text : draft;
    const effectiveFocus = followUp
      ? [focus.trim(), gateFocus.trim(), draft.trim()].filter(part => part).join(' / ')
      : [focus.trim(), gateFocus.trim()].filter(part => part).join(' / ');
    const submitted: FactCheckRequest = {text: effectiveText, focus: effectiveFocus, consent: true as const, modelPreference, ...(detectedLink && !followUp ? {linkUrl: detectedLink} : {}), ...(image ? {image: {mime: image.mime, data: image.data}} : {})};
    if (!followUp) {
      setLiveResult(null);
      dispatch({type: 'reset'});
    }
    dispatch({type: 'start'});
    setNotice(followUp ? '이전 원문을 유지하고 확인 요청으로 이어서 검증합니다.' : '검증 요청을 서버로 전송하고 있습니다.');
    try {
      const response = await fetch('/api/fact-check', {method: 'POST', headers: {'content-type': 'application/json'}, body: JSON.stringify(submitted), signal: controller.signal});
      const result = await readFactCheckStream(response, {
        signal: controller.signal,
        onStage: stage => {
          if (generation.current !== current) return;
          updateProgressMessage({status: stage.message, statusStage: stage.stage, statusElapsedSeconds: elapsedSeconds()});
          setNotice(stage.message);
        },
        onSources: event => {
          if (generation.current !== current) return;
          const elapsed = elapsedSeconds();
          updateProgressMessage(event.phase === 'found'
            ? {sourcesFound: event.sources, sourcesFoundElapsedSeconds: elapsed}
            : {sourcesRead: event.sources, sourcesReadElapsedSeconds: elapsed});
          setNotice(event.phase === 'found'
            ? '검색 결과에서 출처 후보를 찾았어. 원문을 읽고 있어.'
            : '출처 원문을 가져왔어. 주장과 인용을 검증하고 있어.');
        },
        onPreview: event => {
          if (generation.current !== current) return;
          updateProgressMessage({claims: event.claims, claimsElapsedSeconds: elapsedSeconds()});
          setNotice('1차 검증을 마쳤어. 최종 답변과 인용을 정리하고 있어.');
        },
      });
      if (generation.current !== current || controller.signal.aborted) return;
      if (!submitted.linkUrl && !submitted.image && (result.text !== submitted.text || result.focus !== submitted.focus)) throw new Error('제출한 원문과 검증 결과가 일치하지 않습니다. 다시 시도해 주세요.');
      setImage(null);
      setDraft('');
      if (followUp && !result.claims.length) {
        setNotice('추가로 확인된 게 없어서 이전 결과를 유지할게.');
      } else {
        setLiveResult(result);
        dispatch({type: 'load', snapshot: result});
      }
      setMobileTab('results');
      if (!(followUp && !result.claims.length)) setNotice(result.claims.length ? '검증이 완료되었습니다. 아래에서 출처와 남은 불확실성을 확인해 주세요.' : '검증 가능한 주장을 찾지 못했습니다. 결과의 경고를 확인해 주세요.');
      const reply = composeAssistantReply(result);
      const finalMessage: ChatMessage = {id: `message-${messageCounter.current++}`, role: 'assistant', ...reply};
      if (progressMessageId) {
        setMessages(messages => [...messages.map(message => message.id === progressMessageId && message.progress
          ? {...message, progress: {...message.progress, status: '검증 완료', statusElapsedSeconds: elapsedSeconds(), completed: true}}
          : message), finalMessage]);
      } else {
        setMessages(messages => [...messages, finalMessage]);
      }
    } catch (error) {
      if (generation.current !== current || controller.signal.aborted) return;
      dispatch({type: 'cancel'});
      const message = error instanceof FactCheckError && /CONFIG|KEY_MISSING/i.test(error.code) ? configurationHelp : error instanceof Error ? `검증 실패: ${error.message} 다시 시도하실 수 있습니다.` : '검증 요청에 실패했습니다. 네트워크를 확인하고 다시 시도해 주세요.';
      if (error instanceof FactCheckError && /CONFIG|KEY_MISSING/i.test(error.code)) setConfigured(false);
      setNotice(message);
      if (progressMessageId) {
        setMessages(messages => messages.map(item => item.id === progressMessageId && item.progress
          ? {...item, progress: {...item.progress, error: message}}
          : item));
      } else {
        addMessage({role: 'assistant', text: message, tone: 'error'});
      }
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
      <a className="brand" href="#top" aria-label="True or Not 홈"><span className="brand-symbol"><Icon name="lens" size={25}/></span><span><ScrambleText>True or Not</ScrambleText><small>팩트체크 에이전트</small></span></a>
      <div className="workspace-label"><span className="workspace-avatar">F</span><div>나의 워크스페이스<small>프로필</small></div></div>
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
      <header className="topbar"><div className="breadcrumb"><span className="mobile-brand">True or Not</span><strong></strong></div><div className="topbar-actions"><button className="text-button" aria-label="사용 가이드" onClick={() => setDialog('guide')}><Icon name="book"/><span>사용 가이드</span></button><span className="profile-mark" aria-label="로컬 워크스페이스">F</span></div></header>
      <main id="workspace-main" className="page-content">
        <section className="composer panel-host chat-hero" aria-labelledby="chat-heading">
          <div className="chat-intro chat-intro--wordmark">
            <h1 id="chat-heading" className="sr-only">True or Not</h1>
            <VectorWordmark
              text="True or Not"
              font={{fontFamily: 'Inter, system-ui, sans-serif', fontWeight: 800, fontSize: '200px', lineHeight: '1em', letterSpacing: '-0.02em', textAlign: 'center'}}
              background="#00000000"
              textColor="#FFFFFF"
              shade="#FFFFFF"
              accent="#FFFFFF"
              reach={156}
              speed={0}
              damping={100}
              handles={{size: 54, spread: 29, labels: true}}
              fontSizeReference="parent"
              style={{
                position: 'absolute',
                left: 'calc(0px - var(--wordmark-effect-bleed-x))',
                top: 'calc(0px - var(--wordmark-effect-bleed-y))',
                width: 'calc(100% + var(--wordmark-effect-bleed-x) + var(--wordmark-effect-bleed-x))',
                height: 'calc(100% + var(--wordmark-effect-bleed-y) + var(--wordmark-effect-bleed-y))',
                minWidth: 0,
                minHeight: 0,
                overflow: 'visible',
              }}
            />
          </div>
          <div className="chat-thread" aria-live="polite">
            {messages.map(message => <motion.div key={message.id} className={`chat-message ${message.role === 'user' ? 'is-user' : 'is-assistant'} ${message.answer ? 'has-answer' : ''} ${message.progress ? 'has-progress' : ''} ${message.tone === 'error' ? 'is-error' : ''}`} initial={reduce ? false : {opacity: 0, y: 10}} animate={{opacity: 1, y: 0}} transition={{duration: reduce ? 0 : .22}}>
              {message.role === 'assistant' && <span className="chat-avatar"><Icon name="lens" size={16}/></span>}
              <div className={`chat-bubble ${message.answer ? 'chat-bubble--answer' : ''}`}>
                {message.answer ? <AnswerOverview answer={message.answer} sources={message.sources ?? []} messageId={message.id}/> : message.progress ? <ProgressReply progress={message.progress}/> : <>{message.imagePreview && <img className="chat-image-preview" src={message.imagePreview} alt="사용자가 보낸 이미지"/>}{message.text ? <p>{message.text}</p> : null}</>}
                {message.meta && <small>{message.meta}</small>}
              </div>
            </motion.div>)}
            {busy && <div className="chat-message is-assistant chat-message--loading" data-testid="verification-loading"><span className="chat-avatar"><Icon name="lens" size={16}/></span><div className="chat-bubble"><div className="chat-loader-row"><LatticeLoader label="검증 중" doneLabel="검증 완료" errorLabel="검증 실패" pattern="orbit" grid={3} shape="round" cellSize={7} gap={3} fontSize={12} step={75} idleOpacity={0.15} glow color="#ffffff" showTimer/><span>{notice || '근거를 모으고 사실 여부를 대조하고 있습니다.'}</span></div></div></div>}
          </div>
          <form className="chat-form" onSubmit={submit}>
            <div className="chat-input-shell">
              <label className="sr-only" htmlFor="document-text">확인할 원문</label>
              <textarea ref={editor} id="document-text" value={draft} onChange={event => {setDraft(event.target.value); if (sample) {setSample(false); setMessages([WELCOME_MESSAGE]);}}} onPaste={async event => {
                const item = [...(event.clipboardData?.items ?? [])].find(entry => entry.type.startsWith('image/'));
                if (!item || busy) return;
                const file = item.getAsFile();
                if (!file) return;
                const attached = await downscaleImage(file);
                if (attached) setImage(attached);
              }} placeholder="확인하고 싶은 주장이나 원문을 입력해 주세요. 이미지는 Ctrl+V로 붙여넣을 수 있습니다." rows={3} maxLength={12000} onKeyDown={event => {if (event.key !== 'Enter' || event.shiftKey || event.nativeEvent.isComposing) return; event.preventDefault(); event.currentTarget.form?.requestSubmit();}}/>
              <div className="chat-input-meta"><span>{draft.length.toLocaleString()} / 12,000</span><span>Shift+Enter로 줄바꾸기</span></div>
              {(image || detectedLink) && <div className="chat-attachments">
                {image && <span className="attach-chip"><img src={image.preview} alt="첨부 이미지 미리보기"/><button type="button" onClick={() => setImage(null)} aria-label="이미지 제거">×</button></span>}
                {detectedLink && <span className="attach-chip is-link"><Icon name="link" size={14}/><span>링크 인식됨</span></span>}
              </div>}
              <div className="chat-toolbar">
                <div className="chat-tools"><button type="button" className="chat-tool" onClick={() => setDialog('guide')}><Icon name="plus" size={17}/><span>검증 조건</span></button><button type="button" className="chat-tool" onClick={() => fileInput.current?.click()} disabled={busy} aria-label="이미지 첨부"><Icon name="file" size={16}/><span>이미지</span></button><input ref={fileInput} type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" aria-label="이미지 첨부" tabIndex={-1} onChange={async event => {const file = event.target.files?.[0]; event.target.value = ''; if (!file || busy) return; const attached = await downscaleImage(file); if (attached) setImage(attached);}}/><span className="chat-tool is-static"><Icon name="link" size={16}/><span>웹 검색</span></span><label className="chat-focus-control" htmlFor="focus-request"><Icon name="lens" size={15}/><span>확인 요청</span><input id="focus-request" value={focus} maxLength={500} onChange={event => setFocus(event.target.value)} placeholder="선택 입력"/></label></div>
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
                  <button type="submit" className="chat-send" disabled={busy || (!draft.trim() && !image)} aria-label={busy ? '검증 진행 중' : sample ? '예시 다시 보기' : '팩트 검증 시작'}><Icon name="arrow" size={19}/></button>
                </div>
              </div>
            </div>
            <div className="chat-footer"><div>{sample && <span className="sample-state"><Icon name="shield" size={14}/>합성 예시는 외부로 전송하지 않습니다.</span>}</div><button type="button" className="sample-chip" onClick={loadSample}>예시로 시작하기 <Icon name="arrow" size={14}/></button></div>
          </form>
          <div className={`chat-status ${busy ? 'is-busy' : ''}`} role="status" aria-live="polite">{busy ? notice || '검증을 진행하고 있습니다.' : notice || (configured === false ? configurationHelp : '원문을 입력하거나 예시로 시작해 근거를 확인해 보세요.')}</div>
        </section>

        <section id="review" className="review-section" aria-labelledby="review-heading">
          <div className="review-heading dashboard-heading"><div><span className="section-kicker">검증 대시보드</span><h2 id="review-heading"><BlurText text="근거와 함께 확인하세요."/></h2><p>주장별 신뢰지수, 확인된 인용, 출처의 관계를 한 흐름으로 살펴보세요.</p></div><button className="secondary-button export-button" disabled={!snapshot || busy} onClick={download}><Icon name="download" size={16}/><span>{snapshot?.demo ? '예시 내보내기' : '결과 내보내기'}</span></button></div>
          {snapshot ? <>
            <div className="dashboard-meta"><span className="document-title"><Icon name={snapshot.demo ? 'book' : 'file'} size={16}/>{snapshot.demo ? '합성 예시 · 외부 전송 없음' : '직접 입력한 원문 · 실제 검증'}</span><div><span>{snapshot.claims.length}개 주장</span><span>{sourceCount}개 출처</span><span>{snapshot.demo ? '시연용 데이터' : liveResult?.checkedAt || '검증 시점 기록됨'}</span></div></div>
            <div className="dashboard-top-grid">
              <Panel className="trust-panel"><TrustIndex score={trustScore} claimCount={snapshot.claims.length} sourceCount={sourceCount} evidenceCount={evidenceCount} warningCount={warningCount}/></Panel>
              <Panel className="claim-panel"><div className="panel-top"><h3><Icon name="grid" size={17}/><BlurText text="주장별 점수"/></h3><span>선택하면 근거가 바뀝니다</span></div><div className="claim-selector" aria-label="주장 후보 선택">{snapshot.claims.map((claim, index) => <motion.button key={claim.id} ref={spotlight} layout={!reduce} className={`claim-card ${selected?.id === claim.id ? 'is-selected' : ''}`} aria-pressed={selected?.id === claim.id} onClick={() => select(claim.id)}><div className="claim-card-top"><span>주장 {String(index + 1).padStart(2, '0')}</span><Badge claim={claim}/></div><div className="claim-card-score"><strong>{claim.factScore}</strong><span>점</span></div><p>{claim.quote}</p><span className="claim-card-bottom">{selected?.id === claim.id ? '선택한 주장' : '근거 살펴보기'}<Icon name={selected?.id === claim.id ? 'check' : 'arrow'} size={15}/></span></motion.button>)}</div></Panel>
            </div>
            <div className="mobile-tabs" role="group" aria-label="검토 화면 선택"><span className="mobile-tabs-indicator" data-active={mobileTab} aria-hidden="true"/><button aria-pressed={mobileTab === 'original'} onClick={() => setMobileTab('original')}>원문</button><button aria-pressed={mobileTab === 'results'} onClick={() => setMobileTab('results')}>결과</button><button aria-pressed={mobileTab === 'sources'} onClick={() => setMobileTab('sources')}>출처</button></div>
            <div className={`dashboard-detail-layout mobile-${mobileTab}`}>
              <Panel as="article" className="original-panel"><div className="panel-top"><h3><Icon name="file" size={17}/><BlurText text="원문"/></h3><span>{snapshot.demo ? '합성 문서' : '제출한 원문'}</span></div><div className="original-content"><span className="article-kicker">{snapshot.demo ? '문화 행사 · 가상의 사례' : '검증 요청 시점의 원문'}</span><h3>{snapshot.demo ? '달빛시 가을빛 축제, 알아두면 좋은 내용' : '검증한 원문'}</h3><p className="article-byline">{snapshot.demo ? 'True or Not 예시 편집실 · 실제 기사 아님' : '원문을 보존한 상태로 주장을 추출했습니다.'}</p><div className="original-text">{original}</div><div className="highlight-legend"><span/>강조된 문장을 선택하면 오른쪽 근거가 바뀝니다.</div>{snapshot.focus && <div className="focus-note"><Icon name="lens" size={17}/><div><strong>확인하고 싶은 내용</strong><p>{snapshot.focus}</p><small>{snapshot.demo ? '예시의 비교 범위를 보여드립니다.' : '검증의 참고 범위로 전달했습니다.'}</small></div></div>}</div><div className="original-footer"><Icon name="shield" size={15}/>{snapshot.demo ? '실제 인물·지역·사건과 무관한 합성 예시입니다.' : '원문에서 추출한 최대 3개의 주장을 검증합니다.'}</div></Panel>
              <Panel className="evidence-panel"><div className="panel-top"><h3><Icon name="lens" size={18}/><BlurText text="선택한 주장과 근거"/></h3><span>{snapshot.demo ? '예시 비교' : '수집된 원문 비교'}</span></div><AnimatePresence mode="wait" initial={false}><motion.div className="detail-content" key={selected?.id || 'empty'} initial={reduce ? false : {opacity: 0, y: 5}} animate={{opacity: 1, y: 0}} exit={{opacity: 0}} transition={{duration: reduce ? 0 : 0.18}}>{selected ? <>
                <div className="result-overview"><span className="article-kicker">선택한 주장</span><h3>{selected.quote}</h3><FactScore claim={selected}/><Badge claim={selected}/><p>{selected.summary}</p></div>
                <div className="source-content"><div className="source-heading"><h4>근거 출처</h4><span>{snapshot.demo ? `${sourceDocs.length}개 연결` : `${selectedEvidence.length}개 인용 · ${liveResult?.sources.length ?? 0}개 검색`}</span></div>
                  {snapshot.demo
                    ? sourceDocs.length
                      ? <>
                          <div className="comparison-note"><span className="group-symbol">A</span><p><strong>같은 원자료를 공유합니다.</strong><br/>출처 2개가 독립적인 근거 2개를 뜻하지 않습니다.</p></div>
                          {sourceDocs.map((source, index) => <button className="source-card" ref={spotlight} key={source.id} onClick={() => setDialog(source.id)}><div className="source-card-top"><span className="source-index">{String(index + 1).padStart(2, '0')}</span><span className="source-kind">{source.relation} · 예시</span><Icon name="arrow" size={16}/></div><strong>{source.title}</strong><span className="source-publisher">{source.publisher} · {source.date}</span><blockquote>“{selected.id === 'claim-1' ? source.id === 'doc-1' ? '가을빛 축제는 10월 12일부터 14일까지 달빛공원에서 진행합니다.' : '행사는 10월 12일부터 14일까지 열립니다.' : source.id === 'doc-1' ? '공예 체험은 사전 예약이 필요하며 재료비 5,000원이 있습니다.' : '공예 체험은 별도 예약과 재료비가 필요합니다.'}”</blockquote><span className="source-footer">원자료 그룹 A <span>전문 보기</span></span></button>)}
                          <p className="evidence-caution">인용은 시연용 문서 전문에서 확인해 주세요. 실제 검색 결과가 아닙니다.</p>
                        </>
                      : <div className="empty-evidence"><Icon name="file" size={27}/><h4>비교할 근거가 없습니다</h4><p>미래 전망을 현재 사실로 확정하지 않습니다. 예시 문서에도 방문객 추정 근거는 없습니다.</p></div>
                    : selectedEvidence.length
                      ? <>{selectedEvidence.map((evidence, index) => {
                          const source = liveResult?.sources.find(item => item.id === evidence.sourceId);
                          const href = source && safeSourceUrl(source.url);
                          return <article className="source-card" ref={spotlight} key={evidence.id}>
                            <div className="source-card-top"><span className="source-index">{String(index + 1).padStart(2, '0')}</span><span className="source-kind">{source?.sourceType || '출처'} · {evidence.relation === 'supports' ? '지지 근거' : evidence.relation === 'contradicts' ? '반박 근거' : '맥락 근거'}</span><span className="source-verified">{evidence.quoteVerified ? '인용 확인' : '확인 필요'}</span></div>
                            {href ? <a className="source-title-link" href={href} target="_blank" rel="noopener noreferrer">{source?.title || '출처 열기'} <Icon name="arrow" size={14}/></a> : <strong>{source?.title || '출처 확인 불가'}</strong>}
                            <span className="source-publisher">{source?.publisher || '발행 기관 미확인'} · {source?.publishedAt || '발행일 미확인'}</span>
                            <blockquote>“{evidence.quote}”</blockquote>
                            {evidence.sectionTitle && evidence.sectionText ? <details className="source-section-details">
                              <summary><span>‘{evidence.sectionTitle}’</span> 목차 내용 펼치기</summary>
                              <div className="source-section-details-body">
                                <p>{evidence.sectionText}</p>
                                {evidence.sectionTruncated && <small>목차 본문이 길어 앞부분만 표시했습니다.</small>}
                              </div>
                            </details> : null}
                            {hasEnglishText(evidence.quote) && evidence.quoteTranslation ? <div className="source-translation"><span>한국어 번역</span><p>{evidence.quoteTranslation}</p></div> : null}
                            <p className="source-caption">원문 인용 일치 확인 · 출처 독립성은 별도 확인이 필요합니다.</p>
                          </article>;
                        })}</>
                      : <div className="empty-evidence"><Icon name="file" size={27}/><h4>비교할 근거가 없습니다</h4><p>근거 부족은 거짓을 뜻하지 않습니다. 확인 가능한 원문이 없다는 의미입니다.</p></div>}
                </div>
                {!snapshot.demo && !selectedEvidence.length && otherSources.length ? <div className="source-candidate-list"><p className="evidence-caution">출처별 검색 경로와 순위를 확인해. Google 자연검색 순위는 그렇게 표시된 출처에만 해당하고, 아직 선택한 주장과 직접 대조된 인용은 아니야.</p>{otherSources.map((source, index) => {const href = safeSourceUrl(source.url); return <article className="source-card" ref={spotlight} key={source.id}><div className="source-card-top"><span className="source-index">{String(index + 1).padStart(2, '0')}</span><span className="source-kind">{source.sourceType || '검색 출처'}</span><span className="source-verified">{source.accessStatus === 'verified' ? '원문 확인' : '접근 불가'}</span></div>{href ? <a className="source-title-link" href={href} target="_blank" rel="noopener noreferrer">{source.title} <Icon name="arrow" size={14}/></a> : <strong>{source.title}</strong>}<span className="source-publisher">{source.publisher} · {source.publishedAt || '발행일 미확인'}</span><p className="source-caption">{sourceDiscoveryLabel(source)} · 원문 인용이 연결되기 전에는 판정 근거로 사용하지 않습니다.</p></article>;})}</div> : null}
                {!snapshot.demo && youtubeSources.length > 0 ? <section className="youtube-context-list" aria-label="유튜브 영상 정보와 공개 댓글"><div className="source-heading"><h4>유튜브 영상 정보·공개 댓글</h4><span>참고 맥락 · 판정 근거 아님</span></div>{youtubeSources.map(source => {const href = safeSourceUrl(source.url); return <article className="youtube-context-card" key={source.id}><div className="youtube-context-header"><YoutubeThumbnail source={source}/><div className="youtube-context-copy">{href ? <a className="source-title-link" href={href} target="_blank" rel="noopener noreferrer">{source.youtubeTitle || source.title} <Icon name="arrow" size={14}/></a> : <strong>{source.youtubeTitle || source.title}</strong>}<YoutubeVideoMetadata source={source}/></div></div><YoutubeCommentContext source={source}/></article>;})}</section> : null}
                {!snapshot.demo && selectedLiveClaim && <div className="detail-blocks"><div><h4>확인된 내용</h4>{selectedLiveClaim.confirmed.length ? <ul>{selectedLiveClaim.confirmed.map((text, index) => <li key={index}>{text}</li>)}</ul> : <p>직접 확인된 내용이 없습니다.</p>}</div><div><h4>남은 불확실성</h4>{selectedLiveClaim.unresolved.length ? <ul>{selectedLiveClaim.unresolved.map((text, index) => <li key={index}>{text}</li>)}</ul> : <p>현재 기록된 불확실성이 없습니다.</p>}</div>{selectedLiveClaim.warnings.length > 0 && <div><h4>주장별 주의사항</h4><ul>{selectedLiveClaim.warnings.map((text, index) => <li key={index}>{text}</li>)}</ul></div>}</div>}
              </> : <div className="empty-evidence"><Icon name="lens" size={27}/><h4>주장을 선택해 주세요</h4><p>위의 주장 카드를 선택하면 연결된 출처와 인용이 표시됩니다.</p></div>}</motion.div></AnimatePresence></Panel>
              <Panel className="source-index-panel"><div className="panel-top"><h3><Icon name="book" size={17}/><BlurText text="검토한 출처"/></h3><span>{sourceCount}개 수집</span></div><div className="source-index-grid">{snapshot.demo ? documents.map((source, index) => <button className="source-index-card" ref={spotlight} key={source.id} onClick={() => setDialog(source.id)}><span className="source-index-number">{String(index + 1).padStart(2, '0')}</span><span><strong>{source.title}</strong><small>{source.publisher}</small></span><Icon name="arrow" size={15}/></button>) : liveResult?.sources.map((source, index) => {const href = safeSourceUrl(source.url); const sourceLabel = source.sourceType === '유튜브' ? source.youtubeDataStatus === 'collected' ? `공개 댓글 ${source.youtubeComments.length}개` : source.youtubeDataStatus === 'not_configured' ? '댓글 API 미설정' : '댓글 조회 불가' : source.accessStatus === 'verified' ? '원문 확인' : '접근 불가'; const content = <><span className="source-index-number">{String(index + 1).padStart(2, '0')}</span><span><strong>{source.youtubeTitle || source.title}</strong><small>{source.sourceType} · {source.publisher} · {sourceDiscoveryLabel(source)} · {sourceLabel}</small></span><Icon name="arrow" size={15}/></>; return href ? <a className="source-index-card" ref={spotlight} href={href} target="_blank" rel="noopener noreferrer" key={source.id}>{content}</a> : <div className="source-index-card" ref={spotlight} key={source.id}>{content}</div>;})}{!sourceCount && <div className="source-index-empty">아직 수집된 출처가 없습니다.</div>}</div></Panel>
            </div>
          </> : <Panel className="dashboard-empty"><div className="empty-orbit"><Icon name="lens" size={31}/></div><h3>검증 결과가 이곳에 쌓입니다.</h3><p>대화창에 원문을 보내면 주장별 신뢰지수와 근거 출처를 연결해 보여드립니다.</p><div className="empty-preview-stats"><span><strong>--</strong><small>신뢰지수</small></span><span><strong>--</strong><small>검토 출처</small></span><span><strong>--</strong><small>연결 근거</small></span></div><button className="secondary-button" onClick={loadSample}>예시 대시보드 보기 <Icon name="arrow"/></button></Panel>}
        </section>
        <footer className="page-footer"><span><span className="footer-mark">F</span>True or Not <span className="footer-divider">/</span>판단을 대신하지 않고, 근거를 연결합니다.</span><span className="footer-links"><a href="/privacy">개인정보 처리방침</a><a href="/terms">이용약관</a><a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener noreferrer">YouTube 약관</a><a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google 개인정보</a></span><button className="text-button" onClick={() => setDialog('guide')}>검증 원칙<Icon name="arrow" size={15}/></button></footer>
      </main>
    </div>
    <Modal open={dialog !== null} title={activeDocument?.title || (dialog === 'guide' ? '근거를 읽는 세 가지 원칙' : '검증 안내')} onClose={() => setDialog(null)}>{activeDocument ? <><p className="dialog-notice">합성 예시 문서 · 외부 출처 링크가 아닙니다.</p><dl className="document-metadata"><dt>작성 주체</dt><dd>{activeDocument.publisher}</dd><dt>설정 날짜</dt><dd>{activeDocument.date}</dd><dt>원자료 관계</dt><dd>그룹 {activeDocument.group} · {activeDocument.relation}</dd></dl><div className="document-fulltext">{activeDocument.text}</div></> : dialog === 'guide' ? <ol className="guide-list"><li><span>01</span><div><h3>주장을 작게 나누세요.</h3><p>누가, 언제, 어디서, 어떤 조건으로 한 말인지 원문과 함께 확인하세요.</p></div></li><li><span>02</span><div><h3>출처의 수보다 관계를 보세요.</h3><p>같은 발표를 옮긴 여러 문서는 하나의 원자료를 공유할 수 있습니다.</p></div></li><li><span>03</span><div><h3>모르는 것은 남겨 두세요.</h3><p>근거가 없다고 거짓은 아닙니다. 의견과 미래 예측을 확정된 사실처럼 판정하지 않습니다.</p></div></li></ol> : <div className="about-copy"><p>검증을 시작하면 원문과 확인 요청은 서버, 외부 AI 및 검색 서비스로 전송됩니다. 채팅에 붙인 링크의 페이지는 서버에서 직접 가져오고, 첨부한 이미지는 주장 추출을 위해 AI 제공자에게 보내며 서버에 저장하지 않습니다. 관련 YouTube 영상 제목과 공개 댓글 최대 10개는 YouTube Data API로 조회할 수 있습니다. 댓글은 LLM 입력 및 판정 근거로 사용하지 않습니다.</p><p>검증 결과와 YouTube 댓글은 현재 화면 메모리에만 유지되며 새로고침하면 사라집니다. YouTube API 제목·댓글은 JSON 내보내기에서 제외됩니다. 자세한 내용은 <a href="/privacy">개인정보 처리방침</a>과 <a href="/terms">이용약관</a>을 확인해 주세요.</p></div>}</Modal>
  </div></MotionConfig>;
}
