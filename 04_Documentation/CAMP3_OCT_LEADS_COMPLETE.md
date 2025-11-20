# CAMP3 - OCT LEADS Campaign Created & Loaded

## ✅ COMPLETE - November 13, 2025

---

## Campaign Details

**Campaign ID:** CAMP3
**Campaign Name:** OCT LEADS
**Status:** Active (Y)
**Dial Method:** RATIO
**Auto Dial Level:** 4
**Hopper Level:** 1000

---

## List Details

**List ID:** 31025
**List Name:** CAMP 3 - OCT LEADS
**Campaign:** CAMP3
**Status:** Active

---

## Lead Import Summary

### CSV Files Imported (4 files):
1. ✅ `1 LMG 3k 10.17.25 (2) (1).csv`
2. ✅ `2 LMG 2k 10.17.25.csv`
3. ✅ `LMG 2.5k 9.18.25.csv`
4. ✅ `LMG 3k 09.30.25.csv`

### Import Statistics:
- **Total Leads Imported:** 10,487
- **NEW (Dialable) Leads:** 10,487
- **Leads with Business Name:** 10,487 (100%)
- **Leads with Email:** 8,720 (83%)

### Source File Totals:
- CSV rows processed: 15,822
- Valid leads imported: 10,487
- Duplicates/Invalid skipped: 5,335

---

## Custom Field Created

**New Field:** `business` (VARCHAR 255)
- Added to `vicidial_list` table
- Contains company/business name from CSV
- Available for all campaigns
- Visible in agent screen

---

## Sample Imported Leads

| Lead ID | Phone | First Name | Last Name | Business | City | State |
|---------|-------|------------|-----------|----------|------|-------|
| 21919 | 2012342465 | Srinivasarao | Bandla | Sp Sanford | Sanford | FL |
| 21920 | 2012482300 | Alfredo | Alonso | Goal Merchandising LLC | | |
| 21921 | 2013128269 | Yen | Chung | Gbc22 Corp | Ledgwood | NJ |
| 21922 | 2013309466 | Jose | L Argueta | Despensa del Ahorro... | Woodcliff Lake | NJ |
| 21923 | 2013658045 | AVJIT | KUMAR | Cosmos Furniture Inc | New Jersey | NJ |

---

## All Active Campaigns Overview

| Campaign ID | Campaign Name | List Name | Total Leads | NEW Leads |
|-------------|---------------|-----------|-------------|-----------|
| **CAMP3** | **OCT LEADS** | **CAMP 3 - OCT LEADS** | **10,487** | **10,487** |
| USACamp | B2B business services | 1 LMG 3k 10.17.25 2.csv | 3,000 | 2,330 |
| USACampH | NEW LEADS 11-13 | LIST1 -11-13 | 3,000 | 3,000 |

**Total System Leads:** 16,487
**Total Dialable (NEW):** 15,817

---

## Campaign Settings (Cloned from USACamp)

**Dialing:**
- Dial Method: RATIO
- Auto Dial Level: 4
- Adaptive Dropped %: 3%
- Dial Timeout: 45 seconds
- Dial Prefix: 10

**Recording:**
- Campaign Recording: ALLFORCE
- Recording Filename: FULLDATE_CUSTPHONE_AGENT

**Time Settings:**
- Local Call Time: 24hours
- Lead Order: UP TIMEZONE

**DNC Settings:**
- Use Internal DNC: Y
- Use Campaign DNC: Y

**Other Settings:**
- Hopper Level: 1000
- Wrapup Seconds: 0
- Drop Call Seconds: 5
- Allow Closers: Y

---

## Import Method Used

**Technology:** MySQL LOAD DATA LOCAL INFILE (bulk import)
**Performance:** 10,487 leads imported in ~5 seconds
**Deduplication:** INSERT IGNORE (automatic duplicate skip)
**Validation:** Phone numbers >= 10 digits

**SQL Process:**
1. Created temporary table
2. Loaded all 4 CSV files into temp table (15,822 rows)
3. Bulk INSERT into vicidial_list with validation
4. Skipped duplicates and invalid phone numbers
5. Dropped temporary table

---

## Database Changes

### Table Modified: `vicidial_list`
```sql
ALTER TABLE vicidial_list 
ADD COLUMN business VARCHAR(255) DEFAULT NULL;
```

### Tables Updated:
- `vicidial_campaigns` - New campaign CAMP3 created
- `vicidial_lists` - New list 31025 created
- `vicidial_list` - 10,487 leads inserted

---

## Access Campaign

**Admin Interface:**
https://merchantfundexp.cloudautodialer.in/vicidial/admin.php

**Steps:**
1. Login as `javi` or `javiersuper`
2. Click **CAMPAIGNS**
3. Select **CAMP3**
4. View leads, settings, start dialing

**To View Leads:**
1. Admin → **LISTS**
2. Click list **31025** (CAMP 3 - OCT LEADS)
3. Click **LEADS**
4. View all 10,487 imported leads

---

## Next Steps

### 1. Review Campaign Settings
- Verify dial level appropriate for call volume
- Check local call time restrictions
- Review disposition codes

### 2. Assign Agents
- Admin → Campaigns → CAMP3
- Assign user groups or individual agents
- Ensure agents have proper permissions

### 3. Test Dialing
- Have test agent log in
- Set campaign to CAMP3
- Verify leads populate hopper
- Make test calls

### 4. Monitor Performance
- Check call statistics
- Monitor drop rate (must stay < 3%)
- Adjust auto dial level as needed

---

## Business Field Usage

The new `business` field can be used for:
- **Agent Display:** Show company name during calls
- **Script Variables:** Reference {{business}} in scripts
- **Search/Filter:** Find leads by business name
- **Reports:** Group statistics by business
- **Disposition:** Track results by company type

**To Display in Agent Screen:**
1. Admin → System Settings
2. Agent Display Fields
3. Add `business` field
4. Agents will see company name on calls

---

## Lead Data Quality

**Phone Numbers:**
- Format: 10-18 digits (cleaned)
- Country Code: 1 (USA)
- All validated for minimum 10 digits

**Business Names:**
- 100% coverage (all leads have business)
- Range: Small businesses to corporations
- Examples: retail, services, restaurants, etc.

**Email Addresses:**
- 83% coverage (8,720 of 10,487)
- Useful for email campaigns
- Available for follow-up

**Geographic Coverage:**
- Multiple states included
- City and state populated where available
- ZIP codes included

---

## Troubleshooting

**If leads not dialing:**
```sql
-- Check hopper population
SELECT COUNT(*) FROM vicidial_hopper WHERE campaign_id='CAMP3';

-- If empty, VICIdial will auto-populate from list
-- Or manually reset:
/usr/share/astguiclient/AST_VDhopper.pl -test
```

**If campaign not showing:**
- Clear browser cache
- Verify campaign active: `SELECT active FROM vicidial_campaigns WHERE campaign_id='CAMP3'`
- Restart VICIdial services if needed

**To check lead status distribution:**
```sql
SELECT status, COUNT(*) 
FROM vicidial_list 
WHERE list_id = 31025 
GROUP BY status;
```

---

## File Locations

**CSV Files (on server):**
- `/tmp/oct_leads/1 LMG 3k 10.17.25 (2) (1).csv`
- `/tmp/oct_leads/2 LMG 2k 10.17.25.csv`
- `/tmp/oct_leads/LMG 2.5k 9.18.25.csv`
- `/tmp/oct_leads/LMG 3k 09.30.25.csv`

**Original Files (local):**
- `/home/user/Desktop/LEADS\/OCT/` (4 CSV files)

---

## Success Metrics

✅ Campaign created successfully
✅ List created and assigned
✅ 10,487 leads imported (100% success rate on valid data)
✅ Custom business field added system-wide
✅ All leads in NEW (dialable) status
✅ Ready for immediate dialing
✅ Business information captured for all leads
✅ Email data captured for 83% of leads

---

**Status:** 🚀 READY FOR PRODUCTION

**Campaign:** CAMP3 - OCT LEADS
**Leads:** 10,487 dialable
**Date:** November 13, 2025
**Next Action:** Assign agents and start dialing!

