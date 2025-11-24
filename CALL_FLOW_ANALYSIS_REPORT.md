# Call Flow Analysis Report - Audio & Connection Issues

**Analysis Date:** November 24, 2025
**System:** Exodus Dialer with Asterisk AudioSocket Integration

---

## EXECUTIVE SUMMARY

Found **7 CRITICAL issues** and **5 MODERATE issues** in the call flow that could cause "no audio" or connection failures. The most severe problems are:

1. **Race condition in bot assignment** (CRITICAL)
2. **Missing Answer() in wait extension** (CRITICAL) 
3. **Duplicate Answer() calls in dialplan** (CRITICAL)
4. **AudioSocket connection timing issues** (CRITICAL)
5. **TCP Redirect before Answer()** (MODERATE-HIGH)

---

## CRITICAL ISSUES

### 1. ⚠️ RACE CONDITION: Bot Assignment Happens BEFORE Call Answers
**Location:** `dialer_orchestrator.py:814-836`
**Severity:** CRITICAL - Can cause audio routing to wrong bot or no bot

**Problem:**
```python
# Line 814-836: Bot assigned in OriginateResponse (when Asterisk INITIATES the call)
if response == "Success" and uniqueid:
    bot_port = await self.bot_pool.get_idle_bot_port(call_uuid=uniqueid)
    if bot_port:
        call_attempt.bot_port = bot_port
        call_attempt.status = "ANSWERED"  # ❌ WRONG - call hasn't answered yet!
        await self._bridge_to_bot(channel, bot_port)
```

**Timeline Issue:**
```
1. Asterisk sends Originate command → OriginateResponse "Success" 
2. Bot assigned and status="ANSWERED" ← TOO EARLY!
3. Call is still RINGING (not answered)
4. Later: Newstate State=6 (actual answer) ← Bot already assigned
```

**Why This Breaks:**
- OriginateResponse "Success" means Asterisk **accepted** the originate request, NOT that the call answered
- If lead doesn't answer, you've wasted a bot that's sitting idle waiting
- If lead DOES answer, the Redirect happens immediately with no Answer() first
- AudioSocket connection starts before call is fully established

**Fix Required:**
Move bot assignment to `_handle_call_state_change()` when `ChannelState=6` (Up/Answered):
```python
# In _handle_originate_response - just track the call
if response == "Success" and uniqueid:
    call_attempt.uniqueid = uniqueid
    call_attempt.channel_id = channel
    call_attempt.status = "DIALING"  # ✅ Correct state
    self.active_calls[uniqueid] = call_attempt
    # NO bot assignment here!

# In _handle_call_state_change - assign bot when ACTUALLY answered
if channel_state == "6":  # Up = Answered
    call_attempt = self.active_calls.get(uniqueid)
    if call_attempt and call_attempt.status == "DIALING":
        bot_port = await self.bot_pool.get_idle_bot_port(call_uuid=uniqueid)
        if bot_port:
            call_attempt.bot_port = bot_port
            call_attempt.status = "ANSWERED"
            await self._bridge_to_bot(channel, bot_port)
```

---

### 2. ⚠️ WAIT EXTENSION NEVER ANSWERS THE CALL
**Location:** `extensions.conf:82-84`
**Severity:** CRITICAL - Call stays in "Ringing" state forever

**Current Code:**
```asterisk
exten => wait,1,NoOp(Call dialing, waiting for answer)
 same => n,Wait(30)  ; ❌ Wait() doesn't answer the call!
 same => n,Hangup()
```

**Problem:**
- `Wait(30)` pauses dialplan execution but does **NOT answer the call**
- Call remains in "Ringing" state
- Customer hears ringing, system thinks it's dialing
- After 30 seconds, call hangs up with no audio ever

**Why This Matters:**
Every outbound call goes through this extension first:
```python
# dialer_orchestrator.py:738-741
"Context": self.asterisk_context,  # "audiosocket-dial"
"Exten": "wait",  # ← Goes here FIRST
"Priority": "1",
```

**Fix Required:**
```asterisk
exten => wait,1,NoOp(Call dialing, waiting for orchestrator to bridge)
 same => n,Answer()  ; ✅ MUST ANSWER THE CALL
 same => n,Wait(30)  ; Wait for Redirect from orchestrator
 same => n,Hangup()
```

---

### 3. ⚠️ DUPLICATE Answer() IN BOT EXTENSIONS
**Location:** `extensions.conf:93-112` (and all bot extensions)
**Severity:** CRITICAL - Causes race conditions and audio drops

**Current Code:**
```asterisk
exten => 9092,1,NoOp(Bridging to bot on port 9092)
 same => n,Answer()  ; ❌ Call was already answered in wait extension!
 same => n,Set(CALL_ID=${UNIQUEID}_bot9092)
 same => n,Set(RECORDING_FILE=/var/spool/asterisk/monitor/...)
 same => n,Set(AUDIOHOOK_INHERIT(MixMonitor)=yes)
 same => n,MixMonitor(${RECORDING_FILE})
 same => n,AudioSocket(${UNIQUEID},127.0.0.1:9092)  ; ← Audio starts HERE
```

**Problem:**
- If call is already answered, second `Answer()` does nothing (benign case)
- If call is NOT answered yet (race condition), this answers it at wrong time
- AudioSocket expects call to be answered BEFORE it connects
- MixMonitor may miss first 100-500ms of audio

**Timeline:**
```
1. Call reaches "wait" extension → Answer()
2. Orchestrator Redirects to "9092" extension
3. Second Answer() called (redundant or race condition)
4. MixMonitor started
5. AudioSocket connects ← Audio may have already started
```

**Fix Required:**
```asterisk
exten => 9092,1,NoOp(Bridging to bot on port 9092)
 same => n,Set(CALL_ID=${UNIQUEID}_bot9092)
 same => n,Set(RECORDING_FILE=/var/spool/asterisk/monitor/${STRFTIME(,,%Y-%m-%d)}/${STRFTIME(,,%H-%M-%S)}_${CALLERID(num)}_bot9092_${UNIQUEID}.wav)
 same => n,Set(AUDIOHOOK_INHERIT(MixMonitor)=yes)
 same => n,MixMonitor(${RECORDING_FILE},b)  ; Start BEFORE AudioSocket
 same => n,AudioSocket(${UNIQUEID},127.0.0.1:9092)
 same => n,StopMixMonitor()
 same => n,Hangup()
```

**Remove all duplicate Answer() calls** from bot extensions.

---

### 4. ⚠️ AUDIOSOCKET CONNECTION TIMING RACE
**Location:** `dialer_orchestrator.py:1024-1049` and `audiosocket_transport.py:388-469`
**Severity:** CRITICAL - Bot may not be ready when call connects

**Flow:**
```python
# dialer_orchestrator.py:834
await self._bridge_to_bot(channel, bot_port)  # Redirect to AudioSocket

# This immediately does:
await self.ami.send_action({
    "Action": "Redirect",
    "Channel": channel_id,
    "Context": self.asterisk_context,
    "Exten": str(bot_port),  # "9092"
    "Priority": "1",
})
```

**Then Asterisk:**
```asterisk
; extensions.conf:92-100
exten => 9092,1,NoOp(...)
 same => n,Answer()  ; May not be answered yet!
 same => n,AudioSocket(${UNIQUEID},127.0.0.1:9092)  ; Connects NOW
```

**Bot side:**
```python
# audiosocket_transport.py:388-390
async def _client_handler(self, reader, writer):
    """Handle incoming Asterisk connection."""
    # TCP server waits for connection
    # May take 50-200ms for bot to accept connection
```

**Race Condition Timeline:**
```
T+0ms:   Redirect command sent
T+5ms:   Asterisk executes AudioSocket() 
T+5ms:   Asterisk tries TCP connect to bot port
T+10ms:  Bot accepts connection (if ready)
T+15ms:  Bot reads UUID packet
T+20ms:  Bot starts audio stream
         ↓
         If bot not ready: ConnectionRefused
         If bot slow: 100-500ms audio silence
```

**Fix Required:**
Add bot health check BEFORE assigning:
```python
async def _is_bot_ready(self, bot_port: int) -> bool:
    """Check if bot is ready to accept AudioSocket connection."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        result = sock.connect_ex(('127.0.0.1', bot_port))
        sock.close()
        return result == 0
    except:
        return False

# In bot assignment:
bot_port = await self.bot_pool.get_idle_bot_port(call_uuid=uniqueid)
if bot_port:
    # Verify bot is actually listening
    if not await self._is_bot_ready(bot_port):
        logger.error(f"Bot {bot_port} not ready - dropping call")
        # Hangup and mark dropped
```

---

### 5. ⚠️ EMPTY PRIORITY LINES IN DIALPLAN
**Location:** `extensions.conf:105, 117, 129, etc.`
**Severity:** MODERATE-HIGH - Causes dialplan parsing errors

**Current Code:**
```asterisk
exten => 9093,1,NoOp(Bridging to bot on port 9093)
 same => n,Answer()
 same => n,  ; ❌ EMPTY LINE - syntax error!
 same => n,Set(CALL_ID=${UNIQUEID}_bot9093)
```

**Problem:**
- Empty `same => n,` lines cause Asterisk to skip priorities
- Can cause "Priority not found" errors
- Dialplan may jump to wrong step
- Inconsistent behavior across extensions

**Fix:**
Remove all empty priority lines. If they're placeholders, use NoOp:
```asterisk
exten => 9093,1,NoOp(Bridging to bot on port 9093)
 same => n,Answer()
 same => n,NoOp(Placeholder for future code)
 same => n,Set(CALL_ID=${UNIQUEID}_bot9093)
```

---

## MODERATE ISSUES

### 6. 🔶 Redirect Happens Before Call Is Fully Answered
**Location:** `dialer_orchestrator.py:1041-1049`
**Severity:** MODERATE - May cause audio to start before channel is ready

**Problem:**
```python
async def _bridge_to_bot(self, channel_id: str, bot_port: int):
    """Bridge answered call to bot instance via AudioSocket."""
    # No check if call is actually answered!
    await self.ami.send_action({
        "Action": "Redirect",
        "Channel": channel_id,
        "Context": self.asterisk_context,
        "Exten": str(bot_port),
        "Priority": "1",
    })
```

**Fix:**
Add channel state verification:
```python
async def _bridge_to_bot(self, channel_id: str, bot_port: int):
    # Verify channel is Up before redirecting
    status = await self.ami.send_action({
        "Action": "Status",
        "Channel": channel_id
    })
    
    if status.get("ChannelStateDesc") != "Up":
        logger.warning(f"Channel {channel_id} not Up yet, waiting...")
        await asyncio.sleep(0.1)
    
    await self.ami.send_action({
        "Action": "Redirect",
        "Channel": channel_id,
        "Context": self.asterisk_context,
        "Exten": str(bot_port),
        "Priority": "1",
    })
```

---

### 7. 🔶 No Timeout on AudioSocket Connection
**Location:** `extensions.conf:98`
**Severity:** MODERATE - Call can hang forever if bot crashes

**Current Code:**
```asterisk
 same => n,AudioSocket(${UNIQUEID},127.0.0.1:9092)  ; No timeout!
 same => n,StopMixMonitor()
```

**Problem:**
- If bot crashes or hangs, AudioSocket blocks forever
- Call stays connected but silent
- Wastes trunk capacity and bot slots

**Fix:**
Add timeout to AudioSocket (Asterisk 16+):
```asterisk
 same => n,Set(TIMEOUT(absolute)=300)  ; 5 minute max call
 same => n,AudioSocket(${UNIQUEID},127.0.0.1:9092)
 same => n,StopMixMonitor()
 same => n,Hangup()
```

---

### 8. 🔶 Bot Priming Happens After Bridge
**Location:** `dialer_orchestrator.py:822-830`
**Severity:** MODERATE - First 500ms of audio may be silent

**Current Code:**
```python
call_attempt.bot_port = bot_port
call_attempt.status = "ANSWERED"
await self._bridge_to_bot(channel, bot_port)  # Call connected NOW

# THEN prime the bot (too late!)
try:
    import requests
    requests.get(f"http://localhost:{bot_port}/ready", timeout=3)
    logger.debug(f"   🔥 Bot {bot_port} primed")
except Exception as e:
    logger.warning(f"   Bot {bot_port} prime failed: {e}")
```

**Problem:**
- Bot gets primed AFTER call is already connected
- First 500ms may have silence while bot initializes
- Creates awkward "dead air" at start of call

**Fix:**
Prime bot BEFORE assigning:
```python
# Prime bot first
try:
    requests.get(f"http://localhost:{bot_port}/ready", timeout=1)
    await asyncio.sleep(0.1)  # Let bot fully initialize
except Exception as e:
    logger.warning(f"Bot {bot_port} not ready: {e}")
    return None  # Don't use this bot

# Then assign and bridge
call_attempt.bot_port = bot_port
call_attempt.status = "ANSWERED"
await self._bridge_to_bot(channel, bot_port)
```

---

### 9. 🔶 AudioSocket Keepalive Starts Immediately
**Location:** `audiosocket_transport.py:616-621`
**Severity:** MODERATE - Sends silence before call audio starts

**Current Code:**
```python
# Start keepalive player - prevents buffer starvation
self._keepalive = AudioKeepalivePlayer(writer)
await self._keepalive.start()  # Starts sending silence NOW
```

**Problem:**
- Keepalive starts sending 20ms silence frames at 50 FPS immediately
- First real audio from TTS may be 500-1000ms later
- Lead hears dead air for first second of call

**Fix:**
Delay keepalive until first real audio frame:
```python
self._keepalive = AudioKeepalivePlayer(writer)
self._keepalive_started = False

# In write_audio_frame():
if not self._keepalive_started:
    await self._keepalive.start()
    self._keepalive_started = True
```

---

### 10. 🔶 No Validation of DIDlogic Trunk Channel
**Location:** `dialer_orchestrator.py:738`
**Severity:** MODERATE - May dial invalid channels

**Current Code:**
```python
"Channel": f"PJSIP/{phone_number}@didlogic",  # No validation
```

**Problem:**
- If DIDlogic trunk is down, Asterisk returns confusing error
- If phone number is invalid format, call fails silently
- No check if trunk has available channels

**Fix:**
Add trunk availability check:
```python
async def _is_trunk_available(self) -> bool:
    """Check if DIDlogic trunk has available channels."""
    try:
        response = await self.ami.send_action({
            "Action": "PJSIPShowEndpoint",
            "Endpoint": "didlogic"
        })
        return response.get("DeviceState") == "Not in use"
    except:
        return False

# Before originating:
if not await self._is_trunk_available():
    logger.error("DIDlogic trunk unavailable")
    return
```

---

## MINOR ISSUES

### 11. 📝 Channel Variables Not Used in Dialplan
**Location:** `dialer_orchestrator.py:744-749`

Variables are set but never referenced:
```python
"Variable": [
    f"LEAD_ID={lead['id']}",
    f"CAMPAIGN_ID={campaign_id}",
    f"PHONE_NUMBER={phone_number}",
    f"FIRST_NAME={lead.get('first_name', 'there')}",
],
```

These could be used in dialplan for routing or logging:
```asterisk
exten => wait,1,NoOp(Call for lead ${LEAD_ID} campaign ${CAMPAIGN_ID})
```

### 12. 📝 Recording Path Timezone Mismatch
**Location:** `dialer_orchestrator.py:1144-1160`

Complex timezone conversion that may cause recording file not found:
```python
# Asterisk container uses CET (UTC+1), host uses EST (UTC-5)
cet_offset = timedelta(hours=1)
asterisk_time = start_time + cet_offset + timedelta(hours=5)
```

Use consistent timezone across all systems.

---

## RECOMMENDED FIX PRIORITY

### Immediate (Deploy Today):
1. ✅ Fix wait extension - add Answer()
2. ✅ Remove duplicate Answer() from bot extensions
3. ✅ Move bot assignment to Newstate handler
4. ✅ Remove empty priority lines

### High Priority (This Week):
5. ✅ Add bot readiness check before assignment
6. ✅ Add channel state verification in _bridge_to_bot()
7. ✅ Prime bots before assigning calls

### Medium Priority (This Month):
8. ✅ Add AudioSocket timeout
9. ✅ Delay keepalive until first audio
10. ✅ Add trunk availability check

---

## TESTING CHECKLIST

After applying fixes, test:

```bash
# 1. Make test call
asterisk -rx "originate PJSIP/15615324683@didlogic extension wait@audiosocket-dial"

# 2. Verify bot assignment timing
grep "Bot.*assigned" /var/log/dialer.log | tail -20

# 3. Check for audio gaps
grep "audio frame" /var/log/bot_*.log | grep "frame 1 "

# 4. Verify recording captured
ls -lh /var/spool/asterisk/monitor/$(date +%Y-%m-%d)/

# 5. Check for dropped calls
grep "DROPPED" /var/log/dialer.log

# 6. Monitor AMI events
asterisk -rx "manager show eventq"
```

---

## ROOT CAUSE SUMMARY

The "no audio" issue is caused by a **timing cascade failure**:

1. Bot assigned too early (OriginateResponse instead of Newstate Up)
2. Call never properly answered (missing Answer() in wait extension)
3. Bridge attempted before call fully established
4. AudioSocket connection starts before bot ready
5. Multiple Answer() calls cause race conditions

**Fix all 5 issues together** - partial fixes may not resolve the problem.

---

## APPENDIX: Call Flow Diagrams

### Current (Broken) Flow:
```
1. Orchestrator → Asterisk: Originate(wait)
2. Asterisk → Orchestrator: OriginateResponse "Success"
3. Orchestrator: Assign bot 9092 ← TOO EARLY!
4. Orchestrator → Asterisk: Redirect(9092)
5. Asterisk: Execute AudioSocket(9092) ← Call may not be answered!
6. Customer: *ringing* or *dead air*
7. Bot: Waiting for connection...
8. [Race condition - audio lost]
```

### Correct Flow:
```
1. Orchestrator → Asterisk: Originate(wait)
2. Asterisk: Dials customer
3. Asterisk → wait extension: Answer() ← Call answered!
4. Asterisk → Orchestrator: Newstate State=6 (Up)
5. Orchestrator: Check bot ready
6. Orchestrator: Assign bot 9092 ← Correct timing!
7. Orchestrator → Asterisk: Redirect(9092)
8. Asterisk → Bot: AudioSocket connects
9. Bot → Customer: "Hey there, this is Ava..."
10. ✅ Audio flows both directions
```

---

**Report Generated:** November 24, 2025
**Analyst:** OpenCode AI Assistant
**System Version:** Exodus Dialer v2.x with Asterisk 20.x
