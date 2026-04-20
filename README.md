# EXODUS AI Predictive Dialer

**AI-powered predictive dialing platform with a containerized voice-bot pool, real-time AudioSocket streaming, and automatic LLM-driven call disposition.**

EXODUS pairs a FastAPI control plane with Asterisk PBX and a pool of 20 Dockerized AI voice agents (Deepgram STT → Groq LLM → Edge TTS via Pipecat). Outbound calls are originated through Asterisk AMI, audio streams over AudioSocket into the bot pipeline, transcripts are captured live, and each call's outcome is auto-classified by an LLM at hangup. A React dashboard provides live call monitoring, waveform playback, campaign management, and TCPA compliance reporting.

---

## Short description (for GitHub "About")

> AI predictive dialer with 20-bot AVR pool, AudioSocket streaming, auto-disposition via LLM, and a React control panel. FastAPI + Asterisk + Pipecat + Deepgram/Groq/Edge TTS.

---

## Features

- **Predictive dialing engine** with configurable pacing, abandon-rate governance, and TCPA drop-rate enforcement (30-day rolling window)
- **20-bot AVR pool** — Docker-managed Ava sales agents on ports 9092–9111 with round-robin assignment and wrap-up cooldown
- **AudioSocket transport** for low-latency real-time audio between Asterisk and Pipecat bots
- **Auto-disposition** — LLM analyzes the full transcript at hangup and writes a disposition code (INTERESTED, NOT_INTERESTED, CALLBACK, VOICEMAIL, DNC, etc.)
- **Caller-ID rotation** across 5 Twilio DIDs to improve answer rates
- **React dashboard** (`exodus-dashboard-pro/`) — live calls, campaign CRUD, lead import, waveform playback, DNC list, voice settings, WebPhone
- **55 REST endpoints** with Pydantic validation, JWT auth, bulk lead import, call notes, recording playback
- **Observability** — Prometheus metrics, structured logging (loguru), health checks
- **TCPA compliance module** — DNC list, time-zone-aware call windows, drop-rate monitoring
- **Transcript + recording capture** for every call
- **Vicidial lead import** tooling

---

## Architecture

```
┌──────────────────────┐        ┌────────────────────────────────┐
│  React Dashboard     │ HTTPS  │         FastAPI                │
│  (Vite + Tailwind +  │◄──────►│  dialer_api.py — 55 endpoints  │
│   Zustand + jsSIP)   │  WS    │  JWT · Prometheus · loguru     │
└──────────────────────┘        └──────────────┬─────────────────┘
                                               │
                              ┌────────────────┴────────────────┐
                              │     DialerOrchestrator          │
                              │  predictive pacing · TCPA       │
                              │  caller-ID rotation · AMI glue  │
                              └───┬─────────────┬──────────────┬┘
                                  │             │              │
                     ┌────────────▼──┐  ┌───────▼───────┐  ┌───▼──────────┐
                     │ AsyncDialerDB │  │ Asterisk AMI  │  │ AVR Bot Pool │
                     │   (SQLite)    │  │  + AudioSock  │  │  20× Docker  │
                     └───────────────┘  └───────┬───────┘  └───┬──────────┘
                                                │              │
                                        ┌───────▼────┐   ┌─────▼──────────────┐
                                        │   Twilio   │   │ Pipecat pipeline   │
                                        │   Trunk    │   │ Deepgram → Groq →  │
                                        │ (5 DIDs)   │   │ Edge TTS           │
                                        └────────────┘   └────────────────────┘
```

---

## Repository layout

```
exodus-dialer-backup/
├── 01_Core_System/              # Python backend
│   ├── dialer_api.py            # FastAPI app (55 endpoints, JWT, WS)
│   ├── dialer_orchestrator.py   # Predictive engine + AMI event handlers
│   ├── avr_bot_pool_manager.py  # 20-bot Docker pool tracker
│   ├── ava_sales_bot_audiosocket.py  # Pipecat bot (STT→LLM→TTS)
│   ├── audiosocket_transport.py # AudioSocket ↔ Pipecat bridge
│   ├── dialer_db_async.py       # Async SQLite layer
│   ├── tcpa_compliance.py       # DNC + drop-rate enforcement
│   ├── edge_tts_service.py      # Microsoft Edge TTS provider
│   ├── transcript_manager.py    # Transcript + recording capture
│   └── docker-compose-avr-production.yml
├── 02_AVR_Platform/
│   └── custom-providers/        # Dockerized STT/LLM/TTS microservices
│       ├── avr-asr-deepgram-denoised/
│       ├── avr-llm-groq/
│       ├── avr-llm-cerebras/
│       └── avr-tts-edge/
├── 03_Asterisk_Config/conf/     # Full Asterisk config (extensions, SIP, AMI)
├── exodus-dashboard-pro/        # React 18 + Vite + Tailwind dashboard
├── 04_Documentation/            # Design notes, runbooks, research
├── 07_Scripts/                  # Vicidial importers, ops scripts
└── VICIDIAL_INTEGRATION/        # Vicidial SIP + extensions config
```

---

## Requirements

- **OS:** Ubuntu 22.04+ (tested on Linux 6.x)
- **Python:** 3.11+
- **Node:** 18+ (dashboard)
- **Docker + docker-compose** (AVR bot pool)
- **Asterisk:** 20+ with `chan_pjsip` and AudioSocket app
- **SIP trunk:** Twilio (5 DIDs recommended for caller-ID rotation) or equivalent
- **API keys:** Deepgram, Groq (or OpenAI), optional Cerebras

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/Javierg720/exodus-dialer-backup.git
cd exodus-dialer-backup

# 2. Configure environment
cp .env.template .env
# Edit .env — set JWT_SECRET_KEY, AMI creds, API keys, trunk DIDs

# 3. Backend
cd 01_Core_System
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4. Asterisk (copy configs, reload)
sudo cp -r ../03_Asterisk_Config/conf/* /etc/asterisk/
sudo systemctl restart asterisk

# 5. Start the 20-bot AVR pool
docker-compose -f docker-compose-avr-production.yml up -d

# 6. Start the dialer API + orchestrator
./start_production.sh

# 7. Dashboard (separate terminal)
cd ../exodus-dashboard-pro
npm install
npm run dev        # dev on :5173
# or: npm run build && npm run preview
```

API will be on `http://localhost:8000`, dashboard on `http://localhost:5173`.

---

## Environment variables

Minimum required in `.env`:

```env
# API / Auth
JWT_SECRET_KEY=<generate-a-long-random-string>
API_HOST=0.0.0.0
API_PORT=8000

# Asterisk AMI
AMI_HOST=localhost
AMI_PORT=5038
AMI_USERNAME=<ami-user>
AMI_PASSWORD=<ami-pass>

# AI providers
DEEPGRAM_API_KEY=...
GROQ_API_KEY=...
OPENAI_API_KEY=...      # optional fallback

# Trunk / caller IDs
TRUNK_NAME=EXODUS_Dialer
CALLER_IDS=+15551230001,+15551230002,+15551230003,+15551230004,+15551230005

# Database
DB_PATH=./dialer.db
```

---

## Key endpoints

| Method | Path                                | Purpose                         |
|--------|-------------------------------------|---------------------------------|
| POST   | `/auth/login`                       | JWT auth                        |
| GET    | `/health`                           | Liveness + component status     |
| POST   | `/campaigns`                        | Create campaign                 |
| POST   | `/campaigns/{id}/start`             | Start predictive dialing        |
| POST   | `/campaigns/{id}/pause`             | Pause campaign                  |
| POST   | `/leads/bulk`                       | Bulk import leads               |
| PUT    | `/leads/{id}/disposition`           | Manual disposition update       |
| GET    | `/bots`                             | Pool status (busy/idle/crashed) |
| GET    | `/recording/{call_uuid}`            | Stream recording                |
| GET    | `/metrics`                          | Prometheus metrics              |
| WS     | `/ws/live-calls`                    | Live call event stream          |

Full route list: see `dialer_api.py` (55 endpoints).

---

## Compliance

EXODUS is designed for **TCPA-compliant outbound calling**:

- Internal DNC list with per-campaign overrides
- Time-zone-aware call windows (8 AM – 9 PM local, configurable)
- Rolling 30-day abandon/drop-rate calculation
- Full transcript + recording retention
- Auto-disposition audit trail

**You are responsible for obtaining prior express written consent, maintaining your own DNC scrubbing against the national registry, and complying with state-level regulations.** This software does not file compliance on your behalf.

---

## Security notes

Before exposing to the internet:

1. **Rotate `JWT_SECRET_KEY`** — never ship the default
2. **Set strong AMI credentials** — the defaults in source are placeholders
3. **Firewall** AMI (5038), SIP (5060), and AudioSocket ports to trusted hosts only
4. **TLS** the FastAPI layer (reverse proxy via nginx/Caddy)
5. **Remove** the demo `USERS_DB` entry in `dialer_api.py` and wire real auth
6. **Scrub** any committed `.env`, database, or backup files before forking

A full security audit checklist is in `DIALER_API_SECURITY_AUDIT.md`.

---

## Tech stack

**Backend:** FastAPI · Pipecat · asterisk-ami · aiosqlite · SQLAlchemy · loguru · Prometheus client · python-jose · passlib

**AI:** Deepgram SDK · Groq · OpenAI · Edge TTS · Silero VAD · PyTorch/torchaudio

**Telephony:** Asterisk 20+ · AudioSocket · AMI · PJSIP · Twilio trunk

**Frontend:** React 18 · Vite · TypeScript · Tailwind CSS · Zustand · TanStack Query · Framer Motion · Recharts · WaveSurfer.js · jsSIP · Lucide

**Infra:** Docker · docker-compose · SQLite (dev) · systemd

---

## Roadmap

- Postgres migration (SQLite is the current scaling ceiling)
- Horizontal bot pool autoscaling
- Multi-trunk failover
- Native SMS follow-up on disposition
- Agent hand-off for "hot" leads (warm transfer)
- Dashboard: sentiment heatmap v2, per-bot call quality scoring

---

## License

Proprietary — all rights reserved. Contact the author before redistributing.

---

## Author

Built by **Javier G.** ([@Javierg720](https://github.com/Javierg720))

Questions or deployment help: open an issue on the repo.
