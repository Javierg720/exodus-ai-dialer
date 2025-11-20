#!/bin/bash
# Exodus Dialer - Status Check Script

echo "========================================"
echo "  EXODUS DIALER - STATUS"
echo "========================================"
echo ""

# Asterisk
echo "Asterisk:"
if docker exec ava-asterisk asterisk -rx "core show version" 2>/dev/null | grep -q "Asterisk"; then
    echo "  ✅ Running"
    CALLS=$(docker exec ava-asterisk asterisk -rx "core show channels" | grep "active call" | awk '{print $1}')
    echo "     Active calls: $CALLS"
else
    echo "  ❌ Not running"
fi
echo ""

# AVR Bots
echo "AVR Bots:"
BOT_COUNT=$(docker ps | grep -c "avr-bot-" || echo "0")
echo "  $BOT_COUNT/20 running"
echo ""

# Providers
echo "AVR Providers:"
for provider in avr-llm avr-asr-deepgram avr-tts-edge; do
    if docker ps | grep -q "$provider"; then
        echo "  ✅ $provider"
    else
        echo "  ❌ $provider"
    fi
done
echo ""

# Orchestrator
echo "Orchestrator:"
if pgrep -f "dialer_orchestrator.py" > /dev/null; then
    PID=$(pgrep -f "dialer_orchestrator.py")
    echo "  ✅ Running (PID: $PID)"
    if [ -f orchestrator.log ]; then
        echo "     Last log: $(tail -1 orchestrator.log)"
    fi
else
    echo "  ❌ Not running"
fi
echo ""

# API
echo "API:"
if pgrep -f "dialer_api.py" > /dev/null; then
    PID=$(pgrep -f "dialer_api.py")
    echo "  ✅ Running (PID: $PID)"
    echo "     URL: http://localhost:8000"
else
    echo "  ❌ Not running"
fi
echo ""

# Database stats
echo "Database:"
cd "$(dirname "${BASH_SOURCE[0]}")"
if [ -f dialer.db ]; then
    NEW=$(sqlite3 dialer.db "SELECT COUNT(*) FROM leads WHERE status='NEW'" 2>/dev/null)
    CALLING=$(sqlite3 dialer.db "SELECT COUNT(*) FROM leads WHERE status='CALLING'" 2>/dev/null)
    COMPLETED=$(sqlite3 dialer.db "SELECT COUNT(*) FROM leads WHERE status='COMPLETED'" 2>/dev/null)
    TOTAL=$(sqlite3 dialer.db "SELECT COUNT(*) FROM leads" 2>/dev/null)
    
    echo "  Total leads: $TOTAL"
    echo "  NEW: $NEW | CALLING: $CALLING | COMPLETED: $COMPLETED"
    
    ACTIVE_CAMPAIGNS=$(sqlite3 dialer.db "SELECT COUNT(*) FROM campaigns WHERE status='ACTIVE'" 2>/dev/null)
    echo "  Active campaigns: $ACTIVE_CAMPAIGNS"
fi
echo ""
