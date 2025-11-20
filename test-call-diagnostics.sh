#!/bin/bash

echo "=== Starting Call Diagnostics ==="
echo "Press Ctrl+C to stop monitoring"
echo ""

# Enable RTP debug
echo "Enabling RTP debug..."
docker exec ava-asterisk asterisk -rx "rtp set debug on" > /dev/null 2>&1

# Create temporary files for logs
ASTERISK_LOG=$(mktemp)
BOT_LOG=$(mktemp)
RTP_LOG=$(mktemp)

echo "Monitoring started. Make your call to 9092 now..."
echo ""

# Monitor in parallel
(
    while true; do
        docker exec ava-asterisk asterisk -rx "core show channels verbose" 2>/dev/null
        sleep 2
    done
) > "$ASTERISK_LOG" &
ASTERISK_PID=$!

docker logs -f avr-bot-9092 2>&1 > "$BOT_LOG" &
BOT_PID=$!

docker logs -f ava-asterisk 2>&1 | grep -i "rtp\|audio" > "$RTP_LOG" &
RTP_PID=$!

# Wait for interrupt
trap "echo ''; echo 'Stopping monitors...'; kill $ASTERISK_PID $BOT_PID $RTP_PID 2>/dev/null; docker exec ava-asterisk asterisk -rx 'rtp set debug off' > /dev/null 2>&1; echo ''; echo '=== ASTERISK CHANNELS ==='; tail -20 $ASTERISK_LOG; echo ''; echo '=== BOT LOGS ==='; tail -30 $BOT_LOG; echo ''; echo '=== RTP LOGS ==='; tail -20 $RTP_LOG; rm -f $ASTERISK_LOG $BOT_LOG $RTP_LOG; exit 0" SIGINT SIGTERM

wait
