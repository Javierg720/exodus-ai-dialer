# 🎨 Plasma Visualizer Setup Guide

You're seeing the error **"Failed to start session: Unable to connect to transport"** because the backend WebRTC agent isn't running yet.

## The Problem

- ✅ **Frontend is running** on http://localhost:3000
- ❌ **Backend is NOT running** on port 7861
- The frontend needs a Pipecat WebRTC agent to connect to

---

## 🚀 Solution: Two Options

### **Option 1: Automated Setup (Recommended)**

If you have a Daily.co API key:

```bash
# 1. Add Daily API key to .env
echo "DAILY_API_KEY=your_daily_api_key_here" >> .env

# 2. Create a room automatically
source pipecat_env/bin/activate
python3 create_daily_room.py

# 3. Start the agent (it will prompt for the room URL)
./start_plasma_demo.sh

# 4. Open http://localhost:3000 and click Connect!
```

### **Option 2: Manual Setup**

If you don't have a Daily.co API key:

**Step 1: Get a Daily.co Room**
1. Go to https://dashboard.daily.co (free signup)
2. Click "Create Room"
3. Copy the room URL (e.g., `https://your-domain.daily.co/room-name`)

**Step 2: Start the Backend**

```bash
# In Terminal 1 - Start WebRTC Agent
cd /home/user/Desktop/exodus-kali-deploy
source pipecat_env/bin/activate

# Create agent config
cat > temp/plasma_agent_config.json << 'EOF'
{
  "voice_id": "en-US-AriaNeural",
  "speed": 1.0,
  "pitch": 0,
  "prompt": "You are Ava, a friendly AI assistant. Keep responses concise and natural.",
  "campaign_name": "Plasma Demo"
}
EOF

# Start the agent (replace with YOUR room URL)
python3 webrtc_agent.py \
    --room-url https://your-domain.daily.co/your-room \
    --config-file temp/plasma_agent_config.json
```

**Step 3: Open the Frontend**

The frontend is already running at http://localhost:3000

1. Open http://localhost:3000 in your browser
2. Click the **Connect** button
3. Allow microphone access
4. **Start talking and watch the plasma react!** ✨

---

## 🔍 Troubleshooting

### "Port 7861 not responding"
- The backend agent isn't running
- Run `./start_plasma_demo.sh` or follow Option 2

### "Unable to connect to transport"
- Backend is running but frontend can't reach it
- Check backend logs for errors
- Verify GROQ_API_KEY is set in .env

### "No audio / mic not working"
- Browser blocked microphone access
- Click the 🔒 lock icon in address bar → Allow microphone
- Refresh and try again

### "Plasma not showing"
- WebGL might not be supported
- Try a different browser (Chrome/Firefox recommended)
- Check browser console for errors

---

## 📁 File Reference

```
exodus-kali-deploy/
├── start_plasma_demo.sh          # Quick start script
├── create_daily_room.py          # Auto-create Daily rooms
├── webrtc_agent.py               # WebRTC agent (port 7861)
├── .env                          # API keys
└── frontend/voice-ui-kit/
    └── examples/03-tailwind/     # Plasma UI (port 3000)
```

---

## 🎯 Quick Test Checklist

- [ ] Daily.co account created
- [ ] Daily room URL obtained
- [ ] GROQ_API_KEY set in .env
- [ ] Python virtual env activated
- [ ] Backend agent running on 7861
- [ ] Frontend running on 3000
- [ ] Browser allows microphone
- [ ] Connect button clicked

---

## 🆘 Still Having Issues?

Check these logs:

```bash
# Backend logs (if running in terminal)
# Look for "Starting pipeline..." message

# Frontend logs (browser console)
# Press F12 → Console tab

# Check if backend is reachable
curl http://localhost:7861
```

---

## 🎨 What You'll See When It Works

1. **Connect Button** → Click to start session
2. **Plasma Background** → Animated WebGL effect
3. **Transcript Overlay** → Real-time conversation
4. **Mic Button** → Mute/unmute control
5. **Disconnect Button** → End session

**The plasma effect will pulse and flow in response to audio!**

---

## 📚 Learn More

- [Pipecat Docs](https://docs.pipecat.ai)
- [Voice UI Kit](https://voiceuikit.pipecat.ai)
- [Daily.co API](https://docs.daily.co)
- [WebRTC Agent Code](./webrtc_agent.py)
- [Plasma Frontend Code](./frontend/voice-ui-kit/examples/03-tailwind/src/app/app.tsx)
