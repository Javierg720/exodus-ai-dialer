import { Phone, Ear, MessageSquare, PhoneOff } from 'lucide-react'
import { LiveCall } from '../types'
import GlassCard from './GlassCard'
import { motion } from 'framer-motion'

interface LiveCallCardProps {
  call: LiveCall
  onMonitor: (action: 'listen' | 'barge') => void
  onHangup: () => void
}

export default function LiveCallCard({ call, onMonitor, onHangup }: LiveCallCardProps) {
  // Use duration from API if available, otherwise calculate from started_at
  const duration = call.duration || (call.started_at ? Math.floor((Date.now() - new Date(call.started_at).getTime()) / 1000) : 0)
  const minutes = Math.floor(duration / 60)
  const seconds = duration % 60

  return (
    <GlassCard className="relative overflow-hidden">
      {/* Waveform Animation Background */}
      <div className="absolute top-0 right-0 flex items-end gap-1 opacity-10 p-4">
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="w-1 bg-ios-blue rounded-full"
            animate={{ height: ['20px', '40px', '20px'] }}
            transition={{
              duration: 1.2,
              repeat: Infinity,
              delay: i * 0.1,
            }}
          />
        ))}
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-ios-green animate-pulse" />
              <span className="text-lg font-bold">{call.phone_number}</span>
            </div>
            <p className="text-sm text-ios-gray-2 mt-1">
              Agent: {call.agent_name || `Bot ${call.bot_port}`}
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-mono font-bold">
              {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
            </p>
            <p className="text-xs text-ios-gray-2">{call.status}</p>
          </div>
        </div>

        {/* Live Transcription */}
        {call.transcription_stream && call.transcription_stream.length > 0 && (
          <div className="mb-4 p-3 bg-dark-3 rounded-xl max-h-24 overflow-y-auto">
            <p className="text-sm text-ios-gray-2 italic">
              "{call.transcription_stream[call.transcription_stream.length - 1]}"
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => onMonitor('listen')}
            className="flex flex-col items-center gap-1 p-3 rounded-xl bg-dark-3 hover:bg-ios-blue/20 transition-colors group"
            title="Listen to call (muted, zero delay)"
          >
            <Ear className="w-5 h-5 group-hover:text-ios-blue transition-colors" />
            <span className="text-xs">Listen</span>
          </button>
          <button
            onClick={() => onMonitor('barge')}
            className="flex flex-col items-center gap-1 p-3 rounded-xl bg-dark-3 hover:bg-ios-orange/20 transition-colors group"
            title="Join call (speak to both parties, zero delay)"
          >
            <Phone className="w-5 h-5 group-hover:text-ios-orange transition-colors" />
            <span className="text-xs">Barge</span>
          </button>
          <button
            onClick={onHangup}
            className="flex flex-col items-center gap-1 p-3 rounded-xl bg-dark-3 hover:bg-ios-red/20 transition-colors group"
            title="Hangup this call"
          >
            <PhoneOff className="w-5 h-5 group-hover:text-ios-red transition-colors" />
            <span className="text-xs">End</span>
          </button>
        </div>
      </div>
    </GlassCard>
  )
}
