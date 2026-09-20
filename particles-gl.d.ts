declare module 'particles-gl' {
  export type ParticlesGLOptions = {
    target: string;
    character?: string;
    particleSize?: number;
    particleSpacing?: number;
    particleColor?: string;
    sampling?: number;
    tilt?: boolean;
    tiltFactor?: number;
    tiltSpeed?: number;
    displaceStrength?: number;
    displaceRadius?: number;
    velocityInfluence?: number;
    returnSpeed?: number;
    fontSize?: number;
    fontFamily?: string;
    videoUpdateRate?: number;
    modelScale?: number;
    geometry?: number[] | null;
    on?: {
      init?: (instance: {cleanup: () => void}) => void;
    };
  };

  export type ParticlesGLEffect = {
    init: () => void | Promise<void>;
    cleanup: () => void;
    updateOptions: (options: Partial<ParticlesGLOptions>) => void;
    options: ParticlesGLOptions;
  };

  const particlesGL: (options: ParticlesGLOptions) => ParticlesGLEffect | null;
  export default particlesGL;
}
