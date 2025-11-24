import GlassCard from '../components/GlassCard'
import { motion } from 'framer-motion'
import { useStore } from '../lib/store'
import { Moon, Sun, Bell, Shield, Database, Settings as SettingsIcon, Save, Power } from 'lucide-react'
import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import VoiceSettings from '../components/Settings/VoiceSettings'

interface SystemSettings {
  dial_ratio: number
  max_dial_ratio: number
  drop_rate_limit: number
  call_time_start: string
  call_time_end: string
  max_agents: number
  stt_provider: string
  enable_recording: number
  timezone: string
  max_concurrent_calls: number
}

interface CampaignSettings {
  id: number
  name: string
  dial_method: string
  dial_ratio: number
  max_dial_ratio: number
  drop_rate_limit: number
  call_time_start: string
  call_time_end: string
  max_agents: number
  stt_provider: string
  enable_recording: number
  status: string
}

export default function Settings() {
  const { darkMode, toggleDarkMode } = useStore()
  const [systemSettings, setSystemSettings] = useState<SystemSettings | null>(null)
  const [campaigns, setCampaigns] = useState<CampaignSettings[]>([])
  const [selectedCampaign, setSelectedCampaign] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [saveMessage, setSaveMessage] = useState('')
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/campaigns`)
      const data = await response.json()
      if (data.status === 'success') {
        const availableCampaigns = data.campaigns || []
        setCampaigns(availableCampaigns)
        if (availableCampaigns.length > 0) {
          setSelectedCampaign(availableCampaigns[0].id)
        }
      }
    } catch (error) {
      console.error('Failed to fetch settings:', error)
      setCampaigns([])
    } finally {
      setLoading(false)
    }
  }

  const updateCampaignSetting = async (campaignId: number, field: string, value: any) => {
    try {
      const response = await fetch(`${API_URL}/settings/campaign/${campaignId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [field]: value })
      })
      const data = await response.json()
      if (data.status === 'success') {
        setSaveMessage('Settings saved successfully')
        setTimeout(() => setSaveMessage(''), 3000)
        await fetchSettings()
      } else {
        setSaveMessage(`Error: ${data.message}`)
        setTimeout(() => setSaveMessage(''), 5000)
      }
    } catch (error) {
      console.error('Failed to update setting:', error)
      setSaveMessage('Failed to save settings')
      setTimeout(() => setSaveMessage(''), 5000)
    }
  }

  const selectedCampaignData = campaigns?.find(c => c.id === selectedCampaign)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-ios-gray-2">Loading settings...</div>
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
          <h1 className="text-4xl font-bold">Settings</h1>
          <p className="text-ios-gray-2 mt-2">Manage your Exodus Dialer preferences</p>
        </div>
        {saveMessage && (
          <div className="bg-ios-green/20 text-ios-green px-4 py-2 rounded-lg">
            {saveMessage}
          </div>
        )}
      </div>

      {/* Campaign Selector */}
      {campaigns.length > 0 && (
        <GlassCard>
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <SettingsIcon className="w-5 h-5" />
            Campaign Settings
          </h3>
          <select
            value={selectedCampaign || ''}
            onChange={(e) => setSelectedCampaign(Number(e.target.value))}
            className="w-full bg-dark-2 border border-dark-3 rounded-lg px-4 py-2 text-white"
          >
            {campaigns.map(campaign => (
              <option key={campaign.id} value={campaign.id}>
                {campaign.name}
              </option>
            ))}
          </select>
        </GlassCard>
      )}

      {/* Dialer Settings */}
      {selectedCampaignData && (
        <GlassCard>
          <h3 className="text-lg font-semibold mb-4">Dialer Configuration</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-ios-gray-2 mb-2">Dial Method</label>
              <select
                value={selectedCampaignData.dial_method}
                onChange={(e) => updateCampaignSetting(selectedCampaignData.id, 'dial_method', e.target.value)}
                className="w-full bg-dark-2 border border-dark-3 rounded-lg px-4 py-2 text-white"
              >
                <option value="PROGRESSIVE">Progressive</option>
                <option value="PREDICTIVE">Predictive</option>
                <option value="POWER">Power</option>
                <option value="PREVIEW">Preview</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-ios-gray-2 mb-2">
                  Dial Ratio: {selectedCampaignData.dial_ratio}
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="0.5"
                  value={selectedCampaignData.dial_ratio}
                  onChange={(e) => updateCampaignSetting(selectedCampaignData.id, 'dial_ratio', Number(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm text-ios-gray-2 mb-2">
                  Drop Rate Limit: {(selectedCampaignData.drop_rate_limit * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="0.1"
                  step="0.01"
                  value={selectedCampaignData.drop_rate_limit}
                  onChange={(e) => updateCampaignSetting(selectedCampaignData.id, 'drop_rate_limit', Number(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-ios-gray-2 mb-2">Call Time Start</label>
                <input
                  type="time"
                  value={selectedCampaignData.call_time_start}
                  onChange={(e) => updateCampaignSetting(selectedCampaignData.id, 'call_time_start', e.target.value)}
                  className="w-full bg-dark-2 border border-dark-3 rounded-lg px-4 py-2 text-white"
                />
              </div>
              <div>
                <label className="block text-sm text-ios-gray-2 mb-2">Call Time End</label>
                <input
                  type="time"
                  value={selectedCampaignData.call_time_end}
                  onChange={(e) => updateCampaignSetting(selectedCampaignData.id, 'call_time_end', e.target.value)}
                  className="w-full bg-dark-2 border border-dark-3 rounded-lg px-4 py-2 text-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-ios-gray-2 mb-2">
                Max Agents: {selectedCampaignData.max_agents}
              </label>
              <input
                type="range"
                min="1"
                max="100"
                value={selectedCampaignData.max_agents}
                onChange={(e) => updateCampaignSetting(selectedCampaignData.id, 'max_agents', Number(e.target.value))}
                className="w-full"
              />
            </div>
          </div>
        </GlassCard>
      )}

      {/* Voice Settings */}
      {selectedCampaignData && (
        <VoiceSettings campaignId={selectedCampaignData.id} />
      )}

      {/* STT & Recording */}
      {selectedCampaignData && (
        <GlassCard>
          <h3 className="text-lg font-semibold mb-4">Speech & Recording</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-ios-gray-2 mb-2">STT Provider</label>
              <select
                value={selectedCampaignData.stt_provider}
                onChange={(e) => updateCampaignSetting(selectedCampaignData.id, 'stt_provider', e.target.value)}
                className="w-full bg-dark-2 border border-dark-3 rounded-lg px-4 py-2 text-white"
              >
                <option value="deepgram">Deepgram</option>
                <option value="assemblyai">AssemblyAI</option>
                <option value="google">Google Cloud</option>
                <option value="azure">Azure</option>
              </select>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Enable Recording</p>
                <p className="text-sm text-ios-gray-2">Record all calls for this campaign</p>
              </div>
              <button
                onClick={() => updateCampaignSetting(selectedCampaignData.id, 'enable_recording', selectedCampaignData.enable_recording ? 0 : 1)}
                className={`relative w-14 h-8 rounded-full transition-colors ${
                  selectedCampaignData.enable_recording ? 'bg-ios-blue' : 'bg-dark-3'
                }`}
              >
                <motion.div
                  animate={{ x: selectedCampaignData.enable_recording ? 24 : 2 }}
                  className="absolute top-1 w-6 h-6 bg-white rounded-full"
                />
              </button>
            </div>
          </div>
        </GlassCard>
      )}

      {/* System Reboot */}
      <GlassCard>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Power className="w-5 h-5" />
          System Control
        </h3>
        <div className="space-y-3">
          <p className="text-sm text-ios-gray-2">
            Restart the dialer API and all bot instances. This will briefly interrupt active calls.
          </p>
          <button 
            onClick={async () => {
              if (!window.confirm('Are you sure you want to reboot the system? This will restart all bots and the API.')) {
                return
              }
              setSaveMessage('Rebooting system...')
              try {
                await api.rebootSystem()
                setSaveMessage('System reboot initiated. Please wait...')
                setTimeout(() => {
                  window.location.reload()
                }, 5000)
              } catch (error) {
                setSaveMessage('Reboot initiated - refreshing in 5 seconds...')
                setTimeout(() => {
                  window.location.reload()
                }, 5000)
              }
            }}
            className="w-full ios-button bg-ios-orange hover:bg-ios-orange/90 text-white flex items-center justify-center gap-2"
          >
            <Power className="w-5 h-5" />
            Reboot System
          </button>
        </div>
      </GlassCard>

      {/* Appearance */}
      <GlassCard>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          {darkMode ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
          Appearance
        </h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">Dark Mode</p>
            <p className="text-sm text-ios-gray-2">Use dark theme across the app</p>
          </div>
          <button
            onClick={toggleDarkMode}
            className={`relative w-14 h-8 rounded-full transition-colors ${
              darkMode ? 'bg-ios-blue' : 'bg-dark-3'
            }`}
          >
            <motion.div
              animate={{ x: darkMode ? 24 : 2 }}
              className="absolute top-1 w-6 h-6 bg-white rounded-full"
            />
          </button>
        </div>
      </GlassCard>

      {/* Notifications */}
      <GlassCard>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Notifications
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Call Notifications</p>
              <p className="text-sm text-ios-gray-2">Get notified of new calls</p>
            </div>
            <button className="relative w-14 h-8 rounded-full bg-ios-blue">
              <motion.div
                animate={{ x: 24 }}
                className="absolute top-1 w-6 h-6 bg-white rounded-full"
              />
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Campaign Alerts</p>
              <p className="text-sm text-ios-gray-2">Alert when campaigns complete</p>
            </div>
            <button className="relative w-14 h-8 rounded-full bg-ios-blue">
              <motion.div
                animate={{ x: 24 }}
                className="absolute top-1 w-6 h-6 bg-white rounded-full"
              />
            </button>
          </div>
        </div>
      </GlassCard>

      {/* System Info */}
      <GlassCard>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Database className="w-5 h-5" />
          System Information
        </h3>
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-ios-gray-2">API Endpoint</span>
            <span className="font-mono">{import.meta.env.VITE_API_URL || 'http://localhost:8000'}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-ios-gray-2">Version</span>
            <span>1.0.0</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-ios-gray-2">Build</span>
            <span>Production</span>
          </div>
        </div>
      </GlassCard>

      {/* Security */}
      <GlassCard>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5" />
          Security
        </h3>
        <div className="space-y-3">
          <button className="w-full ios-button-secondary text-left">
            Change Password
          </button>
          <button className="w-full ios-button-secondary text-left">
            Two-Factor Authentication
          </button>
          <button className="w-full ios-button bg-ios-red hover:bg-ios-red/90 text-white">
            Sign Out
          </button>
        </div>
      </GlassCard>
    </motion.div>
  )
}
