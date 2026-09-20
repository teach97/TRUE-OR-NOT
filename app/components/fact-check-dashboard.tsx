"use client";

import { AnimatePresence, MotionConfig, motion, useReducedMotion } from 'motion/react';
import { Children, cloneElement, isValidElement, useEffect, useReducer, useRef, useState } from 'react';
import type { FormEvent, ReactElement, ReactNode } from 'react';
import LiquidGlass from 'liquid-glass-react';
import { initialState, transition } from './demo-state';
import type { Claim } from './demo-state';
import type { FactCheckResult } from '../lib/fact-check-contract';
import { FactCheckError, readFactCheckStream, safeSourceUrl } from './fact-check-client';
import { DEMO_FOCUS, DEMO_TEXT, demoPreview, documents } from './demo-fixture';
import ParticlesLogo from './particles-logo';
import {
  defaultParticleLogoControls,
  emitParticleLogoSettings,
  normalizeParticleLogoControls,
  parseParticleLogoControls,
  particleLogoSettingsEvent,
  particleLogoSettingsStorageKey,
} from './particles-settings';
import type { ParticleLogoControls } from './particles-settings';
import ShaderBackground from './shader-background';
import { defaultShaderSettings, parseShaderSettings, shaderSettingsStorageKey } from './shader-settings';
import type { ShaderSettings } from './shader-settings';
import { defaultLensSettings, lensSettingsStorageKey, parseLensSettings } from './lens-settings';
import type { LensSettings } from './lens-settings';

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
type LiquidSettings = {
  displacementScale: number;
  blurAmount: number;
  saturation: number;
  aberrationIntensity: number;
  surfaceOpacity: number;
  cornerRadius: number;
  elasticity: number;
  mode: 'standard' | 'polar' | 'prominent' | 'shader';
};

const defaultLiquidSettings: LiquidSettings = {
  displacementScale: 46,
  blurAmount: 0.14,
  saturation: 160,
  aberrationIntensity: 1.6,
  surfaceOpacity: 0.42,
  cornerRadius: 18,
  elasticity: 0,
  mode: 'standard',
};
const liquidSettingsStorageKey = 'factlens.liquid-settings.v1';

function parseLiquidSettings(raw: string | null): LiquidSettings {
  if (!raw) return {...defaultLiquidSettings};
  try {
    const parsed = JSON.parse(raw) as Partial<LiquidSettings>;
    const number = (value: unknown, min: number, max: number, fallback: number) => typeof value === 'number' && Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : fallback;
    return {
      displacementScale: number(parsed.displacementScale, 0, 70, defaultLiquidSettings.displacementScale),
      blurAmount: number(parsed.blurAmount, 0, 0.25, defaultLiquidSettings.blurAmount),
      saturation: number(parsed.saturation, 80, 190, defaultLiquidSettings.saturation),
      aberrationIntensity: number(parsed.aberrationIntensity, 0, 4, defaultLiquidSettings.aberrationIntensity),
      surfaceOpacity: number(parsed.surfaceOpacity, 0.12, 0.86, defaultLiquidSettings.surfaceOpacity),
      cornerRadius: number(parsed.cornerRadius, 8, 32, defaultLiquidSettings.cornerRadius),
      elasticity: number(parsed.elasticity, 0, 1, defaultLiquidSettings.elasticity),
      mode: parsed.mode === 'polar' || parsed.mode === 'prominent' || parsed.mode === 'shader' || parsed.mode === 'standard' ? parsed.mode : defaultLiquidSettings.mode,
    };
  } catch {
    return {...defaultLiquidSettings};
  }
}

type LiquidNumericKey = keyof Pick<LiquidSettings, 'displacementScale' | 'blurAmount' | 'saturation' | 'aberrationIntensity' | 'surfaceOpacity' | 'cornerRadius' | 'elasticity'>;
type LiquidControl = {key: LiquidNumericKey; label: string; min: number; max: number; step: number; precision: number; percent?: boolean};
const liquidControls: LiquidControl[] = [
  {key: 'displacementScale', label: '왜곡 강도', min: 0, max: 70, step: 1, precision: 0},
  {key: 'blurAmount', label: '배경 블러', min: 0, max: 0.25, step: 0.005, precision: 3},
  {key: 'saturation', label: '색상 채도', min: 80, max: 190, step: 1, precision: 0},
  {key: 'aberrationIntensity', label: '색수차', min: 0, max: 4, step: 0.05, precision: 2},
  {key: 'surfaceOpacity', label: '패널 투명도', min: 0.12, max: 0.86, step: 0.01, precision: 0, percent: true},
  {key: 'cornerRadius', label: '모서리 반경', min: 8, max: 32, step: 1, precision: 0},
  {key: 'elasticity', label: '탄성', min: 0, max: 1, step: 0.01, precision: 2},
];

type ShaderColorKey = 'color1' | 'color2' | 'color3';
type ShaderRangeKey = keyof Pick<ShaderSettings, 'uTime' | 'uSpeed' | 'uStrength' | 'uDensity' | 'uFrequency' | 'uAmplitude' | 'rangeStart' | 'rangeEnd' | 'loopDuration' | 'positionX' | 'positionY' | 'positionZ' | 'rotationX' | 'rotationY' | 'rotationZ' | 'cAzimuthAngle' | 'cPolarAngle' | 'cDistance' | 'cameraZoom' | 'reflection' | 'smoothTime' | 'brightness' | 'grainBlending' | 'pixelDensity' | 'fov' | 'threshold'>;
type ShaderRangeControl = {key: ShaderRangeKey; label: string; min: number; max: number; step: number; precision: number};
const shaderColorKeys: ShaderColorKey[] = ['color1', 'color2', 'color3'];
const shaderMotionControls: ShaderRangeControl[] = [
  {key: 'uTime', label: '고정 시간', min: 0, max: 100, step: 0.1, precision: 1},
  {key: 'uSpeed', label: '애니메이션 속도', min: 0, max: 0.5, step: 0.01, precision: 2},
  {key: 'uStrength', label: '형태 강도', min: 0, max: 6, step: 0.1, precision: 1},
  {key: 'uDensity', label: '밀도', min: 0.5, max: 3, step: 0.1, precision: 1},
  {key: 'uFrequency', label: '주파수', min: 1, max: 10, step: 0.1, precision: 1},
  {key: 'uAmplitude', label: '진폭', min: 0, max: 2, step: 0.05, precision: 2},
  {key: 'rangeStart', label: '범위 시작', min: 0, max: 100, step: 1, precision: 0},
  {key: 'rangeEnd', label: '범위 끝', min: 0, max: 100, step: 1, precision: 0},
  {key: 'loopDuration', label: '루프 시간', min: 1, max: 60, step: 0.5, precision: 1},
];
const shaderShapeControls: ShaderRangeControl[] = [
  {key: 'positionX', label: '위치 X', min: -3, max: 3, step: 0.05, precision: 2},
  {key: 'positionY', label: '위치 Y', min: -3, max: 3, step: 0.05, precision: 2},
  {key: 'positionZ', label: '위치 Z', min: -3, max: 3, step: 0.05, precision: 2},
  {key: 'rotationX', label: '회전 X', min: -180, max: 180, step: 1, precision: 0},
  {key: 'rotationY', label: '회전 Y', min: -180, max: 180, step: 1, precision: 0},
  {key: 'rotationZ', label: '회전 Z', min: -180, max: 180, step: 1, precision: 0},
];
const shaderViewControls: ShaderRangeControl[] = [
  {key: 'cAzimuthAngle', label: '카메라 방위각', min: 0, max: 360, step: 1, precision: 0},
  {key: 'cPolarAngle', label: '카메라 극각', min: 0, max: 180, step: 1, precision: 0},
  {key: 'cDistance', label: '카메라 거리', min: 0.1, max: 20, step: 0.1, precision: 1},
  {key: 'cameraZoom', label: '카메라 줌', min: 0.25, max: 3, step: 0.05, precision: 2},
  {key: 'reflection', label: '반사', min: 0, max: 1, step: 0.01, precision: 2},
];
const shaderEffectControls: ShaderRangeControl[] = [
  {key: 'brightness', label: '밝기', min: 0.5, max: 1.8, step: 0.05, precision: 2},
  {key: 'smoothTime', label: '보간 시간', min: 0, max: 2, step: 0.05, precision: 2},
  {key: 'grainBlending', label: '그레인 혼합', min: 0, max: 1, step: 0.01, precision: 2},
];
const shaderCanvasControls: ShaderRangeControl[] = [
  {key: 'pixelDensity', label: '픽셀 밀도', min: 0.5, max: 2, step: 0.1, precision: 1},
  {key: 'fov', label: '시야각', min: 20, max: 90, step: 1, precision: 0},
  {key: 'threshold', label: '지연 로드 기준', min: 0, max: 1, step: 0.05, precision: 2},
];

type LensColorKey = keyof Pick<LensSettings, 'color1' | 'color2' | 'color3' | 'color4'>;
type LensRangeKey = keyof Pick<LensSettings, 'speed' | 'distortion' | 'swirl' | 'grainMixer' | 'grainOverlay' | 'scale' | 'rotation' | 'originX' | 'originY' | 'offsetX' | 'offsetY' | 'worldWidth' | 'worldHeight'>;
type LensRangeControl = {key: LensRangeKey; label: string; min: number; max: number; step: number; precision: number};
const lensColorKeys: LensColorKey[] = ['color1', 'color2', 'color3', 'color4'];
const lensMotionControls: LensRangeControl[] = [
  {key: 'speed', label: '애니메이션 속도', min: 0, max: 0.5, step: 0.01, precision: 2},
  {key: 'distortion', label: '왜곡', min: 0, max: 1, step: 0.01, precision: 2},
  {key: 'swirl', label: '소용돌이', min: 0, max: 1, step: 0.01, precision: 2},
  {key: 'grainMixer', label: '그레인 변형', min: 0, max: 1, step: 0.01, precision: 2},
  {key: 'grainOverlay', label: '그레인 오버레이', min: 0, max: 1, step: 0.01, precision: 2},
];
const lensSizingControls: LensRangeControl[] = [
  {key: 'scale', label: '크기', min: 0.01, max: 4, step: 0.05, precision: 2},
  {key: 'rotation', label: '회전', min: 0, max: 360, step: 1, precision: 0},
  {key: 'originX', label: '기준점 X', min: 0, max: 1, step: 0.01, precision: 2},
  {key: 'originY', label: '기준점 Y', min: 0, max: 1, step: 0.01, precision: 2},
  {key: 'offsetX', label: '오프셋 X', min: -1, max: 1, step: 0.01, precision: 2},
  {key: 'offsetY', label: '오프셋 Y', min: -1, max: 1, step: 0.01, precision: 2},
  {key: 'worldWidth', label: '가상 너비', min: 0, max: 4096, step: 16, precision: 0},
  {key: 'worldHeight', label: '가상 높이', min: 0, max: 4096, step: 16, precision: 0},
];

type ParticleRangeKey = keyof Pick<ParticleLogoControls, 'sampling' | 'particleSpacing' | 'particleSize' | 'tiltFactor' | 'tiltSpeed' | 'displaceStrength' | 'displaceRadius' | 'velocityInfluence' | 'returnSpeed' | 'canvasOpacity'>;
type ParticleRangeControl = {key: ParticleRangeKey; label: string; min: number; max: number; step: number; precision: number};
const particleAppearanceControls: ParticleRangeControl[] = [
  {key: 'sampling', label: '입자 밀도', min: 2, max: 12, step: 1, precision: 0},
  {key: 'particleSpacing', label: '입자 간격', min: 0.001, max: 0.006, step: 0.0001, precision: 4},
  {key: 'particleSize', label: '입자 크기', min: 0.001, max: 0.02, step: 0.0005, precision: 4},
  {key: 'canvasOpacity', label: '로고 투명도', min: 0.05, max: 1, step: 0.01, precision: 2},
];
const particleInteractionControls: ParticleRangeControl[] = [
  {key: 'tiltFactor', label: '기울기 강도', min: 0, max: 0.3, step: 0.01, precision: 2},
  {key: 'tiltSpeed', label: '기울기 속도', min: 0, max: 0.2, step: 0.005, precision: 3},
  {key: 'displaceStrength', label: '밀어내기 힘', min: 0, max: 2, step: 0.05, precision: 2},
  {key: 'displaceRadius', label: '밀어내기 반경', min: 0.02, max: 0.5, step: 0.01, precision: 2},
  {key: 'velocityInfluence', label: '속도 반영', min: 0, max: 1, step: 0.05, precision: 2},
  {key: 'returnSpeed', label: '복귀 속도', min: 0.005, max: 0.2, step: 0.005, precision: 3},
];

const liquidLabEnabled = process.env.NODE_ENV !== 'production' || process.env.NEXT_PUBLIC_LIQUID_LAB === 'true';

type LabOption = {value: string; label: string};
function LabRange({id, label, value, min, max, step, precision, format, onChange}: {id: string; label: string; value: number; min: number; max: number; step: number; precision: number; format?: (value: number) => string; onChange: (value: number) => void}) {
  return <label className="liquid-control" htmlFor={id}><span>{label}</span><output>{format ? format(value) : value.toFixed(precision)}</output><input id={id} type="range" min={min} max={max} step={step} value={value} onChange={event => onChange(Number(event.currentTarget.value))} aria-label={label}/></label>;
}
function LabSelect({id, label, value, options, onChange}: {id: string; label: string; value: string; options: LabOption[]; onChange: (value: string) => void}) {
  return <label className="liquid-select-control" htmlFor={id}><span>{label}</span><select id={id} value={value} onChange={event => onChange(event.currentTarget.value)} aria-label={label}>{options.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>;
}
function LabToggle({id, label, checked, onChange}: {id: string; label: string; checked: boolean; onChange: (value: boolean) => void}) {
  return <label className="liquid-toggle-control" htmlFor={id}><span>{label}</span><input id={id} type="checkbox" checked={checked} onChange={event => onChange(event.currentTarget.checked)} aria-label={label}/></label>;
}
function LabText({id, label, value, maxLength = 64, onChange}: {id: string; label: string; value: string; maxLength?: number; onChange: (value: string) => void}) {
  return <label className="liquid-text-control" htmlFor={id}><span>{label}</span><input id={id} type="text" value={value} maxLength={maxLength} onChange={event => onChange(event.currentTarget.value)} aria-label={label}/></label>;
}
function LabColor({id, label, value, onChange}: {id: string; label: string; value: string; onChange: (value: string) => void}) {
  return <label className="liquid-color-control" htmlFor={id}><span>{label}</span><input id={id} type="color" value={value} onChange={event => onChange(event.currentTarget.value)} aria-label={label}/><output>{value}</output></label>;
}
function particleColorPreset(value: ParticleLogoControls['particleColor']) {
  return value === 'sample' || value === '#91ddd6' || value === '#b5a6ef' || value === '#b7fff5' ? value : 'custom';
}
function particleSolidColor(value: ParticleLogoControls['particleColor']) {
  return value === 'sample' ? defaultParticleLogoControls.particleColor : value;
}

function createLiquidSizer(children: ReactNode): ReactNode {
  return Children.map(children, child => {
    if (!isValidElement(child)) return child;
    const props = child.props as Record<string, unknown> & {children?: ReactNode};
    const sizerProps: Record<string, unknown> = {
      ...props,
      id: undefined,
      htmlFor: undefined,
      onClick: undefined,
      onChange: undefined,
      onInput: undefined,
      onKeyDown: undefined,
      onSubmit: undefined,
      value: undefined,
      checked: undefined,
      selected: undefined,
      autoFocus: false,
      tabIndex: -1,
      'aria-hidden': true,
    };
    if ('children' in props) sizerProps.children = createLiquidSizer(props.children);
    return cloneElement(child as ReactElement, sizerProps);
  });
}

type LiquidPanelProps = {
  as?: 'div' | 'section' | 'article';
  className?: string;
  children: ReactNode;
  liquid: LiquidSettings;
  glassPadding?: string;
  'aria-labelledby'?: string;
};

function LiquidPanel({as = 'div', className = '', children, liquid, glassPadding = '0', 'aria-labelledby': labelledBy}: LiquidPanelProps) {
  const Element = as;
  const {surfaceOpacity, elasticity, mode, ...glassSettings} = liquid;
  return <Element className={`liquid-panel ${className}`} style={{borderRadius: `${liquid.cornerRadius}px`}} aria-labelledby={labelledBy}>
    <div className="liquid-panel-sizer" aria-hidden="true">{createLiquidSizer(children)}</div>
    <LiquidGlass className="liquid-panel-live" {...glassSettings} elasticity={elasticity} mode={mode} padding={glassPadding} style={{position: 'absolute', top: '50%', left: '50%', width: '100%', height: '100%', borderRadius: `${liquid.cornerRadius}px`, background: `linear-gradient(135deg, rgb(37 64 84 / ${surfaceOpacity}), rgb(8 20 36 / ${surfaceOpacity}))`}}>
      {children}
    </LiquidGlass>
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
  const [liquid, setLiquid] = useState<LiquidSettings>(defaultLiquidSettings);
  const [shader, setShader] = useState<ShaderSettings>(defaultShaderSettings);
  const [lens, setLens] = useState<LensSettings>(defaultLensSettings);
  const [particles, setParticles] = useState<ParticleLogoControls>(defaultParticleLogoControls);
  const [liquidStorageReady, setLiquidStorageReady] = useState(false);
  const [shaderStorageReady, setShaderStorageReady] = useState(false);
  const [lensStorageReady, setLensStorageReady] = useState(false);
  const [particleStorageReady, setParticleStorageReady] = useState(false);
  const [shaderProjectSaving, setShaderProjectSaving] = useState(false);
  const [liquidLabOpen, setLiquidLabOpen] = useState(false);
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
    try { setShader(parseShaderSettings(window.localStorage.getItem(shaderSettingsStorageKey))); }
    catch { /* 브라우저 저장소가 차단된 환경에서는 기본값으로 실행합니다. */ }
    setShaderStorageReady(true);
  }, []);
  useEffect(() => {
    try {
      setLiquid(parseLiquidSettings(window.localStorage.getItem(liquidSettingsStorageKey)));
      setLens(parseLensSettings(window.localStorage.getItem(lensSettingsStorageKey)));
      setParticles(parseParticleLogoControls(window.localStorage.getItem(particleLogoSettingsStorageKey)));
    } catch { /* 브라우저 저장소가 차단된 환경에서는 기본값으로 실행합니다. */ }
    setLiquidStorageReady(true);
    setLensStorageReady(true);
    setParticleStorageReady(true);
  }, []);
  useEffect(() => {
    if (!liquidStorageReady) return;
    try { window.localStorage.setItem(liquidSettingsStorageKey, JSON.stringify(liquid)); }
    catch { /* 저장소 용량·권한 오류가 UI를 중단시키지 않도록 무시합니다. */ }
  }, [liquid, liquidStorageReady]);
  useEffect(() => {
    if (!shaderStorageReady) return;
    try { window.localStorage.setItem(shaderSettingsStorageKey, JSON.stringify(shader)); }
    catch { /* 저장소 용량·권한 오류가 UI를 중단시키지 않도록 무시합니다. */ }
  }, [shader, shaderStorageReady]);
  useEffect(() => {
    if (!lensStorageReady) return;
    try { window.localStorage.setItem(lensSettingsStorageKey, JSON.stringify(lens)); }
    catch { /* 저장소 용량·권한 오류가 UI를 중단시키지 않도록 무시합니다. */ }
  }, [lens, lensStorageReady]);
  useEffect(() => {
    if (!particleStorageReady) return;
    try { window.localStorage.setItem(particleLogoSettingsStorageKey, JSON.stringify(particles)); }
    catch { /* 저장소 용량·권한 오류가 UI를 중단시키지 않도록 무시합니다. */ }
    emitParticleLogoSettings(particles);
  }, [particles, particleStorageReady]);
  useEffect(() => {
    const syncParticles = (event: Event) => {
      const next = normalizeParticleLogoControls((event as CustomEvent<unknown>).detail);
      setParticles(previous => JSON.stringify(previous) === JSON.stringify(next) ? previous : next);
    };
    window.addEventListener(particleLogoSettingsEvent, syncParticles);
    return () => window.removeEventListener(particleLogoSettingsEvent, syncParticles);
  }, []);
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
  function updateLiquid(key: LiquidNumericKey, value: number) {
    setLiquid(previous => ({...previous, [key]: value}));
  }
  function updateShaderColor(key: ShaderColorKey, value: string) {
    setShader(previous => ({...previous, [key]: value}));
  }
  function updateShaderRange(key: ShaderRangeKey, value: number) {
    setShader(previous => ({...previous, [key]: value}));
  }
  function updateShaderOption<K extends keyof ShaderSettings>(key: K, value: ShaderSettings[K]) {
    setShader(previous => ({...previous, [key]: value}));
  }
  function updateLensRange(key: LensRangeKey, value: number) {
    setLens(previous => ({...previous, [key]: value}));
  }
  function updateLensOption<K extends keyof LensSettings>(key: K, value: LensSettings[K]) {
    setLens(previous => ({...previous, [key]: value}));
  }
  function updateParticleRange(key: ParticleRangeKey, value: number) {
    setParticles(previous => ({...previous, [key]: value}));
  }
  function updateParticleOption<K extends keyof ParticleLogoControls>(key: K, value: ParticleLogoControls[K]) {
    setParticles(previous => ({...previous, [key]: value}));
  }
  function resetShader() {
    setShader({...defaultShaderSettings});
    setNotice('셰이더 그라디언트를 기본값으로 되돌렸습니다.');
  }
  function resetLens() {
    setLens({...defaultLensSettings});
    setNotice('렌즈 비주얼을 기본값으로 되돌렸습니다.');
  }
  function resetParticles() {
    setParticles({...defaultParticleLogoControls});
    setNotice('TRUE OR NOT 로고 입자를 기본값으로 되돌렸습니다.');
  }
  async function copyShaderCode() {
    const code = `<ShaderGradientCanvas
  pixelDensity={${shader.pixelDensity}}
  fov={${shader.fov}}
  pointerEvents="${shader.pointerEvents}"
  lazyLoad={${shader.lazyLoad}}
  threshold={${shader.threshold}}
  rootMargin="${shader.rootMargin}"
  preserveDrawingBuffer={${shader.preserveDrawingBuffer}}
  powerPreference="${shader.powerPreference}"
>
  <ShaderGradient
    control="props"
    type="${shader.type}"
    animate="${shader.animate}"
    uTime={${shader.uTime}}
    uSpeed={${shader.uSpeed}}
    uStrength={${shader.uStrength}}
    uDensity={${shader.uDensity}}
    uFrequency={${shader.uFrequency}}
    uAmplitude={${shader.uAmplitude}}
    range="${shader.range}"
    rangeStart={${shader.rangeStart}}
    rangeEnd={${shader.rangeEnd}}
    loop="${shader.loop}"
    loopDuration={${shader.loopDuration}}
    color1="${shader.color1}"
    color2="${shader.color2}"
    color3="${shader.color3}"
    positionX={${shader.positionX}}
    positionY={${shader.positionY}}
    positionZ={${shader.positionZ}}
    rotationX={${shader.rotationX}}
    rotationY={${shader.rotationY}}
    rotationZ={${shader.rotationZ}}
    reflection={${shader.reflection}}
    wireframe={${shader.wireframe}}
    smoothTime={${shader.smoothTime}}
    cAzimuthAngle={${shader.cAzimuthAngle}}
    cPolarAngle={${shader.cPolarAngle}}
    cDistance={${shader.cDistance}}
    cameraZoom={${shader.cameraZoom}}
    lightType="${shader.lightType}"
    brightness={${shader.brightness}}
    envPreset="${shader.envPreset}"
    grain="${shader.grain}"
    grainBlending={${shader.grainBlending}}
    zoomOut={${shader.zoomOut}}
    toggleAxis={${shader.toggleAxis}}
    enableTransition={${shader.enableTransition}}
    enableCameraUpdate={${shader.enableCameraUpdate}}
  />
</ShaderGradientCanvas>`;
    try {
      await navigator.clipboard.writeText(code);
      setNotice('현재 셰이더 설정 JSX를 클립보드에 복사했습니다.');
    } catch {
      setNotice('클립보드 복사에 실패했습니다. 브라우저 권한을 확인해 주세요.');
    }
  }
  async function saveShaderToProject() {
    setShaderProjectSaving(true);
    try {
      const response = await fetch('/api/shader-settings', {
        method: 'POST',
        headers: {'content-type': 'application/json'},
        body: JSON.stringify(shader),
      });
      const result = await response.json() as {error?: string};
      if (!response.ok) throw new Error(result.error || '프로젝트 설정을 저장하지 못했습니다.');
      setNotice('셰이더 설정을 프로젝트 코드에 저장했습니다. 다음 실행부터 기본값으로 사용됩니다.');
    } catch (error) {
      setNotice(error instanceof Error ? error.message : '프로젝트 설정 저장에 실패했습니다.');
    } finally {
      setShaderProjectSaving(false);
    }
  }

  return <MotionConfig reducedMotion="user"><div className="app-shell" id="top">
    <ShaderBackground settings={shader} />
    <a className="skip-link" href="#workspace-main">본문으로 건너뛰기</a>
    <aside className="sidebar">
      <a className="brand" href="#top" aria-label="팩트렌즈 홈"><span className="brand-symbol"><Icon name="lens" size={25}/></span><span>FactLens<small>팩트렌즈</small></span></a>
      <div className="workspace-label"><span className="workspace-avatar">F</span><div>나의 워크스페이스<small>텍스트 검증 · 예시 체험</small></div></div>
      <p className="nav-caption">워크스페이스</p>
      <nav aria-label="주요 메뉴"><a className="nav-item active" href="#review"><Icon name="grid"/>근거 워크스페이스<span className="nav-indicator"/></a><button className="nav-item" onClick={reset}><Icon name="plus"/>새 문서 시작</button><button className="nav-item" onClick={() => setDialog('guide')}><Icon name="book"/>검증 가이드</button></nav>
      <div className="sidebar-bottom"><div className="principle-card"><Icon name="shield"/><strong>결론보다, 근거를 먼저.</strong><p>확인된 내용과 아직 모르는 내용을 나란히 살펴보세요.</p><button onClick={() => setDialog('guide')}>우리의 검증 원칙 <Icon name="arrow" size={15}/></button></div><div className="local-status"><span/>{serviceLabel}</div><p className="sidebar-foot">FACTLENS / EVIDENCE WORKSPACE</p></div>
    </aside>
    <div className="main-shell">
      <header className="topbar"><div className="breadcrumb"><span className="mobile-brand">FactLens</span></div><div className="topbar-actions"><button className="text-button" aria-label="사용 가이드" onClick={() => setDialog('guide')}><Icon name="book"/><span>사용 가이드</span></button>{liquidLabEnabled && <button type="button" className={`text-button liquid-lab-trigger ${liquidLabOpen ? 'is-active' : ''}`} aria-expanded={liquidLabOpen} aria-controls="liquid-lab" onClick={() => setLiquidLabOpen(open => !open)}><Icon name="sliders"/><span>UI 조정</span></button>}<span className="profile-mark" aria-label="로컬 워크스페이스">F</span></div></header>
      <main id="workspace-main" className="page-content">
        <section className="intro"><ParticlesLogo settings={particles}/></section>
        <LiquidPanel as="section" className="composer" glassPadding="22px 25px 0" aria-labelledby="composer-heading" liquid={liquid}>
          <div className="section-heading"><div><span className="step-label">01 / 문서 입력</span><h2 id="composer-heading">어떤 내용을 확인하고 싶으세요?</h2></div><button className="text-button" aria-label="초기화" onClick={reset}><Icon name="reset" size={16}/><span>초기화</span></button></div>
          <form onSubmit={submit}>
            <div className="input-mode" role="group" aria-label="입력 방식"><button type="button" aria-pressed={mode === 'text'} onClick={() => setMode('text')}><Icon name="file" size={16}/>텍스트 입력</button><button type="button" aria-pressed={mode === 'url'} onClick={() => setMode('url')}><Icon name="link" size={16}/>URL 입력<span className="soon-label">준비 중</span></button></div>
            {mode === 'text' ? <div className="editor-wrap"><label htmlFor="document-text">확인할 원문 {sample && <span className="inline-demo">· 합성 예시</span>}</label><textarea ref={editor} id="document-text" value={draft} onChange={e => {setDraft(e.target.value); setSample(false);}} placeholder="기사, 댓글, 궁금한 문장을 붙여넣어 주세요." rows={3} maxLength={12000} onKeyDown={e => {if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {e.preventDefault(); e.currentTarget.form?.requestSubmit();}}}/><span className="character-count">{draft.length.toLocaleString()} / 12,000</span></div> : <div className="url-wrap"><label htmlFor="document-url">확인할 페이지 주소</label><input id="document-url" type="url" value={url} onChange={e => setUrl(e.target.value)} placeholder="https://…"/><p>URL 수집은 아직 연결되지 않았습니다. 원문을 복사해 <button type="button" className="inline-link" onClick={() => setMode('text')}>텍스트로 붙여넣어 주세요.</button></p></div>}
            <div className="focus-row"><label htmlFor="focus-request"><Icon name="lens" size={16}/>확인 요청 <span>선택</span></label><input id="focus-request" value={focus} maxLength={500} onChange={e => setFocus(e.target.value)} placeholder="예: 행사 일정과 무료 참여 조건이 궁금해요."/></div>
            <div className="focus-note"><div><p>gpt-5.6-luna · reasoning max · 웹 검색 사용. 유료 요청이며 시간이 걸릴 수 있습니다.</p>{!sample && <label><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} disabled={busy}/> 원문과 확인 요청을 서버·OpenAI에 보내고 웹 검색에 사용하는 데 동의합니다. 민감한 정보는 제외해 주세요.</label>}<p>{configured === false ? configurationHelp : serviceLabel}</p></div></div><div className="composer-bottom"><p><Icon name="shield" size={15}/>{sample ? '합성 예시는 외부로 전송하지 않습니다.' : '동의한 검증 요청만 외부로 전송합니다.'}</p><div className="submit-actions">{busy && <button type="button" className="secondary-button" onClick={() => {stop(); dispatch({type: 'cancel'}); setNotice('검증 요청을 취소했습니다. 이미 전송된 요청에는 비용이 발생할 수 있습니다.');}}>취소</button>}<button className="primary-button" disabled={busy || mode === 'url' || !draft.trim()}>{busy ? '검증 진행 중' : sample ? '예시 다시 보기' : '팩트 검증 시작'}<Icon name="arrow" size={17}/></button></div></div>
          </form>
          <div className="sample-row"><span>예시로 둘러보기</span><button onClick={loadSample}><span className="sample-dot"/>가상 도시의 문화 행사<Icon name="arrow" size={14}/></button><span className="sample-explainer">일정 · 참여 조건 · 예측</span></div>
        </LiquidPanel>
        <div className="notice-line" role="status" aria-live="polite">{notice || (configured === false ? configurationHelp : '원문을 입력해 실제 검증을 시작하거나, 합성 예시를 선택해 둘러보세요.')}</div>
        <section id="review" className="review-section" aria-labelledby="review-heading">
          <div className="review-heading"><div><span className="step-label">02 / 원문과 근거</span><h2 id="review-heading">흩어진 근거를, 한눈에.</h2></div><button className="secondary-button export-button" disabled={!snapshot || busy} onClick={download}><Icon name="download" size={16}/><span>{snapshot?.demo ? '예시 내보내기' : '결과 내보내기'}</span></button></div>
          {snapshot ? <>
            <div className="review-meta"><span className="document-title"><Icon name="file" size={16}/>{snapshot.demo ? '가을빛 축제 안내 · 합성 예시' : '직접 입력한 문서 · 실제 검증'}</span><div><span>후보 <b>{snapshot.claims.length}</b></span><span>{snapshot.demo ? '예시 문서' : '수집 출처'} <b>{snapshot.demo ? documents.length : liveResult?.sources.length ?? 0}</b></span><span>원자료 그룹 <b>{snapshot.demo ? new Set(documents.map(d => d.group)).size : '관계별 확인'}</b></span></div></div>
            <div className="mobile-tabs" role="group" aria-label="검토 화면 선택">{[['original','원문'],['results','결과'],['sources','출처']].map(([value, label]) => <button key={value} aria-pressed={mobileTab === value} onClick={() => setMobileTab(value)}>{label}</button>)}</div>
            <div className={`review-body mobile-${mobileTab}`}>
              <div className="claim-selector" aria-label="주장 후보 선택">{snapshot.claims.map((claim, index) => <motion.button key={claim.id} layout={!reduce} className={`claim-card ${selected?.id === claim.id ? 'is-selected' : ''}`} aria-pressed={selected?.id === claim.id} onClick={() => select(claim.id)}><div className="claim-card-top"><span>주장 0{index + 1}</span><Badge claim={claim}/></div><strong>{claim.quote}</strong><span className="claim-card-bottom">{selected?.id === claim.id ? '선택한 주장' : '근거 살펴보기'}<Icon name={selected?.id === claim.id ? 'check' : 'arrow'} size={15}/></span></motion.button>)}</div>
              <LiquidPanel as="article" className="original-panel" liquid={liquid}><div className="panel-top"><h3><Icon name="file" size={17}/>원문 읽기</h3><span>{snapshot.demo ? '합성 문서' : '제출한 원문'}</span></div><div className="original-content"><span className="article-kicker">{snapshot.demo ? '문화 · 행사 / 가상의 사례' : '제출 원문 / OpenAI · 웹 검색 검증'}</span><h3>{snapshot.demo ? '달빛시 가을빛 축제,\n알아두면 좋은 세 가지' : '직접 입력한 원문'}</h3><p className="article-byline">{snapshot.demo ? '팩트렌즈 예시 편집실 · 실제 기사 아님' : '검증 요청 시점의 원문을 보존했습니다.'}</p><div className="original-text">{original}</div><div className="highlight-legend"><span/>노란 강조는 선택한 문장입니다. 판정 색상이 아닙니다.</div>{snapshot.focus && <div className="focus-note"><Icon name="lens" size={17}/><div><strong>확인하고 싶은 내용</strong><p>{snapshot.focus}</p><small>{snapshot.demo ? '예시의 비교 범위를 보여드립니다.' : '이 요청을 검증의 참고 범위로 전달했습니다.'}</small></div></div>}</div><div className="original-footer"><Icon name="shield" size={15}/>{snapshot.demo ? '실제 인물·지역·사건과 무관한 합성 예시입니다.' : '원문에서 추출한 최대 3개의 주장을 검증합니다.'}</div></LiquidPanel>
              {selected && snapshot.demo && <LiquidPanel className="evidence-panel" liquid={liquid}><div className="panel-top"><h3><Icon name="lens" size={18}/>주장별 근거</h3><span>{snapshot.demo ? '예시 비교' : '백엔드 미연결'}</span></div><AnimatePresence mode="wait" initial={false}><motion.div className="detail-content" key={selected.id} initial={reduce ? false : {opacity: 0, y: 4}} animate={{opacity: 1, y: 0}} exit={{opacity: 0}} transition={{duration: reduce ? 0 : 0.16}}><div className="result-overview"><span className="article-kicker">선택한 주장 · {snapshot.demo ? '예시 판정' : '문장 후보'}</span><h3>{selected.quote}</h3><Badge claim={selected}/><p>{selected.summary}</p></div><div className="source-content"><div className="source-heading"><h4>근거 문서 비교</h4><span>{sourceDocs.length}개 예시 문서</span></div>{sourceDocs.length ? <><div className="comparison-note"><span className="group-symbol">A</span><p><strong>같은 원자료를 공유합니다.</strong><br/>문서 2개가 독립적인 근거 2개를 뜻하지 않습니다.</p></div>{sourceDocs.map((doc, i) => <button className="source-card" key={doc.id} onClick={() => setDialog(doc.id)}><div className="source-card-top"><span className="source-index">0{i + 1}</span><span className="source-kind">{doc.relation} · 예시</span><Icon name="arrow" size={16}/></div><strong>{doc.title}</strong><span className="source-publisher">{doc.publisher} · {doc.date}</span><blockquote>“{selected.id === 'claim-1' ? (doc.id === 'doc-1' ? '가을빛 축제는 10월 12일부터 14일까지 달빛공원에서 진행합니다.' : '행사는 10월 12일부터 14일까지 열립니다.') : (doc.id === 'doc-1' ? '공예 체험은 사전 예약이 필요하며 재료비 5,000원이 있습니다.' : '공예 체험은 별도 예약과 재료비가 필요합니다.')}”</blockquote><span className="source-footer">원자료 그룹 A <span>예시 문서 전문 보기</span></span></button>)}<p className="evidence-caution">인용 표현은 아래 문서 전문에서 확인해 주세요. 모든 문서는 시연용으로 작성되었습니다.</p></> : <div className="empty-evidence"><Icon name="file" size={27}/><h4>{snapshot.demo ? '비교할 근거가 없습니다' : '아직 검증하지 않았습니다'}</h4><p>{snapshot.demo ? '미래 전망을 현재 사실로 확정하지 않습니다. 예시 문서에도 방문객 추정 근거는 없습니다.' : '현재는 문장을 나누어 보여드리는 로컬 미리보기입니다. 검색·판정 API가 연결되기 전까지 출처와 판정을 생성하지 않습니다.'}</p></div>}</div></motion.div></AnimatePresence></LiquidPanel>}
              {!snapshot.demo && liveResult && <LiquidPanel className="evidence-panel" liquid={liquid}>
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
              </LiquidPanel>}
             </div>
          </> : <LiquidPanel className="empty-workspace" glassPadding="55px 20px" liquid={liquid}><Icon name="lens" size={34}/><h3>첫 번째 문서를 기다리고 있습니다.</h3><p>원문을 붙여넣거나 예시를 불러와 근거 비교 화면을 둘러보세요.</p><button className="secondary-button" onClick={loadSample}>예시 불러오기<Icon name="arrow"/></button></LiquidPanel>}
        </section>
        <footer className="page-footer"><span><span className="footer-mark">F</span>FactLens <span className="footer-divider">/</span>판단을 대신하지 않고, 근거를 연결합니다.</span><button className="text-button" onClick={() => setDialog('guide')}>검증 원칙<Icon name="arrow" size={15}/></button></footer>
      </main>
      {liquidLabEnabled && <AnimatePresence>
        {liquidLabOpen && <motion.aside id="liquid-lab" className="liquid-lab" aria-label="UI 컴포넌트 조정" initial={reduce ? false : {opacity: 0, x: 18, scale: 0.98}} animate={{opacity: 1, x: 0, scale: 1}} exit={reduce ? undefined : {opacity: 0, x: 18, scale: 0.98}} transition={{duration: reduce ? 0 : 0.18}}>
          <div className="liquid-lab-head"><div><span className="liquid-lab-kicker"><Icon name="sliders" size={13}/>DEV TOOL</span><h2>UI Component Lab</h2><p>Glass, shader, lens, particle 설정을 실시간으로 조정합니다.</p></div><button type="button" className="icon-button" onClick={() => setLiquidLabOpen(false)} aria-label="UI 조정 닫기"><Icon name="close" size={17}/></button></div>
          <div className="liquid-lab-scroll">
            <section className="liquid-lab-section" aria-labelledby="liquid-section-heading"><div className="liquid-section-title"><h3 id="liquid-section-heading">Liquid Glass</h3><span>8개 설정</span></div><div className="liquid-controls">{liquidControls.map(control => <LabRange key={control.key} id={`liquid-${control.key}`} label={control.label} value={liquid[control.key]} min={control.min} max={control.max} step={control.step} precision={control.precision} format={control.percent ? value => `${Math.round(value * 100)}%` : undefined} onChange={value => updateLiquid(control.key, value)}/>)}<LabSelect id="liquid-mode" label="렌더 모드" value={liquid.mode} options={[{value: 'standard', label: 'Standard'}, {value: 'polar', label: 'Polar'}, {value: 'prominent', label: 'Prominent'}, {value: 'shader', label: 'Shader'}]} onChange={value => setLiquid(previous => ({...previous, mode: value as LiquidSettings['mode']}))}/></div></section>
            <section className="liquid-lab-section shader-section" aria-labelledby="shader-section-heading"><div className="liquid-section-title"><h3 id="shader-section-heading">Shader Gradient</h3><span>전체 설정 · 자동 저장</span><button type="button" className="lab-reset-button" onClick={resetShader}>초기화</button></div><div className="shader-color-grid">{shaderColorKeys.map((key, index) => <label className="shader-color-control" key={key} htmlFor={`shader-${key}`}><span><b>색상 {index + 1}</b><output>{shader[key]}</output></span><input id={`shader-${key}`} type="color" value={shader[key]} onChange={event => updateShaderColor(key, event.currentTarget.value)} aria-label={`셰이더 색상 ${index + 1}`}/></label>)}</div><div className="liquid-subheading">모션 · 형태</div><div className="liquid-select-grid"><LabSelect id="shader-type" label="형태" value={shader.type} options={[{value: 'plane', label: 'Plane'}, {value: 'sphere', label: 'Sphere'}, {value: 'waterPlane', label: 'Water Plane'}]} onChange={value => updateShaderOption('type', value as ShaderSettings['type'])}/><LabSelect id="shader-animate" label="애니메이션" value={shader.animate} options={[{value: 'on', label: '켜짐'}, {value: 'off', label: '꺼짐'}]} onChange={value => updateShaderOption('animate', value as ShaderSettings['animate'])}/><LabSelect id="shader-range" label="범위" value={shader.range} options={[{value: 'disabled', label: '사용 안 함'}, {value: 'enabled', label: '사용'}]} onChange={value => updateShaderOption('range', value as ShaderSettings['range'])}/><LabSelect id="shader-loop" label="루프" value={shader.loop} options={[{value: 'off', label: '꺼짐'}, {value: 'on', label: '켜짐'}]} onChange={value => updateShaderOption('loop', value as ShaderSettings['loop'])}/></div><div className="liquid-controls shader-controls">{shaderMotionControls.map(control => <LabRange key={control.key} id={`shader-${control.key}`} label={control.label} value={shader[control.key]} min={control.min} max={control.max} step={control.step} precision={control.precision} onChange={value => updateShaderRange(control.key, value)}/>)}</div><div className="liquid-subheading">배치 · 카메라</div><div className="liquid-controls shader-controls">{shaderShapeControls.map(control => <LabRange key={control.key} id={`shader-${control.key}`} label={control.label} value={shader[control.key]} min={control.min} max={control.max} step={control.step} precision={control.precision} onChange={value => updateShaderRange(control.key, value)}/>)}{shaderViewControls.map(control => <LabRange key={control.key} id={`shader-${control.key}`} label={control.label} value={shader[control.key]} min={control.min} max={control.max} step={control.step} precision={control.precision} onChange={value => updateShaderRange(control.key, value)}/>)}</div><div className="liquid-subheading">조명 · 효과</div><div className="liquid-select-grid"><LabSelect id="shader-light-type" label="조명 방식" value={shader.lightType} options={[{value: '3d', label: '3D Light'}, {value: 'env', label: 'Environment'}]} onChange={value => updateShaderOption('lightType', value as ShaderSettings['lightType'])}/><LabSelect id="shader-env-preset" label="환경 프리셋" value={shader.envPreset} options={[{value: 'city', label: 'City'}, {value: 'dawn', label: 'Dawn'}, {value: 'lobby', label: 'Lobby'}]} onChange={value => updateShaderOption('envPreset', value as ShaderSettings['envPreset'])}/><LabSelect id="shader-grain" label="그레인" value={shader.grain} options={[{value: 'off', label: '꺼짐'}, {value: 'on', label: '켜짐'}]} onChange={value => updateShaderOption('grain', value as ShaderSettings['grain'])}/></div><div className="liquid-controls shader-controls">{shaderEffectControls.map(control => <LabRange key={control.key} id={`shader-${control.key}`} label={control.label} value={shader[control.key]} min={control.min} max={control.max} step={control.step} precision={control.precision} onChange={value => updateShaderRange(control.key, value)}/>)}</div><div className="liquid-toggle-grid"><LabToggle id="shader-wireframe" label="와이어프레임" checked={shader.wireframe} onChange={value => updateShaderOption('wireframe', value)}/><LabToggle id="shader-zoom-out" label="줌 아웃" checked={shader.zoomOut} onChange={value => updateShaderOption('zoomOut', value)}/><LabToggle id="shader-toggle-axis" label="축 전환" checked={shader.toggleAxis} onChange={value => updateShaderOption('toggleAxis', value)}/><LabToggle id="shader-transition" label="전환 효과" checked={shader.enableTransition} onChange={value => updateShaderOption('enableTransition', value)}/><LabToggle id="shader-camera-update" label="카메라 업데이트" checked={shader.enableCameraUpdate} onChange={value => updateShaderOption('enableCameraUpdate', value)}/></div><div className="liquid-subheading">캔버스 · 렌더러</div><div className="liquid-controls shader-controls">{shaderCanvasControls.map(control => <LabRange key={control.key} id={`shader-${control.key}`} label={control.label} value={shader[control.key]} min={control.min} max={control.max} step={control.step} precision={control.precision} onChange={value => updateShaderRange(control.key, value)}/>)}</div><div className="liquid-select-grid"><LabSelect id="shader-pointer-events" label="포인터 이벤트" value={shader.pointerEvents} options={[{value: 'none', label: '무시'}, {value: 'auto', label: '허용'}]} onChange={value => updateShaderOption('pointerEvents', value as ShaderSettings['pointerEvents'])}/><LabSelect id="shader-power-preference" label="GPU 선호" value={shader.powerPreference} options={[{value: 'low-power', label: '저전력'}, {value: 'high-performance', label: '고성능'}, {value: 'default', label: '기본'}]} onChange={value => updateShaderOption('powerPreference', value as ShaderSettings['powerPreference'])}/></div><div className="liquid-toggle-grid"><LabToggle id="shader-lazy-load" label="지연 로드" checked={shader.lazyLoad} onChange={value => updateShaderOption('lazyLoad', value)}/><LabToggle id="shader-preserve-buffer" label="버퍼 보존" checked={shader.preserveDrawingBuffer} onChange={value => updateShaderOption('preserveDrawingBuffer', value)}/></div><LabText id="shader-root-margin" label="Intersection root margin" value={shader.rootMargin} onChange={value => updateShaderOption('rootMargin', value)}/></section>
            <section className="liquid-lab-section shader-section" aria-labelledby="lens-section-heading"><div className="liquid-section-title"><h3 id="lens-section-heading">Lens Visual</h3><span>렌즈 코어 · 자동 저장</span><button type="button" className="lab-reset-button" onClick={resetLens}>초기화</button></div><div className="shader-color-grid lens-color-grid">{lensColorKeys.map((key, index) => <label className="shader-color-control" key={key} htmlFor={`lens-${key}`}><span><b>색상 {index + 1}</b><output>{lens[key]}</output></span><input id={`lens-${key}`} type="color" value={lens[key]} onChange={event => updateLensOption(key, event.currentTarget.value)} aria-label={`렌즈 색상 ${index + 1}`}/></label>)}</div><div className="liquid-subheading">모션 · 왜곡</div><div className="liquid-controls shader-controls">{lensMotionControls.map(control => <LabRange key={control.key} id={`lens-${control.key}`} label={control.label} value={lens[control.key]} min={control.min} max={control.max} step={control.step} precision={control.precision} onChange={value => updateLensRange(control.key, value)}/>)}</div><div className="liquid-subheading">크기 · 배치</div><div className="liquid-select-grid"><LabSelect id="lens-fit" label="맞춤 방식" value={lens.fit} options={[{value: 'contain', label: 'Contain'}, {value: 'cover', label: 'Cover'}, {value: 'none', label: 'None'}]} onChange={value => updateLensOption('fit', value as LensSettings['fit'])}/></div><div className="liquid-controls shader-controls">{lensSizingControls.map(control => <LabRange key={control.key} id={`lens-${control.key}`} label={control.label} value={lens[control.key]} min={control.min} max={control.max} step={control.step} precision={control.precision} onChange={value => updateLensRange(control.key, value)}/>)}</div></section>
            <section className="liquid-lab-section shader-section" aria-labelledby="particles-section-heading"><div className="liquid-section-title"><h3 id="particles-section-heading">TRUE OR NOT</h3><span>14개 설정 · 자동 저장</span><button type="button" className="lab-reset-button" onClick={resetParticles}>초기화</button></div><div className="liquid-text-controls"><LabText id="particle-text" label="로고 텍스트" value={particles.particleText} maxLength={40} onChange={value => updateParticleOption('particleText', value)}/><LabText id="particle-character" label="입자 기호" value={particles.particleCharacter} maxLength={2} onChange={value => updateParticleOption('particleCharacter', value)}/></div><div className="liquid-select-grid"><LabSelect id="particle-color" label="입자 색상" value={particleColorPreset(particles.particleColor)} options={[{value: 'sample', label: '원본 샘플'}, {value: '#91ddd6', label: 'Cyan'}, {value: '#b5a6ef', label: 'Violet'}, {value: '#b7fff5', label: 'Mint'}, {value: 'custom', label: '직접 선택'}]} onChange={value => updateParticleOption('particleColor', value === 'custom' ? particleSolidColor(particles.particleColor) : value as ParticleLogoControls['particleColor'])}/><LabColor id="particle-color-custom" label="직접 색상" value={particleSolidColor(particles.particleColor)} onChange={value => updateParticleOption('particleColor', value as ParticleLogoControls['particleColor'])}/></div><div className="liquid-subheading">모양</div><div className="liquid-controls shader-controls">{particleAppearanceControls.map(control => <LabRange key={control.key} id={`particle-${control.key}`} label={control.label} value={particles[control.key]} min={control.min} max={control.max} step={control.step} precision={control.precision} onChange={value => updateParticleRange(control.key, value)}/>)}</div><div className="liquid-toggle-grid"><LabToggle id="particle-tilt" label="기울기 반응" checked={particles.tilt} onChange={value => setParticles(previous => ({...previous, tilt: value}))}/></div><div className="liquid-subheading">상호작용</div><div className="liquid-controls shader-controls">{particleInteractionControls.map(control => <LabRange key={control.key} id={`particle-${control.key}`} label={control.label} value={particles[control.key]} min={control.min} max={control.max} step={control.step} precision={control.precision} onChange={value => updateParticleRange(control.key, value)}/>)}</div></section>
          </div>
          <div className="liquid-lab-foot"><span><span className="live-dot"/>브라우저에 저장됨</span><div className="liquid-lab-actions"><button type="button" className="text-button" onClick={saveShaderToProject} disabled={shaderProjectSaving}>{shaderProjectSaving ? '저장 중' : '프로젝트 저장'}</button><button type="button" className="text-button" onClick={copyShaderCode}>코드 복사</button><button type="button" className="text-button" onClick={resetShader}><Icon name="reset" size={14}/>배경 기본값</button><button type="button" className="text-button" onClick={() => setLiquid(defaultLiquidSettings)}>글래스 기본값</button></div></div>
        </motion.aside>}
      </AnimatePresence>}
    </div>
    <Modal open={dialog !== null} title={activeDocument?.title || (dialog === 'guide' ? '근거를 읽는 세 가지 원칙' : '실제 검증과 합성 예시 안내')} onClose={() => setDialog(null)}>{activeDocument ? <><p className="dialog-notice">합성 예시 문서 · 외부 출처 링크가 아닙니다.</p><dl className="document-metadata"><dt>작성 주체</dt><dd>{activeDocument.publisher}</dd><dt>설정 날짜</dt><dd>{activeDocument.date}</dd><dt>원자료 관계</dt><dd>그룹 {activeDocument.group} · {activeDocument.relation}</dd></dl><div className="document-fulltext">{activeDocument.text}</div></> : dialog === 'guide' ? <ol className="guide-list"><li><span>01</span><div><h3>주장을 작게 나누세요.</h3><p>누가, 언제, 어디서, 어떤 조건으로 한 말인지 원문과 함께 확인하세요.</p></div></li><li><span>02</span><div><h3>출처의 수보다 관계를 보세요.</h3><p>같은 발표를 옮긴 여러 문서는 하나의 원자료를 공유할 수 있습니다.</p></div></li><li><span>03</span><div><h3>모르는 것은 남겨 두세요.</h3><p>근거가 없다고 거짓은 아닙니다. 의견과 미래 예측을 확정된 사실처럼 판정하지 않습니다.</p></div></li></ol> : <div className="about-copy"><p>달빛시와 가을빛 축제는 가상의 사례입니다. 모든 예시 문서와 판정은 인터페이스를 설명하기 위해 작성했습니다.</p><p>동의 후 검증을 시작하면 원문과 확인 요청이 서버와 OpenAI에 전달되며 웹 검색을 사용합니다. gpt-5.6-luna · max 유료 요청입니다. URL 수집은 지원하지 않습니다. 예시는 외부로 전송하지 않습니다.</p><p>이 화면은 작업 이력을 저장하지 않으며 새로고침하면 사라집니다. 외부 서비스의 데이터 처리는 해당 서비스 정책을 따릅니다. 내보내기에는 원문이 포함되고 합성 예시와 실제 결과가 구분됩니다.</p></div>}</Modal>
  </div></MotionConfig>;
}
