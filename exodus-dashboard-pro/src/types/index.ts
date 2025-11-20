export interface Campaign {
  id: number
  name: string
  status: 'active' | 'paused' | 'completed'
  dial_ratio: number
  created_at: string
  total_leads?: number
  dialed?: number
  contacted?: number
  converted?: number
  time_connected?: number
  calls_made_today?: number
  successful_contacts_today?: number
  conversion_rate?: number
  avg_call_duration?: number
  description?: string
  dial_method?: string
  max_agents?: number
}

export interface Lead {
  id: number
  campaign_id: number
  phone_number: string
  first_name?: string
  last_name?: string
  email?: string
  status: 'new' | 'dialing' | 'contacted' | 'failed' | 'dnc' | 'callback'
  disposition?: string
  notes?: string
  created_at: string
  last_called?: string
}

export interface Call {
  id: string
  uuid: string
  campaign_id?: number
  lead_id?: number
  phone_number: string
  bot_port?: number
  status: 'ringing' | 'answered' | 'completed' | 'failed' | 'busy' | 'no-answer'
  duration?: number
  recording_url?: string
  transcript?: string
  transcription_text?: string
  summary?: string
  sentiment?: string
  key_points?: string
  disposition?: string
  started_at: string
  ended_at?: string
}

export interface LiveCall extends Call {
  agent_name?: string
  transcription_stream?: string[]
  waveform_active?: boolean
}

export interface Bot {
  port: number
  status: 'idle' | 'busy' | 'offline'
  current_call_id?: string
  calls_handled: number
}

export interface Stats {
  total_campaigns: number
  active_campaigns: number
  total_leads: number
  new_leads: number
  total_calls_today: number
  active_calls: number
  contacted_today: number
  conversion_rate: number
  average_call_duration: number
  bots_idle: number
  bots_busy: number
  bots_total: number
}

export interface DNCEntry {
  phone_number: string
  added_at: string
  reason?: string
}

export interface Disposition {
  code: string
  label: string
  category: 'success' | 'callback' | 'dnc' | 'failed'
}
