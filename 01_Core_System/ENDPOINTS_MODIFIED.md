# API ENDPOINTS MODIFIED

## Summary
Modified 5 endpoints, added 2 new endpoints for DNC management.

## Modified Endpoints:

### 1. POST /auth/login (Line 647)
**Changes:**
- Changed from query parameters to Form(...) parameters
- Updated response format to standardized `{status, data, message}` format

**Before:**
```python
async def login(username: str, password: str):
    return {"access_token": token, "token_type": "bearer"}
```

**After:**
```python
async def login(username: str = Form(...), password: str = Form(...)):
    return {
        "status": "success",
        "data": {"access_token": token, "token_type": "bearer"},
        "message": "Login successful"
    }
```

### 2. POST /campaigns (Line 670)
**Changes:**
- Added support for additional campaign fields: max_attempts, retry_delay, call_timeout, working_hours_start, working_hours_end
- Updated response format to standardized format
- Calls db.update_campaign() after creation to set additional fields

**New Fields Accepted:**
- `max_attempts` (int, 1-10, default 3)
- `retry_delay` (int, >=0, default 60)
- `call_timeout` (int, 10-120, default 30)
- `working_hours_start` (string, default "09:00")
- `working_hours_end` (string, default "17:00")

### 3. CampaignCreate Model (Line 196)
**Changes:**
- Added 5 new optional fields to the Pydantic model

## New Endpoints:

### 4. DELETE /dnc/{phone_number} (Line 2214) - NEW
**Purpose:** Remove a phone number from the DNC list

**Request:**
```
DELETE /dnc/5551234567
```

**Response:**
```json
{
    "status": "success",
    "data": {"phone_number": "5551234567"},
    "message": "Removed 5551234567 from DNC list"
}
```

**Error (404):**
```json
{
    "detail": "Phone number not in DNC list"
}
```

### 5. GET /dnc/export (Line 2250) - NEW
**Purpose:** Export the entire DNC list as a CSV file

**Request:**
```
GET /dnc/export
```

**Response:**
- Content-Type: text/csv
- Headers: Content-Disposition: attachment; filename=dnc_list.csv
- Body: CSV file with columns: phone_number, reason, added_at

**Example CSV:**
```csv
phone_number,reason,added_at
5551234567,Manual addition,2025-11-23 10:30:00
5559876543,Customer request,2025-11-23 09:15:00
```

## Verified Endpoints (No Changes Needed):

### 6. POST /leads/{lead_id}/callback
**Verification:** Already uses "callback_date" parameter (not "callback_time") ✅

### 7. POST /leads/{lead_id}/notes
**Verification:** Already uses "notes" parameter (not "note") ✅

### 8. GET /leads/{lead_id}/notes
**Verification:** Already returns "notes" field ✅

## Files Modified:
- `01_Core_System/dialer_api.py`

## Database Schema Updates Required:
None - the database already has the fields (max_attempts, retry_delay, call_timeout, call_time_start, call_time_end) in the campaigns table. The API just wasn't accepting/setting them.

## Frontend Updates Required:

### 1. Login Component
Update to send form data instead of JSON:
```typescript
// OLD:
const response = await fetch('/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password})
});

// NEW:
const formData = new FormData();
formData.append('username', username);
formData.append('password', password);
const response = await fetch('/auth/login', {
    method: 'POST',
    body: formData
});

// Update response handling:
const result = await response.json();
const token = result.data.access_token;  // Changed from result.access_token
```

### 2. Campaign Creation Component
Add optional fields to campaign creation form:
```typescript
interface CampaignCreate {
    name: string;
    description?: string;
    dial_method?: string;
    dial_ratio?: number;
    max_dial_ratio?: number;
    stt_provider?: string;
    enable_recording?: boolean;
    // NEW FIELDS:
    max_attempts?: number;        // 1-10, default 3
    retry_delay?: number;         // seconds, default 60
    call_timeout?: number;        // seconds, 10-120, default 30
    working_hours_start?: string; // HH:MM format, default "09:00"
    working_hours_end?: string;   // HH:MM format, default "17:00"
}
```

### 3. DNC Management Component
Add delete button and export functionality:
```typescript
// Delete DNC entry
async function removeDNC(phone: string) {
    const response = await fetch(`/dnc/${phone}`, {method: 'DELETE'});
    const result = await response.json();
    // Handle result.status === "success"
}

// Export DNC list
function exportDNC() {
    window.location.href = '/dnc/export';  // Triggers download
}
```

## Breaking Changes:
1. **Login endpoint**: Frontend must send form data, response structure changed
2. **Campaign creation**: Response structure changed (but old structure still works for data extraction)

## Backward Compatibility:
- Most changes are additive (new optional fields)
- Response format changes may break strict type checking
- Consider versioning API if needed: `/api/v2/auth/login`
