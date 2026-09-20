"use client";

import { ShaderGradient, ShaderGradientCanvas } from '@shadergradient/react';
import type { ShaderSettings } from './shader-settings';

/** 외부 환경맵 없이 주변광만 사용하여 네트워크 의존성을 줄입니다. */
export default function ShaderScene({settings}: {settings: ShaderSettings}) {
  return (
    <ShaderGradientCanvas
      style={{ width: '100%', height: '100%' }}
      pixelDensity={settings.pixelDensity}
      fov={settings.fov}
      pointerEvents={settings.pointerEvents}
      lazyLoad={settings.lazyLoad}
      threshold={settings.threshold}
      rootMargin={settings.rootMargin}
      preserveDrawingBuffer={settings.preserveDrawingBuffer}
      powerPreference={settings.powerPreference}
    >
      <ShaderGradient
        control="props"
        type={settings.type}
        animate={settings.animate}
        uTime={settings.uTime}
        uSpeed={settings.uSpeed}
        uStrength={settings.uStrength}
        uDensity={settings.uDensity}
        uFrequency={settings.uFrequency}
        uAmplitude={settings.uAmplitude}
        range={settings.range}
        rangeStart={settings.rangeStart}
        rangeEnd={settings.rangeEnd}
        loop={settings.loop}
        loopDuration={settings.loopDuration}
        color1={settings.color1}
        color2={settings.color2}
        color3={settings.color3}
        positionX={settings.positionX}
        positionY={settings.positionY}
        positionZ={settings.positionZ}
        rotationX={settings.rotationX}
        rotationY={settings.rotationY}
        rotationZ={settings.rotationZ}
        reflection={settings.reflection}
        wireframe={settings.wireframe}
        smoothTime={settings.smoothTime}
        cAzimuthAngle={settings.cAzimuthAngle}
        cPolarAngle={settings.cPolarAngle}
        cDistance={settings.cDistance}
        cameraZoom={settings.cameraZoom}
        lightType={settings.lightType}
        brightness={settings.brightness}
        envPreset={settings.envPreset}
        grain={settings.grain}
        grainBlending={settings.grainBlending}
        zoomOut={settings.zoomOut}
        toggleAxis={settings.toggleAxis}
        enableTransition={settings.enableTransition}
        enableCameraUpdate={settings.enableCameraUpdate}
      />
    </ShaderGradientCanvas>
  );
}
