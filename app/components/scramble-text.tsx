"use client";

import { useAnimationFrame, useMotionValue, useReducedMotion } from "motion/react";
import { useEffect, useMemo, useRef } from "react";

type ScrambleTextProps = {
  children: string;
  active?: boolean;
  trigger?: "hover" | "mount";
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

function randomizeText(text: string, characters: string) {
  return Array.from(text, character => /\s/.test(character) ? character : randomCharacter(characters)).join("");
}

export default function ScrambleText({
  children,
  active = true,
  trigger = "hover",
  duration = 0.62,
  delay = 0,
  characters = defaultCharacters,
  from = "start",
  className,
}: ScrambleTextProps) {
  const text = String(children);
  const reducedMotion = useReducedMotion();
  const output = useMotionValue(text);
  const hostRef = useRef<HTMLSpanElement>(null);
  const visualRef = useRef<HTMLSpanElement>(null);
  const runRef = useRef<ScrambleRun>({startedAt: 0, lastFrame: text, finished: true});
  const runningRef = useRef(false);
  const hoveringRef = useRef(false);
  const reducedMotionRef = useRef(reducedMotion);
  const textRef = useRef(text);
  const charactersRef = useRef(characters);
  const revealOrder = useMemo(() => getRevealOrder(text.length, from), [text, from]);
  const revealOrderRef = useRef(revealOrder);
  const durationRef = useRef(Math.max(0.08, duration) * 1000);
  const delayRef = useRef(Math.max(0, delay) * 1000);

  function writeVisual(value: string) {
    output.set(value);
    if (visualRef.current && visualRef.current.textContent !== value) {
      visualRef.current.textContent = value;
    }
  }

  function resetVisual() {
    const target = textRef.current;
    runningRef.current = false;
    runRef.current = {startedAt: 0, lastFrame: target, finished: true};
    writeVisual(target);
  }

  function startRun() {
    const target = textRef.current;
    if (reducedMotionRef.current || !active || target.length === 0) {
      resetVisual();
      return;
    }
    runningRef.current = true;
    runRef.current = {startedAt: 0, lastFrame: "", finished: false};
    const scrambled = randomizeText(target, charactersRef.current);
    writeVisual(scrambled);
  }

  useEffect(() => {
    reducedMotionRef.current = reducedMotion;
    textRef.current = text;
    charactersRef.current = characters;
    revealOrderRef.current = revealOrder;
    durationRef.current = Math.max(0.08, duration) * 1000;
    delayRef.current = Math.max(0, delay) * 1000;

    if (trigger === "mount" && active) startRun();
    else if (trigger === "hover" && hoveringRef.current && active) startRun();
    else resetVisual();
  }, [active, characters, delay, duration, reducedMotion, revealOrder, text, trigger]);

  useEffect(() => {
    return output.on("change", latest => {
      if (visualRef.current && visualRef.current.textContent !== latest) {
        visualRef.current.textContent = latest;
      }
    });
  }, [output]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host || trigger !== "hover") return;

    const handleEnter = () => {
      hoveringRef.current = true;
      startRun();
    };
    const handleLeave = () => {
      hoveringRef.current = false;
      resetVisual();
    };

    host.addEventListener("pointerenter", handleEnter);
    host.addEventListener("pointerleave", handleLeave);
    host.addEventListener("focusin", handleEnter);
    host.addEventListener("focusout", handleLeave);
    return () => {
      host.removeEventListener("pointerenter", handleEnter);
      host.removeEventListener("pointerleave", handleLeave);
      host.removeEventListener("focusin", handleEnter);
      host.removeEventListener("focusout", handleLeave);
    };
  }, [active, trigger, text]);

  useAnimationFrame(time => {
    const run = runRef.current;
    const target = textRef.current;
    if (run.finished || !runningRef.current || reducedMotionRef.current || target.length === 0) return;
    if (!run.startedAt) run.startedAt = time;

    const elapsed = time - run.startedAt;
    const progress = Math.min(1, Math.max(0, (elapsed - delayRef.current) / durationRef.current));
    const revealCount = Math.floor(progress * revealOrderRef.current.length);
    const revealed = new Set(revealOrderRef.current.slice(0, revealCount));
    const frame = Array.from(target, (character, index) => {
      if (/\s/.test(character) || revealed.has(index) || progress >= 1) return character;
      return randomCharacter(charactersRef.current);
    }).join("");

    if (frame !== run.lastFrame) {
      run.lastFrame = frame;
      writeVisual(frame);
    }

    if (progress >= 1) {
      run.finished = true;
      runningRef.current = false;
      run.lastFrame = target;
      writeVisual(target);
    }
  });

  return (
    <span
      ref={hostRef}
      className={className}
      aria-label={text}
      style={{display: "inline-grid", whiteSpace: "pre"}}
    >
      <span aria-hidden="true" style={{gridArea: "1 / 1", visibility: "hidden"}}>{text}</span>
      <span ref={visualRef} aria-hidden="true" style={{gridArea: "1 / 1"}}>{text}</span>
    </span>
  );
}
