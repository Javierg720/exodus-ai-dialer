import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Play, Pause, Plus } from 'lucide-react'
import { api } from '../lib/api'
import GlassCard from '../components/GlassCard'
import ErrorAlert from '../components/ErrorAlert'
import { motion } from 'framer-motion'
import { Campaign } from '../types'
import { useState } from 'react'
import AddCampaignModal from '../components/AddCampaignModal'

export default function Campaigns() {
  const queryClient = useQueryClient()
  const [showAddModal, setShowAddModal] = useState(false)
  const [mutationError, setMutationError] = useState<Error | null>(null)
  
  const { data: campaigns, isLoading, error, refetch } = useQuery<Campaign[]>({
    queryKey: ['campaigns'],
    queryFn: () => api.getCampaigns(),
  })

  const startMutation = useMutation({
    mutationFn: (id: number) => api.startCampaign(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      setMutationError(null)
    },
    onError: (error: Error) => {
      setMutationError(error)
    },
  })

  const pauseMutation = useMutation({
    mutationFn: (id: number) => api.pauseCampaign(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      setMutationError(null)
    },
    onError: (error: Error) => {
      setMutationError(error)
    },
  })

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="skeleton h-12 w-64 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton h-64 rounded-2xl" />
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold">Campaigns</h1>
          <p className="text-ios-gray-2 mt-2">{campaigns?.length || 0} total campaigns</p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="ios-button-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          New Campaign
        </button>
      </div>

      {/* Error Alerts */}
      {error && (
        <ErrorAlert
          error={error as Error}
          onRetry={() => refetch()}
          title="Failed to load campaigns"
        />
      )}
      
      {mutationError && (
        <ErrorAlert
          error={mutationError}
          onDismiss={() => setMutationError(null)}
          title="Campaign action failed"
        />
      )}

      {/* Campaigns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {campaigns?.map((campaign: Campaign) => (
          <GlassCard key={campaign.id} hover>
            {/* Status Badge */}
            <div className="flex items-center justify-between mb-4">
              <span className={`ios-badge ${
                campaign.status === 'ACTIVE' ? 'bg-ios-green/20 text-ios-green' :
                campaign.status === 'PAUSED' ? 'bg-ios-orange/20 text-ios-orange' :
                'bg-ios-gray-2/20 text-ios-gray-2'
              }`}>
                {campaign.status}
              </span>
              <span className="text-sm text-ios-gray-2">
                Ratio: {campaign.dial_ratio.toFixed(1)}x
              </span>
            </div>

            {/* Campaign Name */}
            <h3 className="text-xl font-bold mb-2">{campaign.name}</h3>
            <p className="text-sm text-ios-gray-2 mb-4">ID: {campaign.id}</p>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <p className="text-2xl font-bold">{campaign.total_leads || 0}</p>
                <p className="text-xs text-ios-gray-2">Total Leads</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-ios-blue">{campaign.dialed || 0}</p>
                <p className="text-xs text-ios-gray-2">Dialed</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-ios-green">{campaign.contacted || 0}</p>
                <p className="text-xs text-ios-gray-2">Contacted</p>
              </div>
            </div>

            {/* Additional Stats */}
            <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
              <div className="bg-dark-3 rounded-lg p-3">
                <p className="text-ios-gray-2 text-xs mb-1">Today's Calls</p>
                <p className="text-lg font-bold">{campaign.calls_made_today || 0}</p>
              </div>
              <div className="bg-dark-3 rounded-lg p-3">
                <p className="text-ios-gray-2 text-xs mb-1">Conversion Rate</p>
                <p className="text-lg font-bold text-ios-green">{campaign.conversion_rate || 0}%</p>
              </div>
              <div className="bg-dark-3 rounded-lg p-3">
                <p className="text-ios-gray-2 text-xs mb-1">Time Connected</p>
                <p className="text-lg font-bold">{Math.floor((campaign.time_connected || 0) / 60)}m</p>
              </div>
              <div className="bg-dark-3 rounded-lg p-3">
                <p className="text-ios-gray-2 text-xs mb-1">Converted</p>
                <p className="text-lg font-bold text-ios-purple">{campaign.converted || 0}</p>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-dark-3 rounded-full h-2 mb-6">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${((campaign.dialed || 0) / (campaign.total_leads || 1)) * 100}%` }}
                className="bg-ios-blue h-2 rounded-full"
              />
            </div>

            {/* Action Button */}
            <button
              onClick={() => campaign.status === 'ACTIVE' 
                ? pauseMutation.mutate(campaign.id)
                : startMutation.mutate(campaign.id)
              }
              disabled={startMutation.isPending || pauseMutation.isPending}
              className={`w-full ios-button flex items-center justify-center gap-2 ${
                campaign.status === 'ACTIVE' 
                  ? 'bg-ios-orange hover:bg-ios-orange/90'
                  : 'bg-ios-green hover:bg-ios-green/90'
              } text-white`}
            >
              {campaign.status === 'ACTIVE' ? (
                <>
                  <Pause className="w-5 h-5" />
                  Pause Campaign
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Start Campaign
                </>
              )}
            </button>
          </GlassCard>
        ))}
      </div>

      {/* Add Campaign Modal */}
      <AddCampaignModal 
        isOpen={showAddModal} 
        onClose={() => setShowAddModal(false)} 
      />
    </motion.div>
  )
}
