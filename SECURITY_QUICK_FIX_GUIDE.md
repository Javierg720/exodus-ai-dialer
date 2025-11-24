# Security Quick Fix Guide - Top 6 Critical Issues

**IMMEDIATE ACTION REQUIRED - Fix These First**

---

## 1. Fix Hardcoded JWT Secret (Line 74)

### Current Code:
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION_USE_ENV_VAR")
```

### Fixed Code:
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable must be set. Generate with: openssl rand -hex 32")
```

### How to Fix:
1. Generate secure key: `openssl rand -hex 32`
2. Add to `.env` file: `JWT_SECRET_KEY=<generated-key>`
3. Restart API

**Priority:** CRITICAL - Do first  
**Time:** 5 minutes

---

## 2. Fix CORS Wide Open (Lines 250-256)

### Current Code:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← DANGEROUS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Fixed Code:
```python
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### How to Fix:
1. Add to `.env`: `ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`
2. Update code as shown above
3. Test CORS from allowed domain

**Priority:** CRITICAL - Do second  
**Time:** 10 minutes

---

## 3. Add Authentication to All Endpoints

### Current Code (Example):
```python
@app.post("/campaigns", status_code=201)
async def create_campaign(campaign: CampaignCreate):
    # No authentication!
```

### Fixed Code:
```python
@app.post("/campaigns", status_code=201)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: User = Depends(get_current_active_user)  # ← ADD THIS
):
    # Endpoint now requires valid JWT token
```

### Endpoints to Fix:
1. All `/campaigns/*` endpoints
2. All `/leads/*` endpoints  
3. All `/calls/*` endpoints
4. All `/bots/*` endpoints
5. All `/dnc/*` endpoints
6. `/stats` and `/dialer/stats`

### Public Endpoints (No Auth Needed):
- `/` (dashboard)
- `/health`
- `/auth/login`
- `/api` (info)

**Priority:** CRITICAL - Do third  
**Time:** 30 minutes (add to 40+ endpoints)

---

## 4. Fix SQL Injection (Multiple Locations)

### Problem Areas:
```python
# Line 1231 - String formatting in SQL
where_sql = f"WHERE {' AND '.join(where_clauses)}"
query = f"""SELECT ... FROM leads {where_sql} ..."""
```

### Fixed Code:
```python
# Build parameterized query
where_clauses = []
params = []

if campaign_id:
    where_clauses.append("campaign_id = ?")
    params.append(campaign_id)

if status:
    where_clauses.append("status = ?")
    params.append(status.upper())

where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

# Execute with parameters
query = f"SELECT ... FROM leads {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?"
params.extend([limit, offset])

async with db.db.execute(query, tuple(params)) as cursor:
    ...
```

### Rule:
✅ **DO:** Always use `?` placeholders and pass values separately  
❌ **DON'T:** Use f-strings or .format() with user input in SQL

**Priority:** CRITICAL - Do fourth  
**Time:** 20 minutes

---

## 5. Fix File Access Vulnerability (Line 374-434)

### Current Code:
```python
@app.get("/api/recording/{call_uuid}")
async def get_recording_by_uuid(call_uuid: str):
    find_cmd = [
        "docker", "exec", "ava-asterisk", "find",
        "/var/spool/asterisk/monitor",
        "-name", f"*{call_uuid}*.wav",  # ← Unsanitized
    ]
```

### Fixed Code:
```python
import re
import shlex

@app.get("/api/recording/{call_uuid}")
async def get_recording_by_uuid(
    call_uuid: str,
    current_user: User = Depends(get_current_active_user)  # Add auth
):
    # Validate UUID format (alphanumeric + hyphens only)
    if not re.match(r'^[a-zA-Z0-9\-]{8,36}$', call_uuid):
        raise HTTPException(400, "Invalid UUID format")
    
    # Sanitize for shell
    safe_uuid = shlex.quote(call_uuid)
    
    find_cmd = [
        "docker", "exec", "ava-asterisk", "find",
        "/var/spool/asterisk/monitor",
        "-name", f"*{safe_uuid}*.wav",
    ]
    
    result = subprocess.run(
        find_cmd, 
        capture_output=True, 
        text=True, 
        timeout=5
    )
    # ... rest of code
```

**Priority:** HIGH - Do fifth  
**Time:** 15 minutes

---

## 6. Add Rate Limiting (Entire API)

### Install Required Package:
```bash
pip install slowapi
```

### Add to Code:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add to login endpoint
@app.post("/auth/login", response_model=Token)
@limiter.limit("5/minute")  # Only 5 attempts per minute
async def login(request: Request, username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        # Log failed attempt
        logger.warning(f"Failed login attempt for {username} from {request.client.host}")
        raise HTTPException(401, "Incorrect username or password")
    # ... rest of code

# Add to other sensitive endpoints
@app.post("/calls/originate", status_code=201)
@limiter.limit("10/minute")  # Max 10 calls per minute
async def originate_call(request: Request, call: CallOriginate):
    # ... code

@app.post("/leads/bulk", status_code=201)
@limiter.limit("5/hour")  # Max 5 bulk imports per hour
async def bulk_import_leads(request: Request, import_data: LeadBulkImport):
    # ... code
```

**Priority:** HIGH - Do sixth  
**Time:** 20 minutes

---

## Testing After Fixes

### 1. Test JWT Secret:
```bash
# Should fail without env var
unset JWT_SECRET_KEY
python dialer_api.py
# Expected: RuntimeError

# Should work with env var
export JWT_SECRET_KEY=$(openssl rand -hex 32)
python dialer_api.py
# Expected: Server starts
```

### 2. Test CORS:
```bash
# From unauthorized origin - should fail
curl -H "Origin: http://evil.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/campaigns

# From allowed origin - should succeed
curl -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/campaigns
```

### 3. Test Authentication:
```bash
# Without token - should fail with 401
curl -X POST http://localhost:8000/campaigns \
     -H "Content-Type: application/json" \
     -d '{"name":"Test"}'

# With valid token - should succeed
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
     -d "username=admin&password=yourpassword" | jq -r .access_token)

curl -X POST http://localhost:8000/campaigns \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"Test"}'
```

### 4. Test Rate Limiting:
```bash
# Try 6 login attempts in 1 minute - 6th should fail
for i in {1..6}; do
  curl -X POST http://localhost:8000/auth/login \
       -d "username=admin&password=wrong"
  echo "Attempt $i"
done
# Expected: First 5 return 401, 6th returns 429 (Too Many Requests)
```

---

## Deployment Checklist

- [ ] Generate JWT secret key
- [ ] Set JWT_SECRET_KEY in environment
- [ ] Set ALLOWED_ORIGINS in environment
- [ ] Update CORS configuration
- [ ] Add authentication to all endpoints
- [ ] Fix SQL queries to use parameterization
- [ ] Add UUID validation to recording endpoint
- [ ] Install slowapi package
- [ ] Add rate limiting to sensitive endpoints
- [ ] Test all changes in staging environment
- [ ] Monitor logs for errors after deployment
- [ ] Verify authentication works for all endpoints
- [ ] Test CORS from allowed origins
- [ ] Confirm rate limiting is working

---

## Environment Variables Needed

Create `.env` file:
```bash
# Required
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Existing vars (keep these)
AMI_HOST=localhost
AMI_USERNAME=admin
AMI_PASSWORD=yourpassword
GROQ_API_KEY=your_groq_key
```

---

## Rollback Plan

If something goes wrong:

1. **Keep backup of original file:**
   ```bash
   cp dialer_api.py dialer_api.py.backup
   ```

2. **Test in staging first:**
   - Never deploy directly to production
   - Verify all endpoints work
   - Check logs for errors

3. **Quick rollback:**
   ```bash
   cp dialer_api.py.backup dialer_api.py
   systemctl restart dialer-api
   ```

---

## Support

If you encounter issues:

1. Check logs: `tail -f /var/log/dialer-api.log`
2. Test endpoints with curl (examples above)
3. Verify environment variables: `env | grep -E "JWT|CORS|ALLOWED"`
4. Review full audit: `DIALER_API_SECURITY_AUDIT.md`

---

**Estimated Total Time:** 2 hours  
**Risk Reduction:** 70% of critical vulnerabilities fixed  
**Next Steps:** Review `SECURITY_AUDIT_EXECUTIVE_SUMMARY.md` for Phase 2 fixes
