import { useState, useEffect } from 'react';
import GlassCard from './GlassCard';
import { Volume2, Settings } from 'lucide-react';

const AMERICAN_EDGE_VOICES = [
  { value: "en-US-AriaNeural", label: "Aria – Warm & Natural (F)" },
  { value: "en-US-JennyNeural", label: "Jenny – Bright & Friendly (F)" },
  { value: "en-US-SaraNeural", label: "Sara – Calm & Professional (F)" },
  { value: "en-US-GuyNeural", label: "Guy – Deep & Confident (M)" },
  { value: "en-US-AndrewNeural", label: "Andrew – Energetic (M)" },
  { value: "en-US-EmmaNeural", label: "Emma – Soft & Engaging (F)" },
  { value: "en-US-BrianNeural", label: "Brian – Friendly & Versatile (M)" },
  { value: "en-US-AvaNeural", label: "Ava – Modern & Crisp (F)" },
  { value: "en-US-ChristopherNeural", label: "Christopher – Authoritative (M)" },
  { value: "en-US-MichelleNeural", label: "Michelle – Warm & Expressive (F)" },
];

const DYNAMIC_VARS = [
  { var: "{{first_name}}", desc: "Lead's first name" },
  { var: "{{last_name}}", desc: "Lead's last name" },
  { var: "{{full_name}}", desc: "Full name" },
  { var: "{{company}}", desc: "Company name" },
  { var: "{{phone}}", desc: "Lead's phone" },
  { var: "{{city}}", desc: "City" },
  { var: "{{state}}", desc: "State" },
];

export default function VoiceSettings({ campaignId }: { campaignId: number }) {
  const [voice, setVoice] = useState("en-US-AriaNeural");
  const [speed, setSpeed] = useState(1.0);
  const [pitch, setPitch] = useState(0);
  const [interruptSensitivity, setInterruptSensitivity] = useState(0.5);

  return (
    <div className="space-y-6">
      <GlassCard>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Volume2 className="w-5 h-5" />
          Voice Selection (Edge TTS)
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-ios-gray-2 mb-2">Voice</label>
            <select 
              value={voice} 
              onChange={(e) => setVoice(e.target.value)}
              className="w-full bg-dark-2 border border-dark-3 rounded-lg px-4 py-2 text-white"
            >
              {AMERICAN_EDGE_VOICES.map(v => (
                <option key={v.value} value={v.value}>{v.label}</option>
              ))}
            </select>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm text-ios-gray-2 mb-2">
                Speed: {speed.toFixed(2)}x
              </label>
              <input 
                type="range" 
                value={speed} 
                onChange={(e) => setSpeed(parseFloat(e.target.value))}
                min="0.5" 
                max="2.0" 
                step="0.1"
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm text-ios-gray-2 mb-2">
                Pitch: {pitch > 0 ? '+' : ''}{pitch}Hz
              </label>
              <input 
                type="range" 
                value={pitch} 
                onChange={(e) => setPitch(parseInt(e.target.value))}
                min="-100" 
                max="100" 
                step="10"
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm text-ios-gray-2 mb-2">
                Interrupt Sensitivity: {interruptSensitivity.toFixed(2)}
              </label>
              <input 
                type="range" 
                value={interruptSensitivity} 
                onChange={(e) => setInterruptSensitivity(parseFloat(e.target.value))}
                min="0.1" 
                max="1.0" 
                step="0.05"
                className="w-full"
              />
              <p className="text-xs text-ios-gray-3 mt-1">Lower = bot stops faster when lead speaks</p>
            </div>
          </div>
        </div>
      </GlassCard>

      <GlassCard>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Settings className="w-5 h-5" />
          Dynamic Variables
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
          {DYNAMIC_VARS.map(item => (
            <div key={item.var} className="bg-dark-2 p-3 rounded-lg">
              <code className="text-sm font-mono bg-ios-blue/10 px-2 py-1 rounded text-ios-blue">
                {item.var}
              </code>
              <p className="text-xs text-ios-gray-2 mt-1">{item.desc}</p>
            </div>
          ))}
        </div>
        
        <div className="p-4 bg-ios-blue/5 rounded-lg border border-ios-blue/20">
          <p className="text-sm text-ios-gray-2 mb-2"><strong>Example Prompt:</strong></p>
          <p className="text-sm font-mono bg-dark-2 p-3 rounded">
            Hi {"{"}{"{"}}first_name{"}"}{"}"}, this is Sarah from {"{"}{"{"}}company{"}"}{"}"}. How are you today?
          </p>
        </div>
      </GlassCard>

      <button className="w-full ios-button bg-ios-blue hover:bg-ios-blue/90 text-white">
        Save Voice Settings
      </button>
    </div>
  );
}
