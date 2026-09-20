export type LensFit = 'none' | 'contain' | 'cover';

export type LensSettings = {
  color1: string;
  color2: string;
  color3: string;
  color4: string;
  speed: number;
  distortion: number;
  swirl: number;
  grainMixer: number;
  grainOverlay: number;
  fit: LensFit;
  scale: number;
  rotation: number;
  originX: number;
  originY: number;
  offsetX: number;
  offsetY: number;
  worldWidth: number;
  worldHeight: number;
};

export const defaultLensSettings: LensSettings = {
  color1: '#14212e',
  color2: '#327e86',
  color3: '#534379',
  color4: '#141a2b',
  speed: 0.08,
  distortion: 0.45,
  swirl: 0.2,
  grainMixer: 0,
  grainOverlay: 0,
  fit: 'contain',
  scale: 1,
  rotation: 0,
  originX: 0.5,
  originY: 0.5,
  offsetX: 0,
  offsetY: 0,
  worldWidth: 0,
  worldHeight: 0,
};

export const lensSettingsStorageKey = 'factlens.lens-settings.v1';

function clamp(value: unknown, min: number, max: number, fallback: number) {
  return typeof value === 'number' && Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : fallback;
}

function color(value: unknown, fallback: string) {
  return typeof value === 'string' && /^#[0-9a-f]{6}$/i.test(value) ? value : fallback;
}

function fit(value: unknown, fallback: LensFit): LensFit {
  return value === 'none' || value === 'contain' || value === 'cover' ? value : fallback;
}

export function normalizeLensSettings(value: unknown): LensSettings {
  const parsed = value && typeof value === 'object' ? value as Partial<LensSettings> : {};
  return {
    color1: color(parsed.color1, defaultLensSettings.color1),
    color2: color(parsed.color2, defaultLensSettings.color2),
    color3: color(parsed.color3, defaultLensSettings.color3),
    color4: color(parsed.color4, defaultLensSettings.color4),
    speed: clamp(parsed.speed, 0, 0.5, defaultLensSettings.speed),
    distortion: clamp(parsed.distortion, 0, 1, defaultLensSettings.distortion),
    swirl: clamp(parsed.swirl, 0, 1, defaultLensSettings.swirl),
    grainMixer: clamp(parsed.grainMixer, 0, 1, defaultLensSettings.grainMixer),
    grainOverlay: clamp(parsed.grainOverlay, 0, 1, defaultLensSettings.grainOverlay),
    fit: fit(parsed.fit, defaultLensSettings.fit),
    scale: clamp(parsed.scale, 0.01, 4, defaultLensSettings.scale),
    rotation: clamp(parsed.rotation, 0, 360, defaultLensSettings.rotation),
    originX: clamp(parsed.originX, 0, 1, defaultLensSettings.originX),
    originY: clamp(parsed.originY, 0, 1, defaultLensSettings.originY),
    offsetX: clamp(parsed.offsetX, -1, 1, defaultLensSettings.offsetX),
    offsetY: clamp(parsed.offsetY, -1, 1, defaultLensSettings.offsetY),
    worldWidth: clamp(parsed.worldWidth, 0, 4096, defaultLensSettings.worldWidth),
    worldHeight: clamp(parsed.worldHeight, 0, 4096, defaultLensSettings.worldHeight),
  };
}

export function parseLensSettings(raw: string | null): LensSettings {
  if (!raw) return {...defaultLensSettings};
  try {
    return normalizeLensSettings(JSON.parse(raw));
  } catch {
    return {...defaultLensSettings};
  }
}
