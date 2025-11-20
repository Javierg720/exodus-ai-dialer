#!/bin/bash
# Update AVR with custom Groq, Cerebras, and Edge TTS providers

set -e

API_URL="http://localhost:3000"

# Login
echo "🔐 Logging in to AVR..."
TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@agentvoiceresponse.com", "password": "agentvoiceresponse"}' \
  | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Login failed!"
  exit 1
fi

echo "✅ Logged in successfully"
echo ""

# Delete old providers
echo "🗑️  Deleting old providers..."
OLD_PROVIDERS=$(curl -s "$API_URL/providers" -H "Authorization: Bearer $TOKEN" | jq -r '.data[]?.id // empty')
for ID in $OLD_PROVIDERS; do
  curl -s -X DELETE "$API_URL/providers/$ID" \
    -H "Authorization: Bearer $TOKEN" > /dev/null
  echo "  - Deleted provider $ID"
done
echo ""

# Add Groq LLM Provider
echo "🚀 Adding Groq LLM Provider..."
GROQ_ID=$(curl -s -X POST "$API_URL/providers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Groq Llama 3.3 70B",
    "type": "LLM",
    "config": {
      "image": "avr-llm-groq:latest",
      "env": {
        "GROQ_API_KEY": "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",
        "GROQ_MODEL": "llama-3.3-70b-versatile",
        "TEMPERATURE": "0.7",
        "MAX_TOKENS": "500"
      }
    }
  }' | jq -r '.id')
echo "✅ Groq LLM Provider created (ID: $GROQ_ID)"
echo ""

# Add Cerebras LLM Provider
echo "🚀 Adding Cerebras LLM Provider..."
CEREBRAS_ID=$(curl -s -X POST "$API_URL/providers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cerebras Llama 3.3 70B",
    "type": "LLM",
    "config": {
      "image": "avr-llm-cerebras:latest",
      "env": {
        "CEREBRAS_API_KEY": "csk-45rkpchch265v85mj2e85pdtyj3pm8nmdyh85wyk82pprcc3",
        "CEREBRAS_MODEL": "llama-3.3-70b",
        "TEMPERATURE": "0.7",
        "MAX_TOKENS": "500"
      }
    }
  }' | jq -r '.id')
echo "✅ Cerebras LLM Provider created (ID: $CEREBRAS_ID)"
echo ""

# Add Deepgram ASR Provider
echo "🚀 Adding Deepgram ASR Provider..."
ASR_ID=$(curl -s -X POST "$API_URL/providers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deepgram ASR",
    "type": "ASR",
    "config": {
      "image": "agentvoiceresponse/avr-asr-deepgram:latest",
      "env": {
        "DEEPGRAM_API_KEY": "d8191ab87d6958ae361407d2e30d014b7f111cec",
        "DEEPGRAM_MODEL": "nova-2",
        "SPEECH_RECOGNITION_LANGUAGE": "en"
      }
    }
  }' | jq -r '.id')
echo "✅ Deepgram ASR Provider created (ID: $ASR_ID)"
echo ""

# Add Edge TTS Provider
echo "🚀 Adding Edge TTS Provider..."
TTS_ID=$(curl -s -X POST "$API_URL/providers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Edge TTS (FREE)",
    "type": "TTS",
    "config": {
      "image": "avr-tts-edge:latest",
      "env": {
        "VOICE": "en-US-AvaMultilingualNeural",
        "RATE": "+10%",
        "PITCH": "+2Hz"
      }
    }
  }' | jq -r '.id')
echo "✅ Edge TTS Provider created (ID: $TTS_ID)"
echo ""

echo "🎉 All providers configured!"
echo ""
echo "Provider IDs:"
echo "  - Groq LLM: $GROQ_ID"
echo "  - Cerebras LLM: $CEREBRAS_ID"
echo "  - Deepgram ASR: $ASR_ID"
echo "  - Edge TTS: $TTS_ID"
echo ""
echo "✨ Cost Breakdown:"
echo "  - Groq: ~\$0.05 per 1M tokens (super cheap!)"
echo "  - Cerebras: FREE (with your API key)"
echo "  - Deepgram STT: \$0.26/hour (you have credits)"
echo "  - Edge TTS: FREE (Microsoft unofficial API)"
echo ""
echo "Next steps:"
echo "1. Go to http://localhost:3001"
echo "2. Delete your old agent"
echo "3. Create a new agent with these providers:"
echo "   - ASR: Deepgram ASR"
echo "   - LLM: Groq Llama 3.3 70B (or Cerebras)"
echo "   - TTS: Edge TTS (FREE)"
echo "4. Click 'Run' and test!"
echo ""
echo "💡 Tip: Use Cerebras for complex conversations (FREE + powerful)"
echo "💡 Tip: Use Groq for faster responses (cheap + fast)"
