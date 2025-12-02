import React, { useRef, useEffect, useState, useCallback } from 'react';

interface SoundVisualizerProps {
  audioUrl?: string;
  isLive?: boolean;
  audioStream?: MediaStream;
  className?: string;
  barCount?: number;
  showLabel?: boolean;
  labelText?: string;
}

const SoundVisualizer: React.FC<SoundVisualizerProps> = ({
  audioUrl,
  isLive = false,
  audioStream,
  className = '',
  barCount = 13,
  showLabel = true,
  labelText = 'sonusai',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const animationRef = useRef<number | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | MediaElementAudioSourceNode | null>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [barHeights, setBarHeights] = useState<number[]>(Array(barCount).fill(0.1));

  // Color gradient stops matching the design exactly
  const getBarColor = useCallback((index: number, totalBars: number): string => {
    const position = index / (totalBars - 1);

    // Gradient: cyan (#00D4FF) -> blue (#007AFF) -> purple (#7B68EE) -> pink (#FF69B4) -> magenta (#FF1493)
    if (position < 0.25) {
      // Cyan to light blue
      const t = position / 0.25;
      return interpolateColor('#00E5FF', '#00B4FF', t);
    } else if (position < 0.5) {
      // Light blue to blue/purple
      const t = (position - 0.25) / 0.25;
      return interpolateColor('#00B4FF', '#6B5BFF', t);
    } else if (position < 0.75) {
      // Purple to pink
      const t = (position - 0.5) / 0.25;
      return interpolateColor('#6B5BFF', '#E066FF', t);
    } else {
      // Pink to magenta
      const t = (position - 0.75) / 0.25;
      return interpolateColor('#E066FF', '#FF4D94', t);
    }
  }, []);

  const interpolateColor = (color1: string, color2: string, t: number): string => {
    const r1 = parseInt(color1.slice(1, 3), 16);
    const g1 = parseInt(color1.slice(3, 5), 16);
    const b1 = parseInt(color1.slice(5, 7), 16);
    const r2 = parseInt(color2.slice(1, 3), 16);
    const g2 = parseInt(color2.slice(3, 5), 16);
    const b2 = parseInt(color2.slice(5, 7), 16);

    const r = Math.round(r1 + (r2 - r1) * t);
    const g = Math.round(g1 + (g2 - g1) * t);
    const b = Math.round(b1 + (b2 - b1) * t);

    return `rgb(${r}, ${g}, ${b})`;
  };

  // Base heights for the wave pattern (matching the image)
  const getBaseHeight = useCallback((index: number, totalBars: number): number => {
    // Create a wave pattern that matches the image
    // Bars grow toward center, with slight asymmetry
    const center = totalBars / 2;
    const distanceFromCenter = Math.abs(index - center);
    const maxDistance = center;

    // Wave pattern heights based on the image
    const wavePattern = [
      0.08, 0.15, 0.25, 0.35, 0.55, 0.75, 0.95, 0.85, 0.65, 0.45, 0.30, 0.18, 0.10
    ];

    if (index < wavePattern.length) {
      return wavePattern[index];
    }

    return 1 - (distanceFromCenter / maxDistance) * 0.8;
  }, []);

  const drawVisualization = useCallback((dataArray?: Uint8Array) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();

    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const width = rect.width;
    const height = rect.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    const barWidth = 6;
    const barSpacing = 8;
    const totalWidth = barCount * barWidth + (barCount - 1) * barSpacing;
    const startX = (width - totalWidth) / 2;
    const maxBarHeight = height * 0.7;
    const centerY = height * 0.45;

    // Calculate bar heights
    const newBarHeights: number[] = [];

    for (let i = 0; i < barCount; i++) {
      let audioLevel = 0;

      if (dataArray && analyserRef.current) {
        // Map frequency bins to bars
        const binStart = Math.floor((i / barCount) * (dataArray.length / 2));
        const binEnd = Math.floor(((i + 1) / barCount) * (dataArray.length / 2));

        let sum = 0;
        for (let j = binStart; j < binEnd; j++) {
          sum += dataArray[j];
        }
        audioLevel = (sum / (binEnd - binStart)) / 255;
      }

      const baseHeight = getBaseHeight(i, barCount);
      const animatedHeight = baseHeight * (0.3 + audioLevel * 0.7);
      newBarHeights.push(animatedHeight);

      const barHeight = animatedHeight * maxBarHeight;
      const x = startX + i * (barWidth + barSpacing);
      const y = centerY - barHeight / 2;
      const color = getBarColor(i, barCount);

      // Draw bar with rounded ends
      ctx.beginPath();
      ctx.fillStyle = color;
      ctx.roundRect(x, y, barWidth, barHeight, barWidth / 2);
      ctx.fill();

      // Add subtle glow effect
      ctx.shadowColor = color;
      ctx.shadowBlur = 8;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 0;
    }

    // Reset shadow
    ctx.shadowBlur = 0;

    // Draw decorative dots on the sides
    // Left dots (cyan)
    const dotRadius = 2.5;
    const leftDotX = startX - 25;
    const rightDotX = startX + totalWidth + 20;

    // Left main dot
    ctx.beginPath();
    ctx.fillStyle = '#00E5FF';
    ctx.arc(leftDotX, centerY, dotRadius + 1, 0, Math.PI * 2);
    ctx.fill();

    // Left small dots
    ctx.beginPath();
    ctx.fillStyle = '#00E5FF';
    ctx.globalAlpha = 0.5;
    ctx.arc(leftDotX - 12, centerY - 3, dotRadius * 0.6, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(leftDotX - 8, centerY + 8, dotRadius * 0.4, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;

    // Right main dot (pink/red)
    ctx.beginPath();
    ctx.fillStyle = '#FF4D94';
    ctx.arc(rightDotX, centerY, dotRadius + 1, 0, Math.PI * 2);
    ctx.fill();

    // Right small dots
    ctx.beginPath();
    ctx.fillStyle = '#FF4D94';
    ctx.globalAlpha = 0.5;
    ctx.arc(rightDotX + 12, centerY - 3, dotRadius * 0.6, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(rightDotX + 8, centerY + 8, dotRadius * 0.4, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;

    // Draw small horizontal lines/dashes on sides
    ctx.strokeStyle = '#00E5FF';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(leftDotX + 8, centerY);
    ctx.lineTo(leftDotX + 16, centerY);
    ctx.stroke();

    ctx.strokeStyle = '#FF4D94';
    ctx.beginPath();
    ctx.moveTo(rightDotX - 16, centerY);
    ctx.lineTo(rightDotX - 8, centerY);
    ctx.stroke();

    setBarHeights(newBarHeights);
  }, [barCount, getBarColor, getBaseHeight]);

  const animate = useCallback(() => {
    if (!analyserRef.current) {
      drawVisualization();
      return;
    }

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    drawVisualization(dataArray);
    animationRef.current = requestAnimationFrame(animate);
  }, [drawVisualization]);

  // Initialize audio context and analyser
  const initAudio = useCallback(async () => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }

    if (audioContextRef.current.state === 'suspended') {
      await audioContextRef.current.resume();
    }

    if (!analyserRef.current) {
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      analyserRef.current.smoothingTimeConstant = 0.7;
    }
  }, []);

  // Handle audio stream (for live audio)
  useEffect(() => {
    if (!audioStream || !isLive) return;

    const setupStream = async () => {
      await initAudio();

      if (sourceRef.current) {
        sourceRef.current.disconnect();
      }

      sourceRef.current = audioContextRef.current!.createMediaStreamSource(audioStream);
      sourceRef.current.connect(analyserRef.current!);

      setIsPlaying(true);
      animate();
    };

    setupStream();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [audioStream, isLive, initAudio, animate]);

  // Handle audio URL
  useEffect(() => {
    if (!audioUrl) return;

    const audio = new Audio(audioUrl);
    audioElementRef.current = audio;

    const setupAudio = async () => {
      await initAudio();

      if (sourceRef.current) {
        sourceRef.current.disconnect();
      }

      sourceRef.current = audioContextRef.current!.createMediaElementSource(audio);
      sourceRef.current.connect(analyserRef.current!);
      analyserRef.current!.connect(audioContextRef.current!.destination);
    };

    setupAudio();

    audio.onplay = () => {
      setIsPlaying(true);
      animate();
    };

    audio.onpause = () => {
      setIsPlaying(false);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };

    audio.onended = () => {
      setIsPlaying(false);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };

    return () => {
      audio.pause();
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [audioUrl, initAudio, animate]);

  // Initial draw and idle animation
  useEffect(() => {
    let idleAnimation: number;

    const idleAnimate = () => {
      if (!isPlaying) {
        drawVisualization();
      }
      idleAnimation = requestAnimationFrame(idleAnimate);
    };

    // Start idle animation for the static display
    if (!isPlaying && !audioUrl && !audioStream) {
      idleAnimate();
    } else {
      drawVisualization();
    }

    return () => {
      if (idleAnimation) {
        cancelAnimationFrame(idleAnimation);
      }
    };
  }, [isPlaying, audioUrl, audioStream, drawVisualization]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      drawVisualization();
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [drawVisualization]);

  const togglePlayback = async () => {
    if (!audioElementRef.current) return;

    if (isPlaying) {
      audioElementRef.current.pause();
    } else {
      await initAudio();
      await audioElementRef.current.play();
    }
  };

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      {/* Visualizer Container */}
      <div className="relative w-full max-w-md">
        {/* Shadow/Reflection effect */}
        <div
          className="absolute bottom-0 left-1/2 -translate-x-1/2 w-32 h-1 rounded-full opacity-30"
          style={{
            background: 'linear-gradient(90deg, #00E5FF, #6B5BFF, #FF4D94)',
            filter: 'blur(4px)',
          }}
        />

        {/* Canvas */}
        <canvas
          ref={canvasRef}
          className="w-full h-40 cursor-pointer"
          onClick={audioUrl ? togglePlayback : undefined}
        />
      </div>

      {/* Label */}
      {showLabel && (
        <div
          className="mt-4 text-lg font-medium tracking-wider"
          style={{
            background: 'linear-gradient(90deg, #00E5FF 0%, #6B5BFF 50%, #FF4D94 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          {labelText}
        </div>
      )}
    </div>
  );
};

export default SoundVisualizer;
