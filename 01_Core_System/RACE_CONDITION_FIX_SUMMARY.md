# Race Condition Fix - Lead Selection

## Problem
Two or more dialers could claim the same lead because `get_next_leads()` and `mark_lead_calling()` were separate operations, creating a race condition window where:

1. Dialer A calls `get_next_leads()` → gets lead #123
2. Dialer B calls `get_next_leads()` → gets lead #123 (same lead!)
3. Dialer A calls `mark_lead_calling(123)` → marks as CALLING
4. Dialer B calls `mark_lead_calling(123)` → marks as CALLING (duplicate!)
5. Both dialers place calls to the same lead

## Solution
Implemented atomic lead claiming using SQLite's `UPDATE...RETURNING` pattern, which combines the select and update operations into a single atomic transaction.

## Changes Made

### 1. dialer_db_async.py

Added new method `claim_next_leads()`:
```python
async def claim_next_leads(self, campaign_id: int, limit: int = 10) -> List[Dict]:
    """Atomically claim and return next available leads.
    
    Uses UPDATE...RETURNING pattern to prevent race conditions.
    """
    query = """
        UPDATE leads
        SET status = 'CALLING', 
            attempts = attempts + 1,
            last_call_time = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE id IN (
            SELECT id FROM leads
            WHERE campaign_id = ?
            AND status IN ('NEW', 'CALLBACK')
            AND attempts < 5
            AND (next_call_time IS NULL OR next_call_time <= CURRENT_TIMESTAMP)
            ORDER BY
                CASE WHEN status = 'CALLBACK' THEN 0 ELSE 1 END,
                next_call_time ASC,
                created_at ASC
            LIMIT ?
        )
        RETURNING *
    """
```

Deprecated old method `get_next_leads()`:
- Kept for backward compatibility
- Added deprecation warning
- Should not be used in production

### 2. dialer_orchestrator.py

Updated `_place_calls()` method:
```python
# OLD (race condition):
leads = await self.db.get_next_leads(campaign_id, limit=count)
# ... later ...
await self.db.mark_lead_calling(lead_id)

# NEW (atomic):
leads = await self.db.claim_next_leads(campaign_id, limit=count)
# Leads are already marked as CALLING - no separate call needed
```

Removed redundant `mark_lead_calling()` call in `_process_single_lead()`:
```python
# Lead is already marked as CALLING by claim_next_leads()
# This prevents race conditions where two dialers could claim the same lead
```

## Test Results

Created comprehensive test (`test_race_condition_fix.py`) that:
- Creates 50 test leads
- Simulates 5 concurrent dialers
- Each dialer attempts to claim 5 batches of 5 leads
- Verifies no duplicates occur

**Test Results:**
```
Total leads claimed: 50
Unique leads claimed: 50
Duplicates: 0

✅ PASS: No race condition detected! Each lead was claimed exactly once.
Database state is consistent!
```

## Technical Details

### Why UPDATE...RETURNING Works

1. **Atomic Operation**: The entire SELECT + UPDATE happens in a single database transaction
2. **Row Locking**: SQLite locks the rows being updated, preventing concurrent access
3. **RETURNING Clause**: Returns the updated rows immediately, no need for a separate SELECT
4. **Transaction Safety**: Uses WAL mode (Write-Ahead Logging) for concurrent read/write safety

### Performance Benefits

- **Reduced Database Calls**: 1 operation instead of 2 (get + mark)
- **Lower Latency**: No network round-trip between operations
- **Better Concurrency**: Proper locking prevents conflicts
- **Fewer Errors**: No retry logic needed for race conditions

## Verification

To verify the fix is working in production:

1. Check logs for atomic claiming:
   ```
   ✅ DB: Atomically claimed 10 leads - 2 callbacks, 8 new
   ```

2. No deprecation warnings should appear:
   ```
   ⚠️ DEPRECATED: get_next_leads() called - use claim_next_leads() instead
   ```

3. Monitor for duplicate call attempts to the same lead
   ```sql
   SELECT phone_number, COUNT(*) as calls
   FROM call_log
   WHERE start_time > datetime('now', '-1 hour')
   GROUP BY phone_number
   HAVING COUNT(*) > 1;
   ```

## Migration Notes

- **Backward Compatible**: Old `get_next_leads()` still works but logs deprecation warning
- **No Database Schema Changes**: Uses existing table structure
- **Drop-In Replacement**: Just replace the method call, no other changes needed

## Related Files

- `01_Core_System/dialer_db_async.py` - Database interface with atomic claiming
- `01_Core_System/dialer_orchestrator.py` - Orchestrator using atomic claims
- `01_Core_System/test_race_condition_fix.py` - Comprehensive test suite
- `01_Core_System/RACE_CONDITION_FIX_SUMMARY.md` - This document

## Status

✅ **IMPLEMENTED AND TESTED**
- Atomic lead claiming implemented
- Race condition eliminated
- All tests passing
- Production ready
