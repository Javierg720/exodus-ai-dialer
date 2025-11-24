import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Trash2, Upload, Download } from 'lucide-react'
import { api } from '../lib/api'
import GlassCard from '../components/GlassCard'
import ErrorAlert from '../components/ErrorAlert'
import { motion } from 'framer-motion'
import { DNCEntry } from '../types'
import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'

export default function DNCList() {
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [newNumber, setNewNumber] = useState('')
  const [newReason, setNewReason] = useState('')
  const [mutationError, setMutationError] = useState<Error | null>(null)
  
  const { data: dncList, isLoading, error, refetch } = useQuery<DNCEntry[]>({
    queryKey: ['dnc'],
    queryFn: () => api.getDNC(),
  })

  const addMutation = useMutation({
    mutationFn: ({ phone, reason }: { phone: string; reason?: string }) => 
      api.addToDNC(phone, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dnc'] })
      setNewNumber('')
      setNewReason('')
      setMutationError(null)
    },
    onError: (error: Error) => {
      setMutationError(error)
    },
  })

  const removeMutation = useMutation({
    mutationFn: (phoneNumber: string) => api.removeDNC(phoneNumber),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dnc'] })
      setMutationError(null)
    },
    onError: (error: Error) => {
      setMutationError(error)
    },
  })

  const importMutation = useMutation({
    mutationFn: ({ numbers, reason }: { numbers: string[]; reason?: string }) =>
      api.importDNC(numbers, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dnc'] })
      setMutationError(null)
    },
    onError: (error: Error) => {
      setMutationError(error)
    },
  })

  const handleAdd = () => {
    if (newNumber) {
      addMutation.mutate({ phone: newNumber, reason: newReason })
    }
  }

  const handleRemove = (phoneNumber: string) => {
    if (confirm(`Remove ${phoneNumber} from DNC list?`)) {
      removeMutation.mutate(phoneNumber)
    }
  }

  const handleImport = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.csv,.txt'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) return

      const text = await file.text()
      const lines = text.split('\n')
      const numbers: string[] = []

      // Parse CSV - skip header if present
      lines.forEach((line, idx) => {
        const trimmed = line.trim()
        if (trimmed && !trimmed.toLowerCase().includes('phone')) {
          // Extract first column (phone number)
          const phone = trimmed.split(',')[0].trim()
          if (phone) numbers.push(phone)
        }
      })

      if (numbers.length > 0) {
        const reason = prompt('Reason for import:', 'Bulk CSV import')
        if (reason !== null) {
          importMutation.mutate({ numbers, reason })
        }
      }
    }
    input.click()
  }

  const handleExport = async () => {
    try {
      const blob = await api.exportDNC()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `dnc_list_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  const filteredDNC = dncList?.filter((entry: DNCEntry) =>
    entry.phone_number.includes(searchTerm) ||
    entry.reason?.toLowerCase().includes(searchTerm.toLowerCase())
  )

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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold">Do Not Call List</h1>
          <p className="text-ios-gray-2 mt-2">{dncList?.length || 0} numbers blocked</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleImport}
            disabled={importMutation.isPending}
            className="ios-button-secondary flex items-center gap-2"
          >
            <Upload className="w-5 h-5" />
            Import CSV
          </button>
          <button
            onClick={handleExport}
            className="ios-button-secondary flex items-center gap-2"
          >
            <Download className="w-5 h-5" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Error Alerts */}
      {error && (
        <ErrorAlert
          error={error as Error}
          onRetry={() => refetch()}
          title="Failed to load DNC list"
        />
      )}
      
      {mutationError && (
        <ErrorAlert
          error={mutationError}
          onDismiss={() => setMutationError(null)}
          title="DNC operation failed"
        />
      )}

      {/* Add Number Form */}
      <GlassCard>
        <h3 className="text-lg font-semibold mb-4">Add to DNC List</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="tel"
            placeholder="Phone number"
            value={newNumber}
            onChange={(e) => setNewNumber(e.target.value)}
            className="ios-input"
          />
          <input
            type="text"
            placeholder="Reason (optional)"
            value={newReason}
            onChange={(e) => setNewReason(e.target.value)}
            className="ios-input"
          />
          <button
            onClick={handleAdd}
            disabled={!newNumber || addMutation.isPending}
            className="ios-button-primary flex items-center justify-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Add Number
          </button>
        </div>
      </GlassCard>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-ios-gray-2" />
        <input
          type="text"
          placeholder="Search DNC list..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="ios-input pl-12"
        />
      </div>

      {/* DNC List */}
      <div className="space-y-4">
        {filteredDNC?.map((entry: DNCEntry) => (
          <GlassCard key={entry.phone_number}>
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-bold">{entry.phone_number}</h3>
                {entry.reason && (
                  <p className="text-sm text-ios-gray-2 mt-1">{entry.reason}</p>
                )}
                <p className="text-xs text-ios-gray-2 mt-2">
                  Added {formatDistanceToNow(new Date(entry.added_at), { addSuffix: true })}
                </p>
              </div>
              <button 
                onClick={() => handleRemove(entry.phone_number)}
                disabled={removeMutation.isPending}
                className="p-3 rounded-xl bg-ios-red/20 hover:bg-ios-red/30 text-ios-red transition-colors disabled:opacity-50"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </GlassCard>
        ))}
      </div>

      {filteredDNC?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-ios-gray-2 text-lg">No numbers in DNC list</p>
        </div>
      )}
    </motion.div>
  )
}
