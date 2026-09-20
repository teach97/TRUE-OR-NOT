export type ParticleColor = 'sample' | `#${string}`;

export type ParticleLogoControls = {
  particleText: string;
  particleCharacter: string;
  particleColor: ParticleColor;
  sampling: number;
  particleSpacing: number;
  particleSize: number;
  tilt: boolean;
  tiltFactor: number;
  tiltSpeed: number;
  displaceStrength: number;
  displaceRadius: number;
  velocityInfluence: number;
  returnSpeed: number;
  canvasOpacity: number;
};

export const defaultParticleLogoControls: ParticleLogoControls = {
  particleText: 'TRUE OR NOT',
  particleCharacter: '•',
  particleColor: '#b7fff5',
  sampling: 4,
  particleSpacing: 0.0032,
  particleSize: 0.011,
  tilt: false,
  tiltFactor: 0.08,
  tiltSpeed: 0.04,
  displaceStrength: 0.72,
  displaceRadius: 0.18,
  velocityInfluence: 0.5,
  returnSpeed: 0.05,
  canvasOpacity: 0.82,
};

export const particleLogoSettingsStorageKey = 'factlens:particles-logo-settings:v1';
export const particleLogoSettingsEvent = 'factlens:particles-logo-settings-change';

function clamp(value: unknown, min: number, max: number, fallback: number) {
  return typeof value === 'number' && Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : fallback;
}

function particleColor(value: unknown, fallback: ParticleColor): ParticleColor {
  if (value === 'sample') return value;
  return typeof value === 'string' && /^#[0-9a-f]{6}$/i.test(value) ? value.toLowerCase() as ParticleColor : fallback;
}

function particleText(value: unknown, fallback: string) {
  if (typeof value !== 'string') return fallback;
  const normalized = value.replace(/\s+/g, ' ').trim().slice(0, 40);
  return normalized || fallback;
}

function particleCharacter(value: unknown, fallback: string) {
  if (typeof value !== 'string') return fallback;
  const normalized = Array.from(value.trim()).slice(0, 2).join('');
  return normalized || fallback;
}

export function normalizeParticleLogoControls(value: unknown): ParticleLogoControls {
  const parsed = value && typeof value === 'object' ? value as Partial<ParticleLogoControls> : {};
  return {
    particleText: particleText(parsed.particleText, defaultParticleLogoControls.particleText),
    particleCharacter: particleCharacter(parsed.particleCharacter, defaultParticleLogoControls.particleCharacter),
    particleColor: particleColor(parsed.particleColor, defaultParticleLogoControls.particleColor),
    sampling: Math.round(clamp(parsed.sampling, 2, 12, defaultParticleLogoControls.sampling)),
    particleSpacing: clamp(parsed.particleSpacing, 0.001, 0.006, defaultParticleLogoControls.particleSpacing),
    particleSize: clamp(parsed.particleSize, 0.001, 0.02, defaultParticleLogoControls.particleSize),
    tilt: typeof parsed.tilt === 'boolean' ? parsed.tilt : defaultParticleLogoControls.tilt,
    tiltFactor: clamp(parsed.tiltFactor, 0, 0.3, defaultParticleLogoControls.tiltFactor),
    tiltSpeed: clamp(parsed.tiltSpeed, 0, 0.2, defaultParticleLogoControls.tiltSpeed),
    displaceStrength: clamp(parsed.displaceStrength, 0, 2, defaultParticleLogoControls.displaceStrength),
    displaceRadius: clamp(parsed.displaceRadius, 0.02, 0.5, defaultParticleLogoControls.displaceRadius),
    velocityInfluence: clamp(parsed.velocityInfluence, 0, 1, defaultParticleLogoControls.velocityInfluence),
    returnSpeed: clamp(parsed.returnSpeed, 0.005, 0.2, defaultParticleLogoControls.returnSpeed),
    canvasOpacity: clamp(parsed.canvasOpacity, 0.05, 1, defaultParticleLogoControls.canvasOpacity),
  };
}

export function parseParticleLogoControls(raw: string | null): ParticleLogoControls {
  if (!raw) return {...defaultParticleLogoControls};
  try {
    return normalizeParticleLogoControls(JSON.parse(raw));
  } catch {
    return {...defaultParticleLogoControls};
  }
}

export function emitParticleLogoSettings(settings: ParticleLogoControls) {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new CustomEvent<ParticleLogoControls>(particleLogoSettingsEvent, {detail: settings}));
}
