# API CONTRACT FIXES - Frontend/Backend Alignment

## COMPLETED FIXES:

### 1. Login Endpoint (Line ~647) ✅
**FIXED**: Changed from query parameters to Form parameters
```python
# OLD:
@app.post("/auth/login", response_model=Token)
async def login(username: str, password: str):
    return {"access_token": access_token, "token_type": "bearer"}

# NEW:
@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    return {
        "status": "success",
        "data": {
            "access_token": access_token,
            "token_type": "bearer"
        },
        "message": "Login successful"
    }
```

### 2. Campaign Creation Model (Line ~196) ✅
**FIXED**: Added missing fields to CampaignCreate model
```python
class CampaignCreate(BaseModel):
    # ... existing fields ...
    max_attempts: Optional[int] = Field(default=3, ge=1, le=10)
    retry_delay: Optional[int] = Field(default=60, ge=0)
    call_timeout: Optional[int] = Field(default=30, ge=10, le=120)
    working_hours_start: Optional[str] = Field(default="09:00")
    working_hours_end: Optional[str] = Field(default="17:00")
```

### 3. Campaign Creation Endpoint (Line ~670) ✅
**FIXED**: Now accepts and persists additional campaign fields
```python
@app.post("/campaigns", status_code=201)
async def create_campaign(campaign: CampaignCreate):
    # Creates campaign, then updates with additional fields
    update_data = {}
    if campaign.max_attempts is not None:
        update_data['max_attempts'] = campaign.max_attempts
    if campaign.retry_delay is not None:
        update_data['retry_delay'] = campaign.retry_delay
    # ... etc
    
    if update_data:
        await db.update_campaign(campaign_id, update_data)
    
    return {
        "status": "success",
        "data": {"campaign_id": campaign_id},
        "message": "Campaign created successfully"
    }
```

### 4. DNC Endpoints ✅
**ADDED**: Missing DELETE and export endpoints

#### DELETE /dnc/{phone_number} (Line ~2214)
```python
@app.delete("/dnc/{phone_number}")
async def remove_from_dnc(phone_number: str):
    # Removes phone from DNC list
    return {
        "status": "success",
        "data": {"phone_number": phone_number},
        "message": f"Removed {phone_number} from DNC list"
    }
```

#### GET /dnc/export (Line ~2250)
```python
@app.get("/dnc/export")
async def export_dnc():
    # Returns CSV file of all DNC entries
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=dnc_list.csv"}
    )
```

### 5. Parameter Naming ✅
**VERIFIED**: API already uses consistent naming:
- Uses "notes" (not "note") for lead notes - Line 1369
- Uses "callback_date" (not "callback_time") in request body - Line 2349
- Database field is "next_call_time" which stores the callback datetime

## REMAINING WORK:

### 6. Standardize ALL Response Formats ⚠️
**NEEDS WORK**: Many endpoints still return inconsistent formats

Target format:
```python
{
    "status": "success",  # or "error"
    "data": {...},        # actual response data
    "message": "..."      # optional human-readable message
}
```

#### Endpoints that need response standardization:

1. **Campaign Endpoints** (Lines 670-995):
   - `/campaigns` (GET) - returns array directly
   - `/campaigns/active` (GET) - returns array directly  
   - `/campaigns/{id}` (GET) - returns campaign object directly
   - `/campaigns/{id}` (PUT) - returns `{"message": "..."}`
   - `/campaigns/{id}` (DELETE) - returns `{"message": "..."}`
   - `/campaigns/{id}/start` (POST) - returns `{"message": "..."}`
   - `/campaigns/{id}/pause` (POST) - returns `{"message": "..."}`
   - `/campaigns/{id}/stats` (GET) - returns `{"campaign_id": ..., "stats": {...}}`
   - `/campaigns/{id}/leads` (GET) - returns `{"campaign_id": ..., "leads": [...], ...}`
   - `/campaigns/{id}/reset-leads` (POST) - needs standardization

2. **Lead Endpoints** (Lines 997-1380):
   - `/leads/{id}/status` (PUT) - returns `{"message": "..."}`
   - `/leads/{id}/disposition` (PUT) - returns `{"message": "..."}`
   - `/leads/{id}` (DELETE) - returns `{"message": "..."}`
   - `/leads/{id}/notes` (GET) - returns `{"notes": [...]}`
   - `/leads/{id}/notes` (POST) - returns `{"message": "...", "call_id": ...}`
   - `/leads` (GET) - returns array directly
   - `/leads/bulk` (POST) - returns mixed format
   - `/leads/import` (POST) - returns mixed format

3. **Bot Endpoints** (Lines 1381-2052):
   - `/bots` (GET) - returns `{"bots": [...], "summary": {...}}`
   - `/bots/status` (GET) - returns `{"bots": [...], "summary": {...}}`
   - `/bots/restart/{port}` (GET/POST) - returns `{"message": "..."}`
   - `/bots/pool/restart` (POST) - partially standardized
   - `/bots/pool/start` (POST) - partially standardized
   - `/bots/pool/stop` (POST) - partially standardized
   - `/bots/{port}/stop` (POST) - returns `{"message": "..."}`
   - `/bots/{port}/start` (POST) - returns `{"message": "..."}`
   - `/bots/adjust-pool` (POST) - returns `{"message": "...", ...}`

4. **Stats Endpoints** (Lines 2060-2139):
   - `/stats` (GET) - returns complex object directly
   - `/dialer/stats` (GET) - returns stats object directly

5. **DNC Endpoints** (Lines 2147-2290):
   - `/dnc` (POST) - returns `{"message": "..."}`
   - `/dnc/{phone}` (GET) - returns `{"phone_number": "...", "is_dnc": bool}`
   - `/dnc` (GET) - returns array directly
   - Note: DELETE and export already standardized ✅

6. **Disposition/Callback Endpoints** (Lines 2319-2400):
   - `/dispositions` (GET) - returns `{"dispositions": [...]}`
   - `/leads/{id}/callback` (POST) - returns `{"message": "...", ...}`

7. **Call Endpoints** (Lines 2401-2577):
   - `/calls/active` (GET) - returns array directly
   - `/calls/originate` (POST) - returns `{"message": "...", ...}`
   - `/calls/history` (GET) - returns array directly
   - `/calls/transcript` (POST) - returns `{"message": "..."}`
   - `/calls/{uuid}/disposition` (POST) - returns `{"message": "...", ...}`
   - `/calls/monitor` (POST) - returns `{"message": "...", ...}`

8. **Settings Endpoints** (Lines 2684-2835):
   - `/settings` (GET) - partially standardized
   - `/settings/campaign/{id}` (PUT) - uses standard format ✅
   - `/campaigns/{id}/voice-settings` (GET) - uses standard format ✅
   - `/campaigns/{id}/voice-settings` (PUT) - uses standard format ✅
   - `/system/reboot` (POST) - uses standard format ✅

## IMPLEMENTATION PRIORITY:

### High Priority (Breaking Changes):
1. ✅ Login endpoint form parameters
2. ✅ DNC DELETE endpoint
3. ✅ DNC export endpoint
4. ✅ Campaign creation additional fields

### Medium Priority (Consistency):
5. Standardize all GET endpoints that return arrays
6. Standardize all POST/PUT/DELETE success responses
7. Standardize error responses

### Low Priority (Nice to Have):
8. Add response models using Pydantic
9. Add OpenAPI response schemas
10. Consistent error message formatting

## TESTING RECOMMENDATIONS:

After applying response standardization:
1. Test all frontend API calls
2. Update TypeScript interfaces
3. Test error handling paths
4. Verify backward compatibility if needed

## NOTES:

- Many endpoints return data directly (arrays, objects) instead of wrapped in standard format
- This was likely for simplicity but creates inconsistency
- Frontend should be updated to expect standardized responses
- Consider adding a response wrapper middleware for automatic formatting
