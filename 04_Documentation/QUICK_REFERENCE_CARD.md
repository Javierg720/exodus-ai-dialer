# Exodus AI Dialer - Quick Reference Card

## 🚀 Quick Start (z.ai FREE Version)
```bash
cd /home/user/Desktop/exodus-kali-deploy
./start_dialer_zai.sh
# Dashboard: http://localhost:8000/dashboard
```

## 🔑 All API Keys
```bash
# Speech-to-Text
DEEPGRAM_API_KEY=d8191f0f92502c50e9058bfa15a17f8fac916feb
GROQ_API_KEY=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

# Language Models
CEREBRAS_API_KEY=csk-cn2tvnjpx4ey8xvpdffjpyhe3t4twn4ddnyx3m5xmr5fc88w
OPENAI_API_KEY=sk-proj-w7OBqBVvSs-6F7RQNPPHd55nPvLt0cMKqQdwxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ZAI_API_KEY=73fdff33d97e4cf9a2dce9cc781bdce7.wZijjBFhgI2xxcwj

# Telephony
TWILIO_ACCOUNT_SID=AC6e3e1df2a2ae9171e5e52c093fee5d77
TWILIO_PHONE=+19544668818

# System
AMI_USERNAME=admin
AMI_PASSWORD=admin123
SIP_EXTENSION=1000
SIP_PASSWORD=test1000
SUDO_PASSWORD=0000
```

## 📞 SIP Phone Setup
- **Server**: 10.0.0.235 (your machine IP)
- **Port**: 5060
- **Username**: 1000
- **Password**: test1000

## 🤖 Bot Ports
- **9092-9111**: 20 AI bots
- **9999**: Test bot (test_zai_bot.sh)

## 💰 Cost Comparison (Per Hour)
| Config | STT | LLM | TTS | Total |
|--------|-----|-----|-----|-------|
| Original | Deepgram $0.26 | Cerebras $0.007 | Edge FREE | $0.267 |
| z.ai FREE | Groq $0.01 | z.ai FREE | Edge FREE | $0.01 |
| **20 Bots** | | | | **$0.20/hr** |

## 🛠️ Common Commands
```bash
# Start system
./start_dialer_zai.sh

# Test single bot
./test_zai_bot.sh

# Check bot status
curl http://localhost:8000/bots

# Monitor calls
docker exec ava-asterisk asterisk -rx "core show channels"

# Check TCPA compliance
sqlite3 dialer.db "SELECT * FROM v_todays_stats"

# Stop everything
pkill -f "ava_sales_bot|dialer_orchestrator|dialer_api"

# Make test call
docker exec ava-asterisk asterisk -rx "originate PJSIP/twilio/+15551234567 extension 9092@ava-context"
```

## 📊 API Endpoints
```
GET  http://localhost:8000/bots           # Bot status
GET  http://localhost:8000/campaigns      # List campaigns
POST http://localhost:8000/campaigns/1/start  # Start dialing
GET  http://localhost:8000/calls/active   # Active calls
GET  http://localhost:8000/dashboard      # Web UI
```

## 🚨 TCPA Compliance
- **3% Drop Rate Limit** over 30-day rolling window
- **5-second wrap-up** between calls
- **2-second delay** before bot speaks
- **9 AM - 9 PM** calling window (timezone aware)

## 📁 Key Files
```
ava_sales_bot_zai.py         # z.ai bot (FREE)
bot_config_zai.json          # z.ai config
bot_pool_manager.py          # Manages 20 bots
dialer_orchestrator.py       # Predictive algorithm
dialer_api.py               # REST API
dialer.db                   # SQLite database
.env                        # API keys
```

## ⚠️ Troubleshooting
```bash
# Bot not responding?
docker exec ava-asterisk asterisk -rx "dialplan show 9092@ava-context"

# High drop rate?
sqlite3 dialer.db "UPDATE campaigns SET dial_ratio = 1.5"

# Check logs
tail -f nohup.out | grep ERROR

# Restart specific bot
curl -X POST http://localhost:8000/bots/9092/restart
```

## 🔄 Daily Operations
```bash
# Morning
./start_dialer_zai.sh
curl http://localhost:8000/campaigns/1/start

# Evening
curl http://localhost:8000/campaigns/1/stop
pkill -f ava_sales_bot

# Backup
sqlite3 dialer.db ".backup /backup/dialer_$(date +%Y%m%d).db"
```

---
**System Built**: October 8-31, 2025
**Total Cost**: $0.20/hour for 20 AI agents (96% savings)
**Capacity**: 5,000+ calls/day