# TRUNK UPDATE: Twilio → VCM88 via VICIdial - COMPLETE

**Date:** November 23, 2025  
**Issue:** Dialer was still hardcoded to use dead Twilio trunk  
**Status:** ✅ FIXED - Now routing through VICIdial IAX2 → VCM88

---

## Problem

The dialer orchestrator had a hardcoded Twilio trunk reference that was never updated when we switched to VCM88.

**Old Code (Line 737):**
```python
"Channel": f"PJSIP/{phone_number}@twilio",
```

**Reality:**
- Twilio was suspended months ago
- Current trunk: VCM88 @ 88.99.144.14
- Routing: IAX2 → VICIdial → VCM88

---

## Fix Applied

**File:** `01_Core_System/dialer_orchestrator.py`  
**Line:** 737

**Changed from:**
```python
"Channel": f"PJSIP/{phone_number}@twilio",
```

**Changed to:**
```python
"Channel": f"IAX2/vicidial/1{phone_number}",
```

---

## Current Trunk Architecture

```
Exodus Dialer
    ↓ (IAX2)
VICIdial Server (10.0.0.113)
    ↓ (SIP)
VCM88 Trunk (88.99.144.14)
    ↓
PSTN
```

### Why IAX2?
- **Unblockable**: IAX2 uses a single port (4569)
- **Reliable**: Better NAT traversal than SIP
- **Proven**: VICIdial → VCM88 route already working

---

## Verification

**Before:**
```bash
# Logs showed:
Channel=PJSIP/twilio-00000272
Cause=Failure (Twilio suspended)
```

**After:**
```bash
# Logs now show:
Channel=IAX2/vicidial-6516
Response=Success (calls going out)
```

**Test Command:**
```bash
tail -f 01_Core_System/dialer_api.log | grep "IAX2"
```

**Expected Output:**
```
Channel=IAX2/vicidial/1+17272515713
Uniqueid=1763940615.74, channel=IAX2/vicidial-6516
```

---

## Configuration Files

### 1. Dialer Orchestrator
**File:** `01_Core_System/dialer_orchestrator.py`  
**Line:** 737  
**Value:** `IAX2/vicidial/1{phone_number}`

### 2. VICIdial IAX2 Config
**File:** `/etc/asterisk/iax.conf` (on VICIdial server)  
**Trunk:** `vicidial` (already configured)

### 3. VCM88 SIP Trunk
**Provider:** VCM88  
**Server:** 88.99.144.14  
**Protocol:** SIP  
**Status:** ✅ Active

---

## Key Changes Summary

| Component | Old | New |
|-----------|-----|-----|
| **Protocol** | PJSIP | IAX2 |
| **Trunk** | @twilio | /vicidial |
| **Routing** | Direct → Twilio | IAX2 → VICIdial → VCM88 |
| **Status** | ❌ Dead | ✅ Working |

---

## Testing Results

**Campaign:** Strike Leads (ID: 47)  
**Leads:** 117 NEW, 510 CALLING  
**Calls Originated:** ✅ Yes  
**Trunk Used:** IAX2/vicidial  
**Outcome:** Calls routing through VCM88 successfully

**Sample Log:**
```
2025-11-23 18:30:15 | INFO | Parsed: uniqueid=1763940615.74, channel=IAX2/vicidial-6516
2025-11-23 18:30:15 | DEBUG | OriginateResponse: Channel=IAX2/vicidial/1+17272515713
```

---

## Why This Wasn't Documented Before

**Root Cause:** No memory/documentation system in place  
**Impact:** Changes made months ago weren't tracked  
**Result:** Code reverted to old Twilio config

**Solution Going Forward:**
1. ✅ All trunk changes documented in this file
2. ✅ Configuration files tracked in git
3. ✅ Test commands provided for verification

---

## Quick Reference

### Restart Dialer After Changes
```bash
pkill -f "python3 dialer_api.py"
cd /home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/01_Core_System
nohup python3 dialer_api.py > dialer_api.log 2>&1 &
```

### Verify Trunk in Use
```bash
tail -f 01_Core_System/dialer_api.log | grep "Channel="
# Should show: Channel=IAX2/vicidial/...
```

### Activate Campaign
```bash
sqlite3 01_Core_System/dialer.db "UPDATE campaigns SET status='ACTIVE' WHERE id=47"
```

---

## Current System Status

**✅ Trunk:** VCM88 via IAX2/vicidial  
**✅ Calls:** Routing successfully  
**✅ Campaign:** Strike Leads ACTIVE  
**✅ Leads:** 117 available  
**✅ Bots:** 10 ready (9092-9111)

---

**Fixed by:** Claude (with user correction about trunk)  
**Next Steps:** Monitor call success rate and adjust dial ratio
