import { useQuery } from '@tanstack/react-query'
import { api } from '../../lib/api'
import GlassCard from '../GlassCard'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { motion } from 'framer-motion'

interface SentimentPoint {
  time: number
  sentiment: number
  emotion: string
}

interface SentimentData {
  call_id: number
  overall_sentiment: number
  timeline: SentimentPoint[]
  duration_seconds: number
}

interface SentimentHeatmapProps {
  callId: number
}

export default function SentimentHeatmap({ callId }: SentimentHeatmapProps) {
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  
  const { data, isLoading, error } = useQuery<{ status: string; data: SentimentData }>({
    queryKey: ['sentiment', callId],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/calls/${callId}/sentiment`, {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Failed to analyze sentiment')
      return response.json()
    },
    staleTime: Infinity,
    retry: 1,
  })

  if (isLoading) {
    return (
      <GlassCard>
        <div className="p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-ios-blue mx-auto mb-4"></div>
          <p className="text-ios-gray-2">Analyzing sentiment with AI...</p>
        </div>
      </GlassCard>
    )
  }

  if (error || !data?.data) {
    return (
      <GlassCard>
        <div className="p-4 text-center text-ios-gray-2">
          <p>Sentiment analysis unavailable</p>
        </div>
      </GlassCard>
    )
  }

  const points: SentimentPoint[] = data.data.timeline || []
  const overall = data.data.overall_sentiment || 0
  const maxTime = Math.max(...points.map(p => p.time), 60)

  const getColor = (score: number): string => {
    if (score > 0.5) return 'bg-green-500'
    if (score > 0.2) return 'bg-emerald-500'
    if (score > -0.2) return 'bg-yellow-500'
    if (score > -0.5) return 'bg-orange-500'
    return 'bg-red-500'
  }

  const getEmotionLabel = (emotion: string): string => {
    const map: Record<string, string> = {
      happy: '😊 Happy',
      excited: '🎉 Excited',
      neutral: '😐 Neutral',
      sad: '😢 Sad',
      angry: '😠 Angry',
      frustrated: '😤 Frustrated',
      fearful: '😨 Fearful',
    }
    return map[emotion] || '😐 Neutral'
  }

  const getSentimentBadge = () => {
    if (overall > 0.3) {
      return (
        <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-500/20 border border-green-500/30">
          <TrendingUp className="w-5 h-5 text-green-400" />
          <span className="text-green-400 font-semibold">Positive ({(overall * 100).toFixed(0)}%)</span>
        </div>
      )
    } else if (overall > -0.3) {
      return (
        <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-yellow-500/20 border border-yellow-500/30">
          <Minus className="w-5 h-5 text-yellow-400" />
          <span className="text-yellow-400 font-semibold">Neutral ({(overall * 100).toFixed(0)}%)</span>
        </div>
      )
    } else {
      return (
        <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500/20 border border-red-500/30">
          <TrendingDown className="w-5 h-5 text-red-400" />
          <span className="text-red-400 font-semibold">Negative ({(overall * 100).toFixed(0)}%)</span>
        </div>
      )
    }
  }

  return (
    <GlassCard>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">🧠 AI Sentiment Analysis</h3>
          {getSentimentBadge()}
        </div>

        {/* Heatmap Visualization */}
        <div className="relative h-48 bg-dark-2/50 rounded-xl overflow-hidden border border-dark-3">
          <div className="absolute inset-0 flex items-end justify-around px-2 pb-8">
            {points.map((p, i) => {
              const height = Math.abs(p.sentiment) * 100
              const isPositive = p.sentiment >= 0

              return (
                <motion.div
                  key={i}
                  initial={{ height: 0 }}
                  animate={{ height: `${height}%` }}
                  transition={{ duration: 0.5, delay: i * 0.05 }}
                  className={`relative w-4 ${getColor(p.sentiment)} rounded-t-lg transition-all duration-300 hover:scale-110 group cursor-pointer`}
                  style={{
                    transformOrigin: 'bottom',
                  }}
                >
                  {/* Tooltip */}
                  <div className="absolute -top-16 left-1/2 -translate-x-1/2 bg-dark-1 border border-dark-3 text-white text-xs px-3 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none shadow-xl">
                    <div className="font-semibold">{getEmotionLabel(p.emotion)}</div>
                    <div className="text-ios-gray-2">
                      {p.time}s • Score: {p.sentiment > 0 ? '+' : ''}{p.sentiment.toFixed(2)}
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>

          {/* Timeline */}
          <div className="absolute bottom-0 left-0 right-0 h-8 border-t border-dark-3 flex items-center px-4 text-xs text-ios-gray-2 bg-dark-1/50">
            <span>0s</span>
            <div className="flex-1 mx-4 border-t border-dashed border-dark-3" />
            <span>{maxTime}s</span>
          </div>

          {/* Legend */}
          <div className="absolute top-2 right-2 flex flex-wrap gap-1 text-[10px]">
            {['😊', '🎉', '😐', '😤', '😠'].map((emoji, i) => (
              <div
                key={i}
                className="bg-dark-1/80 border border-dark-3 px-2 py-1 rounded backdrop-blur-sm"
              >
                {emoji}
              </div>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="p-3 bg-dark-2/30 rounded-lg">
            <div className="text-2xl font-bold text-green-400">
              {points.filter(p => p.sentiment > 0.3).length}
            </div>
            <div className="text-xs text-ios-gray-2">Positive Moments</div>
          </div>
          <div className="p-3 bg-dark-2/30 rounded-lg">
            <div className="text-2xl font-bold text-yellow-400">
              {points.filter(p => Math.abs(p.sentiment) <= 0.3).length}
            </div>
            <div className="text-xs text-ios-gray-2">Neutral Moments</div>
          </div>
          <div className="p-3 bg-dark-2/30 rounded-lg">
            <div className="text-2xl font-bold text-red-400">
              {points.filter(p => p.sentiment < -0.3).length}
            </div>
            <div className="text-xs text-ios-gray-2">Negative Moments</div>
          </div>
        </div>

        <div className="text-xs text-ios-gray-2 text-center pt-2 border-t border-dark-3">
          Powered by Groq Llama 3.1 70B • {points.length} segments analyzed
        </div>
      </div>
    </GlassCard>
  )
}
