#!/bin/bash

echo "=== Call Diagnostics Monitor ==="
echo "Make your call to 9092 now..."
echo "Press Ctrl+C to stop"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "=== Stopping monitors ==="
    docker exec ava-asterisk asterisk -rx "rtp set debug off" > /dev/null 2>&1
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Enable RTP debug
docker exec ava-asterisk asterisk -rx "rtp set debug on" > /dev/null 2>&1

# Monitor Asterisk logs (filter for relevant lines)
echo "Monitoring Asterisk..."
docker logs -f --tail 0 ava-asterisk 2>&1 &

# Monitor bot logs
echo "Monitoring Bot..."
docker logs -f --tail 0 avr-bot-9092 2>&1 &

wait
