import { useQuery } from '@tanstack/react-query'
import { Search, Play, Download, MessageSquare, Brain } from 'lucide-react'
import { api } from '../lib/api'
import GlassCard from '../components/GlassCard'
import WaveformPlayer from '../components/WaveformPlayer'
import { motion } from 'framer-motion'
import { Call } from '../types'
import { useState, useMemo } from 'react'
import { formatDistanceToNow } from 'date-fns'
import CallHistoryFilters, { CallFilterState } from '../components/CallHistoryFilters'
import SortControls, { SortConfig } from '../components/SortControls'

export default function CallHistory() {
  const [searchTerm, setSearchTerm] = useState('')
  const [playingAudio, setPlayingAudio] = useState<string | null>(null)
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
  const [sortConfig, setSortConfig] = useState<SortConfig>({
    field: 'date',
    direction: 'desc'
  })
  
  const { data: apiCalls, isLoading } = useQuery<any[]>({
    queryKey: ['callHistory'],
    queryFn: () => api.getCallHistory(),
  })

  const { data: campaigns } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => api.getCampaigns(),
  })

  // Transform API response to match Call interface
  const calls: Call[] = apiCalls?.map((apiCall) => ({
    id: String(apiCall.id),
    uuid: apiCall.call_uuid || '',
    campaign_id: apiCall.campaign_id,
    lead_id: apiCall.lead_id,
    phone_number: apiCall.phone_number || 'Unknown',
    bot_port: apiCall.bot_port,
    status: apiCall.call_status?.toLowerCase() || 'unknown',
    duration: apiCall.duration_seconds ? Math.round(apiCall.duration_seconds) : undefined,
    recording_url: apiCall.recording_url,
    transcript: apiCall.transcription_text,
    transcription_text: apiCall.transcription_text,
    summary: apiCall.summary,
    sentiment: apiCall.sentiment,
    key_points: apiCall.key_points,
    disposition: apiCall.disposition_code,
    started_at: apiCall.start_time,
    ended_at: apiCall.end_time,
  })) || []

  const handleSort = (field: string) => {
    setSortConfig((prev) => {
      if (prev.field === field) {
        // Cycle: asc -> desc -> null (original order)
        if (prev.direction === 'asc') return { field, direction: 'desc' }
        if (prev.direction === 'desc') return { field: '', direction: null }
      }
      return { field, direction: 'asc' }
    })
  }

  const sortedAndFilteredCalls = useMemo(() => {
    // First filter
    const filtered = calls?.filter((call: Call) => {
      // Text search
      const matchesSearch =
        call.phone_number.includes(searchTerm) ||
        call.disposition?.toLowerCase().includes(searchTerm.toLowerCase())
      
      if (!matchesSearch) return false

      // Status filter
      if (filters.status && call.status !== filters.status) return false

      // Campaign filter
      if (filters.campaign_id && String(call.campaign_id) !== filters.campaign_id) return false

      // Disposition filter
      if (filters.disposition && call.disposition !== filters.disposition) return false

      // Duration filters
      if (filters.min_duration && (!call.duration || call.duration < parseInt(filters.min_duration))) return false
      if (filters.max_duration && (!call.duration || call.duration > parseInt(filters.max_duration))) return false

      // Recording filter
      if (filters.has_recording && !call.recording_url) return false

      // Transcript filter
      if (filters.has_transcript && !call.transcription_text && !call.transcript) return false

      // Date filters
      if (filters.date_from && call.started_at) {
        const callDate = new Date(call.started_at)
        const fromDate = new Date(filters.date_from)
        if (callDate < fromDate) return false
      }
      if (filters.date_to && call.started_at) {
        const callDate = new Date(call.started_at)
        const toDate = new Date(filters.date_to)
        toDate.setHours(23, 59, 59) // End of day
        if (callDate > toDate) return false
      }

      return true
    }) || []

    // Then sort
    if (!sortConfig.direction || !sortConfig.field) return filtered

    return [...filtered].sort((a, b) => {
      let aVal: any
      let bVal: any

      switch (sortConfig.field) {
        case 'date':
          aVal = new Date(a.started_at || 0).getTime()
          bVal = new Date(b.started_at || 0).getTime()
          break
        case 'phone':
          aVal = a.phone_number
          bVal = b.phone_number
          break
        case 'duration':
          aVal = a.duration || 0
          bVal = b.duration || 0
          break
        case 'status':
          aVal = a.status || ''
          bVal = b.status || ''
          break
        case 'disposition':
          aVal = a.disposition || ''
          bVal = b.disposition || ''
          break
        default:
          aVal = a.id
          bVal = b.id
      }

      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1
      return 0
    })
  }, [calls, searchTerm, filters, sortConfig])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-ios-green/20 text-ios-green'
      case 'failed': return 'bg-ios-red/20 text-ios-red'
      case 'no-answer': return 'bg-ios-orange/20 text-ios-orange'
      default: return 'bg-ios-gray-2/20 text-ios-gray-2'
    }
  }

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="skeleton h-12 w-64 mb-8" />
        <div className="space-y-4">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="skeleton h-24 rounded-2xl" />
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
      <div>
        <h1 className="text-4xl font-bold">Call History</h1>
        <p className="text-ios-gray-2 mt-2">{calls?.length || 0} total calls</p>
      </div>

      {/* Search & Filters */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-ios-gray-2" />
          <input
            type="text"
            placeholder="Search calls by phone or disposition..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="ios-input pl-12"
          />
        </div>

        <CallHistoryFilters onFilterChange={setFilters} campaigns={campaigns} />

        {/* Sort Controls */}
        <SortControls
          sortConfig={sortConfig}
          onSortChange={handleSort}
          fields={[
            { key: 'date', label: 'Date' },
            { key: 'phone', label: 'Phone' },
            { key: 'duration', label: 'Duration' },
            { key: 'status', label: 'Status' },
            { key: 'disposition', label: 'Disposition' },
          ]}
        />
      </div>

      {/* Call History List */}
      <div className="space-y-4">
        {sortedAndFilteredCalls?.map((call: Call) => (
          <GlassCard key={call.id}>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-bold">{call.phone_number}</h3>
                  <span className={`ios-badge ${getStatusColor(call.status)}`}>
                    {call.status}
                  </span>
                  {call.disposition && (
                    <span className="ios-badge bg-ios-blue/20 text-ios-blue">
                      {call.disposition}
                    </span>
                  )}
                  {/* Debug badge */}
                  {call.recording_url && (
                    <span className="ios-badge bg-ios-green/20 text-ios-green text-xs">
                      HAS REC
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-4 text-sm text-ios-gray-2">
                  <span>
                    {call.started_at && formatDistanceToNow(new Date(call.started_at), { addSuffix: true })}
                  </span>
                  {call.duration && (
                    <span>
                      Duration: {Math.floor(call.duration / 60)}:{String(call.duration % 60).padStart(2, '0')}
                    </span>
                  )}
                  {call.bot_port && (
                    <span>Bot {call.bot_port}</span>
                  )}
                </div>
                
                {/* AI-Generated Summary */}
                {call.summary && (
                  <div className="mt-3 p-3 bg-ios-blue/10 border border-ios-blue/30 rounded-xl">
                    <div className="flex items-start gap-2">
                      <Brain className="w-4 h-4 text-ios-blue mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-xs font-semibold text-ios-blue mb-1">AI Summary</p>
                        <p className="text-sm text-white/90 leading-relaxed">{call.summary}</p>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Full Transcript */}
                {call.transcription_text && (
                  <div className="mt-2 p-3 bg-dark-3/50 rounded-xl">
                    <div className="flex items-start gap-2">
                      <MessageSquare className="w-4 h-4 text-ios-gray-2 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-xs font-semibold text-ios-gray-2 mb-1">Full Transcript</p>
                        <p className="text-sm text-ios-gray-2 leading-relaxed whitespace-pre-line line-clamp-3">
                          {call.transcription_text}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Legacy transcript field (fallback) */}
                {!call.transcription_text && call.transcript && (
                  <p className="text-sm text-ios-gray-2 mt-2 italic line-clamp-2">
                    "{call.transcript}"
                  </p>
                )}
              </div>
              
              {call.recording_url && (
                <div className="flex gap-2">
                  <button
                    onClick={() => setPlayingAudio(playingAudio === call.uuid ? null : call.uuid)}
                    className="ios-button-primary flex items-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    {playingAudio === call.uuid ? 'Close Player' : 'Show Waveform'}
                  </button>
                </div>
              )}
            </div>

            {/* Waveform Audio Player */}
            {playingAudio === call.uuid && call.recording_url && (
              <div className="mt-4">
                <WaveformPlayer
                  audioUrl={api.getRecording(call.uuid)}
                  callUuid={call.uuid}
                  onDownload={() => {
                    const link = document.createElement('a')
                    link.href = api.getRecording(call.uuid)
                    link.download = `recording_${call.phone_number}_${call.uuid}.wav`
                    link.click()
                  }}
                />
              </div>
            )}
          </GlassCard>
        ))}
      </div>

      {sortedAndFilteredCalls?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-ios-gray-2 text-lg">No calls found</p>
        </div>
      )}
    </motion.div>
  )
}
