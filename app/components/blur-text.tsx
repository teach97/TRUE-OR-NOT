"use client";

import { useEffect, useRef } from 'react';
import { useReducedMotion } from 'motion/react';
import type { CSSProperties } from 'react';

// React Bits BlurText pattern: word-by-word blur resolve on first view.
export default function BlurText({text, className = ''}: {text: string; className?: string}) {
  const ref = useRef<HTMLSpanElement>(null);
  const reduce = useReducedMotion();
  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (reduce) {
      node.classList.add('is-visible');
      return;
    }
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          node.classList.add('is-visible');
          observer.disconnect();
        }
      }
    }, {threshold: 0.4});
    observer.observe(node);
    return () => observer.disconnect();
  }, [reduce, text]);
  const words = text.split(' ');
  return <span ref={ref} className={`blur-text ${className}`}>
    {words.map((word, index) => <span key={index} className="blur-text-word" style={{'--word-i': index} as CSSProperties}>{word}{index < words.length - 1 ? ' ' : ''}</span>)}
  </span>;
}
