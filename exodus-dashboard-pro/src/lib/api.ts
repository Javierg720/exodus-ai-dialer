const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class APIClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }

  // Auth
  async login(username: string, password: string) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
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
    const formData = new FormData()
    formData.append('file', file)
    if (campaignId) formData.append('campaign_id', campaignId.toString())

    const response = await fetch(`${API_BASE}/leads/import`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Import Error: ${response.statusText}`)
    }

    return response.json()
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
      body: JSON.stringify({ note }),
    })
  }

  async scheduleCallback(id: number, callbackTime: string) {
    return this.request(`/leads/${id}/callback`, {
      method: 'POST',
      body: JSON.stringify({ callback_time: callbackTime }),
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

  async restartBot(botId: number) {
    return this.request(`/bots/${botId}/restart`, {
      method: 'POST',
    })
  }

  async startBot(botId: number) {
    return this.request(`/bots/${botId}/start`, {
      method: 'POST',
    })
  }

  async stopBot(botId: number) {
    return this.request(`/bots/${botId}/stop`, {
      method: 'POST',
    })
  }

  async restartBotPool() {
    return this.request('/bots/pool/restart', {
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
    const response = await fetch(`${API_BASE}/dnc/export`)
    if (!response.ok) {
      throw new Error(`Export Error: ${response.statusText}`)
    }
    return response.blob()
  }

  // Dispositions
  async getDispositions() {
    return this.request('/dispositions')
  }
}

export const api = new APIClient()
