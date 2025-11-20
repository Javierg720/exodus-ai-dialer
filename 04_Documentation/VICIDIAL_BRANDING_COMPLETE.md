# VICIdial Branding Update - Merchant Fund Express

## Completed: November 13, 2025

### Changes Made

#### 1. Logo Replacement ✓

**Original Logo:** `vicidial_admin_web_logo.gif` (VICIdial default)
**New Logo:** `logomfe.png` (Merchant Fund Express logo)

**Files Updated:**
- `/srv/www/htdocs/vicidial/logomfe.png` - Uploaded
- `/srv/www/htdocs/vicidial/vicidial_admin_web_logo.gif` - Replaced
- `/srv/www/htdocs/vicidial/vicidial_admin_web_logo.png` - Replaced

**Backup Created:** `vicidial_admin_web_logo.gif.bak`

#### 2. Color Scheme - Teal & White ✓

**Brand Colors Extracted from Logo:**
- **Primary Teal:** #009B8D (menu backgrounds, headers, text)
- **White:** #FFFFFF (main background)
- **Light Teal:** #E6F7F5 (alternate row backgrounds)
- **Lighter Teal:** #CCF0EC (accents)

**New Color Scheme Created:**
- **ID:** `mfe_teal`
- **Name:** "Merchant Fund Express Teal"
- **Active:** Yes
- **Applied To:** All admin and agent interfaces

**Color Breakdown:**
```
menu_background:      #009B8D  (Teal - menus, headers, separators)
frame_background:     #FFFFFF  (White - main background)
std_row1_background:  #FFFFFF  (White - table rows)
std_row2_background:  #E6F7F5  (Very light teal - alternate rows)
std_row3_background:  #FFFFFF  (White)
std_row4_background:  #E6F7F5  (Very light teal)
std_row5_background:  #CCF0EC  (Light teal - accents)
button_color:         #009B8D  (Teal - buttons)
```

#### 3. System-Wide Settings Updated ✓

**Database Table:** `system_settings`
- `admin_screen_colors` = `mfe_teal`
- `agent_screen_colors` = `mfe_teal`
- `agent_chat_screen_colors` = `mfe_teal`

**Color Scheme Database:** `vicidial_screen_colors`
- New entry created for `mfe_teal`
- Logo reference: `logomfe.png`
- User group: `---ALL---` (applies to everyone)

#### 4. Hardcoded Defaults Updated ✓

**File:** `/srv/www/htdocs/vicidial/admin.php`
- Line 116: `$Mmain_bgcolor` = `#009B8D` (was #015B91)
- Line 6797: `$SSmenu_background` = `009B8D` (was 015B91)
- Lines 6799-6803: Updated row background defaults to white/teal

**Backup Created:** `admin.php.bak`

### What Users Will See

#### Admin Panel (admin.php)
- **Logo:** Merchant Fund Express logo (orange M with teal text)
- **Menu Headers:** Teal background (#009B8D)
- **Page Background:** White (#FFFFFF)
- **Text/Separators:** Teal color (#009B8D)
- **Table Rows:** Alternating white and very light teal
- **Buttons:** Teal background

#### Agent Interface (vicidial.php)
- **Logo:** Merchant Fund Express logo
- **Login Screen:** Teal headers with white background
- **Agent Controls:** Teal accents
- **Buttons:** Teal color scheme

#### All Menus
- Menu separators: Teal lines
- Menu text: Teal color
- Menu backgrounds: Teal (#009B8D)
- Content background: White (#FFFFFF)

### URLs to Test

**Admin Login:**
https://merchantfundexp.cloudautodialer.in/vicidial/admin.php
- Username: `javiersuper` or `javi`
- Password: `oX05mP6450c4L10` or `457332`

**Agent Login:**
https://merchantfundexp.cloudautodialer.in/agc/vicidial.php
- Phone Login: 7531-7536
- Phone Pass: 3Yzurrq4Mb716Wu

### Technical Details

**Color Scheme System:**
VICIdial stores color schemes in the `vicidial_screen_colors` table. Each user group or individual user can be assigned a color scheme. The system-wide defaults are in `system_settings`.

**Logo System:**
Logos are referenced by filename in the `web_logo` column of `vicidial_screen_colors`. The system looks for logo files in `/srv/www/htdocs/vicidial/` directory.

**CSS Override:**
While VICIdial uses inline bgcolor attributes, some styling can also be controlled via `/srv/www/htdocs/vicidial/vicidial_stylesheet.css`.

### Next Steps (Optional)

1. **Test the Interface:**
   - Log in as admin to verify teal color scheme
   - Log in as agent to verify consistency
   - Check all menu pages for proper branding

2. **Custom CSS (if needed):**
   - Further customization can be done in `vicidial_stylesheet.css`
   - Can adjust button hover states, shadows, etc.

3. **Additional Branding:**
   - Email templates (if using VICIdial email features)
   - Report headers/footers
   - Custom scripts/forms

### Files Modified Summary

```
/srv/www/htdocs/vicidial/logomfe.png (new)
/srv/www/htdocs/vicidial/vicidial_admin_web_logo.gif (replaced)
/srv/www/htdocs/vicidial/vicidial_admin_web_logo.png (replaced)
/srv/www/htdocs/vicidial/admin.php (color defaults updated)
Database: vicidial_screen_colors (new mfe_teal scheme)
Database: system_settings (admin/agent colors set)
```

### Rollback Instructions (if needed)

To revert to original VICIdial branding:

```bash
# SSH into server
ssh root@46.62.216.79

# Restore original logo
cp /srv/www/htdocs/vicidial/vicidial_admin_web_logo.gif.bak /srv/www/htdocs/vicidial/vicidial_admin_web_logo.gif

# Restore admin.php
cp /srv/www/htdocs/vicidial/admin.php.bak /srv/www/htdocs/vicidial/admin.php

# Revert to default blue colors
mysql -u root -p3L5v3XzKXC724bM8au8R asterisk << ENDSQL
UPDATE system_settings 
SET admin_screen_colors = 'default_blue_test',
    agent_screen_colors = 'default_grey_agent';
ENDSQL
```

---

**Status:** ✅ COMPLETE
**Tested:** Ready for user verification
**Impact:** All admin and agent interfaces now branded with MFE logo and teal/white color scheme
