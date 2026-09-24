"use client";

import { useCallback } from 'react';

// React Bits SpotlightCard pattern: pointer-tracked radial glow via CSS vars.
// Hover-driven only, so it stays still under prefers-reduced-motion.
export function useSpotlight<T extends HTMLElement>() {
  return useCallback((node: T | null) => {
    if (!node) return undefined;
    const move = (event: PointerEvent) => {
      const rect = node.getBoundingClientRect();
      node.style.setProperty('--spot-x', `${event.clientX - rect.left}px`);
      node.style.setProperty('--spot-y', `${event.clientY - rect.top}px`);
    };
    const leave = () => {
      node.style.removeProperty('--spot-x');
      node.style.removeProperty('--spot-y');
    };
    node.addEventListener('pointermove', move);
    node.addEventListener('pointerleave', leave);
    return () => {
      node.removeEventListener('pointermove', move);
      node.removeEventListener('pointerleave', leave);
    };
  }, []);
}
