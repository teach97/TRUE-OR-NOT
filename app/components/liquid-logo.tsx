"use client";

// Adapted from liquid-logo (PolyForm Shield 1.0.0); see third-party/liquid-logo-LICENSE.md.
import { useEffect, useRef, useState } from 'react';
import { liquidFragSource } from './liquid-logo-shader';

const LOGO = '/true-or-not-logo-04.png';
const VERTEX = '#version 300 es\nprecision mediump float;\nin vec2 a_position;\nout vec2 vUv;\nvoid main() { vUv = .5 * (a_position + 1.); gl_Position = vec4(a_position, 0., 1.); }';

function makeBevel(image: HTMLImageElement): ImageData | null {
  const surface = document.createElement('canvas');
  surface.width = image.naturalWidth;
  surface.height = image.naturalHeight;
  const context = surface.getContext('2d');
  if (!context) return null;
  context.drawImage(image, 0, 0);
  const pixels = context.getImageData(0, 0, surface.width, surface.height);
  const { width, height, data } = pixels;
  const distance = new Float32Array(width * height);
  const diagonal = Math.SQRT2;

  for (let i = 0; i < distance.length; i++) distance[i] = data[i * 4 + 3] > 127 ? 1000 : 0;
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    const i = y * width + x;
    if (x) distance[i] = Math.min(distance[i], distance[i - 1] + 1);
    if (y) distance[i] = Math.min(distance[i], distance[i - width] + 1);
    if (x && y) distance[i] = Math.min(distance[i], distance[i - width - 1] + diagonal);
    if (x < width - 1 && y) distance[i] = Math.min(distance[i], distance[i - width + 1] + diagonal);
  }
  for (let y = height - 1; y >= 0; y--) for (let x = width - 1; x >= 0; x--) {
    const i = y * width + x;
    if (x < width - 1) distance[i] = Math.min(distance[i], distance[i + 1] + 1);
    if (y < height - 1) distance[i] = Math.min(distance[i], distance[i + width] + 1);
    if (x < width - 1 && y < height - 1) distance[i] = Math.min(distance[i], distance[i + width + 1] + diagonal);
    if (x && y < height - 1) distance[i] = Math.min(distance[i], distance[i + width - 1] + diagonal);
  }
  for (let i = 0; i < distance.length; i++) {
    const shade = data[i * 4 + 3] > 127 ? 255 * (1 - Math.min(distance[i] / 12, 1)) : 255;
    data[i * 4] = shade;
    data[i * 4 + 1] = shade;
    data[i * 4 + 2] = shade;
    data[i * 4 + 3] = 255;
  }
  return pixels;
}

export default function LiquidLogo({ className = '' }: { className?: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    const gl = canvas?.getContext('webgl2', { alpha: true, antialias: true });
    if (!canvas || !gl) return;
    let disposed = false;
    let frame = 0;
    let observer: ResizeObserver | undefined;
    let program: WebGLProgram | null = null;
    let vertex: WebGLShader | null = null;
    let fragment: WebGLShader | null = null;
    let buffer: WebGLBuffer | null = null;
    let texture: WebGLTexture | null = null;
    const image = new Image();

    function compile(source: string, type: number) {
      const shader = gl!.createShader(type);
      if (!shader) return null;
      gl!.shaderSource(shader, source);
      gl!.compileShader(shader);
      if (gl!.getShaderParameter(shader, gl!.COMPILE_STATUS)) return shader;
      gl!.deleteShader(shader);
      return null;
    }

    image.onload = () => {
      if (disposed) return;
      const mask = makeBevel(image);
      if (!mask) return;
      vertex = compile(VERTEX, gl.VERTEX_SHADER);
      fragment = compile(liquidFragSource, gl.FRAGMENT_SHADER);
      if (!vertex || !fragment) return;
      program = gl.createProgram();
      if (!program) return;
      gl.attachShader(program, vertex);
      gl.attachShader(program, fragment);
      gl.linkProgram(program);
      if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return;
      gl.useProgram(program);

      buffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
      const position = gl.getAttribLocation(program, 'a_position');
      gl.enableVertexAttribArray(position);
      gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);

      texture = gl.createTexture();
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, texture);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, mask.width, mask.height, 0, gl.RGBA, gl.UNSIGNED_BYTE, mask.data);

      const uniform = (name: string) => gl.getUniformLocation(program!, name);
      gl.uniform1i(uniform('u_image_texture'), 0);
      gl.uniform1f(uniform('u_img_ratio'), mask.width / mask.height);
      gl.uniform1f(uniform('u_patternScale'), 2);
      gl.uniform1f(uniform('u_refraction'), 0.015);
      gl.uniform1f(uniform('u_edge'), 0.4);
      gl.uniform1f(uniform('u_patternBlur'), 0.005);
      gl.uniform1f(uniform('u_liquid'), 0.07);
      const time = uniform('u_time');
      const ratio = uniform('u_ratio');
      const resize = () => {
        const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.max(1, Math.round(canvas.clientWidth * pixelRatio));
        canvas.height = Math.max(1, Math.round(canvas.clientHeight * pixelRatio));
        gl.viewport(0, 0, canvas.width, canvas.height);
        gl.uniform1f(ratio, canvas.width / canvas.height);
      };
      resize();
      observer = new ResizeObserver(resize);
      observer.observe(canvas);
      const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const draw = (now: number) => {
        gl.uniform1f(time, reducedMotion ? 0 : now * 0.3);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        if (!reducedMotion) frame = requestAnimationFrame(draw);
      };
      frame = requestAnimationFrame(draw);
      setReady(true);
    };
    image.src = LOGO;

    return () => {
      disposed = true;
      image.onload = null;
      cancelAnimationFrame(frame);
      observer?.disconnect();
      if (texture) gl.deleteTexture(texture);
      if (buffer) gl.deleteBuffer(buffer);
      if (program) gl.deleteProgram(program);
      if (vertex) gl.deleteShader(vertex);
      if (fragment) gl.deleteShader(fragment);
    };
  }, []);

  return <span className={'liquid-logo ' + className} aria-hidden="true">
    <img src={LOGO} alt="" className="liquid-logo__fallback" style={{ opacity: ready ? 0 : 1 }} />
    <canvas ref={canvasRef} className="liquid-logo__canvas" style={{ opacity: ready ? 1 : 0 }} />
  </span>;
}
