#!/bin/bash
# Exodus Dialer - Quick Start Script
# Starts all dialer components

echo "🚀 Starting Exodus Predictive Dialer..."
echo ""

# Check if Asterisk is running
if ! pgrep -x "asterisk" > /dev/null; then
    echo "❌ Asterisk is not running!"
    echo "   Start Asterisk first: sudo systemctl start asterisk"
    exit 1
fi

echo "✅ Asterisk is running"

# Check if pipecat environment exists
if [ ! -f "pipecat_env_new/bin/python3" ]; then
    echo "❌ Pipecat environment not found at pipecat_env_new/"
    exit 1
fi

echo "✅ Pipecat environment found"

# Check if database exists, if not create it
if [ ! -f "dialer.db" ]; then
    echo "📦 Initializing database..."
    pipecat_env_new/bin/python3 -c "from dialer_db import DialerDB; DialerDB('dialer.db')"
    echo "✅ Database initialized"
else
    echo "✅ Database exists"
fi

# Check if Asterisk dialplan is configured
if ! asterisk -rx "dialplan show audiosocket-dial" | grep -q "9092"; then
    echo "⚠️  WARNING: Asterisk dialplan not configured!"
    echo "   Add asterisk-dialer-config.conf to /etc/asterisk/extensions.conf"
    echo "   Then run: asterisk -rx 'dialplan reload'"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the dialer API (which starts bot pool and orchestrator)
echo ""
echo "🎯 Starting Dialer API..."
echo "   - Bot pool: 20 instances (ports 9092-9111)"
echo "   - Orchestrator: Predictive dialing engine"
echo "   - API server: http://localhost:8000"
echo "   - Dashboard: http://localhost:8000/dashboard"
echo ""
echo "📊 Dashboard will open in your browser..."
echo ""

# Open dashboard in browser (if in desktop environment)
if [ -n "$DISPLAY" ]; then
    sleep 3 && xdg-open "http://localhost:8000/dashboard" 2>/dev/null &
fi

# Start API
pipecat_env_new/bin/python3 dialer_api.py
