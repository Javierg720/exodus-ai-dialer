# VICIdial Campaign Cloned - USACampHELP

## Summary

✅ **Campaign Successfully Created**

**Original Campaign:** USACamp
**New Campaign:** USACampH (truncated from USACampHELP - 8 char limit)

---

## Campaign Details

**Campaign ID:** `USACampH`
**Campaign Name:** B2B business services
**Status:** Active (Y)

**Dial Settings:**
- Hopper Level: 1000
- Auto Dial Level: 4
- Dial Method: RATIO
- Adaptive Dropped %: 3%
- Adaptive Maximum Level: 3.0

**Recording:**
- Campaign Recording: ALLFORCE
- Recording Filename: FULLDATE_CUSTPHONE_AGENT

**Other Key Settings:**
- Local Call Time: 24hours
- Dial Timeout: 45 seconds
- Dial Prefix: 10
- Manual Dial Prefix: 15
- Campaign CID: 19152370839
- Drop Call Seconds: 5
- Wrapup Seconds: 0

---

## List Assignment

**List ID:** 11113
**List Name:** LIST1 -11-13
**Campaign:** USACampH ✅
**Status:** Active
**Current Leads:** 0

⚠️ **Note:** The list currently has 0 leads. You may need to import leads into this list.

---

## All Campaigns in System

| Campaign ID | Campaign Name | Active | Dial Method | Lists |
|------------|---------------|--------|-------------|-------|
| USACamp | B2B business services | Y | RATIO | 1 LMG 3k 10.17.25 2.csv (13101725) |
| USACampH | B2B business services | Y | RATIO | LIST1 -11-13 (11113) |

---

## Settings Cloned

All settings from USACamp were copied to USACampH, including:

✅ Dial status configurations
✅ Lead order settings (UP TIMEZONE)
✅ Recording settings (ALLFORCE)
✅ Transfer settings (allow_closers: Y)
✅ AMD/Voicemail settings
✅ DNC settings (use_internal_dnc: Y, use_campaign_dnc: Y)
✅ Adaptive dialing parameters
✅ Survey settings
✅ CID settings (use_custom_cid: AREACODE)
✅ Agent interface settings
✅ Callback settings
✅ All advanced options

---

## VICIdial Campaign ID Limitation

**Important:** VICIdial campaign IDs are limited to 8 characters maximum.

- Requested: `USACampHELP` (11 characters)
- Created: `USACampH` (8 characters - auto-truncated)

This is a VICIdial database constraint and cannot be changed without modifying the database schema.

---

## Next Steps

1. **Import Leads** (if needed):
   - Go to Admin → Lists
   - Select list 11113 (LIST1 -11-13)
   - Click "LEADS" → "LEAD LOADER"
   - Upload your lead file

2. **Activate Campaign:**
   - Campaign is already active (Y)
   - Auto-dial level set to 4
   - Ready to start dialing when leads are present

3. **Assign Agents:**
   - Go to Admin → Campaigns
   - Select USACampH
   - Assign user groups or individual agents

4. **Test Dialing:**
   - Ensure leads are in the list
   - Have an agent log in
   - Campaign will start auto-dialing based on settings

---

## Access Campaign

**Admin Interface:**
https://merchantfundexp.cloudautodialer.in/vicidial/admin.php

1. Login as `javi` or `javiersuper`
2. Click **CAMPAIGNS**
3. Select **USACampH**
4. View/modify settings as needed

---

## Campaign Configuration Summary

```
Campaign ID: USACampH
Campaign Name: B2B business services
Active: Y
Dial Method: RATIO
Auto Dial Level: 4
Hopper Level: 1000
Dial Timeout: 45
Lead Order: UP TIMEZONE
Recording: ALLFORCE
Local Call Time: 24hours
Use Internal DNC: Y
Use Campaign DNC: Y
Adaptive Dropped %: 3
Manual Dial Allowed: Y
Manual Dial List: 998
```

---

## Database Commands Used

```sql
-- Clone campaign
INSERT INTO vicidial_campaigns 
SELECT 'USACampHELP', [all other fields]...
FROM vicidial_campaigns 
WHERE campaign_id = 'USACamp';

-- Assign list to new campaign
UPDATE vicidial_lists 
SET campaign_id = 'USACampH' 
WHERE list_id = 11113;
```

---

**Status:** ✅ COMPLETE
**Campaign Ready:** Yes (pending lead import)
**Created:** November 13, 2025

---

## Troubleshooting

**If campaign doesn't appear:**
- Clear browser cache
- Refresh admin page
- Check campaign is Active (Y)

**If auto-dialing doesn't start:**
- Verify leads exist in list 11113
- Check hopper has leads: `SELECT * FROM vicidial_hopper WHERE campaign_id='USACampH'`
- Ensure agents are logged in and available
- Check auto_dial_level is > 0

**To check hopper status:**
```sql
SELECT COUNT(*) FROM vicidial_hopper WHERE campaign_id='USACampH';
```

**To manually reset hopper:**
```sql
DELETE FROM vicidial_hopper WHERE campaign_id='USACampH';
-- Then let VICIdial auto-populate it
```

