import React, { useState, useRef } from 'react';
import { Mic, MicOff, Upload, Play, Pause } from 'lucide-react';
import SoundVisualizer from '../components/SoundVisualizer';

const SoundVisualizerDemo: React.FC = () => {
  const [audioStream, setAudioStream] = useState<MediaStream | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const startMicrophone = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setAudioStream(stream);
      setIsListening(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopMicrophone = () => {
    if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop());
      setAudioStream(null);
    }
    setIsListening(false);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
      setIsListening(false);
      stopMicrophone();
    }
  };

  const togglePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-dark-1 dark:to-dark-2 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Sound Visualizer
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time audio visualization with gradient effects
          </p>
        </div>

        {/* Main Visualizer Display */}
        <div className="bg-white dark:bg-dark-3 rounded-2xl shadow-xl p-8 mb-8">
          <SoundVisualizer
            audioStream={isListening ? audioStream || undefined : undefined}
            audioUrl={!isListening && audioUrl ? audioUrl : undefined}
            isLive={isListening}
            className="py-8"
            barCount={13}
            showLabel={true}
            labelText="sonusai"
          />
        </div>

        {/* Controls */}
        <div className="flex flex-wrap justify-center gap-4">
          {/* Microphone Toggle */}
          <button
            onClick={isListening ? stopMicrophone : startMicrophone}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
              isListening
                ? 'bg-red-500 text-white hover:bg-red-600'
                : 'bg-ios-blue text-white hover:bg-blue-600'
            }`}
          >
            {isListening ? (
              <>
                <MicOff className="w-5 h-5" />
                Stop Listening
              </>
            ) : (
              <>
                <Mic className="w-5 h-5" />
                Use Microphone
              </>
            )}
          </button>

          {/* File Upload */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 px-6 py-3 rounded-xl font-medium bg-gray-200 dark:bg-dark-4 text-gray-800 dark:text-white hover:bg-gray-300 dark:hover:bg-dark-5 transition-all"
          >
            <Upload className="w-5 h-5" />
            Upload Audio
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="audio/*"
            onChange={handleFileUpload}
            className="hidden"
          />

          {/* Play/Pause for uploaded audio */}
          {audioUrl && !isListening && (
            <button
              onClick={togglePlayback}
              className="flex items-center gap-2 px-6 py-3 rounded-xl font-medium bg-green-500 text-white hover:bg-green-600 transition-all"
            >
              {isPlaying ? (
                <>
                  <Pause className="w-5 h-5" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Play
                </>
              )}
            </button>
          )}
        </div>

        {/* Hidden audio element for playback */}
        {audioUrl && (
          <audio
            ref={audioRef}
            src={audioUrl}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            onEnded={() => setIsPlaying(false)}
          />
        )}

        {/* Variants Showcase */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Compact variant */}
          <div className="bg-white dark:bg-dark-3 rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Compact (8 bars)
            </h3>
            <SoundVisualizer
              barCount={8}
              showLabel={false}
              className="py-4"
            />
          </div>

          {/* Wide variant */}
          <div className="bg-white dark:bg-dark-3 rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Wide (18 bars)
            </h3>
            <SoundVisualizer
              barCount={18}
              showLabel={false}
              className="py-4"
            />
          </div>

          {/* Custom label */}
          <div className="bg-white dark:bg-dark-3 rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Custom Label
            </h3>
            <SoundVisualizer
              barCount={13}
              showLabel={true}
              labelText="exodus"
              className="py-4"
            />
          </div>

          {/* Dark background variant */}
          <div className="bg-gray-900 rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              On Dark Background
            </h3>
            <SoundVisualizer
              barCount={13}
              showLabel={true}
              labelText="sonusai"
              className="py-4"
            />
          </div>
        </div>

        {/* Usage Code */}
        <div className="mt-12 bg-gray-900 rounded-2xl p-6 overflow-x-auto">
          <h3 className="text-lg font-semibold text-white mb-4">Usage</h3>
          <pre className="text-sm text-gray-300">
{`import SoundVisualizer from './components/SoundVisualizer';

// Static display
<SoundVisualizer />

// With microphone input
<SoundVisualizer
  audioStream={mediaStream}
  isLive={true}
/>

// With audio file
<SoundVisualizer
  audioUrl="/path/to/audio.mp3"
/>

// Customized
<SoundVisualizer
  barCount={13}
  showLabel={true}
  labelText="sonusai"
  className="py-8"
/>`}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default SoundVisualizerDemo;
