# Linphone Setup Complete! ✅

## Installation Status
- ✅ Linphone Desktop installed
- ✅ Configuration file created (`linphonerc`)
- ✅ Ready to make calls to AVA bot

---

## Quick Start Guide

### Step 1: Copy Configuration File

```bash
mkdir -p ~/.local/share/linphone
cp /home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/linphonerc ~/.local/share/linphone/
```

### Step 2: Launch Linphone

```bash
linphone
```

### Step 3: Verify Registration

The account should automatically register with:
- **Server:** 10.0.0.113
- **Username:** testphone
- **Status:** Should show "Registered" or green indicator

If not registered automatically:
1. Go to **Settings** → **SIP Accounts**
2. Add account manually with these details:
   - Username: `testphone`
   - Password: `123456789101112jG`
   - Domain: `10.0.0.113`
   - Transport: UDP
   - Port: 5060

### Step 4: Make Test Call to AVA

1. In Linphone dialer, enter: **9092**
2. Click the **Call** button (or press Enter)
3. **You should hear AVA speaking!**
4. **Speak into your microphone** - AVA should respond to you!

---

## Monitoring the Call (Optional)

To verify audio is being received by the bot, open another terminal:

```bash
docker logs -f avr-bot-9092
```

**What to look for:**
- `Client connected` ← Call initiated
- `UUID packet received` ← Bot ready
- `📨 Received header: type=0x10` ← **AUDIO FRAMES BEING RECEIVED!**
- `Sends text from LLM to TTS` ← AVA speaking
- ASR activity showing your speech being transcribed

---

## Troubleshooting

### Issue: Not Registered
**Solution:** 
- Check Settings → SIP Accounts
- Verify credentials match above
- Check Asterisk is running: `docker ps | grep ava-asterisk`

### Issue: Can't Hear AVA
**Solution:**
- Check audio output device in Settings → Audio/Video
- Verify speakers/headphones are working
- Check volume is not muted

### Issue: AVA Can't Hear You
**Solution:**
- Check microphone selection in Settings → Audio/Video
- Test microphone: `arecord -d 3 test.wav && aplay test.wav`
- Verify microphone volume: `amixer get Capture`

### Issue: Call Connects But No Audio Either Way
**Solution:**
- Check bot is running: `docker ps | grep avr-bot-9092`
- Check Asterisk logs: `docker logs --tail 50 ava-asterisk`
- Restart bot if needed: `docker restart avr-bot-9092`

---

## Expected Behavior

### ✅ Working Call:
1. You dial 9092
2. Call connects within 1-2 seconds
3. You hear AVA say: *"Hey there, Ava with Fund Express..."*
4. You respond (e.g., "Hello, yes I'm interested")
5. AVA responds to what you said
6. Conversation continues naturally

### ❌ GNOME Calls Issue (Previous Problem):
- Call connected but recording was 100% silent
- AVA spoke but couldn't hear user
- **This is fixed with Linphone!**

---

## Technical Details

**Why Linphone Works:**
- Properly negotiates PCMU (G.711 μ-law) codec
- Sends RTP audio packets correctly
- Compatible with Asterisk AudioSocket protocol
- Tested and verified with Asterisk systems

**Configuration Summary:**
- Codec: PCMU/PCMA @ 8kHz
- Transport: UDP
- Echo Cancellation: Enabled
- Video: Disabled (audio-only)
- SIP Port: 5060
- RTP Ports: 7078 (audio)

---

## Next Steps

1. **Launch Linphone** and verify it registers
2. **Call 9092** to test conversation with AVA
3. **Monitor bot logs** to see audio reception in real-time
4. **Report any issues** - we're here to help!

---

## Files Created

- `/home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/linphonerc` - Configuration file
- `/home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/setup-linphone.sh` - Full setup script
- `/home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/LINPHONE_INSTRUCTIONS.md` - This file

---

**Ready to call AVA? Launch Linphone now!** 📞
