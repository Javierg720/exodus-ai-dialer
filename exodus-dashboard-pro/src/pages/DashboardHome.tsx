import { useQuery } from '@tanstack/react-query'
import { Activity, Phone, Target, TrendingUp, Users, Bot } from 'lucide-react'
import { api } from '../lib/api'
import StatCard from '../components/StatCard'
import GlassCard from '../components/GlassCard'
import ErrorAlert from '../components/ErrorAlert'
import { motion } from 'framer-motion'

export default function DashboardHome() {
  const { data: stats, isLoading, error, refetch } = useQuery<any>({
    queryKey: ['stats'],
    queryFn: () => api.getStats(),
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  const { data: activeCalls, error: activeCallsError } = useQuery<any[]>({
    queryKey: ['activeCalls'],
    queryFn: () => api.getActiveCalls(),
    refetchInterval: 2000, // Refresh every 2 seconds
  })

  const { data: bots, error: botsError } = useQuery<any>({
    queryKey: ['botsStatus'],
    queryFn: () => api.getBotsStatus(),
    refetchInterval: 5000,
  })

  // Fetch leads to get accurate count (fixes Dashboard showing 0 when stats endpoint doesn't return total_leads)
  const { data: leads, error: leadsError } = useQuery<any[]>({
    queryKey: ['leads'],
    queryFn: () => api.getLeads(),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  if (isLoading) {
    return (
      <div className="p-8 space-y-8">
        <div className="skeleton h-12 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-32 rounded-2xl" />
          ))}
        </div>
      </div>
    )
  }

  const primaryError = error || activeCallsError || botsError || leadsError

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-4 md:p-8 space-y-8"
    >
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold">Dashboard</h1>
        <p className="text-ios-gray-2 mt-2">Live overview of your calling operations</p>
      </div>

      {/* Error Alert */}
      {primaryError && (
        <ErrorAlert
          error={primaryError as Error}
          onRetry={() => refetch()}
          title="Failed to load dashboard data"
        />
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Calls"
          value={stats?.active_calls || activeCalls?.length || 0}
          icon={Phone}
          color="ios-green"
        />
        <StatCard
          title="Active Campaigns"
          value={stats?.active_campaigns || 0}
          icon={Target}
          color="ios-blue"
        />
        <StatCard
          title="Calls Today"
          value={stats?.total_calls_today || 0}
          icon={Activity}
          color="ios-orange"
        />
        <StatCard
          title="Conversion Rate"
          value={`${stats?.conversion_rate?.toFixed(1) || 0}%`}
          icon={TrendingUp}
          color="ios-green"
          trend={stats?.conversion_rate}
        />
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Total Leads"
          value={stats?.total_leads || leads?.length || 0}
          icon={Users}
        />
        <StatCard
          title="New Leads"
          value={stats?.new_leads || 0}
          icon={Users}
          color="ios-blue"
        />
        <StatCard
          title="Bots Idle"
          value={`${bots?.summary?.idle || bots?.idle || 0}/${bots?.summary?.total || bots?.total || 10}`}
          icon={Bot}
          color="ios-gray-2"
        />
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard>
          <h3 className="text-lg font-semibold mb-4">Performance Today</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-ios-gray-2">Contacted</span>
              <span className="text-2xl font-bold">{stats?.contacted_today || 0}</span>
            </div>
            <div className="w-full bg-dark-3 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${((stats?.contacted_today || 0) / (stats?.total_calls_today || 1)) * 100}%` }}
                className="bg-ios-green h-2 rounded-full"
              />
            </div>
            <div className="flex justify-between items-center pt-2">
              <span className="text-ios-gray-2">Avg Call Duration</span>
              <span className="text-xl font-bold">
                {Math.floor((stats?.average_call_duration || 0) / 60)}:{String(Math.floor((stats?.average_call_duration || 0) % 60)).padStart(2, '0')}
              </span>
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <h3 className="text-lg font-semibold mb-4">Bot Pool Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-ios-green" />
                <span>Idle</span>
              </div>
              <span className="text-xl font-bold">{bots?.summary?.idle || bots?.idle || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-ios-blue" />
                <span>Busy</span>
              </div>
              <span className="text-xl font-bold">{bots?.summary?.busy || bots?.busy || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-ios-red" />
                <span>Offline</span>
              </div>
              <span className="text-xl font-bold">{(bots?.summary?.total || bots?.total || 10) - (bots?.summary?.idle || bots?.idle || 0) - (bots?.summary?.busy || bots?.busy || 0)}</span>
            </div>
          </div>
        </GlassCard>
      </div>
    </motion.div>
  )
}
