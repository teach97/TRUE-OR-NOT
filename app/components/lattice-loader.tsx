'use client';

import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import type { CSSProperties } from 'react';
import './lattice-loader.css';

type GridSize = 3 | 4;
type LoaderStatus = 'working' | 'done' | 'error';
type Pattern = { cells: Array<number | null>; loop: number; scale: number; lit?: number };
type PatternName = 'arrow' | 'dots' | 'ripple' | 'spiral' | 'orbit' | 'snake' | 'sweep' | 'spin' | 'rain' | 'pulse';
type PatternInput = Pattern | PatternName;
type LoaderStyle = CSSProperties & Record<`--ll-${string}`, string | number>;

const PATTERNS: Record<PatternName, Partial<Record<GridSize, Pattern>>> = {
  arrow: {3: {cells: [1, 2, 3, 0, 1, 2, 1, 2, 3], loop: 7.2, scale: 1}},
  dots: {3: {cells: [0, 1, 2, 0, 1, 2, 0, 1, 2], loop: 3, scale: 2.4}},
  ripple: {3: {cells: [2, 1, 2, 1, 0, 1, 2, 1, 2], loop: 4.8, scale: 1.5}},
  spiral: {3: {cells: [0, 1, 2, 7, 8, 3, 6, 5, 4], loop: 9, scale: 1.2, lit: 0.35}},
  orbit: {
    3: {cells: [0, 1, 2, 7, null, 3, 6, 5, 4], loop: 8, scale: 1.2},
    4: {cells: [0, 1, 2, 3, 11, null, null, 4, 10, null, null, 5, 9, 8, 7, 6], loop: 6, scale: 1.2, lit: 0.45},
  },
  snake: {
    3: {cells: [0, 1, 2, 5, 4, 3, 6, 7, 8], loop: 9, scale: 1, lit: 0.35},
    4: {cells: [0, 1, 2, 3, 7, 6, 5, 4, 8, 9, 10, 11, 15, 14, 13, 12], loop: 16, scale: 1, lit: 0.25},
  },
  sweep: {4: {cells: [0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5, 3, 4, 5, 6], loop: 5, scale: 1, lit: 0.45}},
  spin: {4: {cells: [0, 0, 1, 1, 0, 0, 1, 1, 3, 3, 2, 2, 3, 3, 2, 2], loop: 4, scale: 1.6, lit: 0.35}},
  rain: {4: {cells: [0, 2, 1, 3, 1, 3, 2, 4, 2, 4, 3, 5, 3, 5, 4, 6], loop: 4, scale: 1.2, lit: 0.35}},
  pulse: {4: {cells: [2, 1, 1, 2, 1, 0, 0, 1, 1, 0, 0, 1, 2, 1, 1, 2], loop: 2.4, scale: 2.5, lit: 0.45}},
};
const DEFAULT_PATTERN: Record<GridSize, PatternName> = {3: 'orbit', 4: 'sweep'};
const MARKS: Record<GridSize, Record<'done' | 'error', number[]>> = {
  3: {done: [2, 3, 5, 7], error: [0, 2, 4, 6, 8]},
  4: {done: [7, 8, 10, 13], error: [0, 3, 5, 6, 9, 10, 12, 15]},
};

function resolvePattern(pattern: PatternInput, grid: GridSize): Pattern {
  if (typeof pattern === 'string') return PATTERNS[pattern]?.[grid] || PATTERNS[DEFAULT_PATTERN[grid]][grid]!;
  const cells = Array.from({length: grid * grid}, (_, index) => pattern.cells[index] ?? null);
  const max = Math.max(0, ...cells.filter((value): value is number => value != null));
  return {cells, loop: pattern.loop ?? max + 4.2, scale: pattern.scale ?? 1, lit: pattern.lit ?? 0.62};
}

function formatElapsed(deciseconds: number) {
  return deciseconds < 600
    ? `${(deciseconds / 10).toFixed(1)}s`
    : `${Math.floor(deciseconds / 600)}m ${((deciseconds % 600) / 10).toFixed(1)}s`;
}

function spokenElapsed(deciseconds: number) {
  return deciseconds < 600
    ? `${(deciseconds / 10).toFixed(1)} seconds`
    : `${Math.floor(deciseconds / 600)} minutes ${((deciseconds % 600) / 10).toFixed(1)} seconds`;
}

type LatticeLoaderProps = {
  label?: string;
  doneLabel?: string;
  errorLabel?: string;
  status?: LoaderStatus;
  pattern?: PatternInput;
  grid?: GridSize;
  shape?: 'square' | 'round';
  color?: string;
  doneColor?: string;
  errorColor?: string;
  cellSize?: number;
  gap?: number;
  fontSize?: number;
  step?: number;
  idleOpacity?: number;
  glow?: boolean;
  glowColor?: string;
  showTimer?: boolean;
  elapsed?: number;
  className?: string;
  style?: CSSProperties;
};

/** React Bits Lattice Loader, kept local for the verification progress state. */
export default function LatticeLoader({
  label = '검증 중',
  doneLabel = '완료',
  errorLabel = '실패',
  status = 'working',
  pattern = 'orbit',
  grid = 3,
  shape = 'round',
  color = 'currentColor',
  doneColor = '#22c55e',
  errorColor = '#ef4444',
  cellSize = 7,
  gap = 3,
  fontSize = 14,
  step = 75,
  idleOpacity = 0.15,
  glow = true,
  glowColor = '',
  showTimer = true,
  elapsed,
  className = '',
  style,
}: LatticeLoaderProps) {
  const n: GridSize = grid === 4 ? 4 : 3;
  const pat = resolvePattern(pattern, n);
  const marks = MARKS[n];
  const duration = step * pat.scale;
  const cycle = Math.round(pat.loop * duration);
  const timerRef = useRef<HTMLSpanElement>(null);
  const decisecondsRef = useRef(0);
  const markRef = useRef<'done' | 'error'>('done');
  const mark = status === 'working' ? markRef.current : status;
  markRef.current = mark;
  const [announce, setAnnounce] = useState(`${label}, 진행 중`);

  const paint = (deciseconds: number) => {
    decisecondsRef.current = deciseconds;
    if (timerRef.current) timerRef.current.textContent = formatElapsed(deciseconds);
  };

  useLayoutEffect(() => {
    if (elapsed != null) {
      paint(Math.round(elapsed * 10));
      return undefined;
    }
    if (status !== 'working') return undefined;
    const startedAt = performance.now();
    paint(0);
    const id = setInterval(() => paint(Math.floor((performance.now() - startedAt) / 100)), 100);
    return () => clearInterval(id);
  }, [status, elapsed]);

  useEffect(() => {
    if (status === 'working') setAnnounce(`${label}, 진행 중`);
    else setAnnounce(`${status === 'done' ? doneLabel : errorLabel}${showTimer ? ` ${spokenElapsed(decisecondsRef.current)}` : ''}`);
  }, [status, label, doneLabel, errorLabel, showTimer]);

  const loaderStyle = {
    '--ll-n': n,
    '--ll-cell': `${cellSize}px`,
    '--ll-gap': `${gap}px`,
    '--ll-font': `${fontSize}px`,
    '--ll-color': color,
    '--ll-mark': status === 'error' ? errorColor : doneColor,
    '--ll-idle': idleOpacity,
    '--ll-glow': glowColor || color,
    '--ll-mark-glow': glowColor || (status === 'error' ? errorColor : doneColor),
    '--ll-cycle': `${cycle}ms`,
    ...style,
  } as LoaderStyle;

  return (
    <span
      role="status"
      className={`lattice-loader${className ? ` ${className}` : ''}`}
      data-status={status}
      data-shape={shape}
      data-glow={glow ? '' : undefined}
      style={loaderStyle}
    >
      <span className="lattice-loader__grid" aria-hidden="true">
        <span className="lattice-loader__layer lattice-loader__run">
          {pat.cells.map((unit, index) => (
            <span
              key={index}
              className="lattice-loader__cell"
              data-hole={unit == null ? '' : undefined}
              data-lit={pat.lit && pat.lit !== 0.62 ? Math.round(pat.lit * 100) : undefined}
              style={unit == null ? undefined : {animationDelay: `${Math.round(unit * duration)}ms`}}
            />
          ))}
        </span>
        <span className="lattice-loader__layer lattice-loader__mark">
          {pat.cells.map((_, index) => <span key={index} className="lattice-loader__cell" data-on={marks[mark].includes(index) ? '' : undefined} />)}
        </span>
      </span>
      <span className="lattice-loader__label" aria-hidden="true">
        <span className="lattice-loader__text" data-active={status === 'working' ? '' : undefined}>{label}</span>
        <span className="lattice-loader__text" data-active={status === 'done' ? '' : undefined}>{doneLabel}</span>
        <span className="lattice-loader__text" data-active={status === 'error' ? '' : undefined}>{errorLabel}</span>
      </span>
      {showTimer ? <span ref={timerRef} className="lattice-loader__timer" aria-hidden="true">0.0s</span> : null}
      <span className="lattice-loader__sr">{announce}</span>
    </span>
  );
}
