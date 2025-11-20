import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bot as BotIcon, RefreshCw, Activity, Power, PowerOff, RotateCcw, Zap } from 'lucide-react'
import { api } from '../lib/api'
import GlassCard from '../components/GlassCard'
import { motion } from 'framer-motion'

interface BotData {
  id: number
  port: number
  status: string
  pid: number | null
  uptime: number
  cpu_percent: number
  memory_mb: number
  calls_handled: number
}

interface BotResponse {
  bots: BotData[]
  summary: {
    total: number
    running: number
    stopped: number
    idle: number
    busy: number
  }
}

export default function Bots() {
  const queryClient = useQueryClient()
  
  const { data, isLoading } = useQuery<BotResponse>({
    queryKey: ['bots'],
    queryFn: () => api.getBots(),
    refetchInterval: 3000,
  })

  const startMutation = useMutation({
    mutationFn: (botId: number) => api.startBot(botId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bots'] })
    },
  })

  const stopMutation = useMutation({
    mutationFn: (botId: number) => api.stopBot(botId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bots'] })
    },
  })

  const restartMutation = useMutation({
    mutationFn: (botId: number) => api.restartBot(botId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bots'] })
    },
  })

  const restartPoolMutation = useMutation({
    mutationFn: () => api.restartBotPool(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bots'] })
    },
  })

  const formatUptime = (seconds: number) => {
    if (seconds === 0) return '0s'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hours > 0) return `${hours}h ${minutes}m`
    if (minutes > 0) return `${minutes}m ${secs}s`
    return `${secs}s`
  }

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="skeleton h-12 w-64 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="skeleton h-48 rounded-2xl" />
          ))}
        </div>
      </div>
    )
  }

  const summary = data?.summary || { total: 10, running: 0, stopped: 10, idle: 0, busy: 0 }
  const bots = data?.bots || []

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-4 md:p-8 space-y-8"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold">Bot Pool</h1>
          <p className="text-ios-gray-2 mt-2">
            {summary.running} running · {summary.stopped} stopped · {summary.total} total
          </p>
        </div>
        <button
          onClick={() => restartPoolMutation.mutate()}
          disabled={restartPoolMutation.isPending}
          className="ios-button bg-ios-blue hover:bg-ios-blue/90 text-white flex items-center gap-2"
        >
          <Zap className="w-5 h-5" />
          {restartPoolMutation.isPending ? 'Restarting Pool...' : 'Restart All Bots'}
        </button>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <GlassCard>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-ios-gray-2">Running</p>
              <p className="text-4xl font-bold mt-2 text-ios-green">{summary.running}</p>
            </div>
            <div className="p-4 rounded-xl bg-ios-green/10">
              <BotIcon className="w-8 h-8 text-ios-green" />
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-ios-gray-2">Stopped</p>
              <p className="text-4xl font-bold mt-2 text-ios-red">{summary.stopped}</p>
            </div>
            <div className="p-4 rounded-xl bg-ios-red/10">
              <PowerOff className="w-8 h-8 text-ios-red" />
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-ios-gray-2">Idle</p>
              <p className="text-4xl font-bold mt-2 text-ios-blue">{summary.idle}</p>
            </div>
            <div className="p-4 rounded-xl bg-ios-blue/10">
              <Activity className="w-8 h-8 text-ios-blue" />
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-ios-gray-2">Busy</p>
              <p className="text-4xl font-bold mt-2 text-ios-orange">{summary.busy}</p>
            </div>
            <div className="p-4 rounded-xl bg-ios-orange/10">
              <BotIcon className="w-8 h-8 text-ios-orange" />
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Bot Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {bots.map((bot: BotData) => (
          <GlassCard key={bot.id} hover>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  bot.status === 'RUNNING' ? 'bg-ios-green' : 'bg-ios-red'
                } ${bot.status === 'RUNNING' ? 'animate-pulse' : ''}`} />
                <span className="font-semibold">Bot #{bot.id}</span>
              </div>
              <span className="text-xs text-ios-gray-2">:{bot.port}</span>
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-ios-gray-2">Status</span>
                <span className={`font-medium ${
                  bot.status === 'RUNNING' ? 'text-ios-green' : 'text-ios-red'
                }`}>
                  {bot.status}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-ios-gray-2">Uptime</span>
                <span className="font-medium">{formatUptime(bot.uptime)}</span>
              </div>
              {bot.status === 'RUNNING' && (
                <>
                  <div className="flex justify-between text-sm">
                    <span className="text-ios-gray-2">CPU</span>
                    <span className="font-medium">{bot.cpu_percent}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-ios-gray-2">Memory</span>
                    <span className="font-medium">{bot.memory_mb} MB</span>
                  </div>
                </>
              )}
              <div className="flex justify-between text-sm">
                <span className="text-ios-gray-2">Calls</span>
                <span className="font-medium">{bot.calls_handled}</span>
              </div>
              {bot.pid && (
                <div className="flex justify-between text-sm">
                  <span className="text-ios-gray-2">PID</span>
                  <span className="font-mono text-xs">{bot.pid}</span>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              {bot.status === 'RUNNING' ? (
                <>
                  <button
                    onClick={() => stopMutation.mutate(bot.id)}
                    disabled={stopMutation.isPending}
                    className="flex-1 ios-button bg-ios-red/20 hover:bg-ios-red/30 text-ios-red flex items-center justify-center gap-1"
                  >
                    <PowerOff className="w-4 h-4" />
                    Stop
                  </button>
                  <button
                    onClick={() => restartMutation.mutate(bot.id)}
                    disabled={restartMutation.isPending}
                    className="flex-1 ios-button bg-ios-orange/20 hover:bg-ios-orange/30 text-ios-orange flex items-center justify-center gap-1"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Restart
                  </button>
                </>
              ) : (
                <button
                  onClick={() => startMutation.mutate(bot.id)}
                  disabled={startMutation.isPending}
                  className="w-full ios-button bg-ios-green/20 hover:bg-ios-green/30 text-ios-green flex items-center justify-center gap-1"
                >
                  <Power className="w-4 h-4" />
                  Start
                </button>
              )}
            </div>
          </GlassCard>
        ))}
      </div>
    </motion.div>
  )
}
