"use client";

import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';

// Animata Donut Chart pattern: SVG ring with animated stroke offset.
export default function DonutChart({
  size,
  progress,
  circleWidth = 14,
  progressWidth = 14,
  className = '',
  label,
  children,
}: {
  size: number;
  progress: number;
  circleWidth?: number;
  progressWidth?: number;
  className?: string;
  label?: string;
  children?: ReactNode;
}) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const timeout = setTimeout(() => {
      // Start at zero so the ring sweeps on first paint.
      setReady(true);
    }, 250);
    return () => clearTimeout(timeout);
  }, []);

  const radius = size / 2 - Math.max(progressWidth, circleWidth) / 2;
  const circumference = Math.PI * radius * 2;
  const offset = ready ? circumference * ((100 - Math.max(0, Math.min(100, progress))) / 100) : circumference;

  return (
    <div className={`donut-chart ${className}`} role="img" aria-label={label}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        version="1.1"
        xmlns="http://www.w3.org/2000/svg"
        style={{transform: 'rotate(-90deg)'}}
        aria-hidden="true"
      >
        <circle
          r={radius}
          cx={size / 2}
          cy={size / 2}
          fill="transparent"
          stroke="currentColor"
          strokeWidth={`${circleWidth}px`}
          className="donut-chart-track"
        />
        <circle
          r={radius}
          cx={size / 2}
          cy={size / 2}
          stroke="currentColor"
          className="donut-chart-progress"
          strokeWidth={`${progressWidth}px`}
          strokeLinecap="round"
          fill="transparent"
          strokeDasharray={`${circumference}px`}
          strokeDashoffset={`${offset}px`}
        />
      </svg>
      <div className="donut-chart-center">{children}</div>
    </div>
  );
}
