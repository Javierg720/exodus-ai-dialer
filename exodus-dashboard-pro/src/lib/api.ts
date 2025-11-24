import toast from 'react-hot-toast'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string,
    public details?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

class APIClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      })

      if (!response.ok) {
        // Try to parse error response body for detailed error message
        let errorMessage = response.statusText
        let errorDetails = null

        try {
          const errorData = await response.json()
          // Check for common error response formats
          if (errorData.detail) {
            errorMessage = typeof errorData.detail === 'string' 
              ? errorData.detail 
              : JSON.stringify(errorData.detail)
          } else if (errorData.message) {
            errorMessage = errorData.message
          } else if (errorData.error) {
            errorMessage = errorData.error
          }
          errorDetails = errorData
        } catch {
          // If response is not JSON, try to get text
          try {
            const errorText = await response.text()
            if (errorText) {
              errorMessage = errorText
            }
          } catch {
            // Keep default statusText
          }
        }

        // Create user-friendly error messages based on status code
        let userFriendlyMessage = errorMessage

        if (response.status === 404) {
          userFriendlyMessage = 'Resource not found'
        } else if (response.status === 401) {
          userFriendlyMessage = 'Authentication required. Please log in.'
        } else if (response.status === 403) {
          userFriendlyMessage = 'You do not have permission to perform this action'
        } else if (response.status === 500) {
          userFriendlyMessage = 'Server error. Please try again later.'
        } else if (response.status === 503) {
          userFriendlyMessage = 'Service temporarily unavailable. Please try again later.'
        } else if (response.status >= 400 && response.status < 500) {
          userFriendlyMessage = errorMessage || 'Invalid request. Please check your input.'
        } else if (response.status >= 500) {
          userFriendlyMessage = 'Server error. Please contact support if this persists.'
        }

        const apiError = new APIError(
          userFriendlyMessage,
          response.status,
          response.statusText,
          errorDetails
        )
        toast.error(userFriendlyMessage)
        throw apiError
      }

      return response.json()
    } catch (error) {
      // Handle network errors
      if (error instanceof APIError) {
        throw error
      }
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        const networkError = new APIError(
          'Unable to connect to server. Please check your connection.',
          0,
          'Network Error'
        )
        toast.error('Unable to connect to server. Please check your connection.')
        throw networkError
      }

      const unexpectedError = new APIError(
        'An unexpected error occurred. Please try again.',
        0,
        'Unknown Error',
        error
      )
      toast.error('An unexpected error occurred. Please try again.')
      throw unexpectedError
    }
  }

  // Auth
  async login(username: string, password: string) {
    try {
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      })
      
      if (!response.ok) {
        const errorMessage = `API Error: ${response.statusText}`
        toast.error(errorMessage)
        throw new Error(errorMessage)
      }
      
      return response.json()
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Login failed'
      if (!(error instanceof Error) || !error.message.includes('API Error')) {
        toast.error(errorMsg)
      }
      throw error
    }
  }

  // Stats
  async getStats() {
    return this.request('/stats')
  }

  async getDialerStats() {
    return this.request('/dialer/stats')
  }

  // Campaigns
  async getCampaigns(): Promise<any[]> {
    return this.request<any[]>('/campaigns')
  }

  async getActiveCampaigns() {
    return this.request('/campaigns/active')
  }

  async getCampaign(id: number) {
    return this.request(`/campaigns/${id}`)
  }

  async createCampaign(data: any) {
    return this.request('/campaigns', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateCampaign(id: number, data: any) {
    return this.request(`/campaigns/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteCampaign(id: number) {
    return this.request(`/campaigns/${id}`, {
      method: 'DELETE',
    })
  }

  async startCampaign(id: number) {
    return this.request(`/campaigns/${id}/start`, {
      method: 'POST',
    })
  }

  async pauseCampaign(id: number) {
    return this.request(`/campaigns/${id}/pause`, {
      method: 'POST',
    })
  }

  async getCampaignStats(id: number) {
    return this.request(`/campaigns/${id}/stats`)
  }

  async getCampaignLeads(id: number) {
    return this.request(`/campaigns/${id}/leads`)
  }

  async resetCampaignLeads(id: number) {
    return this.request(`/campaigns/${id}/reset-leads`, {
      method: 'POST',
    })
  }

  // Leads
  async getLeads(): Promise<any[]> {
    return this.request<any[]>('/leads')
  }

  async createLead(data: any) {
    return this.request('/leads', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async bulkCreateLeads(data: any[]) {
    return this.request('/leads/bulk', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async importLeads(file: File, campaignId?: number) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (campaignId) formData.append('campaign_id', campaignId.toString())

      const response = await fetch(`${API_BASE}/leads/import`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        let errorMessage = 'Failed to import leads'
        try {
          const errorData = await response.json()
          if (errorData.detail) {
            errorMessage = typeof errorData.detail === 'string' 
              ? errorData.detail 
              : JSON.stringify(errorData.detail)
          } else if (errorData.message) {
            errorMessage = errorData.message
          }
        } catch {
          errorMessage = response.statusText || errorMessage
        }

        const importError = new APIError(
          errorMessage,
          response.status,
          response.statusText
        )
        toast.error(errorMessage)
        throw importError
      }

      return response.json()
    } catch (error) {
      if (error instanceof APIError) {
        throw error
      }
      const importError = new APIError(
        'Failed to import leads. Please check the file format and try again.',
        0,
        'Import Error',
        error
      )
      toast.error('Failed to import leads. Please check the file format and try again.')
      throw importError
    }
  }

  async updateLeadStatus(id: number, status: string) {
    return this.request(`/leads/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    })
  }

  async updateLeadDisposition(id: number, disposition: string) {
    return this.request(`/leads/${id}/disposition`, {
      method: 'PUT',
      body: JSON.stringify({ disposition }),
    })
  }

  async addLeadNote(id: number, note: string) {
    return this.request(`/leads/${id}/notes`, {
      method: 'POST',
      body: JSON.stringify({ notes: note }),
    })
  }

  async scheduleCallback(id: number, callbackTime: string) {
    return this.request(`/leads/${id}/callback`, {
      method: 'POST',
      body: JSON.stringify({ callback_date: callbackTime }),
    })
  }

  async deleteLead(id: number) {
    return this.request(`/leads/${id}`, {
      method: 'DELETE',
    })
  }

  // Calls
  async getActiveCalls(): Promise<any[]> {
    return this.request<any[]>('/calls/active')
  }

  async getCallHistory(): Promise<any[]> {
    return this.request<any[]>('/calls/history')
  }

  async originateCall(phoneNumber: string, campaignId?: number) {
    return this.request('/calls/originate', {
      method: 'POST',
      body: JSON.stringify({ phone_number: phoneNumber, campaign_id: campaignId }),
    })
  }

  async hangupCall(channel: string) {
    return this.request(`/calls/${encodeURIComponent(channel)}/hangup`, {
      method: 'POST',
    })
  }

  async monitorCall(channel: string, action: 'listen' | 'barge') {
    return this.request('/calls/monitor', {
      method: 'POST',
      body: JSON.stringify({ channel: channel, action: action, supervisor_phone: 'supervisor-web' }),
    })
  }

  getRecording(callUuid: string): string {
    return `${API_BASE}/api/recording/${callUuid}`
  }

  // Bots
  async getBots() {
    return this.request('/bots')
  }

  async getBotsStatus() {
    return this.request('/bots')
  }

  async restartBot(botPort: number) {
    return this.request(`/bots/${botPort}/restart`, {
      method: 'POST',
    })
  }

  async startBot(botPort: number) {
    return this.request(`/bots/${botPort}/start`, {
      method: 'POST',
    })
  }

  async stopBot(botPort: number) {
    return this.request(`/bots/${botPort}/stop`, {
      method: 'POST',
    })
  }

  async restartBotPool() {
    return this.request('/bots/pool/restart', {
      method: 'POST',
    })
  }

  async startAllBots() {
    return this.request('/bots/pool/start', {
      method: 'POST',
    })
  }

  async stopAllBots() {
    return this.request('/bots/pool/stop', {
      method: 'POST',
    })
  }

  async rebootSystem() {
    return this.request('/system/reboot', {
      method: 'POST',
    })
  }

  // DNC
  async getDNC(): Promise<any[]> {
    return this.request<any[]>('/dnc')
  }

  async addToDNC(phoneNumber: string, reason?: string) {
    return this.request('/dnc', {
      method: 'POST',
      body: JSON.stringify({ phone_number: phoneNumber, reason }),
    })
  }

  async checkDNC(phoneNumber: string) {
    return this.request(`/dnc/${phoneNumber}`)
  }

  async removeDNC(phoneNumber: string) {
    return this.request(`/dnc/${phoneNumber}`, {
      method: 'DELETE',
    })
  }

  async importDNC(phoneNumbers: string[], reason?: string) {
    return this.request('/dnc/import', {
      method: 'POST',
      body: JSON.stringify({ phone_numbers: phoneNumbers, reason }),
    })
  }

  async exportDNC(): Promise<Blob> {
    try {
      const response = await fetch(`${API_BASE}/dnc/export`)
      if (!response.ok) {
        const exportError = new APIError(
          'Failed to export DNC list',
          response.status,
          response.statusText
        )
        toast.error('Failed to export DNC list')
        throw exportError
      }
      return response.blob()
    } catch (error) {
      if (error instanceof APIError) {
        throw error
      }
      const exportError = new APIError(
        'Failed to export DNC list. Please try again.',
        0,
        'Export Error',
        error
      )
      toast.error('Failed to export DNC list. Please try again.')
      throw exportError
    }
  }

  // Dispositions
  async getDispositions() {
    return this.request('/dispositions')
  }
}

export const api = new APIClient()
