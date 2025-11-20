#!/bin/bash

echo "=== EXODUS PRODUCTION READINESS CHECK ==="
echo ""

# 1. Check Asterisk
echo "[1/8] Checking Asterisk..."
if docker exec ava-asterisk asterisk -rx "core show version" &>/dev/null; then
    echo "✅ Asterisk is running"
else
    echo "❌ Asterisk is DOWN"
    exit 1
fi

# 2. Check AMI connectivity
echo "[2/8] Checking AMI connectivity..."
if timeout 2 bash -c 'echo -e "Action: Login\r\nUsername: admin\r\nSecret: asterisk_admin_pwd\r\n\r\n" | nc localhost 5038' | grep -q "Success"; then
    echo "✅ AMI accessible"
else
    echo "❌ AMI not responding"
    exit 1
fi

# 3. Check bot containers
echo "[3/8] Checking AVR bot containers..."
BOT_COUNT=$(docker ps | grep -c "avr-bot-")
if [ "$BOT_COUNT" -eq 20 ]; then
    echo "✅ All 20 bots running"
else
    echo "⚠️  Only $BOT_COUNT/20 bots running"
fi

# 4. Check database
echo "[4/8] Checking database..."
cd /home/user/Desktop/Projects_Organized/01_Exodus_Dialer/exodus-kali-deploy
if sqlite3 dialer.db "SELECT COUNT(*) FROM campaigns" &>/dev/null; then
    echo "✅ Database accessible"
else
    echo "❌ Database error"
    exit 1
fi

# 5. Check for leads
echo "[5/8] Checking leads..."
NEW_LEADS=$(sqlite3 dialer.db "SELECT COUNT(*) FROM leads WHERE status='NEW'")
echo "   NEW leads: $NEW_LEADS"
if [ "$NEW_LEADS" -eq 0 ]; then
    echo "⚠️  No NEW leads - need to import or reset"
fi

# 6. Check Twilio SIP trunk
echo "[6/8] Checking Twilio SIP trunk..."
if docker exec ava-asterisk asterisk -rx "pjsip show endpoints" | grep -q "twilio.*Avail"; then
    echo "✅ Twilio trunk registered"
else
    echo "❌ Twilio trunk NOT registered"
fi

# 7. Check orchestrator
echo "[7/8] Checking orchestrator..."
if pgrep -f "dialer_orchestrator.py" > /dev/null; then
    echo "✅ Orchestrator running"
else
    echo "❌ Orchestrator NOT running"
fi

# 8. Check API
echo "[8/8] Checking API..."
if pgrep -f "dialer_api.py" > /dev/null; then
    API_PID=$(pgrep -f "dialer_api.py")
    echo "✅ API running (PID: $API_PID)"
else
    echo "❌ API NOT running"
fi

echo ""
echo "=== CHECK COMPLETE ==="
