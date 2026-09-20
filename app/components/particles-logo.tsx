"use client";

import { useEffect, useRef, useState } from 'react';
import { useReducedMotion } from 'motion/react';
import type { ParticlesGLOptions, ParticlesGLEffect } from 'particles-gl';
import {
  defaultParticleLogoControls,
  emitParticleLogoSettings,
  normalizeParticleLogoControls,
  parseParticleLogoControls,
  particleLogoSettingsEvent,
  particleLogoSettingsStorageKey,
} from './particles-settings';
import type { ParticleLogoControls } from './particles-settings';

const logoSelector = '[data-particles-gl-logo-target]';

type TweakpaneChangeEvent = {value: unknown};
type TweakpaneBinding = {
  on: (event: 'change' | 'click', handler: (event: TweakpaneChangeEvent) => void) => TweakpaneBinding;
};
type TweakpaneFolder = {
  addBinding: (
    object: ParticleLogoControls,
    key: keyof ParticleLogoControls,
    options?: Record<string, unknown>,
  ) => TweakpaneBinding;
};
type TweakpanePane = {
  element: HTMLElement;
  addFolder: (options: {title: string}) => TweakpaneFolder;
  addButton: (options: {title: string}) => TweakpaneBinding;
  refresh: () => void;
  dispose: () => void;
};

function saveControls(controls: ParticleLogoControls) {
  const normalized = normalizeParticleLogoControls(controls);
  try {
    window.localStorage.setItem(particleLogoSettingsStorageKey, JSON.stringify(normalized));
  } catch {
    // 저장소를 사용할 수 없는 브라우저에서는 현재 세션 값만 유지합니다.
  }
}

function getParticleOptions(controls: ParticleLogoControls): Omit<ParticlesGLOptions, 'target' | 'on'> {
  return {
    character: controls.particleCharacter,
    particleColor: controls.particleColor,
    sampling: controls.sampling,
    particleSpacing: controls.particleSpacing,
    particleSize: controls.particleSize,
    tilt: controls.tilt,
    tiltFactor: controls.tiltFactor,
    tiltSpeed: controls.tiltSpeed,
    displaceStrength: controls.displaceStrength,
    displaceRadius: controls.displaceRadius,
    velocityInfluence: controls.velocityInfluence,
    returnSpeed: controls.returnSpeed,
  };
}

function updateParticleEffect(effect: ParticlesGLEffect | null, controls: ParticleLogoControls) {
  effect?.updateOptions(getParticleOptions(controls));
}

function updateCanvasOpacity(value: number) {
  document.documentElement.style.setProperty('--logo-particles-opacity', String(value));
}

type ParticlesLogoProps = {settings?: ParticleLogoControls};

export default function ParticlesLogo({settings}: ParticlesLogoProps) {
  const reduce = useReducedMotion();
  const [sourceText, setSourceText] = useState(settings?.particleText ?? defaultParticleLogoControls.particleText);
  const particleEffectRef = useRef<ParticlesGLEffect | null>(null);
  const controlsRef = useRef<ParticleLogoControls>(normalizeParticleLogoControls(settings ?? defaultParticleLogoControls));
  const paneRef = useRef<TweakpanePane | null>(null);

  useEffect(() => {
    const next = settings
      ? normalizeParticleLogoControls(settings)
      : parseParticleLogoControls(window.localStorage.getItem(particleLogoSettingsStorageKey));
    controlsRef.current = next;
    setSourceText(previous => previous === next.particleText ? previous : next.particleText);
    updateCanvasOpacity(next.canvasOpacity);
  }, [settings]);

  useEffect(() => {
    if (reduce) return;

    let disposed = false;
    const controls = controlsRef.current;
    if (sourceText !== controls.particleText) {
      setSourceText(controls.particleText);
      return;
    }
    updateCanvasOpacity(controls.canvasOpacity);

    const options: ParticlesGLOptions = {
      target: logoSelector,
      ...getParticleOptions(controls),
      on: {
        init: instance => {
          if (disposed) instance.cleanup();
        },
      },
    };

    const initTimer = window.setTimeout(() => {
      void import('particles-gl')
        .then(({default: particlesGL}) => {
          if (disposed) return;
          particleEffectRef.current = particlesGL(options);
          updateParticleEffect(particleEffectRef.current, controlsRef.current);
          if (disposed) particleEffectRef.current?.cleanup();
        })
        .catch(error => {
          if (!disposed) console.warn('TRUE OR NOT 로고 particlesGL을 초기화하지 못했습니다.', error);
        });
    }, 100);

    return () => {
      disposed = true;
      window.clearTimeout(initTimer);
      particleEffectRef.current?.cleanup();
      particleEffectRef.current = null;
      document.documentElement.style.removeProperty('--logo-particles-opacity');
    };
  }, [reduce, sourceText]);

  useEffect(() => {
    if (reduce) return;

    const syncSettings = (event: Event) => {
      const next = normalizeParticleLogoControls((event as CustomEvent<unknown>).detail);
      controlsRef.current = next;
      setSourceText(previous => previous === next.particleText ? previous : next.particleText);
      updateCanvasOpacity(next.canvasOpacity);
      updateParticleEffect(particleEffectRef.current, next);
      saveControls(next);
      paneRef.current?.refresh();
    };

    window.addEventListener(particleLogoSettingsEvent, syncSettings);
    return () => window.removeEventListener(particleLogoSettingsEvent, syncSettings);
  }, [reduce]);

  useEffect(() => {
    if (reduce || process.env.NODE_ENV === 'production') return;

    let disposed = false;
    let pane: TweakpanePane | null = null;
    const controls = controlsRef.current;

    void import('tweakpane')
      .then(({Pane}) => {
        if (disposed) return;

        const instance = new Pane({title: 'TRUE OR NOT', expanded: true}) as unknown as TweakpanePane;
        pane = instance;
        paneRef.current = instance;
        instance.element.classList.add('particles-logo-debug-pane');
        Object.assign(instance.element.style, {
          position: 'fixed',
          top: '86px',
          right: '18px',
          zIndex: '50',
          width: '300px',
        });

        const applyAndSave = () => {
          const normalized = normalizeParticleLogoControls(controls);
          Object.assign(controls, normalized);
          updateCanvasOpacity(controls.canvasOpacity);
          updateParticleEffect(particleEffectRef.current, controls);
          saveControls(controls);
          emitParticleLogoSettings(controls);
        };

        const appearance = instance.addFolder({title: 'Appearance'});
        appearance.addBinding(controls, 'particleText', {
          label: 'Text',
        }).on('change', applyAndSave);
        appearance.addBinding(controls, 'particleCharacter', {
          label: 'Particle',
        }).on('change', applyAndSave);
        appearance.addBinding(controls, 'particleColor', {
          label: 'Color',
        }).on('change', applyAndSave);
        appearance.addBinding(controls, 'sampling', {
          label: 'Density',
          min: 2,
          max: 12,
          step: 1,
        }).on('change', applyAndSave);
        appearance.addBinding(controls, 'particleSpacing', {
          label: 'Spacing',
          min: 0.001,
          max: 0.006,
          step: 0.0001,
        }).on('change', applyAndSave);
        appearance.addBinding(controls, 'particleSize', {
          label: 'Size',
          min: 0.001,
          max: 0.02,
          step: 0.0005,
        }).on('change', applyAndSave);
        appearance.addBinding(controls, 'canvasOpacity', {
          label: 'Opacity',
          min: 0.05,
          max: 1,
          step: 0.01,
        }).on('change', applyAndSave);

        const interaction = instance.addFolder({title: 'Interaction'});
        interaction.addBinding(controls, 'tilt', {label: 'Tilt'}).on('change', applyAndSave);
        interaction.addBinding(controls, 'tiltFactor', {
          label: 'Tilt factor',
          min: 0,
          max: 0.3,
          step: 0.01,
        }).on('change', applyAndSave);
        interaction.addBinding(controls, 'tiltSpeed', {
          label: 'Tilt speed',
          min: 0,
          max: 0.2,
          step: 0.005,
        }).on('change', applyAndSave);
        interaction.addBinding(controls, 'displaceStrength', {
          label: 'Push force',
          min: 0,
          max: 2,
          step: 0.05,
        }).on('change', applyAndSave);
        interaction.addBinding(controls, 'displaceRadius', {
          label: 'Push radius',
          min: 0.02,
          max: 0.5,
          step: 0.01,
        }).on('change', applyAndSave);
        interaction.addBinding(controls, 'velocityInfluence', {
          label: 'Velocity',
          min: 0,
          max: 1,
          step: 0.05,
        }).on('change', applyAndSave);
        interaction.addBinding(controls, 'returnSpeed', {
          label: 'Return speed',
          min: 0.005,
          max: 0.2,
          step: 0.005,
        }).on('change', applyAndSave);

        instance.addButton({title: '저장'}).on('click', () => {
          saveControls(controls);
          emitParticleLogoSettings(controls);
        });
        instance.addButton({title: '초기화'}).on('click', () => {
          Object.assign(controls, defaultParticleLogoControls);
          applyAndSave();
          instance.refresh();
        });

        saveControls(controls);
      })
      .catch(error => {
        if (!disposed) console.warn('로고 Tweakpane을 초기화하지 못했습니다.', error);
      });

    return () => {
      disposed = true;
      pane?.dispose();
      if (paneRef.current === pane) paneRef.current = null;
    };
  }, [reduce]);

  return (
    <svg
      className="particles-logo-source"
      data-particles-gl-logo-target
      width="1600"
      height="390"
      viewBox="0 0 1600 390"
      preserveAspectRatio="none"
      aria-hidden="true"
      focusable="false"
    >
      <text x="800" y="318" textAnchor="middle" textLength="1450" lengthAdjust="spacingAndGlyphs" fill="#b7fff5" stroke="#b7fff5" strokeWidth="1.5" strokeLinejoin="round" fontFamily="Arial Black, Arial, sans-serif" fontSize="254" fontWeight="900" letterSpacing="8">{sourceText}</text>
    </svg>
  );
}
