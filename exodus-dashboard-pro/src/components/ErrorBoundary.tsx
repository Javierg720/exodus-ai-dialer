import { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import GlassCard from './GlassCard'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onReset?: () => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error details to console for debugging
    console.error('Error Boundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo,
    })

    // You can also log the error to an error reporting service here
    // Example: logErrorToService(error, errorInfo)
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
    
    // Call custom reset handler if provided
    if (this.props.onReset) {
      this.props.onReset()
    }
  }

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-dark-1 flex items-center justify-center p-4">
          <GlassCard className="max-w-2xl w-full">
            <div className="text-center space-y-6">
              {/* Error Icon */}
              <div className="flex justify-center">
                <div className="p-4 rounded-full bg-ios-red/10">
                  <AlertTriangle className="w-16 h-16 text-ios-red" />
                </div>
              </div>

              {/* Error Message */}
              <div>
                <h1 className="text-3xl font-bold mb-2">Something went wrong</h1>
                <p className="text-ios-gray-2 text-lg">
                  We encountered an unexpected error. Please try again.
                </p>
              </div>

              {/* Error Details (in development) */}
              {import.meta.env.DEV && this.state.error && (
                <div className="bg-dark-3 rounded-xl p-4 text-left">
                  <p className="text-sm font-mono text-ios-red mb-2">
                    {this.state.error.toString()}
                  </p>
                  {this.state.errorInfo && (
                    <details className="mt-2">
                      <summary className="text-sm text-ios-gray-2 cursor-pointer hover:text-white">
                        Stack trace
                      </summary>
                      <pre className="text-xs text-ios-gray-2 mt-2 overflow-x-auto">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </details>
                  )}
                </div>
              )}

              {/* Reset Button */}
              <button
                onClick={this.handleReset}
                className="ios-button-primary flex items-center gap-2 mx-auto"
              >
                <RefreshCw className="w-5 h-5" />
                Try Again
              </button>

              {/* Additional Help */}
              <p className="text-sm text-ios-gray-2">
                If the problem persists, please contact support or refresh the page.
              </p>
            </div>
          </GlassCard>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
