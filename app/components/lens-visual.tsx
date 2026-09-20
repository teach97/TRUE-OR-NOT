"use client";

import dynamic from 'next/dynamic';
import { Component, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { useReducedMotion } from 'motion/react';
import type { LensSettings } from './lens-settings';
const MeshGradient = dynamic(() => import('@paper-design/shaders-react').then(m => m.MeshGradient), {ssr: false});
class ShaderBoundary extends Component<{children: ReactNode}, {failed: boolean}> {
  state = {failed: false};
  static getDerivedStateFromError() { return {failed: true}; }
  render() { return this.state.failed ? null : this.props.children; }
}
export default function LensVisual({settings}: {settings: LensSettings}) {
  const reduce = useReducedMotion();
  const [supported, setSupported] = useState(false);
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2');
    if (gl) {
      setSupported(true);
      gl.getExtension('WEBGL_lose_context')?.loseContext();
    }
  }, []);
  return <div className="lens-art" aria-hidden="true">
    <div className="lens-grid" />
    <div className="lens-orbit orbit-one" /><div className="lens-orbit orbit-two" />
    <div className="lens-core">{supported && !reduce && <ShaderBoundary><MeshGradient colors={[settings.color1, settings.color2, settings.color3, settings.color4]} speed={settings.speed} distortion={settings.distortion} swirl={settings.swirl} grainMixer={settings.grainMixer} grainOverlay={settings.grainOverlay} fit={settings.fit} scale={settings.scale} rotation={settings.rotation} originX={settings.originX} originY={settings.originY} offsetX={settings.offsetX} offsetY={settings.offsetY} worldWidth={settings.worldWidth} worldHeight={settings.worldHeight} style={{width: '100%', height: '100%'}} /></ShaderBoundary>}<span className="lens-cross" /></div>
    <span className="lens-caption">주장에서 근거로</span>
    <span className="lens-point point-one" /><span className="lens-point point-two" />
  </div>;
}
