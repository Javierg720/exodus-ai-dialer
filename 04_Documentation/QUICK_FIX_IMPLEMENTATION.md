# Exodus Dialer - Quick Fix Implementation Guide
**IMMEDIATE ACTIONS TO RESTORE FUNCTIONALITY**

---

## 🚨 CRITICAL: DO THESE FIRST (30 minutes)

### Step 1: Stop Broken Orchestrator
```bash
cd /home/user/Desktop/Projects_Organized/01_Exodus_Dialer/exodus-kali-deploy

# Kill any running orchestrator
pkill -f dialer_orchestrator.py

# Verify it's stopped
ps aux | grep dialer_orchestrator
```

### Step 2: Emergency Dial Ratio Reduction
```bash
# Reduce dial ratio to conservative safe levels
sqlite3 dialer.db "UPDATE campaigns SET dial_ratio=1.5, max_dial_ratio=2.0 WHERE id=47"

# Verify change
sqlite3 dialer.db "SELECT id, name, dial_ratio, max_dial_ratio FROM campaigns WHERE id=47"
# Expected output: 47|Strike Leads|1.5|2.0
```

### Step 3: Optimize SQLite Performance
```bash
# Run database optimization
sqlite3 dialer.db <<EOF
PRAGMA optimize;
PRAGMA wal_checkpoint(TRUNCATE);
PRAGMA synchronous=NORMAL;
.exit
EOF
```

### Step 4: Verify AVR Bots Running
```bash
# Count running AVR bots
docker ps | grep avr-bot | wc -l
# Should show: 20

# If less than 20, start all bots
docker-compose -f docker-compose-avr-bots.yml up -d

# Wait 30 seconds, then verify
sleep 30
docker ps | grep avr-bot | wc -l
```

---

## 📝 IMPLEMENT BOT POOL ADAPTER (1 hour)

### Create Bot Pool Interface

**File**: `bot_pool_interface.py`

```bash
cat > bot_pool_interface.py << 'EOF'
#!/usr/bin/env python3
"""Abstract interface for bot pool implementations."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List

class BotPoolInterface(ABC):
    """Abstract interface for bot pool implementations."""

    @abstractmethod
    async def get_available_bot_count(self) -> int:
        """Return number of bots ready to accept calls."""
        pass

    @abstractmethod
    async def assign_bot(self, call_uuid: str) -> Optional[int]:
        """Assign an idle bot to a call. Returns bot port or None."""
        pass

    @abstractmethod
    async def release_bot(self, port: int, call_uuid: str) -> None:
        """Mark bot as idle after call ends."""
        pass

    @abstractmethod
    async def get_bot_status(self, port: int) -> Dict:
        """Get detailed status of specific bot."""
        pass

    @abstractmethod
    async def get_all_bots_status(self) -> List[Dict]:
        """Get status of all bots in pool."""
        pass
EOF
```

### Create AVR Bot Pool Implementation

**File**: `avr_bot_pool.py`

```bash
cat > avr_bot_pool.py << 'EOF'
#!/usr/bin/env python3
"""AVR Docker container bot pool implementation."""

import docker
import asyncio
from typing import Dict, Optional, List
from loguru import logger
from bot_pool_interface import BotPoolInterface

class AVRBotPool(BotPoolInterface):
    """Bot pool implementation for AVR Docker containers."""

    def __init__(self, port_range: tuple = (9092, 9111)):
        self.docker_client = docker.from_env()
        self.port_start, self.port_end = port_range
        self.bot_assignments: Dict[int, Optional[str]] = {}  # port -> call_uuid
        self.lock = asyncio.Lock()
        logger.info(f"🐳 AVR Bot Pool initialized: ports {port_range[0]}-{port_range[1]}")

    async def get_available_bot_count(self) -> int:
        """Count AVR containers that are running and idle."""
        count = 0
        async with self.lock:
            for port in range(self.port_start, self.port_end + 1):
                try:
                    container_name = f"avr-bot-{port}"
                    container = self.docker_client.containers.get(container_name)

                    # Check if running
                    if container.status != "running":
                        continue

                    # Check if idle
                    if self.bot_assignments.get(port) is None:
                        count += 1

                except docker.errors.NotFound:
                    continue
                except Exception as e:
                    logger.debug(f"Error checking bot {port}: {e}")

        logger.debug(f"📊 Available AVR bots: {count}")
        return count

    async def assign_bot(self, call_uuid: str) -> Optional[int]:
        """Assign first available AVR bot to call."""
        async with self.lock:
            for port in range(self.port_start, self.port_end + 1):
                try:
                    # Check if bot is idle
                    if self.bot_assignments.get(port) is not None:
                        continue

                    # Check container is running
                    container_name = f"avr-bot-{port}"
                    container = self.docker_client.containers.get(container_name)

                    if container.status == "running":
                        # Assign this bot
                        self.bot_assignments[port] = call_uuid
                        logger.info(f"🤖 Assigned AVR bot {port} to call {call_uuid}")
                        return port

                except docker.errors.NotFound:
                    continue
                except Exception as e:
                    logger.debug(f"Error assigning bot {port}: {e}")

        logger.warning(f"⚠️ No available AVR bots for call {call_uuid}")
        return None

    async def release_bot(self, port: int, call_uuid: str) -> None:
        """Release bot back to idle pool."""
        async with self.lock:
            if self.bot_assignments.get(port) == call_uuid:
                self.bot_assignments[port] = None
                logger.info(f"🔓 Released AVR bot {port} from call {call_uuid}")
            else:
                logger.debug(f"Bot {port} not assigned to call {call_uuid}")

    async def get_bot_status(self, port: int) -> Dict:
        """Get detailed status of specific AVR bot."""
        try:
            container_name = f"avr-bot-{port}"
            container = self.docker_client.containers.get(container_name)

            return {
                "port": port,
                "status": "BUSY" if self.bot_assignments.get(port) else "IDLE",
                "container_status": container.status,
                "call_uuid": self.bot_assignments.get(port),
                "container_id": container.short_id,
                "type": "avr"
            }
        except docker.errors.NotFound:
            return {
                "port": port,
                "status": "CRASHED",
                "container_status": "not_found",
                "call_uuid": None,
                "container_id": None,
                "type": "avr"
            }

    async def get_all_bots_status(self) -> List[Dict]:
        """Get status of all AVR bots."""
        statuses = []
        for port in range(self.port_start, self.port_end + 1):
            status = await self.get_bot_status(port)
            statuses.append(status)
        return statuses

    async def close(self):
        """Cleanup resources."""
        # Docker client doesn't need explicit cleanup
        pass
EOF
```

### Test Bot Pool Adapter

```bash
cat > test_avr_pool.py << 'EOF'
#!/usr/bin/env python3
"""Test AVR bot pool implementation."""

import asyncio
from avr_bot_pool import AVRBotPool

async def test_bot_pool():
    print("🧪 Testing AVR Bot Pool...")

    pool = AVRBotPool()

    # Test 1: Count available bots
    count = await pool.get_available_bot_count()
    print(f"✅ Available bots: {count}")
    assert count > 0, "❌ No bots available"

    # Test 2: Assign bot
    port = await pool.assign_bot("test-call-123")
    print(f"✅ Assigned bot: {port}")
    assert port is not None, "❌ Bot assignment failed"

    # Test 3: Check assignment
    status = await pool.get_bot_status(port)
    print(f"✅ Bot status: {status}")
    assert status["call_uuid"] == "test-call-123", "❌ Assignment not tracked"

    # Test 4: Count again (should be 1 less)
    count2 = await pool.get_available_bot_count()
    print(f"✅ Available after assignment: {count2}")
    assert count2 == count - 1, "❌ Count not decremented"

    # Test 5: Release bot
    await pool.release_bot(port, "test-call-123")
    status = await pool.get_bot_status(port)
    print(f"✅ Bot released: {status}")
    assert status["call_uuid"] is None, "❌ Bot not released"

    # Test 6: Count restored
    count3 = await pool.get_available_bot_count()
    print(f"✅ Available after release: {count3}")
    assert count3 == count, "❌ Count not restored"

    print("\n🎉 All tests passed!")

asyncio.run(test_bot_pool())
EOF

# Run test
python3 test_avr_pool.py
```

---

## 🔧 UPDATE ORCHESTRATOR (30 minutes)

### Modify Orchestrator to Use Bot Pool Interface

```bash
# Backup current version
cp dialer_orchestrator.py dialer_orchestrator.py.backup-before-avr-fix

# Apply changes (manual edit required - see below)
```

**Edit `dialer_orchestrator.py`**:

**Line 32** - Add import:
```python
from avr_bot_pool import AVRBotPool
```

**Lines 388-396** - Replace with:
```python
# Get available bots from pool (works for both Pipecat and AVR)
available_bots = await self.bot_pool.get_available_bot_count()

if available_bots == 0:
    logger.debug(f"No available bots for campaign '{campaign_name}'")
    return
```

**Lines 645-646** - Update bot assignment:
```python
# Assign bot from pool
bot_port = await self.bot_pool.assign_bot(call_uuid=uniqueid)

if bot_port is None:
    logger.error(f"❌ No bot available for call {uniqueid} - DROPPING")
    # This is a drop event (call answered but no bot)
    await self._log_dropped_call(call_attempt, uniqueid)
    return
```

**After line 872** - Add bot release:
```python
# Release bot back to pool
if call_attempt.bot_port:
    await self.bot_pool.release_bot(
        port=call_attempt.bot_port,
        call_uuid=uniqueid
    )
```

### Create New Startup Script

**File**: `start_production_avr.sh`

```bash
cat > start_production_avr.sh << 'EOF'
#!/bin/bash
# Exodus Dialer - Production Startup with AVR Bot Pool

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  EXODUS DIALER - AVR PRODUCTION START"
echo "========================================"

# 1. Check Asterisk
echo "[1/4] Checking Asterisk..."
if ! docker ps | grep -q "ava-asterisk"; then
    docker start ava-asterisk
    sleep 5
fi
echo "  ✅ Asterisk running"

# 2. Check AVR bots
echo "[2/4] Checking AVR bots..."
BOT_COUNT=$(docker ps | grep -c "avr-bot-" || true)
if [ "$BOT_COUNT" -lt 20 ]; then
    echo "  Starting AVR bots..."
    docker-compose -f docker-compose-avr-bots.yml up -d
    sleep 10
fi
BOT_COUNT=$(docker ps | grep -c "avr-bot-" || true)
echo "  ✅ $BOT_COUNT/20 AVR bots running"

# 3. Start API
echo "[3/4] Starting API..."
if ! pgrep -f dialer_api.py > /dev/null; then
    nohup python3 dialer_api.py > api.out 2>&1 &
    sleep 3
fi
echo "  ✅ API running"

# 4. Start Orchestrator with AVR pool
echo "[4/4] Starting Orchestrator with AVR pool..."
if pgrep -f dialer_orchestrator.py > /dev/null; then
    echo "  Stopping old orchestrator..."
    pkill -f dialer_orchestrator.py
    sleep 2
fi

nohup python3 -c "
import asyncio
from dialer_orchestrator import DialerOrchestrator
from dialer_db_async import AsyncDialerDB
from avr_bot_pool import AVRBotPool

async def main():
    # Initialize database
    db = AsyncDialerDB('dialer.db')
    await db.init()

    # Initialize AVR bot pool
    bot_pool = AVRBotPool(port_range=(9092, 9111))

    # Initialize orchestrator with AVR pool
    orchestrator = DialerOrchestrator(
        db=db,
        bot_pool=bot_pool,
        ami_host='localhost',
        ami_port=5038,
        ami_username='ava',
        ami_password='ava123'
    )

    # Start orchestrator
    await orchestrator.start()

    # Run forever
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await orchestrator.stop()

asyncio.run(main())
" > orchestrator.out 2>&1 &

sleep 5
echo "  ✅ Orchestrator running (PID: $!)"

echo ""
echo "========================================"
echo "  ✅ SYSTEM READY WITH AVR BOTS"
echo "========================================"
echo ""
echo "Monitor: tail -f orchestrator.out"
echo "Status:  python3 test_avr_pool.py"
echo ""
EOF

chmod +x start_production_avr.sh
```

---

## ✅ VALIDATION (15 minutes)

### Test 1: Verify Bot Pool Working
```bash
python3 test_avr_pool.py
# Expected: All tests pass
```

### Test 2: Start System
```bash
./start_production_avr.sh

# Wait 30 seconds
sleep 30

# Check orchestrator is running
ps aux | grep dialer_orchestrator
# Should show: python3 -c ... (orchestrator running)
```

### Test 3: Monitor Logs
```bash
# Watch orchestrator logs
tail -f orchestrator.out

# You should see:
# - "AVR Bot Pool initialized: ports 9092-9111"
# - "Available AVR bots: 20"
# - "Assigned AVR bot 9092 to call 1763..."
# - No errors about "bot_pool is None"
```

### Test 4: Check Lead Progress
```bash
# Wait 5 minutes, then check
sqlite3 dialer.db "SELECT
    COUNT(*) as total,
    SUM(CASE WHEN status='NEW' THEN 1 ELSE 0 END) as new,
    SUM(CASE WHEN status='CALLING' THEN 1 ELSE 0 END) as calling,
    SUM(CASE WHEN status='COMPLETED' THEN 1 ELSE 0 END) as completed
FROM leads WHERE campaign_id=47"

# Expected progression:
# - NEW decreasing
# - CALLING shows active calls (0-20)
# - COMPLETED increasing
```

### Test 5: Verify No Over-Dialing
```bash
# Check dial attempts aren't exceeding bot count
tail -100 orchestrator.out | grep "placing.*calls"

# Should see lines like:
# "placing 5 calls (20 bots, 15 inflight...)"
# NOT:
# "placing 60 calls (20 bots, 0 inflight...)"  ⚠️ BAD
```

---

## 🎯 SUCCESS CRITERIA

Within 1 hour of starting:
- ✅ No orchestrator crashes
- ✅ Dial attempts ≤ 40 concurrent (2x dial ratio × 20 bots)
- ✅ Leads progressing from NEW → COMPLETED
- ✅ Logs show "Assigned AVR bot X to call..."

Within 24 hours:
- ✅ All 761 leads called
- ✅ Zero orchestrator downtime
- ✅ Drop rate < 3% (TCPA compliant)

---

## 🚨 TROUBLESHOOTING

### Problem: "No bots available"
```bash
# Check AVR containers
docker ps | grep avr-bot

# Restart if needed
docker-compose -f docker-compose-avr-bots.yml restart
```

### Problem: Orchestrator not starting
```bash
# Check for errors
tail -50 orchestrator.out

# Common fix: Kill conflicting process
pkill -f dialer_orchestrator.py
./start_production_avr.sh
```

### Problem: Still attempting 60 dials
```bash
# Verify dial ratio reduction worked
sqlite3 dialer.db "SELECT dial_ratio, max_dial_ratio FROM campaigns WHERE id=47"
# Should show: 1.5|2.0

# If not, run again:
sqlite3 dialer.db "UPDATE campaigns SET dial_ratio=1.5, max_dial_ratio=2.0 WHERE id=47"

# Restart orchestrator
pkill -f dialer_orchestrator.py
./start_production_avr.sh
```

### Problem: Database locked errors
```bash
# Optimize SQLite
sqlite3 dialer.db "PRAGMA wal_checkpoint(TRUNCATE); PRAGMA optimize;"

# Verify WAL mode
sqlite3 dialer.db "PRAGMA journal_mode"
# Should show: wal
```

---

## 📊 MONITORING COMMANDS

**Every 5 minutes, run**:
```bash
# Lead status distribution
sqlite3 dialer.db "SELECT status, COUNT(*) FROM leads WHERE campaign_id=47 GROUP BY status"

# Calls in last hour
sqlite3 dialer.db "SELECT COUNT(*) FROM call_log WHERE start_time > datetime('now', '-1 hour')"

# Bot utilization
python3 -c "
import asyncio
from avr_bot_pool import AVRBotPool

async def status():
    pool = AVRBotPool()
    bots = await pool.get_all_bots_status()
    busy = sum(1 for b in bots if b['status'] == 'BUSY')
    idle = sum(1 for b in bots if b['status'] == 'IDLE')
    print(f'Busy: {busy}, Idle: {idle}, Utilization: {busy/20*100:.1f}%')

asyncio.run(status())
"
```

---

## 🔄 ROLLBACK (if needed)

```bash
# Stop new system
pkill -f dialer_orchestrator.py

# Restore backup
cp dialer_orchestrator.py.backup-before-avr-fix dialer_orchestrator.py

# Restore dial ratio
sqlite3 dialer.db "UPDATE campaigns SET dial_ratio=2.0, max_dial_ratio=3.5 WHERE id=47"

# Start old way
nohup python3 dialer_orchestrator.py > orchestrator.out 2>&1 &
```

---

**Last Updated**: November 16, 2025
**Estimated Implementation Time**: 2 hours
**Required Downtime**: 5 minutes
