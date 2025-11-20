import { useState } from 'react'
import { X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

interface AddLeadModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function AddLeadModal({ isOpen, onClose }: AddLeadModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    campaign_id: '',
    phone_number: '',
    first_name: '',
    last_name: '',
    email: '',
    company: '',
    city: '',
    state: '',
    zip_code: ''
  })
  const [error, setError] = useState('')

  const { data: campaigns } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => api.getCampaigns(),
    enabled: isOpen
  })

  const createLeadMutation = useMutation({
    mutationFn: (data: any) => api.createLead(data),
    onSuccess: (response: any) => {
      if (response.status === 'success') {
        queryClient.invalidateQueries({ queryKey: ['leads'] })
        handleClose()
      } else {
        setError(response.message || 'Failed to create lead')
      }
    },
    onError: (err: any) => {
      setError(err.message || 'Failed to create lead')
    }
  })

  const handleClose = () => {
    setFormData({
      campaign_id: '',
      phone_number: '',
      first_name: '',
      last_name: '',
      email: '',
      company: '',
      city: '',
      state: '',
      zip_code: ''
    })
    setError('')
    onClose()
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validate required fields
    if (!formData.campaign_id) {
      setError('Please select a campaign')
      return
    }

    if (!formData.phone_number) {
      setError('Phone number is required')
      return
    }

    // Normalize phone number
    let phone = formData.phone_number.replace(/\D/g, '')
    if (phone.length === 10) {
      phone = '1' + phone
    }
    if (!phone.startsWith('1') && phone.length === 11) {
      phone = '1' + phone
    }

    createLeadMutation.mutate({
      ...formData,
      phone_number: '+' + phone,
      campaign_id: parseInt(formData.campaign_id)
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
                <h2 className="text-2xl font-bold">Add New Lead</h2>
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
                {/* Campaign Selection */}
                <div>
                  <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                    Campaign <span className="text-ios-red">*</span>
                  </label>
                  <select
                    value={formData.campaign_id}
                    onChange={(e) => setFormData({ ...formData, campaign_id: e.target.value })}
                    className="ios-input"
                    required
                  >
                    <option value="">Select a campaign</option>
                    {campaigns?.map((campaign: any) => (
                      <option key={campaign.id} value={campaign.id}>
                        {campaign.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Phone Number */}
                <div>
                  <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                    Phone Number <span className="text-ios-red">*</span>
                  </label>
                  <input
                    type="tel"
                    value={formData.phone_number}
                    onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                    placeholder="+1 (555) 123-4567"
                    className="ios-input"
                    required
                  />
                  <p className="text-xs text-ios-gray-2 mt-1">
                    Enter with country code (e.g., +1 for US) or 10 digits
                  </p>
                </div>

                {/* First Name & Last Name */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      value={formData.first_name}
                      onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                      placeholder="John"
                      className="ios-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      value={formData.last_name}
                      onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                      placeholder="Doe"
                      className="ios-input"
                    />
                  </div>
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="john@example.com"
                    className="ios-input"
                  />
                </div>

                {/* Company */}
                <div>
                  <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                    Company
                  </label>
                  <input
                    type="text"
                    value={formData.company}
                    onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                    placeholder="Acme Corp"
                    className="ios-input"
                  />
                </div>

                {/* City, State, Zip */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                      City
                    </label>
                    <input
                      type="text"
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                      placeholder="New York"
                      className="ios-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                      State
                    </label>
                    <input
                      type="text"
                      value={formData.state}
                      onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                      placeholder="NY"
                      maxLength={2}
                      className="ios-input uppercase"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-ios-gray-2 mb-2">
                    Zip Code
                  </label>
                  <input
                    type="text"
                    value={formData.zip_code}
                    onChange={(e) => setFormData({ ...formData, zip_code: e.target.value })}
                    placeholder="10001"
                    maxLength={10}
                    className="ios-input"
                  />
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={handleClose}
                    className="flex-1 ios-button-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createLeadMutation.isPending}
                    className="flex-1 ios-button-primary"
                  >
                    {createLeadMutation.isPending ? 'Creating...' : 'Add Lead'}
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
