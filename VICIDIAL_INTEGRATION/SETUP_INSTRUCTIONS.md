# Exodus Dialer - ViciDial Integration Setup

## Your ViciDial Server Details

| Item | Value |
|------|-------|
| **Server IP** | 46.62.216.79 |
| **Dialer URL** | https://merchantfundexp.cloudautodialer.in |
| **Admin User** | javiersuperPass |
| **Admin Pass** | oX05mP6450c4L10 |
| **Agent Logins** | 7531-7536 |
| **Agent Pass** | 3Yzurrq4Mb716Wu |
| **SSH Root** | root / 3L5v3XzKXC724bM8au8R |

## VoIP Provider Details

| Item | Value |
|------|-------|
| **Portal** | http://88.99.144.14:7153/eng/ |
| **Username** | Javier-Gonzalez |
| **Password** | xhHQNxvh |

---

## Option 1: Run Exodus Bots on ViciDial Server (Recommended)

This installs the AI bot system directly on your ViciDial server.

### Step 1: SSH into ViciDial Server

```bash
ssh root@46.62.216.79
# Password: 3L5v3XzKXC724bM8au8R
```

### Step 2: Install Docker (if not present)

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker
```

### Step 3: Copy Exodus Bot Files

From your local machine:
```bash
scp -r /home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/01_Core_System root@46.62.216.79:/opt/exodus/
scp /home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/VICIDIAL_INTEGRATION/*.conf root@46.62.216.79:/etc/asterisk/
```

### Step 4: Configure Asterisk on ViciDial

```bash
# Backup existing configs
cp /etc/asterisk/sip.conf /etc/asterisk/sip.conf.backup
cp /etc/asterisk/extensions.conf /etc/asterisk/extensions.conf.backup

# Add Exodus configs (append, don't replace)
cat /etc/asterisk/sip_vicidial.conf >> /etc/asterisk/sip.conf
cat /etc/asterisk/extensions_vicidial.conf >> /etc/asterisk/extensions.conf

# Reload Asterisk
asterisk -rx "sip reload"
asterisk -rx "dialplan reload"
```

### Step 5: Start Exodus AI Bots

```bash
cd /opt/exodus
docker-compose -f docker-compose-avr-production.yml up -d
```

### Step 6: Configure ViciDial Campaign to Use Exodus

1. Login to ViciDial Admin: https://merchantfundexp.cloudautodialer.in
2. Go to **Campaigns > Your Campaign > Detail View**
3. Set **Dial Method**: `RATIO`
4. Set **Auto Dial Level**: `1.0` (start conservative)
5. Create a new **In-Group** for AI bot transfers:
   - Name: `EXODUS_AI`
   - Extension: `9092` (first bot port)

---

## Option 2: Connect Remote Exodus to ViciDial via SIP Trunk

If Exodus runs on a separate server and connects to ViciDial remotely.

### On Your Exodus Server:

1. Copy the new Asterisk configs:
```bash
cp VICIDIAL_INTEGRATION/sip_vicidial.conf /etc/asterisk/sip.conf
cp VICIDIAL_INTEGRATION/extensions_vicidial.conf /etc/asterisk/extensions.conf
```

2. Reload Asterisk:
```bash
asterisk -rx "sip reload"
asterisk -rx "dialplan reload"
```

3. Verify trunk registration:
```bash
asterisk -rx "sip show peers"
# Should show vicidial-trunk as "OK"
```

### On ViciDial Server (SSH as root):

1. Add Exodus as a SIP peer in `/etc/asterisk/sip.conf`:
```ini
[exodus-remote]
type=friend
host=YOUR_EXODUS_SERVER_IP
context=from-exodus
insecure=port,invite
disallow=all
allow=ulaw
qualify=yes
```

2. Add inbound context in `/etc/asterisk/extensions.conf`:
```ini
[from-exodus]
exten => _X.,1,NoOp(Call from Exodus AI)
 same => n,Dial(SIP/${EXTEN}@your-voip-trunk,60)
 same => n,Hangup()
```

---

## Testing the Connection

### Test 1: Check SIP Registration
```bash
asterisk -rx "sip show registry"
asterisk -rx "sip show peers"
```

### Test 2: Make a Test Call
```bash
# From Asterisk CLI
asterisk -rx "channel originate SIP/7531@vicidial-trunk extension 9092@audiosocket-dial"
```

### Test 3: Check Bot Connectivity
```bash
# Verify bots are running
docker ps | grep avr-bot

# Check bot logs
docker logs avr-bot-9092
```

---

## Dialer Orchestrator Configuration

Update `/opt/exodus/01_Core_System/dialer_orchestrator.py` to use ViciDial trunk:

```python
# Change the SIP dial string from:
dial_string = f"SIP/{phone_number}@starcom"

# To:
dial_string = f"SIP/{phone_number}@vicidial-trunk"
```

Or in the dialer config, set:
```python
SIP_TRUNK = "vicidial-trunk"
```

---

## Important Notes

1. **Caller ID**: VoIP provider requires valid ANI. Update `DEFAULT_CID` in extensions.conf
2. **Change ANI Weekly**: Provider recommends changing caller ID 1-2 times per week
3. **No Third-Party VoIP**: Provider prohibits using other VoIP services
4. **Compliance**: Only legal campaigns allowed

---

## Troubleshooting

### "SIP trunk not registered"
```bash
# Check firewall
iptables -L -n | grep 5060
# Ensure UDP 5060 is open

# Check credentials
asterisk -rx "sip show registry"
```

### "No audio on calls"
```bash
# Check RTP ports
iptables -L -n | grep 10000:20000
# Ensure UDP 10000-20000 is open

# Check NAT settings in sip.conf
nat=force_rport,comedia
```

### "Bots not connecting"
```bash
# Verify AudioSocket ports are listening
netstat -tlnp | grep 909
# Should show ports 9092-9111
```
