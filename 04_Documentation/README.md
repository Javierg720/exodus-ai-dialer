# Exodus Kali Deploy - Voice AI System

## Project Structure

```
exodus-kali-deploy/
│
├── bots/                    # All bot implementations
│   ├── voice_ui_kit_bot.py  # Main WebRTC bot (Ava Sterling script)
│   ├── twilio_server.py     # Twilio server
│   ├── twilio_agent.py      # Twilio agent handler
│   └── edge_tts_*.py        # Edge TTS services
│
├── frontend/                # Frontend applications
│   └── voice-ui-kit-main/   # Voice UI Kit React app
│       └── examples/
│           └── 03-tailwind/  # Main frontend (port 3002)
│
├── config/                  # Configuration files
│   └── *.json              # Various config files
│
├── scripts/                 # Utility scripts
│   └── *.js, *.sh          # Automation scripts
│
├── logs/                    # Application logs
│   └── *.log               # Runtime logs
│
├── docs/                    # Documentation
│   └── *.md, *.txt         # Setup and usage docs
│
└── pipecat_env/            # Python virtual environment

```

## Active Services

### 1. Voice UI Kit Bot (WebRTC)
- **File**: `bots/voice_ui_kit_bot.py`
- **Port**: 7861
- **Model**: gemma2-9b-it (Groq)
- **STT**: Local Whisper (CPU)
- **TTS**: Edge TTS (Ava voice)
- **Script**: Ava Sterling Fund Express sales script

### 2. Twilio Voice Bot
- **File**: `bots/twilio_server.py`
- **Port**: 8080
- **Same AI configuration as WebRTC bot**

### 3. Frontend (Voice UI Kit)
- **Path**: `frontend/voice-ui-kit-main/examples/03-tailwind`
- **Port**: 3002
- **URL**: http://localhost:3002

## Quick Start Commands

```bash
# Start Voice UI Kit Bot (WebRTC)
cd /home/ubuntu/Desktop/exodus-kali-deploy
source pipecat_env/bin/activate
python3 bots/voice_ui_kit_bot.py

# Start Twilio Server
source pipecat_env/bin/activate
python3 bots/twilio_server.py

# Start Frontend
cd frontend/voice-ui-kit-main/examples/03-tailwind
PORT=3002 pnpm dev

# Create Public Tunnel
npx localtunnel --port 3002
```

## Sales Script Features
- Immediate pitch opening with dramatic pauses
- One question at a time qualifying flow
- Comprehensive objection handlers
- Never-repeat-rebuttals logic
- Emphasis control with ALL CAPS + "..." pattern

## Environment Variables Required
- `GROQ_API_KEY`
- `TWILIO_ACCOUNT_SID` (for Twilio)
- `TWILIO_AUTH_TOKEN` (for Twilio)