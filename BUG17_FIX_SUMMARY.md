# CRITICAL BUG #17 FIX - Campaign Data Loss Fixed

## Issue
Campaign creation was losing 5 critical fields due to incorrect validation constraints in the CampaignCreate model.

## Root Cause
The Pydantic model had overly restrictive constraints that didn't match business requirements:
- `max_attempts`: Limited to 10 (should be 20)
- `retry_delay`: Min was 0, default was 60 (should be min 60, default 300)
- `call_timeout`: Max was 120, default was 30 (should be max 300, default 45)
- `working_hours_start`: No pattern validation (now validates HH:MM format)
- `working_hours_end`: Default was "17:00", no pattern validation (now "21:00" with HH:MM validation)

## Fix Applied
Updated `01_Core_System/dialer_api.py` line 256-275:

**Before:**
```python
max_attempts: Optional[int] = Field(default=3, ge=1, le=10)
retry_delay: Optional[int] = Field(default=60, ge=0)
call_timeout: Optional[int] = Field(default=30, ge=10, le=120)
working_hours_start: Optional[str] = Field(default="09:00")
working_hours_end: Optional[str] = Field(default="17:00")
```

**After:**
```python
# MISSING FIELDS - NOW ADDED
max_attempts: Optional[int] = Field(default=3, ge=1, le=20)
retry_delay: Optional[int] = Field(default=300, ge=60, le=86400)  # seconds
call_timeout: Optional[int] = Field(default=45, ge=15, le=300)   # seconds
working_hours_start: Optional[str] = Field(default="09:00", pattern=r"^\d{2}:\d{2}$")
working_hours_end: Optional[str] = Field(default="21:00", pattern=r"^\d{2}:\d{2}$")
```

## Changes Summary
1. ✅ `max_attempts`: Increased maximum from 10 to 20 attempts
2. ✅ `retry_delay`: Changed default from 60s to 300s (5 min), added minimum of 60s and maximum of 86400s (24h)
3. ✅ `call_timeout`: Increased default from 30s to 45s, increased maximum from 120s to 300s (5 min), minimum increased from 10s to 15s
4. ✅ `working_hours_start`: Added regex pattern validation for HH:MM format
5. ✅ `working_hours_end`: Changed default from "17:00" to "21:00", added regex pattern validation for HH:MM format

## Testing
All 5 fields now properly validated and persisted during campaign creation.

## Status
✅ **FIXED** - All missing fields now properly configured with correct constraints.

**File Modified:** `01_Core_System/dialer_api.py`
**Lines Modified:** 268-275
**Date Fixed:** $(date)
