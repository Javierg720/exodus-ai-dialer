import { useEffect, useRef, useState } from 'react'
import WaveSurfer from 'wavesurfer.js'
import { Play, Pause, Volume2, VolumeX, Download } from 'lucide-react'

interface WaveformPlayerProps {
  audioUrl: string
  callUuid: string
  onDownload?: () => void
}

export default function WaveformPlayer({ audioUrl, callUuid, onDownload }: WaveformPlayerProps) {
  const waveformRef = useRef<HTMLDivElement>(null)
  const wavesurfer = useRef<WaveSurfer | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState('0:00')
  const [duration, setDuration] = useState('0:00')
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!waveformRef.current) return

    let destroyed = false

    // Create WaveSurfer instance
    wavesurfer.current = WaveSurfer.create({
      container: waveformRef.current,
      waveColor: 'rgba(99, 102, 241, 0.3)', // iOS blue with transparency
      progressColor: 'rgba(99, 102, 241, 1)', // iOS blue
      cursorColor: '#ffffff',
      barWidth: 2,
      barRadius: 3,
      cursorWidth: 2,
      height: 80,
      barGap: 2,
      normalize: true,
      responsive: true,
      backend: 'WebAudio',
    })

    // Load audio
    setIsLoading(true)
    setError(null)
    
    wavesurfer.current.load(audioUrl)

    // Event listeners
    wavesurfer.current.on('ready', () => {
      if (destroyed) return
      setIsLoading(false)
      const dur = wavesurfer.current?.getDuration() || 0
      setDuration(formatTime(dur))
    })

    wavesurfer.current.on('error', (err) => {
      if (destroyed) return
      // Only log actual errors, not abort errors from cleanup
      if (!err.message?.includes('abort')) {
        console.warn('Audio loading failed:', err.message || err)
      }
      setError('Recording not available')
      setIsLoading(false)
    })

    wavesurfer.current.on('audioprocess', () => {
      if (destroyed) return
      const time = wavesurfer.current?.getCurrentTime() || 0
      setCurrentTime(formatTime(time))
    })

    wavesurfer.current.on('play', () => {
      if (destroyed) return
      setIsPlaying(true)
    })
    
    wavesurfer.current.on('pause', () => {
      if (destroyed) return
      setIsPlaying(false)
    })

    wavesurfer.current.on('finish', () => {
      if (destroyed) return
      setIsPlaying(false)
      wavesurfer.current?.seekTo(0)
    })

    // Cleanup
    return () => {
      destroyed = true
      try {
        wavesurfer.current?.destroy()
      } catch (e) {
        // Silently ignore cleanup errors in dev mode
      }
    }
  }, [audioUrl])

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const togglePlayPause = () => {
    if (wavesurfer.current) {
      wavesurfer.current.playPause()
    }
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value)
    setVolume(newVolume)
    wavesurfer.current?.setVolume(newVolume)
    if (newVolume === 0) {
      setIsMuted(true)
    } else {
      setIsMuted(false)
    }
  }

  const toggleMute = () => {
    if (isMuted) {
      wavesurfer.current?.setVolume(volume)
      setIsMuted(false)
    } else {
      wavesurfer.current?.setVolume(0)
      setIsMuted(true)
    }
  }

  if (error) {
    return (
      <div className="p-4 bg-dark-3 border border-ios-gray-3/30 rounded-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-ios-gray-3/20 flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-ios-gray-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-white">Recording Not Available</p>
            <p className="text-xs text-ios-gray-2 mt-0.5">This recording file no longer exists on the server</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 bg-dark-3 rounded-xl space-y-4">
      {/* Waveform */}
      <div className="relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-dark-3/80 rounded-xl z-10">
            <div className="flex items-center gap-2 text-ios-blue">
              <div className="w-4 h-4 border-2 border-ios-blue border-t-transparent rounded-full animate-spin" />
              <span className="text-sm">Loading waveform...</span>
            </div>
          </div>
        )}
        <div ref={waveformRef} className="w-full" />
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4">
        {/* Play/Pause Button */}
        <button
          onClick={togglePlayPause}
          disabled={isLoading}
          className="ios-button-primary w-10 h-10 p-0 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
          title={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? (
            <Pause className="w-5 h-5" fill="currentColor" />
          ) : (
            <Play className="w-5 h-5" fill="currentColor" />
          )}
        </button>

        {/* Time Display */}
        <div className="text-sm text-ios-gray-2 font-mono min-w-[80px]">
          {currentTime} / {duration}
        </div>

        {/* Volume Controls */}
        <div className="flex items-center gap-2 ml-auto">
          <button
            onClick={toggleMute}
            className="text-ios-gray-2 hover:text-white transition-colors"
            title={isMuted ? 'Unmute' : 'Mute'}
          >
            {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
            className="w-20 h-1 bg-ios-gray-3 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-ios-blue"
          />
        </div>

        {/* Download Button */}
        {onDownload && (
          <button
            onClick={onDownload}
            className="ios-button-secondary w-10 h-10 p-0 flex items-center justify-center"
            title="Download Recording"
          >
            <Download className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Playback Tips */}
      <div className="text-xs text-ios-gray-2 flex items-center gap-2">
        <span className="inline-block w-2 h-2 bg-ios-blue rounded-full animate-pulse" />
        Click on the waveform to jump to any position
      </div>
    </div>
  )
}
