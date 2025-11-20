import { Filter, X } from 'lucide-react'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface CallHistoryFiltersProps {
  onFilterChange: (filters: CallFilterState) => void
  campaigns?: Array<{ id: number; name: string }>
}

export interface CallFilterState {
  status: string
  campaign_id: string
  min_duration: string
  max_duration: string
  has_recording: boolean
  has_transcript: boolean
  date_from: string
  date_to: string
  disposition: string
}

export default function CallHistoryFilters({ onFilterChange, campaigns }: CallHistoryFiltersProps) {
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<CallFilterState>({
    status: '',
    campaign_id: '',
    min_duration: '',
    max_duration: '',
    has_recording: false,
    has_transcript: false,
    date_from: '',
    date_to: '',
    disposition: '',
  })

  const handleFilterChange = (key: keyof CallFilterState, value: any) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  const clearFilters = () => {
    const emptyFilters: CallFilterState = {
      status: '',
      campaign_id: '',
      min_duration: '',
      max_duration: '',
      has_recording: false,
      has_transcript: false,
      date_from: '',
      date_to: '',
      disposition: '',
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
                <h3 className="text-lg font-bold">Filter Calls</h3>
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
                  <label className="block text-sm font-medium mb-2">Call Status</label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    className="ios-input"
                  >
                    <option value="">All Statuses</option>
                    <option value="answered">Answered</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                    <option value="no-answer">No Answer</option>
                    <option value="busy">Busy</option>
                  </select>
                </div>

                {/* Disposition Filter */}
                <div>
                  <label className="block text-sm font-medium mb-2">Disposition</label>
                  <select
                    value={filters.disposition}
                    onChange={(e) => handleFilterChange('disposition', e.target.value)}
                    className="ios-input"
                  >
                    <option value="">All Dispositions</option>
                    <option value="INTERESTED">Interested</option>
                    <option value="NOT_INTERESTED">Not Interested</option>
                    <option value="CALLBACK">Callback</option>
                    <option value="VOICEMAIL">Voicemail</option>
                    <option value="WRONG_NUMBER">Wrong Number</option>
                    <option value="DNC">DNC</option>
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

                {/* Date From */}
                <div>
                  <label className="block text-sm font-medium mb-2">From Date</label>
                  <input
                    type="date"
                    value={filters.date_from}
                    onChange={(e) => handleFilterChange('date_from', e.target.value)}
                    className="ios-input"
                  />
                </div>

                {/* Date To */}
                <div>
                  <label className="block text-sm font-medium mb-2">To Date</label>
                  <input
                    type="date"
                    value={filters.date_to}
                    onChange={(e) => handleFilterChange('date_to', e.target.value)}
                    className="ios-input"
                  />
                </div>

                {/* Min Duration */}
                <div>
                  <label className="block text-sm font-medium mb-2">Min Duration (sec)</label>
                  <input
                    type="number"
                    min="0"
                    value={filters.min_duration}
                    onChange={(e) => handleFilterChange('min_duration', e.target.value)}
                    placeholder="0"
                    className="ios-input"
                  />
                </div>

                {/* Max Duration */}
                <div>
                  <label className="block text-sm font-medium mb-2">Max Duration (sec)</label>
                  <input
                    type="number"
                    min="0"
                    value={filters.max_duration}
                    onChange={(e) => handleFilterChange('max_duration', e.target.value)}
                    placeholder="600"
                    className="ios-input"
                  />
                </div>

                {/* Has Recording */}
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="has-recording"
                    checked={filters.has_recording}
                    onChange={(e) => handleFilterChange('has_recording', e.target.checked)}
                    className="w-5 h-5 rounded border-white/20 bg-dark-3 text-ios-blue focus:ring-ios-blue"
                  />
                  <label htmlFor="has-recording" className="text-sm font-medium cursor-pointer">
                    Has Recording
                  </label>
                </div>

                {/* Has Transcript */}
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="has-transcript"
                    checked={filters.has_transcript}
                    onChange={(e) => handleFilterChange('has_transcript', e.target.checked)}
                    className="w-5 h-5 rounded border-white/20 bg-dark-3 text-ios-blue focus:ring-ios-blue"
                  />
                  <label htmlFor="has-transcript" className="text-sm font-medium cursor-pointer">
                    Has Transcript
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
