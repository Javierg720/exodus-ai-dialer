import { LucideIcon } from 'lucide-react'
import { motion } from 'framer-motion'
import GlassCard from './GlassCard'

interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  trend?: number
  color?: string
}

export default function StatCard({ title, value, icon: Icon, trend, color = 'ios-blue' }: StatCardProps) {
  return (
    <GlassCard>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-ios-gray-2 font-medium">{title}</p>
          <motion.p
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-3xl font-bold mt-2"
          >
            {value}
          </motion.p>
          {trend !== undefined && (
            <p className={`text-sm mt-2 ${trend >= 0 ? 'text-ios-green' : 'text-ios-red'}`}>
              {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
            </p>
          )}
        </div>
        <div className={`p-3 rounded-xl bg-${color}/10`}>
          <Icon className={`w-6 h-6 text-${color}`} />
        </div>
      </div>
    </GlassCard>
  )
}
