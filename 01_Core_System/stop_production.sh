#!/bin/bash
# Exodus Dialer - Production Shutdown Script

echo "========================================"
echo "  EXODUS DIALER - SHUTDOWN"
echo "========================================"
echo ""

# Stop orchestrator
echo "[1/3] Stopping Orchestrator..."
if pgrep -f "dialer_orchestrator.py" > /dev/null; then
    pkill -f "dialer_orchestrator.py"
    echo "  ✅ Orchestrator stopped"
else
    echo "  Already stopped"
fi

# Stop API
echo "[2/3] Stopping API..."
if pgrep -f "dialer_api.py" > /dev/null; then
    pkill -f "dialer_api.py"
    echo "  ✅ API stopped"
else
    echo "  Already stopped"
fi

# AVR bots stay running (they're lightweight)
echo "[3/3] AVR bots remain running (use docker-compose down to stop)"

echo ""
echo "✅ Shutdown complete"
echo ""
