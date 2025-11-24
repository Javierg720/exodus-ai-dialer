import { AlertTriangle, RefreshCw, X } from 'lucide-react'
import { APIError } from '../lib/api'

interface ErrorAlertProps {
  error: Error | APIError | null
  onRetry?: () => void
  onDismiss?: () => void
  title?: string
}

export function ErrorAlert({ error, onRetry, onDismiss, title = 'Error' }: ErrorAlertProps) {
  if (!error) return null

  const isAPIError = error instanceof APIError
  const statusCode = isAPIError ? error.status : null

  return (
    <div className="bg-ios-red/10 border border-ios-red/20 rounded-2xl p-4 mb-6">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-xl bg-ios-red/20">
          <AlertTriangle className="w-5 h-5 text-ios-red" />
        </div>
        
        <div className="flex-1">
          <div className="flex items-start justify-between mb-1">
            <h3 className="font-semibold text-white">{title}</h3>
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="p-1 hover:bg-dark-3 rounded-lg transition-colors"
              >
                <X className="w-4 h-4 text-ios-gray-2" />
              </button>
            )}
          </div>
          
          <p className="text-sm text-ios-gray-2 mb-3">
            {error.message}
          </p>

          {/* Show status code in development */}
          {import.meta.env.DEV && statusCode !== null && statusCode !== 0 && (
            <p className="text-xs text-ios-gray-2 mb-2">
              Status Code: {statusCode}
            </p>
          )}

          {/* Action Buttons */}
          {onRetry && (
            <button
              onClick={onRetry}
              className="ios-button bg-ios-red/20 hover:bg-ios-red/30 text-ios-red flex items-center gap-2 text-sm"
            >
              <RefreshCw className="w-4 h-4" />
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default ErrorAlert
