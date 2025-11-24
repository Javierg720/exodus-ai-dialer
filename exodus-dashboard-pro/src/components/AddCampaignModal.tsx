import { useState } from 'react'
import { X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'

interface AddCampaignModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function AddCampaignModal({ isOpen, onClose }: AddCampaignModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    name: '',
    dial_ratio: '1.0',
    max_attempts: '3',
    retry_delay: '3600',
    call_timeout: '30',
    working_hours_start: '09:00',
    working_hours_end: '17:00',
  })
  const [error, setError] = useState('')

  const createCampaignMutation = useMutation({
    mutationFn: (data: any) => api.createCampaign(data),
    onSuccess: (response: any) => {
      // Backend returns { campaign_id: number, message: string } on success
      if (response.campaign_id) {
        queryClient.invalidateQueries({ queryKey: ['campaigns'] })
        handleClose()
      } else if (response.detail) {
        // FastAPI error format
        setError(response.detail)
      } else {
        setError(response.message || 'Failed to create campaign')
      }
    },
    onError: (err: any) => {
      setError(err.message || 'Failed to create campaign')
    }
  })

  const handleClose = () => {
    setFormData({
      name: '',
      dial_ratio: '1.0',
      max_attempts: '3',
      retry_delay: '3600',
      call_timeout: '30',
      working_hours_start: '09:00',
      working_hours_end: '17:00',
    })
    setError('')
    onClose()
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.name.trim()) {
      setError('Campaign name is required')
      return
    }

    createCampaignMutation.mutate({
      name: formData.name.trim(),
      dial_ratio: parseFloat(formData.dial_ratio),
      max_attempts: parseInt(formData.max_attempts),
      retry_delay: parseInt(formData.retry_delay),
      call_timeout: parseInt(formData.call_timeout),
      working_hours_start: formData.working_hours_start,
      working_hours_end: formData.working_hours_end,
      status: 'PAUSED',
    })
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          />

          {/* Modal */}
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-dark-2 rounded-3xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-dark-3"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Create New Campaign</h2>
                <button
                  onClick={handleClose}
                  className="p-2 hover:bg-dark-3 rounded-xl transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mb-6 p-4 bg-ios-red/20 border border-ios-red/50 rounded-xl text-ios-red">
                  {error}
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Campaign Name */}
                <div>
                  <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                    Campaign Name <span className="text-ios-red">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., Q4 Sales Outreach"
                    className="ios-input"
                    required
                  />
                </div>

                {/* Dial Ratio & Max Attempts */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                      Dial Ratio
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      min="0.1"
                      max="5.0"
                      value={formData.dial_ratio}
                      onChange={(e) => setFormData({ ...formData, dial_ratio: e.target.value })}
                      className="ios-input"
                    />
                    <p className="text-xs text-ios-gray-2 mt-1">Calls per available agent (1.0 - 5.0)</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                      Max Attempts
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={formData.max_attempts}
                      onChange={(e) => setFormData({ ...formData, max_attempts: e.target.value })}
                      className="ios-input"
                    />
                    <p className="text-xs text-ios-gray-2 mt-1">Max call attempts per lead</p>
                  </div>
                </div>

                {/* Retry Delay & Call Timeout */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                      Retry Delay (seconds)
                    </label>
                    <input
                      type="number"
                      min="60"
                      max="86400"
                      value={formData.retry_delay}
                      onChange={(e) => setFormData({ ...formData, retry_delay: e.target.value })}
                      className="ios-input"
                    />
                    <p className="text-xs text-ios-gray-2 mt-1">Wait time before retry (3600 = 1 hour)</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                      Call Timeout (seconds)
                    </label>
                    <input
                      type="number"
                      min="15"
                      max="120"
                      value={formData.call_timeout}
                      onChange={(e) => setFormData({ ...formData, call_timeout: e.target.value })}
                      className="ios-input"
                    />
                    <p className="text-xs text-ios-gray-2 mt-1">Ring time before hangup</p>
                  </div>
                </div>

                {/* Working Hours */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                      Working Hours Start
                    </label>
                    <input
                      type="time"
                      value={formData.working_hours_start}
                      onChange={(e) => setFormData({ ...formData, working_hours_start: e.target.value })}
                      className="ios-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                      Working Hours End
                    </label>
                    <input
                      type="time"
                      value={formData.working_hours_end}
                      onChange={(e) => setFormData({ ...formData, working_hours_end: e.target.value })}
                      className="ios-input"
                    />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault()
                      e.stopPropagation()
                      handleClose()
                    }}
                    className="flex-1 ios-button-secondary cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createCampaignMutation.isPending}
                    className="flex-1 ios-button-primary"
                  >
                    {createCampaignMutation.isPending ? 'Creating...' : 'Create Campaign'}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}
