import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import LiveCallCard from '../components/LiveCallCard'
import ErrorAlert from '../components/ErrorAlert'
import { motion } from 'framer-motion'
import { LiveCall } from '../types'
import { Phone } from 'lucide-react'
import { useState } from 'react'

export default function LiveCalls() {
  const queryClient = useQueryClient()
  const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null)

  const { data: activeCalls, isLoading, error, refetch } = useQuery<LiveCall[]>({
    queryKey: ['activeCalls'],
    queryFn: () => api.getActiveCalls(),
    refetchInterval: 1000, // Refresh every second for live updates
  })

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message })
    setTimeout(() => setNotification(null), 3000)
  }

  const handleMonitor = async (callId: string, action: 'listen' | 'whisper' | 'barge') => {
    try {
      const result = await api.monitorCall(callId, action)
      if (result.status === 'error') {
        showNotification('error', result.message || 'Monitor action failed')
      } else if (result.status === 'partial') {
        showNotification('error', result.message || 'Feature requires SIP phone setup')
      } else {
        showNotification('success', `${action.charAt(0).toUpperCase() + action.slice(1)} mode activated`)
      }
    } catch (error) {
      showNotification('error', 'Monitor action failed')
      console.error('Monitor failed:', error)
    }
  }

  const handleHangup = async (channel: string) => {
    try {
      const result = await api.hangupCall(channel)
      if (result.status === 'success') {
        showNotification('success', 'Call hung up successfully')
        // Refresh the calls list immediately
        queryClient.invalidateQueries({ queryKey: ['activeCalls'] })
      } else {
        showNotification('error', result.message || 'Failed to hangup call')
      }
    } catch (error) {
      showNotification('error', 'Failed to hangup call')
      console.error('Hangup failed:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="skeleton h-12 w-64 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton h-80 rounded-2xl" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-4 md:p-8 space-y-8"
    >
      {/* Notification Toast */}
      {notification && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className={`fixed top-4 right-4 z-50 px-6 py-4 rounded-xl shadow-lg ${
            notification.type === 'success' 
              ? 'bg-ios-green/20 border border-ios-green/30 text-ios-green' 
              : 'bg-ios-red/20 border border-ios-red/30 text-ios-red'
          }`}
        >
          {notification.message}
        </motion.div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold">Live Calls</h1>
          <p className="text-ios-gray-2 mt-2">
            {activeCalls?.length || 0} active calls right now
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-ios-green/20">
          <div className="w-2 h-2 rounded-full bg-ios-green animate-pulse" />
          <span className="text-ios-green font-semibold">LIVE</span>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <ErrorAlert
          error={error as Error}
          onRetry={() => refetch()}
          title="Failed to load active calls"
        />
      )}

      {/* Active Calls Grid */}
      {activeCalls && activeCalls.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {activeCalls.map((call: LiveCall) => (
            <LiveCallCard
              key={call.channel}
              call={call}
              onMonitor={(action) => handleMonitor(call.channel, action)}
              onHangup={() => handleHangup(call.channel)}
            />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="p-6 rounded-full bg-dark-3 mb-6">
            <Phone className="w-12 h-12 text-ios-gray-2" />
          </div>
          <h3 className="text-2xl font-bold mb-2">No Active Calls</h3>
          <p className="text-ios-gray-2">Calls will appear here when agents are on the line</p>
        </div>
      )}
    </motion.div>
  )
}
