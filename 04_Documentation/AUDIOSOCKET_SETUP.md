# AudioSocket Integration - Complete Setup Guide

## Overview

This setup enables **Ava sales bot** to handle phone calls via **Asterisk AudioSocket** protocol - completely free, no cloud costs!

### Architecture

```
SIP Phone → Asterisk (Docker) → AudioSocket (TCP) → Pipecat → Ava Bot
           Extension 9092         Port 9092          Pipeline
```

### Components

1. **Asterisk 22.4.0** (Docker) - PBX handling SIP calls
2. **AudioSocketTransport** - Pipecat transport for Asterisk integration
3. **Ava Sales Bot** - AI-powered business funding specialist

---

## Prerequisites

- ✅ Docker installed
- ✅ Python 3.13 with pipecat_env_new
- ✅ API Keys: Deepgram, Cerebras (or Groq)
- ✅ SIP phone or softphone for testing

---

## Installation

### Step 1: Asterisk Container (Already Running)

Asterisk is configured and running at `/home/user/Desktop/ava-asterisk-config/`

```bash
# Check status
sudo docker ps --filter "name=ava-asterisk"

# View logs
sudo docker logs -f ava-asterisk

# Restart if needed
cd /home/user/Desktop/ava-asterisk-config
sudo docker compose restart
```

**Key Configuration:**
- **SIP Endpoint 1000**: Username `1000`, Password `testpass1000`
- **Extension 9092**: Routes to AudioSocket at `host.docker.internal:9092`
- **Extension 600**: Echo test (for testing SIP connection)
- **Extension 500**: Status check (plays "Hello World")

### Step 2: Verify AudioSocket in Asterisk

```bash
# Check AudioSocket application is available
sudo docker exec -it ava-asterisk asterisk -rx "core show application AudioSocket"

# Check dialplan loaded
sudo docker exec -it ava-asterisk asterisk -rx "dialplan show ava-context"

# Check SIP endpoint
sudo docker exec -it ava-asterisk asterisk -rx "pjsip show endpoints"
```

---

## Running Ava with AudioSocket

### Start the Bot

```bash
cd /home/user/Desktop/exodus-kali-deploy
source pipecat_env_new/bin/activate
python3 ava_sales_bot_audiosocket.py --contact-name "John"
```

**Expected Output:**
```
✅ AudioSocket server listening on ('0.0.0.0', 9092)
🎙️  AudioSocket server ready on 0.0.0.0:9092
💡 Dial extension 9092 from SIP phone to connect to Ava
```

### Command-Line Options

```bash
python3 ava_sales_bot_audiosocket.py --help

Options:
  --host HOST              Host to bind AudioSocket server (default: 0.0.0.0)
  --port PORT              Port to bind (default: 9092)
  --contact-name NAME      Prospect's first name (default: "there")
```

---

## Testing

### Test 1: SIP Connection (Echo Test)

1. **Register SIP phone:**
   - Server: `<your-kali-ip>:5060`
   - Username: `1000`
   - Password: `testpass1000`

2. **Call extension 600** (echo test)
   - Should hear "echo test" prompt
   - Everything you say should echo back
   - Confirms SIP connectivity

### Test 2: Ava Bot Call

1. **Start Ava bot** (see "Running Ava" above)

2. **Call extension 9092** from SIP phone

3. **Expected Flow:**
   - AudioSocket connects (you'll see logs in bot terminal)
   - Ava greets: "Hey John, calling about the money you were seeking for the business..."
   - Have a conversation following her sales script

4. **Check Logs:**

   **Bot Terminal:**
   ```
   📞 Asterisk connected from ('172.17.0.1', 54321)
   📋 Call UUID: abc-123-def
   ✅ Call connected: abc-123-def
   ```

   **Asterisk Logs:**
   ```bash
   sudo docker logs -f ava-asterisk | grep AudioSocket
   ```

---

## Troubleshooting

### Issue 1: Bot Won't Start

**Error:** `Address already in use`
```bash
# Kill process using port 9092
sudo lsof -ti:9092 | xargs kill -9

# Restart bot
python3 ava_sales_bot_audiosocket.py
```

### Issue 2: SIP Phone Can't Register

**Symptom:** Registration fails

```bash
# Check Asterisk is listening on port 5060
sudo docker exec -it ava-asterisk netstat -tulpn | grep 5060

# Check endpoint configuration
sudo docker exec -it ava-asterisk asterisk -rx "pjsip show endpoints"

# Verify credentials in config
cat /home/user/Desktop/ava-asterisk-config/conf/pjsip.conf
```

### Issue 3: Call Connects but No Audio

**Check:**
1. **AudioSocket Connection:**
   ```bash
   # See if Asterisk connected to bot
   sudo docker logs ava-asterisk | tail -20
   ```

2. **Bot Logs:**
   - Should see "📞 Asterisk connected from..."
   - Should see "📋 Call UUID: ..."

3. **API Keys:**
   ```bash
   # Verify environment variables
   source pipecat_env_new/bin/activate
   python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Deepgram:', 'OK' if os.getenv('DEEPGRAM_API_KEY') else 'MISSING')"
   ```

### Issue 4: Ava Doesn't Respond

**Check LLM Configuration:**
```bash
# Test Cerebras API
curl -X POST https://api.cerebras.ai/v1/chat/completions \
  -H "Authorization: Bearer $CEREBRAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3.1-8b","messages":[{"role":"user","content":"Hi"}]}'
```

---

## Architecture Deep Dive

### AudioSocket Protocol Flow

1. **Asterisk Initiates:**
   - User dials extension 9092
   - Asterisk executes: `AudioSocket(host.docker.internal:9092/${UUID})`
   - TCP connection to bot on port 9092

2. **Handshake:**
   - Asterisk sends: UUID + `\x00` (null-terminated string)
   - Bot reads UUID and sets up session

3. **Bidirectional Audio:**
   - **Asterisk → Bot:** Raw 16-bit PCM audio @ 8kHz mono
   - **Bot → Asterisk:** Raw 16-bit PCM audio @ 8kHz mono
   - AudioSocketTransport resamples: 8kHz ↔ 16kHz (Pipecat uses 16kHz)

4. **Hangup:**
   - Either side closes TCP connection
   - Call ends

### Resampling

```python
# AudioResampler in audiosocket_transport.py
8kHz (Asterisk) → 16kHz (Pipecat) → LLM/TTS → 16kHz → 8kHz (Asterisk)
```

Uses **scipy.signal.resample_poly** for high-quality resampling.

---

## Configuration Files

### Asterisk Dialplan (`extensions.conf`)

```ini
[ava-context]
exten => 9092,1,NoOp(Connecting to Ava via AudioSocket)
 same => n,Answer()
 same => n,Ringing()
 same => n,Wait(1)
 same => n,Set(UUID=${SHELL(uuidgen | tr -d '\n')})
 same => n,Set(CONTACT_NAME=TestCaller)
 same => n,NoOp(Dialing AudioSocket - UUID: ${UUID})
 same => n,AudioSocket(host.docker.internal:9092/${UUID})
 same => n,Hangup()
```

### SIP Endpoint (`pjsip.conf`)

```ini
[1000](webrtc-template)
auth=1000
aors=1000

[1000]
type=auth
auth_type=userpass
username=1000
password=testpass1000
```

### Bot Configuration (`bot_config.json`)

```json
{
  "ava_sales_bot": {
    "llm": {
      "provider": "cerebras",
      "model": "llama3.1-8b",
      "temperature": 0.5
    },
    "tts": {
      "provider": "edge",
      "voice": "en-US-AvaMultilingualNeural",
      "rate": "+10%"
    }
  }
}
```

---

## Next Steps: ViciDial Integration

### Phase 2 Goals:

1. **Install ViciDial** on Kali or VM
2. **Configure Campaigns** with lead lists
3. **Route Calls** to Ava via AudioSocket
4. **Predictive Dialing** for high-volume outbound

### Benefits:

- **Campaign Management** - Upload CSV lead lists
- **Auto-Dialing** - Predictive/progressive modes
- **Lead Disposition** - Track outcomes (interested/not interested/callback)
- **Call Recording** - For quality assurance
- **Agent Routing** - Hot transfer qualified leads to human agents
- **Reporting** - Call statistics and conversion rates

---

## Performance Notes

### Current Setup (Single Bot Instance):

- **Concurrent Calls:** 1 (single AudioSocket connection)
- **Audio Quality:** 8kHz (standard telephony)
- **Latency:** ~200-500ms (LLM + TTS)
- **Cost:** $0 infrastructure (only API usage)

### Scaling for Production:

1. **Multiple Bot Instances:**
   - Run bot on different ports (9092, 9093, 9094...)
   - Update Asterisk dialplan to load balance

2. **Bot Pool Manager:**
   - Track available bot instances
   - Route calls to free bots
   - Handle failover

3. **LLM Optimization:**
   - Use Cerebras for speed (200-300ms)
   - Or Groq for cost ($0.07/$0.27 per 1M tokens)

---

## Cost Analysis

### AudioSocket vs Alternatives:

| Solution | Cost | Pros | Cons |
|----------|------|------|------|
| **AudioSocket + Asterisk** | $0 infra | Free, full control | Self-hosted, need SIP trunks |
| **Daily.co SIP** | $0.005/min | Easy, WebRTC | Ongoing cost, cloud dependency |
| **LiveKit** | $0.004/min (after 1K free) | 1K free min/mo | Cloud dependency |
| **Twilio WebSocket** | $0.014/min | Integrated platform | Most expensive |

**Estimated Costs (1000 calls/day, 5 min avg):**
- AudioSocket: **$0** (infrastructure) + API costs only
- Daily.co: **$750/month**
- LiveKit: **$600/month**
- Twilio: **$2,100/month**

---

## Monitoring & Logs

### Real-Time Monitoring

```bash
# Watch bot logs
tail -f ava_bot.log

# Watch Asterisk logs
sudo docker logs -f ava-asterisk

# Monitor active calls
sudo docker exec -it ava-asterisk asterisk -rx "core show channels"
```

### Debugging Commands

```bash
# Check AudioSocket connection
sudo docker exec -it ava-asterisk asterisk -rx "core show channels verbose"

# See call details
sudo docker exec -it ava-asterisk asterisk -rx "pjsip show channels"

# Full debug (verbose!)
sudo docker exec -it ava-asterisk asterisk -rx "core set debug 5"
```

---

## Summary

✅ **Asterisk AudioSocket** - Free telephony infrastructure
✅ **Pipecat Integration** - AI voice pipeline
✅ **Ava Sales Bot** - Business funding specialist
✅ **Production Ready** - Scalable architecture

**Next:** ViciDial for campaign management and predictive dialing

---

## Quick Reference

```bash
# Start bot
cd /home/user/Desktop/exodus-kali-deploy
source pipecat_env_new/bin/activate
python3 ava_sales_bot_audiosocket.py --contact-name "Lead Name"

# Check Asterisk
sudo docker ps --filter "name=ava-asterisk"
sudo docker exec -it ava-asterisk asterisk -rx "core show channels"

# Test call: Dial extension 9092 from SIP phone (1000/testpass1000)
```
