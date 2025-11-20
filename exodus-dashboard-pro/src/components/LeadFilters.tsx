import { Filter, X } from 'lucide-react'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface LeadFiltersProps {
  onFilterChange: (filters: LeadFilterState) => void
  campaigns?: Array<{ id: number; name: string }>
}

export interface LeadFilterState {
  status: string
  campaign_id: string
  min_attempts: string
  max_attempts: string
  has_email: boolean
  has_company: boolean
}

export default function LeadFilters({ onFilterChange, campaigns }: LeadFiltersProps) {
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<LeadFilterState>({
    status: '',
    campaign_id: '',
    min_attempts: '',
    max_attempts: '',
    has_email: false,
    has_company: false,
  })

  const handleFilterChange = (key: keyof LeadFilterState, value: any) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  const clearFilters = () => {
    const emptyFilters: LeadFilterState = {
      status: '',
      campaign_id: '',
      min_attempts: '',
      max_attempts: '',
      has_email: false,
      has_company: false,
    }
    setFilters(emptyFilters)
    onFilterChange(emptyFilters)
  }

  const activeFilterCount = Object.entries(filters).filter(([key, value]) => {
    if (typeof value === 'boolean') return value
    return value !== ''
  }).length

  return (
    <div className="space-y-4">
      {/* Filter Toggle Button */}
      <button
        onClick={() => setShowFilters(!showFilters)}
        className="ios-button-secondary flex items-center gap-2 relative"
      >
        <Filter className="w-5 h-5" />
        Filters
        {activeFilterCount > 0 && (
          <span className="absolute -top-2 -right-2 bg-ios-blue text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
            {activeFilterCount}
          </span>
        )}
      </button>

      {/* Filter Panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="bg-dark-2/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">Filter Leads</h3>
                {activeFilterCount > 0 && (
                  <button
                    onClick={clearFilters}
                    className="text-ios-red text-sm flex items-center gap-1 hover:underline"
                  >
                    <X className="w-4 h-4" />
                    Clear All
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Status Filter */}
                <div>
                  <label className="block text-sm font-medium mb-2">Status</label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    className="ios-input"
                  >
                    <option value="">All Statuses</option>
                    <option value="NEW">New</option>
                    <option value="CALLING">Calling</option>
                    <option value="ANSWERED">Answered</option>
                    <option value="NO_ANSWER">No Answer</option>
                    <option value="BUSY">Busy</option>
                    <option value="FAILED">Failed</option>
                    <option value="COMPLETED">Completed</option>
                  </select>
                </div>

                {/* Campaign Filter */}
                {campaigns && campaigns.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Campaign</label>
                    <select
                      value={filters.campaign_id}
                      onChange={(e) => handleFilterChange('campaign_id', e.target.value)}
                      className="ios-input"
                    >
                      <option value="">All Campaigns</option>
                      {campaigns.map((campaign) => (
                        <option key={campaign.id} value={campaign.id}>
                          {campaign.name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Min Attempts */}
                <div>
                  <label className="block text-sm font-medium mb-2">Min Attempts</label>
                  <input
                    type="number"
                    min="0"
                    value={filters.min_attempts}
                    onChange={(e) => handleFilterChange('min_attempts', e.target.value)}
                    placeholder="0"
                    className="ios-input"
                  />
                </div>

                {/* Max Attempts */}
                <div>
                  <label className="block text-sm font-medium mb-2">Max Attempts</label>
                  <input
                    type="number"
                    min="0"
                    value={filters.max_attempts}
                    onChange={(e) => handleFilterChange('max_attempts', e.target.value)}
                    placeholder="10"
                    className="ios-input"
                  />
                </div>

                {/* Has Email */}
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="has-email"
                    checked={filters.has_email}
                    onChange={(e) => handleFilterChange('has_email', e.target.checked)}
                    className="w-5 h-5 rounded border-white/20 bg-dark-3 text-ios-blue focus:ring-ios-blue"
                  />
                  <label htmlFor="has-email" className="text-sm font-medium cursor-pointer">
                    Has Email
                  </label>
                </div>

                {/* Has Company */}
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="has-company"
                    checked={filters.has_company}
                    onChange={(e) => handleFilterChange('has_company', e.target.checked)}
                    className="w-5 h-5 rounded border-white/20 bg-dark-3 text-ios-blue focus:ring-ios-blue"
                  />
                  <label htmlFor="has-company" className="text-sm font-medium cursor-pointer">
                    Has Company
                  </label>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
