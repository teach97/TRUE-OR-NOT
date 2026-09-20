"use client";

import { useEffect, useRef, useState } from 'react';
import type { ShaderSettings } from './shader-settings';

type TiltPoint = {
  x: number;
  y: number;
};

export default function ShaderBackground({settings: _settings}: {settings: ShaderSettings}) {
  const stage = useRef<HTMLDivElement>(null);
  const targetTilt = useRef<TiltPoint>({x: 0, y: 0});
  const currentTilt = useRef<TiltPoint>({x: 0, y: 0});
  const frame = useRef<number | null>(null);
  const [reduced, setReduced] = useState(true);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const syncMotion = () => setReduced(media.matches);
    syncMotion();
    media.addEventListener('change', syncMotion);
    return () => media.removeEventListener('change', syncMotion);
  }, []);

  useEffect(() => {
    const root = stage.current;
    if (!root) return;

    const resetTilt = () => {
      targetTilt.current = {x: 0, y: 0};
      if (frame.current === null) frame.current = requestAnimationFrame(animate);
    };

    const animate = () => {
      frame.current = null;
      const current = currentTilt.current;
      const target = targetTilt.current;
      current.x += (target.x - current.x) * 0.12;
      current.y += (target.y - current.y) * 0.12;
      root.style.setProperty('--tilt-x', `${current.x.toFixed(3)}deg`);
      root.style.setProperty('--tilt-y', `${current.y.toFixed(3)}deg`);

      if (Math.abs(target.x - current.x) > 0.01 || Math.abs(target.y - current.y) > 0.01) {
        frame.current = requestAnimationFrame(animate);
      }
    };

    const handlePointerMove = (event: PointerEvent) => {
      if (reduced || paused || !window.innerWidth || !window.innerHeight) {
        resetTilt();
        return;
      }
      targetTilt.current = {
        x: ((event.clientY / window.innerHeight) - 0.5) * -2.4,
        y: ((event.clientX / window.innerWidth) - 0.5) * 3,
      };
      if (frame.current === null) frame.current = requestAnimationFrame(animate);
    };

    const handlePointerLeave = () => resetTilt();
    const handleVisibilityChange = () => {
      if (document.hidden) resetTilt();
    };

    if (!reduced && !paused) {
      window.addEventListener('pointermove', handlePointerMove, {passive: true});
      window.addEventListener('pointerleave', handlePointerLeave);
      window.addEventListener('blur', handlePointerLeave);
      document.addEventListener('visibilitychange', handleVisibilityChange);
    } else {
      resetTilt();
    }

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerleave', handlePointerLeave);
      window.removeEventListener('blur', handlePointerLeave);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      if (frame.current !== null) cancelAnimationFrame(frame.current);
      frame.current = null;
      targetTilt.current = {x: 0, y: 0};
      currentTilt.current = {x: 0, y: 0};
      root.style.setProperty('--tilt-x', '0deg');
      root.style.setProperty('--tilt-y', '0deg');
    };
  }, [paused, reduced]);

  const active = !reduced && !paused;
  return <>
    <div ref={stage} className="shader-background" data-shader-background data-active={active} aria-hidden="true">
      <img
        className="shader-background-image"
        src="/backgrounds/factlens-stripes.png"
        alt=""
        aria-hidden="true"
        draggable={false}
        decoding="async"
        fetchPriority="high"
      />
    </div>
    {!reduced && <button
      type="button"
      className="background-toggle"
      aria-label={paused ? '배경 기울기 켜기' : '배경 기울기 끄기'}
      aria-pressed={!paused}
      onClick={() => setPaused(value => !value)}
    >
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
        {paused ? <path d="m5 3 7 5-7 5Z"/> : <path d="M5 3v10M11 3v10"/>}
      </svg>
      배경 기울기 {paused ? '끔' : '켬'}
    </button>}
  </>;
}
