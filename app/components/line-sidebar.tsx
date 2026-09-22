"use client";

import {useCallback, useEffect, useRef, useState, type CSSProperties, type PointerEvent, type ReactNode} from 'react';

/**
 * Adapted from React Bits Line Sidebar:
 * https://reactbits.dev/components/line-sidebar
 *
 * The component stays local so the existing navigation actions can remain
 * in the dashboard without adding a runtime dependency.
 */

type Falloff = 'linear' | 'smooth' | 'sharp';

export type LineSidebarItem = {
  label: string;
  icon?: ReactNode;
};

type LineSidebarProps = {
  items: LineSidebarItem[];
  accentColor?: string;
  textColor?: string;
  markerColor?: string;
  showIndex?: boolean;
  showMarker?: boolean;
  proximityRadius?: number;
  maxShift?: number;
  falloff?: Falloff;
  markerLength?: number;
  markerGap?: number;
  tickScale?: number;
  scaleTick?: boolean;
  itemGap?: number;
  fontSize?: number;
  smoothing?: number;
  defaultActive?: number | null;
  onItemClick?: (index: number, label: string) => void;
  className?: string;
  ariaLabel?: string;
};

const FALLOFF_CURVES: Record<Falloff, (progress: number) => number> = {
  linear: progress => progress,
  smooth: progress => progress * progress * (3 - 2 * progress),
  sharp: progress => progress * progress * progress,
};

type LineSidebarStyle = CSSProperties & Record<`--${string}`, string | number>;

export default function LineSidebar({
  items,
  accentColor = '#f4f4f4',
  textColor = '#9b9b9b',
  markerColor = '#ffffff30',
  showIndex = true,
  showMarker = true,
  proximityRadius = 84,
  maxShift = 16,
  falloff = 'smooth',
  markerLength = 30,
  markerGap = 0,
  tickScale = 0.5,
  scaleTick = true,
  itemGap = 12,
  fontSize = 0.78,
  smoothing = 90,
  defaultActive = null,
  onItemClick,
  className = '',
  ariaLabel = '사이드바 메뉴',
}: LineSidebarProps) {
  const itemCount = items.length;
  const listRef = useRef<HTMLUListElement>(null);
  const itemRefs = useRef<Array<HTMLLIElement | null>>([]);
  const targetsRef = useRef<number[]>([]);
  const currentRef = useRef<number[]>([]);
  const rafRef = useRef<number | null>(null);
  const lastRef = useRef(0);
  const activeRef = useRef(defaultActive);
  const smoothingRef = useRef(smoothing);
  const reducedMotionRef = useRef(false);
  const [activeIndex, setActiveIndex] = useState(defaultActive);

  activeRef.current = activeIndex;
  smoothingRef.current = smoothing;

  const runFrame = useCallback((now: number) => {
    const deltaTime = Math.min((now - lastRef.current) / 1000, 0.05);
    lastRef.current = now;
    const timeConstant = Math.max(smoothingRef.current, 1) / 1000;
    const easing = 1 - Math.exp(-deltaTime / timeConstant);
    let moving = false;

    for (let index = 0; index < itemCount; index += 1) {
      const item = itemRefs.current[index];
      if (!item) continue;

      const target = Math.max(targetsRef.current[index] || 0, activeRef.current === index ? 1 : 0);
      const current = currentRef.current[index] || 0;
      const next = current + (target - current) * easing;
      const settled = Math.abs(target - next) < 0.0015;
      const value = settled ? target : next;

      currentRef.current[index] = value;
      item.style.setProperty('--effect', value.toFixed(4));
      if (!settled) moving = true;
    }

    rafRef.current = moving ? requestAnimationFrame(runFrame) : null;
  }, [itemCount]);

  const startLoop = useCallback(() => {
    if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    lastRef.current = performance.now();
    rafRef.current = requestAnimationFrame(runFrame);
  }, [runFrame]);

  const handlePointerMove = useCallback((event: PointerEvent<HTMLUListElement>) => {
    if (reducedMotionRef.current) return;
    const list = listRef.current;
    if (!list) return;

    const rect = list.getBoundingClientRect();
    const pointerY = event.clientY - rect.top;
    const ease = FALLOFF_CURVES[falloff] ?? FALLOFF_CURVES.linear;

    for (let index = 0; index < itemCount; index += 1) {
      const item = itemRefs.current[index];
      if (!item) continue;
      const center = item.offsetTop + item.offsetHeight / 2;
      const distance = Math.abs(pointerY - center);
      targetsRef.current[index] = ease(Math.max(0, 1 - distance / proximityRadius));
    }
    startLoop();
  }, [falloff, itemCount, proximityRadius, startLoop]);

  const handlePointerLeave = useCallback(() => {
    targetsRef.current = Array.from({length: itemCount}, () => 0);
    startLoop();
  }, [itemCount, startLoop]);

  const handleClick = useCallback((index: number, label: string) => {
    setActiveIndex(index);
    onItemClick?.(index, label);
  }, [onItemClick]);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const updateReducedMotion = () => {
      reducedMotionRef.current = mediaQuery.matches;
      if (mediaQuery.matches) {
        targetsRef.current = Array.from({length: itemCount}, () => 0);
        startLoop();
      }
    };

    updateReducedMotion();
    mediaQuery.addEventListener('change', updateReducedMotion);
    return () => mediaQuery.removeEventListener('change', updateReducedMotion);
  }, [itemCount, startLoop]);

  useEffect(() => {
    startLoop();
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    };
  }, [activeIndex, startLoop]);

  const style: LineSidebarStyle = {
    '--accent-color': accentColor,
    '--text-color': textColor,
    '--marker-color': markerColor,
    '--marker-length': `${markerLength}px`,
    '--marker-gap': `${markerGap}px`,
    '--tick-scale': tickScale,
    '--max-shift': `${maxShift}px`,
    '--item-gap': `${itemGap}px`,
    '--font-size': `${fontSize}rem`,
    '--smoothing': `${smoothing}ms`,
  };

  return (
    <nav
      className={`line-sidebar${showMarker ? ' line-sidebar--markers' : ''}${scaleTick ? ' line-sidebar--scale-tick' : ''}${className ? ` ${className}` : ''}`}
      style={style}
      aria-label={ariaLabel}
    >
      <ul ref={listRef} className="line-sidebar__list" onPointerMove={handlePointerMove} onPointerLeave={handlePointerLeave}>
        {items.map((item, index) => (
          <li
            key={`${item.label}-${index}`}
            ref={element => { itemRefs.current[index] = element; }}
            className="line-sidebar__item"
            aria-current={activeIndex === index ? 'true' : undefined}
          >
            <button type="button" className="line-sidebar__button" onClick={() => handleClick(index, item.label)}>
              {showMarker && <span className="line-sidebar__marker" aria-hidden="true" />}
              <span className="line-sidebar__label">
                {showIndex && <span className="line-sidebar__index">{String(index + 1).padStart(2, '0')}</span>}
                {item.icon && <span className="line-sidebar__icon" aria-hidden="true">{item.icon}</span>}
                <span className="line-sidebar__text">{item.label}</span>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
