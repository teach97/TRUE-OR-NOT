"use client";

import { useEffect, useRef } from 'react';
import type { CSSProperties } from 'react';

interface Rgb {
  r: number;
  g: number;
  b: number;
}

type Letter = {
  char: string;
  rgb: Rgb;
  fromRgb: Rgb;
  targetRgb: Rgb;
  colorProgress: number;
};

export type LetterGlitchProps = {
  glitchColors?: string[];
  glitchSpeed?: number;
  centerVignette?: boolean;
  outerVignette?: boolean;
  smooth?: boolean;
  lightMode?: boolean;
  backgroundColor?: string;
  className?: string;
  characters?: string;
};

const FALLBACK_RGB: Rgb = {r: 255, g: 255, b: 255};
const DEFAULT_COLORS = ['#2b4539', '#61dca3', '#61b3dc'];
const DEFAULT_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$&*()-_+=/[]{};:<>.,0123456789';

function LetterGlitch({
  glitchColors = DEFAULT_COLORS,
  glitchSpeed = 50,
  centerVignette = false,
  outerVignette = true,
  smooth = true,
  lightMode = false,
  backgroundColor,
  className = '',
  characters = DEFAULT_CHARACTERS
}: LetterGlitchProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationRef = useRef<number | null>(null);
  const letters = useRef<Letter[]>([]);
  const grid = useRef({columns: 0, rows: 0});
  const context = useRef<CanvasRenderingContext2D | null>(null);
  const lastGlitchTime = useRef(Date.now());

  const lettersAndSymbols = Array.from(characters);
  const palette = glitchColors.length > 0 ? glitchColors : DEFAULT_COLORS;
  const fontSize = 16;
  const charWidth = 10;
  const charHeight = 20;

  const getRandomChar = () => lettersAndSymbols[Math.floor(Math.random() * lettersAndSymbols.length)] || 'A';

  const getRandomRgb = (): Rgb => {
    const color = palette[Math.floor(Math.random() * palette.length)];
    return hexToRgb(color) || FALLBACK_RGB;
  };

  const calculateGrid = (width: number, height: number) => ({
    columns: Math.ceil(width / charWidth),
    rows: Math.ceil(height / charHeight)
  });

  const initializeLetters = (columns: number, rows: number) => {
    grid.current = {columns, rows};
    letters.current = Array.from({length: columns * rows}, () => {
      const rgb = getRandomRgb();
      return {
        char: getRandomChar(),
        rgb,
        fromRgb: rgb,
        targetRgb: getRandomRgb(),
        colorProgress: 1
      };
    });
  };

  const drawLetters = (indices?: number[]) => {
    if (!context.current || letters.current.length === 0 || !canvasRef.current) return;

    const ctx = context.current;
    const {width, height} = canvasRef.current.getBoundingClientRect();
    ctx.font = `${fontSize}px monospace`;
    ctx.textBaseline = 'top';

    const drawLetter = (index: number) => {
      const letter = letters.current[index];
      if (!letter) return;

      const x = (index % grid.current.columns) * charWidth;
      const y = Math.floor(index / grid.current.columns) * charHeight;
      ctx.clearRect(x, y, charWidth, charHeight);
      ctx.fillStyle = `rgb(${letter.rgb.r}, ${letter.rgb.g}, ${letter.rgb.b})`;
      ctx.fillText(letter.char, x, y);
    };

    if (!indices) {
      ctx.clearRect(0, 0, width, height);
      letters.current.forEach((_letter, index) => drawLetter(index));
      return;
    }

    new Set(indices).forEach(index => drawLetter(index));
  };

  const resizeCanvas = () => {
    const canvas = canvasRef.current;
    const parent = canvas?.parentElement;
    if (!canvas || !parent) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = parent.getBoundingClientRect();
    canvas.width = Math.floor(rect.width * dpr);
    canvas.height = Math.floor(rect.height * dpr);
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    context.current?.setTransform(dpr, 0, 0, dpr, 0, 0);
    const {columns, rows} = calculateGrid(rect.width, rect.height);
    initializeLetters(columns, rows);
    drawLetters();
  };

  const updateLetters = (): number[] => {
    if (letters.current.length === 0) return [];

    const updateCount = Math.max(1, Math.floor(letters.current.length * 0.05));
    const changed = new Set<number>();
    for (let i = 0; i < updateCount; i += 1) {
      const index = Math.floor(Math.random() * letters.current.length);
      const letter = letters.current[index];
      if (!letter) continue;

      letter.char = getRandomChar();
      letter.fromRgb = letter.rgb;
      letter.targetRgb = getRandomRgb();

      if (!smooth) {
        letter.rgb = letter.targetRgb;
        letter.colorProgress = 1;
      } else {
        letter.colorProgress = 0;
      }
      changed.add(index);
    }

    return [...changed];
  };

  const handleSmoothTransitions = (): number[] => {
    const changed: number[] = [];

    letters.current.forEach((letter, index) => {
      if (letter.colorProgress < 1) {
        letter.colorProgress = Math.min(1, letter.colorProgress + 0.05);
        letter.rgb = mixRgb(letter.fromRgb, letter.targetRgb, letter.colorProgress);
        changed.push(index);
      }
    });

    return changed;
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    let disposed = false;
    let resizeTimeout: ReturnType<typeof setTimeout> | undefined;
    context.current = canvas.getContext('2d');
    if (!context.current) return;

    const animate = () => {
      if (disposed) return;

      const changed = new Set<number>();
      const now = Date.now();
      if (now - lastGlitchTime.current >= glitchSpeed) {
        updateLetters().forEach(index => changed.add(index));
        lastGlitchTime.current = now;
      }

      if (smooth) handleSmoothTransitions().forEach(index => changed.add(index));
      if (changed.size > 0) drawLetters([...changed]);
      animationRef.current = requestAnimationFrame(animate);
    };

    resizeCanvas();
    lastGlitchTime.current = Date.now();
    animate();

    const handleResize = () => {
      if (resizeTimeout) clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        if (!disposed) resizeCanvas();
      }, 100);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      disposed = true;
      if (resizeTimeout) clearTimeout(resizeTimeout);
      if (animationRef.current !== null) cancelAnimationFrame(animationRef.current);
      window.removeEventListener('resize', handleResize);
      context.current = null;
      letters.current = [];
    };
  }, [characters, glitchColors, glitchSpeed, smooth]);

  const containerStyle: CSSProperties = {
    position: 'relative',
    width: '100%',
    height: '100%',
    overflow: 'hidden',
    backgroundColor: backgroundColor ?? (lightMode ? '#ffffff' : '#000000')
  };

  const canvasStyle: CSSProperties = {
    display: 'block',
    width: '100%',
    height: '100%'
  };

  const vignetteStyle: CSSProperties = {
    position: 'absolute',
    inset: 0,
    pointerEvents: 'none',
    background: lightMode
      ? 'radial-gradient(circle, rgba(255,255,255,0) 58%, rgba(255,255,255,0.96) 100%)'
      : 'radial-gradient(circle, rgba(0,0,0,0) 60%, rgba(0,0,0,1) 100%)'
  };

  const centerVignetteStyle: CSSProperties = {
    position: 'absolute',
    inset: 0,
    pointerEvents: 'none',
    background: lightMode
      ? 'radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0) 60%)'
      : 'radial-gradient(circle, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 60%)'
  };

  return (
    <div style={containerStyle} className={className}>
      <canvas ref={canvasRef} style={canvasStyle} />
      {outerVignette && <div style={vignetteStyle} />}
      {centerVignette && <div style={centerVignetteStyle} />}
    </div>
  );
}

function hexToRgb(hex: string): Rgb | null {
  const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
  const normalized = hex.replace(shorthandRegex, (_match, r, g, b) => r + r + g + g + b + b);
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(normalized);

  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      }
    : null;
}

function mixRgb(start: Rgb, end: Rgb, factor: number): Rgb {
  return {
    r: Math.round(start.r + (end.r - start.r) * factor),
    g: Math.round(start.g + (end.g - start.g) * factor),
    b: Math.round(start.b + (end.b - start.b) * factor)
  };
}

export default LetterGlitch;
