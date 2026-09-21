"use client";

import { useAnimationFrame, useMotionValue, useReducedMotion } from "motion/react";
import { useEffect, useMemo, useRef } from "react";

type ScrambleTextProps = {
  children: string;
  active?: boolean;
  duration?: number;
  delay?: number;
  characters?: string;
  from?: "start" | "center" | "end";
  className?: string;
};

const defaultCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?/+-=~";

type ScrambleRun = {
  startedAt: number;
  lastFrame: string;
  finished: boolean;
};

function getRevealOrder(length: number, from: ScrambleTextProps["from"]) {
  const indexes = Array.from({length}, (_, index) => index);
  if (from === "end") return indexes.reverse();
  if (from === "center") {
    const center = (length - 1) / 2;
    return indexes.sort((a, b) => Math.abs(a - center) - Math.abs(b - center));
  }
  return indexes;
}

function randomCharacter(characters: string) {
  return characters[Math.floor(Math.random() * characters.length)] || "·";
}

export default function ScrambleText({
  children,
  active = true,
  duration = 0.62,
  delay = 0,
  characters = defaultCharacters,
  from = "center",
  className,
}: ScrambleTextProps) {
  const text = String(children);
  const reducedMotion = useReducedMotion();
  const output = useMotionValue(text);
  const visualRef = useRef<HTMLSpanElement>(null);
  const runRef = useRef<ScrambleRun>({startedAt: 0, lastFrame: text, finished: true});
  const revealOrder = useMemo(() => getRevealOrder(text.length, from), [text, from]);
  const safeDuration = Math.max(0.08, duration) * 1000;
  const safeDelay = Math.max(0, delay) * 1000;

  useEffect(() => {
    const shouldSkip = reducedMotion || !active || text.length === 0;
    runRef.current = {
      startedAt: 0,
      lastFrame: shouldSkip ? text : "",
      finished: shouldSkip,
    };
    output.set(shouldSkip ? text : text.replace(/[^\s]/g, () => randomCharacter(characters)));
  }, [active, characters, output, reducedMotion, text]);

  useEffect(() => {
    return output.on("change", latest => {
      if (visualRef.current && visualRef.current.textContent !== latest) {
        visualRef.current.textContent = latest;
      }
    });
  }, [output]);

  useAnimationFrame(time => {
    const run = runRef.current;
    if (run.finished || reducedMotion || !active || text.length === 0) return;
    if (!run.startedAt) run.startedAt = time;

    const elapsed = time - run.startedAt;
    const progress = Math.min(1, Math.max(0, (elapsed - safeDelay) / safeDuration));
    const revealCount = Math.floor(progress * revealOrder.length);
    const revealed = new Set(revealOrder.slice(0, revealCount));
    const frame = Array.from(text, (character, index) => {
      if (/\s/.test(character) || revealed.has(index) || progress >= 1) return character;
      return randomCharacter(characters);
    }).join("");

    if (frame !== run.lastFrame) {
      run.lastFrame = frame;
      output.set(frame);
    }

    if (progress >= 1) {
      run.finished = true;
      run.lastFrame = text;
      output.set(text);
    }
  });

  return (
    <span className={className} aria-label={text}>
      <span ref={visualRef} aria-hidden="true">{text}</span>
    </span>
  );
}
