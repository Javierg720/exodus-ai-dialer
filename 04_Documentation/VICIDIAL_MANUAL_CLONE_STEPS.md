# VICIdial User Cloning - Manual Steps

## Current Situation
The provided credentials (root / 3L5v3XzKXC724bM8au8R) are being rejected by the VICIdial API and admin panel.

## Error Message
```
ERROR: Login incorrect, please try again: |root|3L5v3XzKXC724bM8au8R|BAD|
```

## Manual Steps to Clone User

### Option 1: Via Web Browser (Recommended)

1. Open browser and go to: https://merchantfundexp.cloudautodialer.in/vicidial/admin.php

2. Try logging in with:
   - Username: root
   - Password: 3L5v3XzKXC724bM8au8R
   
3. If login fails, try alternative usernames:
   - Username: 6666 (common VICIdial default admin)
   - Username: admin
   - Username: shiva37284 (if they have admin access)

4. Once logged in:
   - Click "ADMIN" → "Users"
   - Search for user "shiva37284"
   - Click "COPY" or "CLONE" next to the user
   - Enter new username: javi
   - Enter new password: 457332
   - Ensure "User Level" is set to 9 (Super Admin)
   - Click "SUBMIT"

### Option 2: Via Database (If SSH Access Available)

If you have SSH access to the VICIdial server:

```bash
# SSH into the server
ssh root@merchantfundexp.cloudautodialer.in

# Access MySQL
mysql -u cron -p
# (password is usually in /etc/astguiclient.conf)

# Switch to asterisk database
USE asterisk;

# First, get shiva37284's complete settings
SELECT * FROM vicidial_users WHERE user='shiva37284'\G

# Clone the user
INSERT INTO vicidial_users 
SELECT * FROM vicidial_users WHERE user='shiva37284';

# Update the new record
UPDATE vicidial_users 
SET user='javi', 
    pass='457332',
    full_name='Javi'
WHERE user='shiva37284' 
  AND user IN (SELECT user FROM vicidial_users WHERE user='shiva37284' LIMIT 1 OFFSET 1);

# Verify
SELECT user, full_name, user_level, user_group FROM vicidial_users WHERE user IN ('shiva37284', 'javi');
```

### Option 3: Password Reset

The credentials might be incorrect. Try resetting via command line:

```bash
# SSH into server
ssh root@merchantfundexp.cloudautodialer.in

# Reset root password directly in database
mysql -u cron -p asterisk

UPDATE vicidial_users SET pass='3L5v3XzKXC724bM8au8R' WHERE user='root';
```

## What I Tried

1. ✗ Non-agent API - Login rejected
2. ✗ AGC API - Invalid username/password
3. ✗ Admin panel POST - 401 Unauthorized
4. ✗ Alternative endpoints - 404 Not Found

## Next Steps

1. Verify the root credentials are correct by logging in manually via browser
2. Check if there's SSH access to the server
3. Check /etc/astguiclient.conf on the server for actual credentials
4. Contact the VICIdial system administrator

## Database Schema Info

Based on API error message, the query being run is:
```sql
SELECT count(*) 
FROM vicidial_users 
WHERE user='root' 
  AND pass='3L5v3XzKXC724bM8au8R' 
  AND user_level > 0 
  AND active='Y'
```

This confirms passwords are stored in plain text in the `vicidial_users` table.
