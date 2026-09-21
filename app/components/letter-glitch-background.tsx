"use client";

import {Component, useEffect, useState} from 'react';
import type {ReactNode} from 'react';
import LetterGlitch from './letter-glitch';

const letterGlitchColors = ['#2b4539', '#61dca3', '#0adce8'];

class BackgroundBoundary extends Component<{children: ReactNode}, {failed: boolean}> {
  state = {failed: false};

  static getDerivedStateFromError() {
    return {failed: true};
  }

  render() {
    return this.state.failed ? null : this.props.children;
  }
}

export default function LetterGlitchBackground() {
  const [supported, setSupported] = useState(false);
  const [reduced, setReduced] = useState(true);
  const [visible, setVisible] = useState(true);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const syncMotion = () => setReduced(media.matches);
    const syncVisibility = () => setVisible(!document.hidden);

    syncMotion();
    syncVisibility();
    media.addEventListener('change', syncMotion);
    document.addEventListener('visibilitychange', syncVisibility);

    try {
      const canvas = document.createElement('canvas');
      setSupported(Boolean(canvas.getContext('2d')));
    } catch {
      setSupported(false);
    }

    return () => {
      media.removeEventListener('change', syncMotion);
      document.removeEventListener('visibilitychange', syncVisibility);
    };
  }, []);

  const active = supported && !reduced && visible && !paused;

  return (
    <>
      <div className="letter-glitch-background" data-letter-glitch-background data-active={active} aria-hidden="true">
        {active && (
          <BackgroundBoundary>
            <LetterGlitch
              glitchColors={letterGlitchColors}
              glitchSpeed={75}
              smooth
              outerVignette
              backgroundColor="transparent"
            />
          </BackgroundBoundary>
        )}
      </div>
      {supported && !reduced && (
        <button
          type="button"
          className="background-toggle"
          aria-label={paused ? '배경 움직임 켜기' : '배경 움직임 끄기'}
          aria-pressed={!paused}
          onClick={() => setPaused(value => !value)}
        >
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
            {paused ? <path d="m5 3 7 5-7 5Z" /> : <path d="M5 3v10M11 3v10" />}
          </svg>
          배경 모션 {paused ? '끔' : '켬'}
        </button>
      )}
    </>
  );
}
