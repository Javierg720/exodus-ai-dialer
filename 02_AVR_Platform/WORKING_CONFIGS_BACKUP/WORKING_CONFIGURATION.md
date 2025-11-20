# WORKING AVR CONFIGURATION - DO NOT CHANGE
**Date**: 2025-11-07
**Status**: FULLY FUNCTIONAL - LLM→TTS handoff working perfectly

## Critical Success Factors

This configuration achieves **perfect bidirectional conversation** with:
- ✅ Intro plays flawlessly
- ✅ User speech transcribed by Deepgram
- ✅ LLM generates responses via Groq
- ✅ **TTS receives LLM responses and generates audio**
- ✅ User hears bot respond naturally
- ✅ Multi-turn conversation works

## The Key Fix: Response Format

**CRITICAL**: AVR Core expects plain JSON (NOT SSE-wrapped) for buffered mode:

```javascript
res.json({ type: 'text', content: responseText })
```

**DO NOT USE**:
- `res.json({ response: responseText })` ❌
- `res.json({ content: responseText })` ❌
- SSE format with `data:` prefix ❌

**CORRECT FORMAT**:
```javascript
{
  "type": "text",
  "content": "The LLM's response text here"
}
```

## Working Stack Configuration

### LLM Provider: Groq (FREE)
- **Model**: `llama-3.3-70b-versatile`
- **API Key**: `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`
- **Temperature**: `0.6`
- **Port**: `6002`
- **Image**: `avr-llm-groq:latest`

### ASR Provider: Deepgram
- **Model**: `nova-2-phonecall`
- **API Key**: `44f464f1116d54ee9412f7b9214cdde028240091`
- **Port**: `6010`

### TTS Provider: Edge TTS (FREE)
- **Voice**: `en-US-AvaMultilingualNeural`
- **Port**: `6011`
- **Rate**: `+10%`
- **Cost**: FREE

### Bot Configuration (Port 9092)
```yaml
environment:
  - PORT=9092
  - ASR_URL=http://avr-asr:6010/speech-to-text-stream
  - LLM_URL=http://avr-llm:6002/prompt-stream
  - TTS_URL=http://avr-tts:6011/text-to-speech-stream
  - INTERRUPT_LISTENING=false
  - MIN_SPEECH_MS=500
  - VAD_SENSITIVITY=3
  - SYSTEM_MESSAGE=Hey there, Ava with Fund Express. Calling about the money you were seeking for the business. Did you secure those funds?
```

## Complete Working Files

### 1. avr-llm-groq/index.js (EXACT WORKING VERSION)

```javascript
const express = require('express');
const { OpenAI } = require('openai');
const app = express();
app.use(express.json());

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const MODEL = process.env.GROQ_MODEL || 'llama3-8b-8192';
const TEMPERATURE = parseFloat(process.env.TEMPERATURE || '0.7');

const openai = new OpenAI({
  apiKey: GROQ_API_KEY,
  baseURL: 'https://api.groq.com/openai/v1',  // Groq's OpenAI-compatible endpoint
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', provider: 'groq', model: MODEL });
});

// AVR /prompt-stream endpoint (SSE format with type: "text")
app.post('/prompt-stream', async (req, res) => {
  try {
    const { messages = [], systemPrompt = 'You are a helpful assistant.' } = req.body;
    const formattedMessages = [
      { role: 'system', content: systemPrompt },
      ...messages
    ];

    console.log(`[Groq] /prompt-stream with ${messages.length} messages`);

    const completion = await openai.chat.completions.create({
      model: MODEL,
      messages: formattedMessages,
      temperature: TEMPERATURE,
      stream: false  // Buffered full response
    });

    const responseText = completion.choices[0]?.message?.content || '';
    console.log(`[Groq] Response: ${responseText.substring(0, 50)}...`);

    // AVR expects plain JSON with "type": "text" and "content": responseText (not wrapped in SSE)
    res.json({ type: 'text', content: responseText });
  } catch (error) {
    console.error('[Groq] Error:', error.message);
    res.status(500).json({ error: error.message });
  }
});

app.listen(6002, () => {
  console.log('[Groq LLM Provider] Running on port 6002');
});
```

### 2. avr-llm-groq/package.json

```json
{
  "name": "avr-llm-groq",
  "version": "1.0.0",
  "description": "AVR LLM Provider for Groq (OpenAI-compatible)",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "openai": "^4.20.0"
  }
}
```

### 3. avr-llm-groq/Dockerfile

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --only=production
COPY . .
EXPOSE 6002
CMD ["node", "index.js"]
```

### 4. docker-compose-avr-bots.yml (LLM Section)

```yaml
avr-llm:
  image: avr-llm-groq:latest
  platform: linux/x86_64
  container_name: avr-llm-groq
  restart: always
  environment:
    - PORT=6002
    - GROQ_API_KEY=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
    - GROQ_MODEL=llama-3.3-70b-versatile
    - TEMPERATURE=0.6
  networks:
    - avr-net
```

## Build & Deploy Commands

```bash
# Build Groq LLM provider
cd /home/user/Desktop/Projects_Organized/02_AVR_Voice_Platform/avr-app/custom-providers/avr-llm-groq
docker build -t avr-llm-groq:latest .

# Deploy (single bot)
cd /home/user/Desktop/Projects_Organized/01_Exodus_Dialer/exodus-kali-deploy
docker-compose -f docker-compose-avr-bots.yml up -d avr-llm avr-bot-9092

# Test call
docker exec ava-asterisk asterisk -rx "channel originate PJSIP/+13057768712@twilio extension 9092@audiosocket-dial"

# Check logs
docker logs avr-bot-9092 --tail 50
docker logs avr-llm-groq --tail 20
docker logs avr-tts-edge --tail 20
```

## Expected Log Output (Success)

**Bot logs:**
```
[INFO]: Received data from external asr service: yes i did
[INFO]: Sends transcript from ASR to LLM: yes i did
[INFO]: Received data from LLM service: {"type":"text","content":"That's great to hear..."}
[INFO]: Handling text content: That's great to hear...
[INFO]: Sends text from LLM to TTS: That's great to hear...
[INFO]: LLM streaming complete
```

**Groq logs:**
```
[Groq] /prompt-stream with 2 messages
[Groq] Response: That's great to hear that you were able to secure...
```

**TTS logs:**
```
[Edge TTS] Generating audio for: "That's great to hear..."
[Edge TTS] Converted to 8kHz LINEAR16 PCM
```

## Critical Troubleshooting

### If you see "Unknown data type: undefined"
- Response format is wrong
- Must be: `{ type: 'text', content: '...' }`

### If you see "Error parsing LLM service response: SyntaxError"
- You're sending SSE format with `data:` prefix
- AVR Core tries to JSON.parse() it directly
- Remove SSE headers and use plain `res.json()`

### If intro plays but bot goes silent
- LLM→TTS handoff broken
- Check LLM response format
- Verify TTS receives text (check TTS logs)

## Cost Analysis

| Component | Provider | Cost | Notes |
|-----------|----------|------|-------|
| LLM | Groq | **FREE** | llama-3.3-70b-versatile |
| ASR | Deepgram | $0.26/hr | User has credits |
| TTS | Edge | **FREE** | Unofficial Microsoft API |
| **Total** | | **$0.26/hr** | Per bot |

**20 bots**: $5.20/hour (only ASR costs)

## Success Metrics (2025-11-07)

- ✅ Intro plays perfectly
- ✅ ASR transcribes user speech
- ✅ Groq LLM generates responses (llama-3.3-70b)
- ✅ **TTS receives LLM responses** (THE KEY FIX)
- ✅ Edge TTS generates audio
- ✅ Multi-turn conversation works
- ✅ User hears bot respond naturally
- ✅ No "Unknown data type" errors
- ✅ No JSON parsing errors
- ✅ Complete bidirectional audio flow

## What Changed to Make It Work

**Failed Attempts**:
1. `{ response: text }` - Unknown data type error
2. `{ content: text }` - Unknown data type error
3. SSE format: `data: {"content": "..."}\n\n` - JSON parse error
4. SSE format: `data: {"type":"text","content":"..."}\n\n` - JSON parse error

**Working Solution**:
```javascript
res.json({ type: 'text', content: responseText })
```

**Why It Works**:
- AVR Core in buffered mode expects plain parseable JSON
- Requires `type` field to identify content type
- Requires `content` field with the actual text
- NO SSE wrapping for buffered responses
- Uses official OpenAI SDK format (Groq compatible)

## Backup Location

All working files backed up to:
- **Directory**: `/home/user/Desktop/Projects_Organized/02_AVR_Voice_Platform/WORKING_CONFIGS_BACKUP/`
- **Groq Provider**: `avr-llm-groq_WORKING/`
- **Docker Compose**: `docker-compose-avr-bots_WORKING.yml`
- **This Document**: `WORKING_CONFIGURATION.md`

## DO NOT CHANGE

This exact configuration achieves perfect LLM→TTS handoff. Any changes to the response format may break the pipeline. If you need to modify:

1. Make a backup first
2. Test on single bot (9092) before scaling
3. Verify logs show "Sends text from LLM to TTS"
4. Confirm TTS generates audio

**Last Verified Working**: 2025-11-07 at 19:51 UTC
**Test Results**: User confirmed "working perfectly"
