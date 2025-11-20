import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'

export interface SortConfig {
  field: string
  direction: 'asc' | 'desc' | null
}

interface SortControlsProps {
  sortConfig: SortConfig
  onSortChange: (field: string) => void
  fields: Array<{ key: string; label: string }>
}

export default function SortControls({ sortConfig, onSortChange, fields }: SortControlsProps) {
  const getSortIcon = (field: string) => {
    if (sortConfig.field !== field || sortConfig.direction === null) {
      return <ArrowUpDown className="w-4 h-4 text-ios-gray-2" />
    }
    if (sortConfig.direction === 'asc') {
      return <ArrowUp className="w-4 h-4 text-ios-blue" />
    }
    return <ArrowDown className="w-4 h-4 text-ios-blue" />
  }

  return (
    <div className="bg-dark-2/80 backdrop-blur-xl border border-white/10 rounded-2xl p-4">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-sm font-medium text-ios-gray-2">Sort by:</span>
        {fields.map((field) => (
          <button
            key={field.key}
            onClick={() => onSortChange(field.key)}
            className={`flex items-center gap-2 px-3 py-2 rounded-xl transition-all ${
              sortConfig.field === field.key
                ? 'bg-ios-blue/20 text-ios-blue border border-ios-blue/30'
                : 'bg-dark-3/50 text-white hover:bg-dark-3 border border-white/10'
            }`}
          >
            {field.label}
            {getSortIcon(field.key)}
          </button>
        ))}
      </div>
    </div>
  )
}
