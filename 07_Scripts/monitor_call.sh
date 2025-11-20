#!/bin/bash
# Multi-pane call monitoring

echo "🎯 Starting call monitoring..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Monitor ASR denoising in background
docker logs -f avr-asr-deepgram-denoised 2>&1 | grep --line-buffered -E "Denoised|text:|error" &
ASR_PID=$!

# Monitor bot 9092 in background
docker logs -f avr-bot-9092 2>&1 | grep --line-buffered -E "Received data|Sends|LLM|TTS" &
BOT_PID=$!

# Wait a bit for monitors to start
sleep 1

echo "✅ Monitors active (ASR PID: $ASR_PID, Bot PID: $BOT_PID)"
echo "🚀 Initiating call to +13057768712 via bot 9092..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Make the call
docker exec ava-asterisk asterisk -rx "channel originate PJSIP/+13057768712@twilio extension 9092@audiosocket-dial"

echo ""
echo "📞 Call initiated! Monitoring for 30 seconds..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Monitor for 30 seconds
sleep 30

# Kill monitors
kill $ASR_PID $BOT_PID 2>/dev/null

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Monitoring complete! Checking call log..."

# Check database for the call
sqlite3 /home/user/Desktop/Projects_Organized/01_Exodus_Dialer/exodus-kali-deploy/dialer.db << SQL
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━';
SELECT 'LATEST CALL LOG:';
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━';
SELECT 
  id,
  lead_id,
  call_status,
  duration_seconds,
  bot_port,
  SUBSTR(transcription_text, 1, 100) || '...' as transcript_preview
FROM call_log 
ORDER BY id DESC 
LIMIT 1;
SQL

