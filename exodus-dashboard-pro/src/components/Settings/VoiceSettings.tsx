import { useState, useEffect } from 'react'
import GlassCard from '../GlassCard'
import { Mic, Volume2, Zap, FileText, Save, Play } from 'lucide-react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'

const AMERICAN_EDGE_VOICES = [
  { value: "en-US-AriaNeural", label: "Aria – Warm & Natural (F)" },
  { value: "en-US-JennyNeural", label: "Jenny – Bright & Friendly (F)" },
  { value: "en-US-SaraNeural", label: "Sara – Calm & Professional (F)" },
  { value: "en-US-GuyNeural", label: "Guy – Deep & Confident (M)" },
  { value: "en-US-AndrewNeural", label: "Andrew – Energetic & Clear (M)" },
  { value: "en-US-EmmaNeural", label: "Emma – Soft & Engaging (F)" },
  { value: "en-US-BrianNeural", label: "Brian – Friendly & Versatile (M)" },
  { value: "en-US-AvaNeural", label: "Ava – Modern & Crisp (F)" },
  { value: "en-US-AvaMultilingualNeural", label: "Ava Multilingual – Global (F)" },
  { value: "en-US-ChristopherNeural", label: "Christopher – Strong & Authoritative (M)" },
  { value: "en-US-MichelleNeural", label: "Michelle – Warm & Expressive (F)" },
  { value: "en-US-EricNeural", label: "Eric – Professional & Clear (M)" },
  { value: "en-US-JacobNeural", label: "Jacob – Youthful & Casual (M)" },
  { value: "en-US-JaneNeural", label: "Jane – Reliable & Steady (F)" },
  { value: "en-US-JasonNeural", label: "Jason – Energetic & Bold (M)" },
  { value: "en-US-NancyNeural", label: "Nancy – Cheerful & Upbeat (F)" },
  { value: "en-US-TonyNeural", label: "Tony – Smooth & Charismatic (M)" },
]

const DYNAMIC_VARIABLES = [
  { var: "{{first_name}}", desc: "Lead's first name" },
  { var: "{{last_name}}", desc: "Lead's last name" },
  { var: "{{full_name}}", desc: "Full name" },
  { var: "{{company}}", desc: "Company name" },
  { var: "{{phone}}", desc: "Lead's phone" },
  { var: "{{city}}", desc: "City" },
  { var: "{{state}}", desc: "State" },
  { var: "{{custom1}}", desc: "Custom field 1" },
  { var: "{{custom2}}", desc: "Custom field 2" },
]

interface VoiceSettingsProps {
  campaignId?: number
}

export default function VoiceSettings({ campaignId }: VoiceSettingsProps) {
  const [voice, setVoice] = useState("en-US-AvaMultilingualNeural")
  const [speed, setSpeed] = useState(1.3)
  const [pitch, setPitch] = useState(0)
  const [interruptSensitivity, setInterruptSensitivity] = useState(0.5)
  const [loading, setLoading] = useState(false)
  const [previewing, setPreviewing] = useState(false)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    if (campaignId) {
      fetchVoiceSettings()
    }
  }, [campaignId])

  const fetchVoiceSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/campaigns/${campaignId}/voice-settings`)
      const data = await response.json()
      if (data.status === 'success' && data.voice_settings) {
        setVoice(data.voice_settings.voice || "en-US-AvaMultilingualNeural")
        setSpeed(data.voice_settings.speed || 1.3)
        setPitch(data.voice_settings.pitch || 0)
        setInterruptSensitivity(data.voice_settings.interrupt_sensitivity || 0.5)
      }
    } catch (error) {
      console.error('Failed to fetch voice settings:', error)
    }
  }

  const saveVoiceSettings = async () => {
    if (!campaignId) {
      toast.error('Please select a campaign first')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/campaigns/${campaignId}/voice-settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          voice,
          speed,
          pitch,
          interrupt_sensitivity: interruptSensitivity
        })
      })
      const data = await response.json()
      if (data.status === 'success') {
        toast.success('Voice settings saved successfully!')
      } else {
        toast.error(`Error: ${data.message}`)
      }
    } catch (error) {
      console.error('Failed to save voice settings:', error)
      toast.error('Failed to save settings')
    } finally {
      setLoading(false)
    }
  }

  const handlePreview = async () => {
    setPreviewing(true)
    const text = "Hello, this is a preview of the voice you selected. Thank you for testing Exodus Dialer."
    const ssml = `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  <voice name="${voice}">
    <prosody rate="${speed.toFixed(1)}" pitch="${pitch > 0 ? '+' : ''}${pitch}Hz">
      ${text}
    </prosody>
  </voice>
</speak>`.trim()

    try {
      const resp = await fetch(`${API_URL}/tts/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ssml })
      })

      if (!resp.ok) {
        throw new Error('TTS preview failed')
      }

      const audioBlob = await resp.blob()
      const url = URL.createObjectURL(audioBlob)
      const audio = new Audio(url)
      audio.play()
      toast.success('Playing preview...')
    } catch (err) {
      console.error('Preview error:', err)
      toast.error('Preview failed — check TTS server')
    } finally {
      setPreviewing(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Live Preview Button */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-6 text-white shadow-2xl"
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold mb-1">🎤 Live Voice Preview</h3>
            <p className="text-white/90">Click below to hear exactly how your bot will sound</p>
          </div>
          <button
            onClick={handlePreview}
            disabled={previewing}
            className="bg-white text-purple-600 hover:bg-white/90 disabled:bg-white/50 disabled:cursor-not-allowed px-8 py-4 rounded-xl font-semibold flex items-center gap-3 shadow-lg transition-all transform hover:scale-105"
          >
            <Play className="w-6 h-6" fill="currentColor" />
            {previewing ? 'Playing...' : 'Play Preview'}
          </button>
        </div>
      </motion.div>

      {/* Voice Selection */}
      <GlassCard>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Mic className="w-5 h-5 text-ios-blue" />
          Voice Selection (Edge TTS – American)
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-ios-gray-2 mb-2">Voice</label>
            <select
              value={voice}
              onChange={(e) => setVoice(e.target.value)}
              className="w-full bg-dark-2 border border-dark-3 rounded-lg px-4 py-3 text-white focus:border-ios-blue focus:outline-none transition-colors"
            >
              {AMERICAN_EDGE_VOICES.map(v => (
                <option key={v.value} value={v.value}>
                  {v.label}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            {/* Speed Control */}
            <div className="p-4 bg-dark-2/50 rounded-xl border border-dark-3">
              <label className="block text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <Volume2 className="w-4 h-4 text-ios-blue" />
                Speed
              </label>
              <div className="text-3xl font-bold text-ios-blue mb-4">
                {speed.toFixed(1)}×
              </div>
              <input
                type="range"
                value={speed}
                onChange={(e) => setSpeed(Number(e.target.value))}
                min={0.5}
                max={2.0}
                step={0.1}
                className="w-full h-2 bg-dark-3 rounded-lg appearance-none cursor-pointer accent-ios-blue"
              />
              <div className="flex justify-between text-xs text-ios-gray-2 mt-2">
                <span>0.5x</span>
                <span>2.0x</span>
              </div>
            </div>

            {/* Pitch Control */}
            <div className="p-4 bg-dark-2/50 rounded-xl border border-dark-3">
              <label className="block text-sm font-semibold text-white mb-3">
                Pitch
              </label>
              <div className="text-3xl font-bold text-purple-400 mb-4">
                {pitch > 0 ? '+' : ''}{pitch}Hz
              </div>
              <input
                type="range"
                value={pitch}
                onChange={(e) => setPitch(Number(e.target.value))}
                min={-100}
                max={100}
                step={10}
                className="w-full h-2 bg-dark-3 rounded-lg appearance-none cursor-pointer accent-purple-400"
              />
              <div className="flex justify-between text-xs text-ios-gray-2 mt-2">
                <span>-100Hz</span>
                <span>+100Hz</span>
              </div>
            </div>

            {/* Interrupt Sensitivity */}
            <div className="p-4 bg-dark-2/50 rounded-xl border border-dark-3">
              <label className="block text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <Zap className="w-4 h-4 text-ios-green" />
                Interrupt
              </label>
              <div className="text-3xl font-bold text-ios-green mb-4">
                {interruptSensitivity.toFixed(2)}
              </div>
              <input
                type="range"
                value={interruptSensitivity}
                onChange={(e) => setInterruptSensitivity(Number(e.target.value))}
                min={0.1}
                max={1.0}
                step={0.05}
                className="w-full h-2 bg-dark-3 rounded-lg appearance-none cursor-pointer accent-ios-green"
              />
              <p className="text-xs text-ios-gray-2 mt-2">
                Lower = stops faster when lead speaks
              </p>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Dynamic Variables */}
      <GlassCard>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-ios-green" />
          Dynamic Variables (Use in Prompts)
        </h3>
        <div className="space-y-4">
          <p className="text-sm text-ios-gray-2">
            Insert these variables in your bot prompts to personalize conversations
          </p>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {DYNAMIC_VARIABLES.map(item => (
              <motion.div
                key={item.var}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="bg-dark-2/50 p-4 rounded-lg border border-dark-3 hover:border-ios-blue transition-colors cursor-pointer"
                onClick={() => {
                  navigator.clipboard.writeText(item.var)
                  toast.success(`Copied ${item.var}`)
                }}
              >
                <code className="text-sm font-semibold font-mono text-ios-blue">
                  {item.var}
                </code>
                <p className="text-xs text-ios-gray-2 mt-1">{item.desc}</p>
              </motion.div>
            ))}
          </div>

          {/* Example Usage */}
          <div className="mt-6 p-6 bg-gradient-to-r from-ios-blue/10 to-purple-500/10 rounded-xl border border-ios-blue/30">
            <p className="text-sm font-semibold mb-3 text-ios-blue">Example Prompt:</p>
            <div className="bg-dark-2 p-4 rounded-lg font-mono text-sm">
              <p className="text-white leading-relaxed">
                Hi <span className="text-ios-green font-bold">{'{{first_name}}'}</span>, 
                this is Sarah from <span className="text-ios-green font-bold">{'{{company}}'}</span>. 
                How are you today?
              </p>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Save Button */}
      <div className="flex items-center gap-4">
        <button
          onClick={saveVoiceSettings}
          disabled={loading || !campaignId}
          className="flex-1 ios-button bg-ios-blue hover:bg-ios-blue/90 text-white flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed py-4 text-lg font-semibold rounded-xl transition-all transform hover:scale-[1.02]"
        >
          <Save className="w-5 h-5" />
          {loading ? 'Saving...' : 'Save Voice Settings'}
        </button>
      </div>
    </div>
  )
}
