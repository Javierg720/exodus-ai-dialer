# 🎨 FINAL SETUP - Plasma Visualizer with FREE TTS

## ✅ What's Working
- ✅ Frontend with Plasma Visualizer: http://localhost:3000
- ✅ Daily.co Room created: https://shared-exodus-room.daily.co/74m2Hmi7RonSu55Z3idu
- ✅ WebRTC Agent configured with **FREE Google TTS (gTTS)**
- ✅ Groq LLM + Groq STT working

## ⚠️ Missing: ffmpeg

The agent needs **ffmpeg** to convert TTS audio. Install it:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

## 🚀 Start Everything

### 1. Install ffmpeg (one-time setup)
```bash
sudo apt-get install -y ffmpeg
```

### 2. Start the WebRTC Agent
```bash
cd /home/user/Desktop/exodus-kali-deploy
/home/user/Desktop/exodus-kali-deploy/pipecat_env_new/bin/python3 webrtc_agent.py \
  --room-url "https://shared-exodus-room.daily.co/74m2Hmi7RonSu55Z3idu" \
  --config-file temp/plasma_agent_config.json
```

### 3. Open the Plasma UI
The frontend is already running at:
```
http://localhost:3000
```

### 4. Test It!
1. Open http://localhost:3000
2. Click "Connect"
3. Allow microphone
4. Start talking!
5. **Watch the plasma effect react to your voice** 🎨

---

## 🔧 What's Configured

**Services (ALL FREE):**
- **LLM:** Groq (llama-3.1-8b-instant)
- **STT:** Groq (whisper-large-v3-turbo)
- **TTS:** Google TTS (gTTS) - completely free
- **WebRTC:** Daily.co
- **Frontend:** Next.js 15 + React 19 + Three.js WebGL

**Daily.co Room:**
```
https://shared-exodus-room.daily.co/74m2Hmi7RonSu55Z3idu
```

**Agent Config:** `temp/plasma_agent_config.json`

---

## 📊 Services Status

| Service | Status | Port | Command |
|---------|--------|------|---------|
| Frontend | ✅ Running | 3000 | Job ID: ae5f26 |
| Agent | ⏸️ Waiting for ffmpeg | - | Job ID: 5dfd6b |

---

## 🐛 If You Get Errors

### "ffmpeg not found"
```bash
sudo apt-get install ffmpeg
```

### "Room expired"
Create a new room:
```bash
curl -X POST https://api.daily.co/v1/rooms \
  -H "Authorization: Bearer 307f89b2a79448f218eb1d9ed9eeb1662cdcad3905f59f3e9f9d50f151821cf4" \
  -H "Content-Type: application/json" \
  -d '{"properties":{"enable_chat":false}}'
```

### "Can't hear AI"
- Check ffmpeg is installed
- Check browser audio isn't muted
- Restart the agent

### "AI can't hear me"
- Allow microphone in browser
- Check mic in system settings

---

## 🎯 Quick Test Checklist

- [ ] ffmpeg installed
- [ ] Agent running (no errors in logs)
- [ ] Frontend open at http://localhost:3000
- [ ] Clicked "Connect" button
- [ ] Microphone allowed
- [ ] Can speak and AI responds
- [ ] Plasma effect visible and reacting

---

## 📝 Key Files

- `/home/user/Desktop/exodus-kali-deploy/webrtc_agent.py` - Main agent
- `/home/user/Desktop/exodus-kali-deploy/gtts_service.py` - Free TTS service
- `/home/user/Desktop/exodus-kali-deploy/temp/plasma_agent_config.json` - Config
- `/home/user/Desktop/exodus-kali-deploy/frontend/voice-ui-kit/examples/03-tailwind/` - Frontend

---

## 🎨 After Setup Works

You'll have:
- Real-time voice conversation with AI
- WebGL plasma visualizer that reacts to audio
- Live transcripts on screen
- All using FREE services (Groq + gTTS)

**Just install ffmpeg and restart the agent!**
