# VICIdial Hotkeys Enabled

## ✅ Status: ENABLED

Hotkeys have been enabled for all admin users and agents.

---

## Users with Hotkeys Enabled

### Admin Users (Level 9)
- **javi** - Hotkeys: ✅ Enabled
- **javiersuper** - Hotkeys: ✅ Enabled  
- **shiva37284** - Hotkeys: ✅ Enabled

### Agent Users (Level 5)
- **7531** - Hotkeys: ✅ Enabled
- **7532** - Hotkeys: ✅ Enabled
- **7533** - Hotkeys: ✅ Enabled
- **7534** - Hotkeys: ✅ Enabled
- **7535** - Hotkeys: ✅ Enabled
- **7536** - Hotkeys: ✅ Enabled

---

## VICIdial Default Hotkeys

### Call Control Hotkeys

| Key | Function | Description |
|-----|----------|-------------|
| **SPACE** | Pause Call | Pause/Resume on active call |
| **ENTER** | Hangup Customer | Hangup the customer line |
| **1** | Disposition | Open disposition screen |
| **2** | Customer Hangup | Hangup customer only |
| **3** | Dial Next Number | Skip to next lead |
| **4** | Transfer Xfer | Customer transfer |
| **5** | Transfer Conf | Customer 3-way conference |
| **6** | Grab Call | Grab next call from queue |
| **7** | Park Call | Park the customer call |
| **8** | Resume | Resume paused call |
| **9** | Blind Transfer | Blind transfer customer |

### Agent Status Hotkeys

| Key | Function | Description |
|-----|----------|-------------|
| **P** | Pause | Pause (ready status) |
| **R** | Resume | Resume from pause |
| **W** | Wrapup | Enter wrapup/after-call work |

### Advanced Hotkeys

| Key | Function | Description |
|-----|----------|-------------|
| **H** | Hangup Both | Hangup both agent and customer |
| **D** | Disposition | Quick disposition |
| **Q** | Quiet Mode | Toggle quiet mode |
| **A** | Activate | Activate next call |
| **S** | Script | Toggle script display |

---

## How to Use Hotkeys

### Agent Interface

1. **Log in to Agent Interface:**
   - https://merchantfundexp.cloudautodialer.in/agc/vicidial.php
   - Login: 7531-7536
   - Pass: 3Yzurrq4Mb716Wu

2. **Hotkeys Work Automatically:**
   - No need to enable in settings
   - Works when agent screen is in focus
   - Press the key directly (no modifier needed)

3. **Common Workflow:**
   - Call comes in → Press **SPACE** to pause if needed
   - During call → Use **4** or **5** for transfers
   - After call → Press **1** for disposition
   - Between calls → Press **3** for next lead

### Customizing Hotkeys

**Admin can customize hotkeys via:**
1. Admin Interface → System Settings
2. Scroll to "Hotkeys Configuration"
3. Modify default key assignments
4. Save changes

**Per-User Hotkey Override:**
1. Admin → Users
2. Select user (e.g., javi)
3. Scroll to "Hotkeys Active" → Should be "1" ✅
4. Custom hotkey assignments can be configured

---

## Hotkey Configuration in Database

```sql
-- Enable hotkeys for a user
UPDATE vicidial_users 
SET hotkeys_active = '1' 
WHERE user = 'javi';

-- Disable hotkeys for a user
UPDATE vicidial_users 
SET hotkeys_active = '0' 
WHERE user = 'javi';

-- Check who has hotkeys enabled
SELECT user, full_name, hotkeys_active 
FROM vicidial_users 
WHERE hotkeys_active = '1';
```

---

## Important Notes

1. **Browser Focus Required:**
   - Hotkeys only work when agent screen has focus
   - Click on the agent interface window first

2. **Campaign Settings:**
   - Some hotkeys may be disabled by campaign settings
   - Check Campaign → Hotkeys settings

3. **Disposition Hotkeys:**
   - Number keys (1-9) can be mapped to specific dispositions
   - Configured in Admin → System Settings → Hotkeys

4. **Testing Hotkeys:**
   - Have agent log in
   - Make a test call
   - Try pressing hotkey combinations
   - Watch for button activation on screen

---

## Troubleshooting

**Hotkeys not working?**

1. **Check user setting:**
   ```sql
   SELECT hotkeys_active FROM vicidial_users WHERE user='7531';
   ```
   Should return: `1`

2. **Clear browser cache**
   - Press Ctrl+Shift+Delete
   - Clear cache and cookies
   - Reload agent screen

3. **Check browser console**
   - Press F12
   - Look for JavaScript errors
   - Hotkeys use JavaScript

4. **Verify campaign allows hotkeys**
   - Admin → Campaigns → [Campaign]
   - Check hotkey settings

5. **Test with different browser**
   - Chrome recommended
   - Firefox also works
   - Avoid Internet Explorer

---

## Hotkey Best Practices

### For Agents:
- **Learn the basics first:** SPACE (pause), ENTER (hangup), 1 (dispo)
- **Practice on test calls** before live campaign
- **Keep cheat sheet nearby** until memorized
- **Use consistently** to build muscle memory

### For Admins:
- **Train agents on hotkeys** during onboarding
- **Create custom mappings** that match workflow
- **Monitor usage** to ensure agents utilize them
- **Disable conflicting keys** if issues arise

---

## Common Hotkey Combinations

**Quick Disposition:**
1. Finish call
2. Press **1** (opens disposition)
3. Select status
4. Press **ENTER** (submit)

**Fast Transfer:**
1. During call, press **4** (transfer)
2. Type extension/number
3. Press **DIAL**
4. Press **PARK** to complete

**Pause Between Calls:**
1. Press **P** (pause)
2. Select pause code
3. Do after-call work
4. Press **R** (resume)

**Skip to Next Lead:**
1. In preview mode
2. Press **3** (dial next)
3. Skips current lead
4. Loads next available

---

## Custom Hotkey Setup (Advanced)

**Admin Configuration Path:**
1. Admin → System Settings
2. Section: "Agent Screen Settings"
3. Find: "Hotkeys Active" → YES
4. Custom mappings available

**Available for Mapping:**
- Disposition codes
- Pause codes
- Transfer presets
- Script tabs
- Custom buttons

**Example Custom Mapping:**
- **F1** → "SALE" disposition
- **F2** → "NO ANSWER" disposition
- **F3** → "CALLBACK" disposition
- **F4** → Transfer to supervisor

---

## Status: ✅ COMPLETE

**All users have hotkeys enabled and ready to use!**

**Test by:**
1. Having agent log in
2. Making a test call
3. Pressing hotkeys during call
4. Verifying button activation on screen

---

**Updated:** November 13, 2025
**Enabled For:** 9 users (3 admins + 6 agents)
**Configuration:** Database `vicidial_users.hotkeys_active = '1'`

