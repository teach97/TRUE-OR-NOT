export type ShaderGradientType = 'plane' | 'sphere' | 'waterPlane';
export type ShaderAnimate = 'on' | 'off';
export type ShaderRange = 'enabled' | 'disabled';
export type ShaderLoop = 'on' | 'off';
export type ShaderLightType = '3d' | 'env';
export type ShaderEnvironmentPreset = 'city' | 'dawn' | 'lobby';
export type ShaderPointerEvents = 'none' | 'auto';
export type ShaderPowerPreference = 'default' | 'high-performance' | 'low-power';

export type ShaderSettings = {
  pixelDensity: number;
  fov: number;
  pointerEvents: ShaderPointerEvents;
  lazyLoad: boolean;
  threshold: number;
  rootMargin: string;
  preserveDrawingBuffer: boolean;
  powerPreference: ShaderPowerPreference;
  type: ShaderGradientType;
  animate: ShaderAnimate;
  uTime: number;
  uSpeed: number;
  uStrength: number;
  uDensity: number;
  uFrequency: number;
  uAmplitude: number;
  range: ShaderRange;
  rangeStart: number;
  rangeEnd: number;
  loop: ShaderLoop;
  loopDuration: number;
  positionX: number;
  positionY: number;
  positionZ: number;
  rotationX: number;
  rotationY: number;
  rotationZ: number;
  color1: string;
  color2: string;
  color3: string;
  reflection: number;
  wireframe: boolean;
  smoothTime: number;
  cAzimuthAngle: number;
  cPolarAngle: number;
  cDistance: number;
  cameraZoom: number;
  lightType: ShaderLightType;
  brightness: number;
  envPreset: ShaderEnvironmentPreset;
  grain: ShaderAnimate;
  grainBlending: number;
  zoomOut: boolean;
  toggleAxis: boolean;
  enableTransition: boolean;
  enableCameraUpdate: boolean;
};

export {defaultShaderSettings} from './shader-settings-config';
import {defaultShaderSettings} from './shader-settings-config';

export const shaderSettingsStorageKey = 'factlens.shader-settings.v1';

function clamp(value: unknown, min: number, max: number, fallback: number) {
  return typeof value === 'number' && Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : fallback;
}

function color(value: unknown, fallback: string) {
  return typeof value === 'string' && /^#[0-9a-f]{6}$/i.test(value) ? value : fallback;
}

function enumValue<T extends string>(value: unknown, allowed: readonly T[], fallback: T): T {
  return typeof value === 'string' && (allowed as readonly string[]).includes(value) ? value as T : fallback;
}

function booleanValue(value: unknown, fallback: boolean) {
  return typeof value === 'boolean' ? value : fallback;
}

function text(value: unknown, fallback: string, maxLength: number) {
  return typeof value === 'string' && value.length <= maxLength ? value : fallback;
}

export function normalizeShaderSettings(value: unknown): ShaderSettings {
  const parsed = value && typeof value === 'object' ? value as Partial<ShaderSettings> : {};
  return {
    pixelDensity: clamp(parsed.pixelDensity, 0.5, 2, defaultShaderSettings.pixelDensity),
    fov: clamp(parsed.fov, 20, 90, defaultShaderSettings.fov),
    pointerEvents: enumValue(parsed.pointerEvents, ['none', 'auto'], defaultShaderSettings.pointerEvents),
    lazyLoad: booleanValue(parsed.lazyLoad, defaultShaderSettings.lazyLoad),
    threshold: clamp(parsed.threshold, 0, 1, defaultShaderSettings.threshold),
    rootMargin: text(parsed.rootMargin, defaultShaderSettings.rootMargin, 80),
    preserveDrawingBuffer: booleanValue(parsed.preserveDrawingBuffer, defaultShaderSettings.preserveDrawingBuffer),
    powerPreference: enumValue(parsed.powerPreference, ['default', 'high-performance', 'low-power'], defaultShaderSettings.powerPreference),
    type: enumValue(parsed.type, ['plane', 'sphere', 'waterPlane'], defaultShaderSettings.type),
    animate: enumValue(parsed.animate, ['on', 'off'], defaultShaderSettings.animate),
    uTime: clamp(parsed.uTime, 0, 100, defaultShaderSettings.uTime),
    uSpeed: clamp(parsed.uSpeed, 0, 0.5, defaultShaderSettings.uSpeed),
    uStrength: clamp(parsed.uStrength, 0, 6, defaultShaderSettings.uStrength),
    uDensity: clamp(parsed.uDensity, 0.5, 3, defaultShaderSettings.uDensity),
    uFrequency: clamp(parsed.uFrequency, 1, 10, defaultShaderSettings.uFrequency),
    uAmplitude: clamp(parsed.uAmplitude, 0, 2, defaultShaderSettings.uAmplitude),
    range: enumValue(parsed.range, ['enabled', 'disabled'], defaultShaderSettings.range),
    rangeStart: clamp(parsed.rangeStart, 0, 100, defaultShaderSettings.rangeStart),
    rangeEnd: clamp(parsed.rangeEnd, 0, 100, defaultShaderSettings.rangeEnd),
    loop: enumValue(parsed.loop, ['on', 'off'], defaultShaderSettings.loop),
    loopDuration: clamp(parsed.loopDuration, 1, 60, defaultShaderSettings.loopDuration),
    positionX: clamp(parsed.positionX, -3, 3, defaultShaderSettings.positionX),
    positionY: clamp(parsed.positionY, -3, 3, defaultShaderSettings.positionY),
    positionZ: clamp(parsed.positionZ, -3, 3, defaultShaderSettings.positionZ),
    rotationX: clamp(parsed.rotationX, -180, 180, defaultShaderSettings.rotationX),
    rotationY: clamp(parsed.rotationY, -180, 180, defaultShaderSettings.rotationY),
    rotationZ: clamp(parsed.rotationZ, -180, 180, defaultShaderSettings.rotationZ),
    color1: color(parsed.color1, defaultShaderSettings.color1),
    color2: color(parsed.color2, defaultShaderSettings.color2),
    color3: color(parsed.color3, defaultShaderSettings.color3),
    reflection: clamp(parsed.reflection, 0, 1, defaultShaderSettings.reflection),
    wireframe: booleanValue(parsed.wireframe, defaultShaderSettings.wireframe),
    smoothTime: clamp(parsed.smoothTime, 0, 2, defaultShaderSettings.smoothTime),
    cAzimuthAngle: clamp(parsed.cAzimuthAngle, 0, 360, defaultShaderSettings.cAzimuthAngle),
    cPolarAngle: clamp(parsed.cPolarAngle, 0, 180, defaultShaderSettings.cPolarAngle),
    cDistance: clamp(parsed.cDistance, 0.1, 20, defaultShaderSettings.cDistance),
    cameraZoom: clamp(parsed.cameraZoom, 0.25, 3, defaultShaderSettings.cameraZoom),
    lightType: enumValue(parsed.lightType, ['3d', 'env'], defaultShaderSettings.lightType),
    brightness: clamp(parsed.brightness, 0.1, 3, defaultShaderSettings.brightness),
    envPreset: enumValue(parsed.envPreset, ['city', 'dawn', 'lobby'], defaultShaderSettings.envPreset),
    grain: enumValue(parsed.grain, ['on', 'off'], defaultShaderSettings.grain),
    grainBlending: clamp(parsed.grainBlending, 0, 1, defaultShaderSettings.grainBlending),
    zoomOut: booleanValue(parsed.zoomOut, defaultShaderSettings.zoomOut),
    toggleAxis: booleanValue(parsed.toggleAxis, defaultShaderSettings.toggleAxis),
    enableTransition: booleanValue(parsed.enableTransition, defaultShaderSettings.enableTransition),
    enableCameraUpdate: booleanValue(parsed.enableCameraUpdate, defaultShaderSettings.enableCameraUpdate),
  };
}

export function parseShaderSettings(raw: string | null): ShaderSettings {
  if (!raw) return {...defaultShaderSettings};
  try {
    return normalizeShaderSettings(JSON.parse(raw));
  } catch {
    return {...defaultShaderSettings};
  }
}
