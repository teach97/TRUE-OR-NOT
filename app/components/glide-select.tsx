"use client";

import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import type { CSSProperties, KeyboardEvent, ReactNode } from 'react';
import './glide-select.css';

export type GlideSelectOption = {
  value: string;
  label: ReactNode;
  tag?: string;
  disabled?: boolean;
};

type OptionInput = string | GlideSelectOption;
type GlideSelectProps = {
  options: OptionInput[];
  value?: string;
  defaultValue?: string;
  onChange?: (value: string, option: GlideSelectOption) => void;
  placeholder?: string;
  showTags?: boolean;
  accentColor?: string;
  surfaceColor?: string;
  highlightColor?: string;
  textColor?: string;
  size?: 'sm' | 'md' | 'lg';
  radius?: number;
  menuWidth?: number;
  placement?: 'top' | 'bottom';
  align?: 'left' | 'right';
  popDuration?: number;
  glideDuration?: number;
  disabled?: boolean;
  ariaLabel?: string;
  ariaDescribedBy?: string;
  className?: string;
};

const SIZES = {
  sm: {chip: 28, row: 26, font: 12},
  md: {chip: 32, row: 30, font: 13},
  lg: {chip: 44, row: 40, font: 14},
} as const;
const MENU_GAP = 6;

function normalizeOption(option: OptionInput): GlideSelectOption {
  return typeof option === 'string' ? {value: option, label: option} : option;
}

function labelText(option: GlideSelectOption) {
  return typeof option.label === 'string' ? option.label : option.value;
}

function nextEnabled(items: GlideSelectOption[], from: number, direction: 1 | -1, wrap = true) {
  for (let offset = 1; offset <= items.length; offset += 1) {
    const candidate = from + offset * direction;
    if (!wrap && (candidate < 0 || candidate >= items.length)) return from;
    const index = (candidate + items.length) % items.length;
    if (!items[index].disabled) return index;
  }
  return from;
}

export default function GlideSelect({
  options,
  value,
  defaultValue,
  onChange,
  placeholder = 'Select…',
  showTags = true,
  accentColor = '#f5f5f5',
  surfaceColor = '#27272a',
  highlightColor = '#3f3f46',
  textColor = '#f5f5f5',
  size = 'md',
  radius = 10,
  menuWidth = 176,
  placement = 'bottom',
  align = 'left',
  popDuration = 180,
  glideDuration = 220,
  disabled = false,
  ariaLabel = 'Select',
  ariaDescribedBy,
  className = '',
}: GlideSelectProps) {
  const items = options.map(normalizeOption);
  const [innerValue, setInnerValue] = useState(defaultValue ?? '');
  const current = value ?? innerValue;
  const selected = items.findIndex(option => option.value === current);
  const [phase, setPhase] = useState<'closed' | 'open' | 'closing'>('closed');
  const [active, setActive] = useState<number | null>(null);
  const [highlightGeometry, setHighlightGeometry] = useState({top: 0, height: 0});
  const [highlightReady, setHighlightReady] = useState(false);
  const [side, setSide] = useState(placement);
  const rootRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const typeahead = useRef('');
  const typeaheadTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const id = useId();
  const sizeValues = SIZES[size] ?? SIZES.md;
  const popOut = Math.round(popDuration * 2 / 3);

  const close = useCallback((instant = false) => {
    setActive(null);
    if (closeTimer.current) clearTimeout(closeTimer.current);
    if (instant) {
      setPhase('closed');
      return;
    }
    setPhase('closing');
    closeTimer.current = setTimeout(() => setPhase('closed'), popOut + 20);
  }, [popOut]);

  const open = useCallback((viaKeyboard = false) => {
    if (disabled) return;
    if (closeTimer.current) clearTimeout(closeTimer.current);
    setSide(placement);
    setActive(selected >= 0 ? selected : (viaKeyboard ? items.findIndex(option => !option.disabled) : null));
    setHighlightReady(false);
    setPhase('open');
  }, [disabled, items, placement, selected]);

  useLayoutEffect(() => {
    if (phase !== 'open') return;
    const root = rootRef.current;
    const menu = menuRef.current;
    if (!root || !menu) return;
    const rect = root.getBoundingClientRect();
    const needed = menu.offsetHeight + MENU_GAP;
    setSide(placement === 'bottom' && rect.bottom + needed > window.innerHeight
      ? 'top'
      : placement === 'top' && rect.top - needed < 0
        ? 'bottom'
        : placement);
  }, [phase, placement, items.length]);

  useEffect(() => {
    if (phase === 'closed') return;
    const onPointerDown = (event: PointerEvent) => {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) close();
    };
    document.addEventListener('pointerdown', onPointerDown, true);
    return () => document.removeEventListener('pointerdown', onPointerDown, true);
  }, [close, phase]);

  useEffect(() => {
    if (disabled && phase !== 'closed') close(true);
  }, [close, disabled, phase]);

  useEffect(() => () => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    if (typeaheadTimer.current) clearTimeout(typeaheadTimer.current);
  }, []);

  const pick = (index: number) => {
    const option = items[index];
    if (!option || option.disabled) {
      close(true);
      return;
    }
    if (option.value !== current) {
      if (value === undefined) setInnerValue(option.value);
      onChange?.(option.value, option);
    }
    close(true);
    rootRef.current?.querySelector<HTMLButtonElement>('.glide-select__trigger')?.focus({preventScroll: true});
  };

  const onTriggerKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    const key = event.key;
    const isOpen = phase === 'open';
    if (!isOpen) {
      if (['Enter', ' ', 'ArrowDown', 'ArrowUp'].includes(key)) {
        event.preventDefault();
        open(true);
      }
      return;
    }

    const currentIndex = active ?? Math.max(0, selected);
    if (key === 'ArrowDown' || key === 'ArrowUp') {
      event.preventDefault();
      setActive(nextEnabled(items, currentIndex, key === 'ArrowDown' ? 1 : -1, false));
    } else if (key === 'Home' || key === 'End') {
      event.preventDefault();
      const start = key === 'Home' ? -1 : items.length;
      const direction = key === 'Home' ? 1 : -1;
      setActive(nextEnabled(items, start, direction, false));
    } else if (key === 'Enter' || key === ' ') {
      event.preventDefault();
      if (active !== null) pick(active);
    } else if (key === 'Escape') {
      event.preventDefault();
      close(true);
    } else if (key.length === 1 && !event.metaKey && !event.ctrlKey && !event.altKey) {
      typeahead.current += key.toLocaleLowerCase();
      if (typeaheadTimer.current) clearTimeout(typeaheadTimer.current);
      typeaheadTimer.current = setTimeout(() => { typeahead.current = ''; }, 600);
      for (let offset = 1; offset <= items.length; offset += 1) {
        const index = (currentIndex + offset + items.length) % items.length;
        if (!items[index].disabled && labelText(items[index]).toLocaleLowerCase().startsWith(typeahead.current)) {
          setActive(index);
          break;
        }
      }
    }
  };

  const highlightIndex = active ?? selected;

  useLayoutEffect(() => {
    if (phase !== 'open' || highlightIndex < 0) return;
    const list = menuRef.current?.querySelector<HTMLDivElement>('.glide-select__list');
    const option = list?.querySelector<HTMLButtonElement>(`[data-index="${highlightIndex}"]`);
    if (!list || !option) return;

    const updateGeometry = () => {
      const next = {top: option.offsetTop, height: option.offsetHeight};
      setHighlightGeometry(current => current.top === next.top && current.height === next.height ? current : next);
    };

    updateGeometry();
    const readyFrame = requestAnimationFrame(() => setHighlightReady(true));
    const observer = new ResizeObserver(updateGeometry);
    observer.observe(list);
    observer.observe(option);
    return () => {
      cancelAnimationFrame(readyFrame);
      observer.disconnect();
    };
  }, [phase, highlightIndex, items.length]);

  const style = {
    '--gs-accent': accentColor,
    '--gs-surface': surfaceColor,
    '--gs-highlight': highlightColor,
    '--gs-text': textColor,
    '--gs-radius': `${radius}px`,
    '--gs-inner-radius': `${Math.max(3, radius - 4)}px`,
    '--gs-chip': `${sizeValues.chip}px`,
    '--gs-row': `${sizeValues.row}px`,
    '--gs-font': `${sizeValues.font}px`,
    '--gs-menu-w': `${menuWidth}px`,
    '--gs-pop': `${popDuration}ms`,
    '--gs-pop-out': `${popOut}ms`,
    '--gs-glide': `${glideDuration}ms`,
  } as CSSProperties;

  return <div ref={rootRef} className={`glide-select ${className}`.trim()} data-size={size} data-disabled={disabled ? '' : undefined} style={style}>
    <button
      type="button"
      className="glide-select__trigger"
      role="combobox"
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      aria-haspopup="listbox"
      aria-expanded={phase === 'open'}
      aria-controls={`${id}-listbox`}
      aria-activedescendant={phase === 'open' && active !== null ? `${id}-option-${active}` : undefined}
      disabled={disabled}
      onClick={() => phase === 'open' ? close() : open()}
      onKeyDown={onTriggerKeyDown}
    >
      <span className="glide-select__label" data-empty={selected < 0 ? '' : undefined}>{selected < 0 ? placeholder : items[selected].label}</span>
      <svg className="glide-select__chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m7 10 5 5 5-5"/></svg>
    </button>
    {phase !== 'closed' && <div ref={menuRef} className="glide-select__menu" data-state={phase === 'open' ? 'open' : 'closed'} data-side={side} data-align={align}>
      <div id={`${id}-listbox`} className="glide-select__list" role="listbox" aria-label={ariaLabel} data-live={active !== null ? '' : undefined} data-geometry-ready={highlightReady ? '' : undefined}>
        {highlightIndex >= 0 && <span className="glide-select__pill" aria-hidden="true" style={{transform: `translateY(${highlightGeometry.top}px)`, height: `${highlightGeometry.height}px`}}/>}
        {items.map((option, index) => <button
          id={`${id}-option-${index}`}
          className="glide-select__option"
          type="button"
          role="option"
          aria-selected={index === selected}
          key={option.value}
          disabled={option.disabled}
          tabIndex={-1}
          data-index={index}
          onPointerEnter={event => {if (event.pointerType !== 'touch' && !option.disabled) setActive(index);}}
          onClick={() => pick(index)}
        >
          <span className="glide-select__name">{option.label}</span>
          {showTags && option.tag && <span className="glide-select__tag">{option.tag}</span>}
          <svg className="glide-select__check" data-on={index === selected ? '' : undefined} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg>
        </button>)}
      </div>
    </div>}
  </div>;
}
