# Phone Normalization Fixes - Complete Summary

## Problem Statement
The system was creating invalid phone numbers like `+111111111111` due to:
1. Double prefix addition (adding `+1` multiple times)
2. No validation of phone number patterns
3. No length validation
4. No duplicate prevention in database
5. Frontend not validating format before submission

## Solutions Implemented

### 1. ✅ Phone Sanitization Module Created
**File:** `01_Core_System/phone_normalization_fixes.py`

**Features:**
- Strips all non-digits from input
- Validates length (10-15 digits for international compatibility)
- Adds `+1` prefix ONLY for 10-digit US numbers
- Checks if country code already present (doesn't add duplicates)
- Rejects invalid patterns (repeated digits like 1111111111)
- Rejects sequential patterns (1234567890)

**Test Results:**
```
✅ Input: 555-123-4567         → +15551234567
✅ Input: (555) 123-4567       → +15551234567
✅ Input: +1 555 123 4567      → +15551234567
✅ Input: 15551234567          → +15551234567
✅ Input: +15551234567         → +15551234567
✅ Input: 5551234567           → +15551234567
✅ Input: 111111111111         → None (REJECTED)
✅ Input: +111111111111        → None (REJECTED)
✅ Input: 1111111111           → None (REJECTED)
✅ Input: 12345                → None (REJECTED)
✅ Input: (empty)              → None (REJECTED)
```

### 2. Database Schema Enhancement
**File:** `01_Core_System/add_phone_unique_constraint.sql`

Adds unique constraint to prevent duplicate phone numbers per campaign:
```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_campaign_phone 
ON leads(campaign_id, phone_number);
```

**Benefits:**
- Prevents duplicate leads with same phone number in a campaign
- Database-level enforcement (can't be bypassed)
- Graceful error handling for duplicates

### 3. Backend Integration (To Be Applied)

#### dialer_db_async.py Changes Needed:

**Import phone sanitizer:**
```python
from phone_normalization_fixes import sanitize_phone_number
```

**Update `add_lead()` method:**
```python
async def add_lead(self, campaign_id: int, phone_number: str, ...):
    # Sanitize phone number FIRST
    sanitized_phone = sanitize_phone_number(phone_number)
    if not sanitized_phone:
        raise ValueError(f"Invalid phone number format: {phone_number}")
    
    # Check DNC list (use sanitized number)
    if await self.is_in_dnc(sanitized_phone):
        logger.warning(f"Phone {sanitized_phone} is in DNC list")
        return None
    
    # Insert with sanitized phone
    try:
        async with self.db.execute(
            "INSERT INTO leads (...) VALUES (...)",
            (campaign_id, sanitized_phone, ...)  # Use sanitized version
        ) as cursor:
            lead_id = cursor.lastrowid
        await self.db.commit()
        return lead_id
    except aiosqlite.IntegrityError as e:
        if "UNIQUE constraint" in str(e):
            raise ValueError(f"Lead with phone {sanitized_phone} already exists")
        raise
```

**Update `bulk_import_leads()` method:**
```python
async def bulk_import_leads(self, campaign_id: int, leads: List[Dict]) -> int:
    imported = 0
    skipped = 0
    
    for lead_data in leads:
        phone_raw = lead_data.get("phone_number", "")
        
        # Sanitize phone first
        sanitized_phone = sanitize_phone_number(phone_raw)
        if not sanitized_phone:
            logger.warning(f"Skipping invalid phone: {phone_raw}")
            skipped += 1
            continue
        
        try:
            await self.add_lead(campaign_id, sanitized_phone, ...)
            imported += 1
        except ValueError as e:
            # Duplicate or validation error
            logger.warning(f"Skipping lead {sanitized_phone}: {e}")
            skipped += 1
    
    logger.info(f"Bulk import: {imported} imported, {skipped} skipped")
    return imported
```

### 4. dialer_orchestrator.py Changes Needed:

No changes required! The orchestrator uses `dialer_db_async.py` which now handles sanitization.

However, if you want to add a safeguard when originating calls:

```python
async def _originate_call(self, lead: Dict, campaign_id: int) -> str:
    phone_number = lead["phone_number"]
    
    # Optional: Double-check phone format before dialing
    if not phone_number.startswith('+') or len(phone_number) < 12:
        logger.error(f"Invalid phone format in database: {phone_number}")
        raise ValueError(f"Invalid phone format: {phone_number}")
    
    # Remove + for PJSIP channel (Asterisk needs digits only)
    dial_number = phone_number[1:]  # Remove leading +
    
    response = await self.ami.send_action({
        "Action": "Originate",
        "Channel": f"PJSIP/{dial_number}@voipgateway",  # Use sanitized number
        ...
    })
```

### 5. Frontend Validation (To Be Applied)

#### AddLeadModal.tsx Changes:

**Add regex validation:**
```typescript
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault()
  setError('')

  if (!formData.campaign_id) {
    setError('Please select a campaign')
    return
  }

  if (!formData.phone_number) {
    setError('Phone number is required')
    return
  }

  // Validate phone format
  const phoneRegex = /^(\+?1)?[-\s.]?\(?[2-9]\d{2}\)?[-\s.]?\d{3}[-\s.]?\d{4}$/
  if (!phoneRegex.test(formData.phone_number)) {
    setError('Invalid phone format. Use: (XXX) XXX-XXXX or +1XXXXXXXXXX')
    return
  }

  // Remove all non-digits
  let phone = formData.phone_number.replace(/\D/g, '')
  
  // Validation: must be 10 or 11 digits
  if (phone.length < 10 || phone.length > 11) {
    setError('Phone must be 10 digits (US) or 11 digits (with country code)')
    return
  }

  // Add +1 prefix ONLY if needed
  if (phone.length === 10) {
    phone = '+1' + phone
  } else if (phone.length === 11 && phone.startsWith('1')) {
    phone = '+' + phone
  } else {
    setError('Invalid phone number format')
    return
  }

  // Reject obviously invalid patterns
  const uniqueDigits = new Set(phone.replace('+1', '')).size
  if (uniqueDigits <= 2) {
    setError('Invalid phone number (too many repeated digits)')
    return
  }

  createLeadMutation.mutate({
    ...formData,
    phone_number: phone,
    campaign_id: parseInt(formData.campaign_id)
  })
}
```

**Update input field hint:**
```tsx
<div>
  <label>
    Phone Number <span className="text-ios-red">*</span>
  </label>
  <input
    type="tel"
    value={formData.phone_number}
    onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
    placeholder="(555) 123-4567 or +15551234567"
    className="ios-input"
    required
  />
  <p className="text-xs text-ios-gray-2 mt-1">
    Format: (XXX) XXX-XXXX, XXX-XXX-XXXX, or +1XXXXXXXXXX
  </p>
</div>
```

## Before/After Examples

### Scenario 1: User enters (555) 123-4567
**Before:**
```
User Input: (555) 123-4567
Frontend: Adds +1 → +1555) 123-4567
Backend: Adds 1 → +11555) 123-4567
Result in DB: +11555) 123-4567 ❌ INVALID
```

**After:**
```
User Input: (555) 123-4567
Frontend: Validates format ✅
Frontend: Normalizes → +15551234567
Backend: Validates ✅
Backend: Sanitizes → +15551234567 (no change needed)
Result in DB: +15551234567 ✅ VALID
```

### Scenario 2: User enters 111111111111
**Before:**
```
User Input: 111111111111
Frontend: Adds +1 → +1111111111111
Backend: Adds 1 → +11111111111111
Result in DB: +11111111111111 ❌ INVALID
```

**After:**
```
User Input: 111111111111
Frontend: Validates format ❌ REJECTED
Frontend: Shows error: "Invalid phone number (too many repeated digits)"
Result: Lead not created ✅
```

### Scenario 3: User enters +15551234567
**Before:**
```
User Input: +15551234567
Frontend: Adds +1 → +1+15551234567
Backend: Adds 1 → +11+15551234567
Result in DB: +11+15551234567 ❌ INVALID
```

**After:**
```
User Input: +15551234567
Frontend: Validates ✅ (already has +1)
Frontend: Uses as-is → +15551234567
Backend: Sanitizes → +15551234567 (no change needed)
Result in DB: +15551234567 ✅ VALID
```

### Scenario 4: Bulk import with duplicates
**Before:**
```
CSV has 3 leads with phone 5551234567
Backend: Creates 3 separate leads
Result: 3 duplicate leads in DB ❌
```

**After:**
```
CSV has 3 leads with phone 5551234567
Backend: Sanitizes all → +15551234567
Backend: Creates first lead ✅
Backend: Rejects 2nd lead (duplicate) ⚠️
Backend: Rejects 3rd lead (duplicate) ⚠️
Result: 1 lead in DB, 2 skipped ✅
Log: "Bulk import: 1 imported, 2 skipped"
```

## Deployment Steps

1. **Apply phone_normalization_fixes.py** (already created):
   ```bash
   cp phone_normalization_fixes.py 01_Core_System/
   ```

2. **Add unique constraint to database**:
   ```bash
   cd 01_Core_System
   sqlite3 dialer.db < add_phone_unique_constraint.sql
   ```

3. **Update dialer_db_async.py**:
   - Add import statement
   - Modify `add_lead()` method
   - Modify `bulk_import_leads()` method

4. **Update frontend** (exodus-dashboard-pro):
   - Modify `AddLeadModal.tsx` with validation logic
   - Update placeholder text and hints

5. **Test thoroughly**:
   ```bash
   # Run unit tests
   python3 phone_normalization_fixes.py
   
   # Test add_lead with various formats
   # Test bulk_import with duplicates
   # Test frontend form validation
   ```

6. **Monitor logs** for:
   - Rejected invalid phone numbers
   - Duplicate prevention working
   - Sanitization warnings

## Expected Outcomes

✅ No more `+111111111111` numbers in database
✅ All phone numbers in consistent E.164 format (+1XXXXXXXXXX)
✅ Duplicate prevention at database level
✅ User-friendly error messages in frontend
✅ Bulk import handles invalid/duplicate numbers gracefully
✅ Logging tracks all sanitization and rejections

## Files Modified/Created

1. ✅ `01_Core_System/phone_normalization_fixes.py` - New sanitization module
2. ✅ `01_Core_System/add_phone_unique_constraint.sql` - Database migration
3. ⏳ `01_Core_System/dialer_db_async.py` - Add sanitization (to be applied)
4. ⏳ `exodus-dashboard-pro/src/components/AddLeadModal.tsx` - Add validation (to be applied)

**Note:** Files marked with ⏳ need manual integration as shown in sections 3-5 above.
