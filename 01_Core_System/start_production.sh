#!/bin/bash
# Exodus Dialer - Production Startup Script
# This script starts all components in the correct order with proper error handling

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  EXODUS DIALER - PRODUCTION STARTUP"
echo "========================================"
echo ""

# Function to check if process is running
is_running() {
    pgrep -f "$1" > /dev/null
}

# Function to wait for service
wait_for_service() {
    local service=$1
    local check_cmd=$2
    local max_wait=30
    local waited=0
    
    echo -n "Waiting for $service..."
    while ! eval "$check_cmd" &>/dev/null; do
        if [ $waited -ge $max_wait ]; then
            echo " TIMEOUT!"
            return 1
        fi
        sleep 1
        waited=$((waited + 1))
        echo -n "."
    done
    echo " OK"
    return 0
}

# 1. Check Asterisk
echo "[1/5] Checking Asterisk..."
if ! docker ps | grep -q "ava-asterisk"; then
    echo "  Starting Asterisk container..."
    docker start ava-asterisk
    wait_for_service "Asterisk" "docker exec ava-asterisk asterisk -rx 'core show version'"
fi
echo "  ✅ Asterisk running"

# 2. Check AVR infrastructure
echo "[2/5] Checking AVR infrastructure..."
BOT_COUNT=$(docker ps | grep -c "avr-bot-" || true)
if [ "$BOT_COUNT" -lt 20 ]; then
    echo "  ⚠️  Only $BOT_COUNT/20 bots running. Starting missing bots..."
    cd "$SCRIPT_DIR"
    docker-compose -f docker-compose-avr-bots.yml up -d
fi
echo "  ✅ AVR bots ready ($BOT_COUNT/20)"

# Check providers
if ! docker ps | grep -q "avr-llm"; then
    echo "  Starting AVR providers..."
    docker-compose -f docker-compose-avr-bots.yml up -d avr-llm avr-asr-deepgram avr-tts-edge
fi
echo "  ✅ AVR providers running"

# 3. Check database
echo "[3/5] Checking database..."
if ! sqlite3 dialer.db "SELECT COUNT(*) FROM campaigns" &>/dev/null; then
    echo "  ❌ Database error!"
    exit 1
fi
NEW_LEADS=$(sqlite3 dialer.db "SELECT COUNT(*) FROM leads WHERE status='NEW'")
echo "  ✅ Database OK ($NEW_LEADS NEW leads)"

if [ "$NEW_LEADS" -eq 0 ]; then
    echo "  ⚠️  WARNING: No NEW leads available!"
    echo "  Run: sqlite3 dialer.db \"UPDATE leads SET status='NEW', attempts=0 WHERE id IN (SELECT id FROM leads LIMIT 10)\""
fi

# 4. Start API
echo "[4/5] Starting API server..."
if is_running "dialer_api.py"; then
    echo "  API already running (PID: $(pgrep -f dialer_api.py))"
else
    nohup python3 dialer_api.py > api.log 2>&1 &
    API_PID=$!
    echo "  Started API (PID: $API_PID)"
    wait_for_service "API" "curl -s http://localhost:8000/health"
fi
echo "  ✅ API running on http://localhost:8000"

# 5. Start Orchestrator
echo "[5/5] Starting Orchestrator..."
if is_running "dialer_orchestrator.py"; then
    echo "  Orchestrator already running (PID: $(pgrep -f dialer_orchestrator.py))"
else
    nohup python3 dialer_orchestrator.py > orchestrator.log 2>&1 &
    ORCH_PID=$!
    echo "  Started Orchestrator (PID: $ORCH_PID)"
    sleep 3  # Give it time to initialize
fi
echo "  ✅ Orchestrator running"

echo ""
echo "========================================"
echo "  ✅ EXODUS DIALER IS READY"
echo "========================================"
echo ""
echo "Services:"
echo "  • API:          http://localhost:8000"
echo "  • Dashboard:    http://localhost:3003 (if running)"
echo "  • Logs:         tail -f api.log orchestrator.log"
echo ""
echo "Quick commands:"
echo "  • Check status:  ./check_status.sh"
echo "  • Stop all:      ./stop_production.sh"
echo "  • View logs:     tail -f orchestrator.log"
echo ""
