import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Upload, Phone, Plus, Search } from 'lucide-react'
import { api } from '../lib/api'
import GlassCard from '../components/GlassCard'
import { motion } from 'framer-motion'
import { Lead } from '../types'
import { useState, useRef, useMemo } from 'react'
import AddLeadModal from '../components/AddLeadModal'
import LeadFilters, { LeadFilterState } from '../components/LeadFilters'
import SortControls, { SortConfig } from '../components/SortControls'

export default function Leads() {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [importing, setImporting] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)
  const [filters, setFilters] = useState<LeadFilterState>({
    status: '',
    campaign_id: '',
    min_attempts: '',
    max_attempts: '',
    has_email: false,
    has_company: false,
  })
  const [sortConfig, setSortConfig] = useState<SortConfig>({
    field: 'id',
    direction: 'desc'
  })
  
  const { data: leads, isLoading } = useQuery<Lead[]>({
    queryKey: ['leads'],
    queryFn: () => api.getLeads(),
  })

  const { data: campaigns } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => api.getCampaigns(),
  })

  const callMutation = useMutation({
    mutationFn: async ({ phoneNumber, campaignId }: { phoneNumber: string; campaignId?: number }) => {
      console.log('Initiating call to:', phoneNumber, 'campaign:', campaignId)
      const result = await api.originateCall(phoneNumber, campaignId)
      console.log('Call API response:', result)
      return result
    },
    onSuccess: (data: any) => {
      console.log('✅ Call initiated successfully:', data)
      // Check if response has status field
      if (data && data.status === 'success') {
        // Success - show confirmation
        const message = `✅ Call initiated!\n\nPhone: ${data.phone_number}\nBot Port: ${data.bot_port}\n\nThe customer's phone should be ringing now.`
        alert(message)
      } else if (data && data.status === 'error') {
        // Error from API
        alert(`❌ Call failed: ${data.message || 'Unknown error'}`)
      } else {
        // Successful call (no status field means success in some APIs)
        alert(`✅ Call initiated successfully!`)
      }
    },
    onError: (error: any) => {
      console.error('❌ Call failed:', error)
      alert(`Failed to initiate call: ${error.message || 'Unknown error'}`)
    }
  })

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setImporting(true)
    try {
      await api.importLeads(file)
      queryClient.invalidateQueries({ queryKey: ['leads'] })
    } catch (error) {
      console.error('Import failed:', error)
    } finally {
      setImporting(false)
    }
  }

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

  const sortedAndFilteredLeads = useMemo(() => {
    // First filter
    const filtered = leads?.filter((lead: Lead) => {
      // Text search
      const matchesSearch = 
        lead.phone_number.includes(searchTerm) ||
        lead.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (lead as any).company?.toLowerCase().includes(searchTerm.toLowerCase())
      
      if (!matchesSearch) return false

      // Status filter
      if (filters.status && lead.status?.toUpperCase() !== filters.status) return false

      // Campaign filter
      if (filters.campaign_id && String(lead.campaign_id) !== filters.campaign_id) return false

      // Attempts filters
      const attempts = (lead as any).attempts || 0
      if (filters.min_attempts && attempts < parseInt(filters.min_attempts)) return false
      if (filters.max_attempts && attempts > parseInt(filters.max_attempts)) return false

      // Email filter
      if (filters.has_email && !lead.email) return false

      // Company filter
      if (filters.has_company && !(lead as any).company) return false

      return true
    }) || []

    // Then sort
    if (!sortConfig.direction || !sortConfig.field) return filtered

    return [...filtered].sort((a, b) => {
      let aVal: any
      let bVal: any

      switch (sortConfig.field) {
        case 'name':
          aVal = (a.first_name || a.phone_number).toLowerCase()
          bVal = (b.first_name || b.phone_number).toLowerCase()
          break
        case 'phone':
          aVal = a.phone_number
          bVal = b.phone_number
          break
        case 'status':
          aVal = a.status || ''
          bVal = b.status || ''
          break
        case 'company':
          aVal = ((a as any).company || '').toLowerCase()
          bVal = ((b as any).company || '').toLowerCase()
          break
        case 'attempts':
          aVal = (a as any).attempts || 0
          bVal = (b as any).attempts || 0
          break
        case 'created':
          aVal = new Date((a as any).created_at || 0).getTime()
          bVal = new Date((b as any).created_at || 0).getTime()
          break
        case 'id':
        default:
          aVal = a.id
          bVal = b.id
      }

      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1
      return 0
    })
  }, [leads, searchTerm, filters, sortConfig])

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="skeleton h-12 w-64 mb-8" />
        <div className="space-y-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="skeleton h-20 rounded-2xl" />
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
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold">Leads</h1>
          <p className="text-ios-gray-2 mt-2">{leads?.length || 0} total leads</p>
        </div>
        <div className="flex gap-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".csv"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={importing}
            className="ios-button-secondary flex items-center gap-2"
          >
            <Upload className="w-5 h-5" />
            {importing ? 'Importing...' : 'Import CSV'}
          </button>
          <button 
            onClick={() => setShowAddModal(true)}
            className="ios-button-primary flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Add Lead
          </button>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-ios-gray-2" />
          <input
            type="text"
            placeholder="Search leads by name, phone, or company..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="ios-input pl-12"
          />
        </div>

        <LeadFilters onFilterChange={setFilters} campaigns={campaigns} />

        {/* Sort Controls */}
        <SortControls
          sortConfig={sortConfig}
          onSortChange={handleSort}
          fields={[
            { key: 'name', label: 'Name' },
            { key: 'phone', label: 'Phone' },
            { key: 'status', label: 'Status' },
            { key: 'company', label: 'Company' },
            { key: 'attempts', label: 'Attempts' },
            { key: 'created', label: 'Date Added' },
          ]}
        />
      </div>

      {/* Leads Table/Cards */}
      <div className="space-y-4">
        {sortedAndFilteredLeads?.map((lead: Lead) => (
          <GlassCard key={lead.id} hover>
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-xl font-bold">
                    {lead.first_name || lead.phone_number}
                    {lead.last_name && ` ${lead.last_name}`}
                  </h3>
                  <span className={`ios-badge ${
                    lead.status === 'new' || lead.status === 'NEW' ? 'bg-ios-blue/20 text-ios-blue' :
                    lead.status === 'contacted' || lead.status === 'CONTACTED' ? 'bg-ios-green/20 text-ios-green' :
                    lead.status === 'failed' || lead.status === 'FAILED' ? 'bg-ios-red/20 text-ios-red' :
                    lead.status === 'COMPLETED' ? 'bg-ios-green/20 text-ios-green' :
                    'bg-ios-gray-2/20 text-ios-gray-2'
                  }`}>
                    {lead.status}
                  </span>
                </div>
                {(lead as any).company && (
                  <p className="text-base font-medium text-ios-blue mb-1">🏢 {(lead as any).company}</p>
                )}
                <p className="text-ios-gray-2 font-mono">📞 {lead.phone_number}</p>
                {lead.email && (
                  <p className="text-sm text-ios-gray-2 mt-1">📧 {lead.email}</p>
                )}
                {((lead as any).city || (lead as any).state) && (
                  <p className="text-sm text-ios-gray-2 mt-1">
                    📍 {(lead as any).city}{(lead as any).city && (lead as any).state && ', '}{(lead as any).state}
                  </p>
                )}
              </div>
              <button
                onClick={() => callMutation.mutate({ 
                  phoneNumber: lead.phone_number, 
                  campaignId: lead.campaign_id 
                })}
                disabled={callMutation.isPending}
                className="ios-button-primary flex items-center gap-2 whitespace-nowrap"
              >
                <Phone className="w-5 h-5" />
                {callMutation.isPending ? 'Calling...' : 'Call Now'}
              </button>
            </div>
          </GlassCard>
        ))}
      </div>

      {sortedAndFilteredLeads?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-ios-gray-2 text-lg">No leads found</p>
        </div>
      )}

      {/* Add Lead Modal */}
      <AddLeadModal 
        isOpen={showAddModal} 
        onClose={() => setShowAddModal(false)} 
      />
    </motion.div>
  )
}
