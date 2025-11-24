# Voice Settings Feature - Complete Implementation

## Overview

I've added a complete voice settings system to your Exodus dashboard with:
- **25 American Edge-TTS voices** (male & female)
- **Speed control** (0.5x to 2.0x)
- **Pitch adjustment** (-100Hz to +100Hz)  
- **Interrupt sensitivity** (barge-in threshold)
- **12 dynamic variables** for personalized conversations

---

## Files Created/Modified

### Frontend (Dashboard)
1. **`exodus-dashboard-pro/src/components/Settings/VoiceSettings.tsx`** (NEW)
   - Beautiful voice settings UI component
   - Real-time sliders for speed/pitch/sensitivity
   - Click-to-copy dynamic variables
   - Live example prompts

2. **`exodus-dashboard-pro/src/pages/Settings.tsx`** (MODIFIED)
   - Integrated VoiceSettings component
   - Shows voice settings per campaign

### Backend (API)
3. **`01_Core_System/dialer_api.py`** (MODIFIED)
   - Added `GET /campaigns/{id}/voice-settings`
   - Added `PUT /campaigns/{id}/voice-settings`
   - Validates settings ranges

4. **`01_Core_System/voice_utils.py`** (NEW)
   - `replace_dynamic_vars()` - Replace {{variables}} in prompts
   - `generate_ssml()` - Generate Edge TTS SSML with voice settings
   - `get_voice_config()` - Extract voice config from campaign

---

## Features

### 1. Voice Selection (25 American Voices)

**Female Voices:**
- Aria - Natural & Warm ✨ (Professional, versatile)
- Jenny - Bright & Friendly (Upbeat, energetic)
- Sara - Calm & Professional (Business-appropriate)
- Emma - Soft & Engaging (Gentle, approachable)
- Ava - Modern & Crisp (Contemporary, clear)
- **Ava Multilingual** - Global (Works great for any accent) ⭐
- Michelle - Warm & Expressive (Emotional range)
- Jane - Reliable & Steady (Consistent tone)
- Nancy - Cheerful & Upbeat (Happy, positive)
- Amber - Sweet & Gentle (Soft-spoken)
- Ashley - Young & Fresh (Youthful energy)
- Cora - Sophisticated & Elegant (Refined)
- Elizabeth - Regal & Refined (Authoritative elegance)
- Monica - Dynamic & Lively (High energy)

**Male Voices:**
- Guy - Deep & Confident (Strong, mature)
- Andrew - Clear & Energetic (Active, enthusiastic)
- Brian - Friendly & Versatile (All-purpose)
- Christopher - Strong & Authoritative (Leadership tone)
- Eric - Professional & Clear (Business formal)
- Jacob - Youthful & Casual (Relaxed, informal)
- Jason - Energetic & Bold (Assertive)
- Tony - Smooth & Charismatic (Persuasive)
- Davis - Mature & Wise (Experienced)
- Roger - Classic & Timeless (Traditional)
- Steffan - Modern & Cool (Contemporary male)

### 2. Voice Controls

**Speed:** 0.5x to 2.0x (default: 1.3x)
- Lower = Slower, more deliberate
- Higher = Faster, more energetic
- **Recommended for sales:** 1.2-1.4x

**Pitch:** -100Hz to +100Hz (default: 0Hz)
- Negative = Lower pitch (more authoritative)
- Positive = Higher pitch (more energetic)
- **Recommended range:** -20Hz to +20Hz

**Interrupt Sensitivity:** 0.1 to 1.0 (default: 0.5)
- Lower (0.1-0.3) = Bot stops talking IMMEDIATELY when lead speaks
- Medium (0.4-0.6) = Balanced interruption handling
- Higher (0.7-1.0) = Bot continues talking unless strong interruption
- **For natural conversation:** 0.3-0.5

### 3. Dynamic Variables (12 Total)

These variables get automatically replaced with lead data:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{{first_name}}` | Lead's first name | "John" |
| `{{last_name}}` | Lead's last name | "Smith" |
| `{{full_name}}` | Full name | "John Smith" |
| `{{company}}` | Company name | "Acme Corp" |
| `{{phone}}` | Phone number | "415-555-1234" |
| `{{city}}` | City | "San Francisco" |
| `{{state}}` | State | "CA" |
| `{{zip}}` | ZIP code | "94102" |
| `{{email}}` | Email address | "john@acme.com" |
| `{{custom1}}` | Custom field 1 | Any custom data |
| `{{custom2}}` | Custom field 2 | Any custom data |
| `{{campaign}}` | Campaign name | "Q4 Outreach" |

---

## How to Use

### Step 1: Access Voice Settings

1. Go to **Settings** page in dashboard
2. Select a **Campaign** from the dropdown
3. Scroll to **Voice Settings** section

### Step 2: Configure Voice

1. **Choose a voice** from the dropdown (25 American options)
2. **Adjust speed** - Drag slider (0.5x to 2.0x)
3. **Set pitch** - Drag slider (-100Hz to +100Hz)
4. **Configure interrupt sensitivity** - Lower = more responsive
5. Click **Save Voice Settings**

### Step 3: Use Dynamic Variables in Prompts

**Example Prompt:**
```
Hi {{first_name}}, this is Sarah from {{company}}. 
I'm calling regarding the business funding application for 
your location in {{city}}, {{state}}. How are you today?
```

**This becomes (for John Smith in San Francisco):**
```
Hi John, this is Sarah from Fund Express. 
I'm calling regarding the business funding application for 
your location in San Francisco, CA. How are you today?
```

### Step 4: Test Your Bot

1. Make a test call from the dashboard
2. Listen to the voice with your new settings
3. Adjust as needed

---

## API Endpoints

### Get Voice Settings
```http
GET /campaigns/{campaign_id}/voice-settings
```

**Response:**
```json
{
  "status": "success",
  "voice_settings": {
    "voice": "en-US-AvaMultilingualNeural",
    "speed": 1.3,
    "pitch": 0,
    "interrupt_sensitivity": 0.5
  }
}
```

### Update Voice Settings
```http
PUT /campaigns/{campaign_id}/voice-settings
Content-Type: application/json

{
  "voice": "en-US-AriaNeural",
  "speed": 1.2,
  "pitch": -10,
  "interrupt_sensitivity": 0.4
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Voice settings updated successfully",
  "voice_settings": {
    "voice": "en-US-AriaNeural",
    "speed": 1.2,
    "pitch": -10,
    "interrupt_sensitivity": 0.4
  }
}
```

---

## Using in Your Bot Code

### Import the Helper Functions

```python
from voice_utils import replace_dynamic_vars, generate_ssml, get_voice_config
```

### Example: Personalize Opening Message

```python
# Your bot's opening prompt template
opening_template = """
Hi {{first_name}}, this is Ava with Fund Express. 
Calling about the money you were seeking for {{company}}. 
Did you secure those funds?
"""

# Get lead data
lead = {
    "first_name": "Sarah",
    "vendor_lead_name": "ABC Industries",
    "city": "Miami",
    "state": "FL"
}

# Replace variables
personalized_message = replace_dynamic_vars(opening_template, lead)
# Result: "Hi Sarah, this is Ava with Fund Express. Calling about 
#          the money you were seeking for ABC Industries. Did you secure those funds?"

# Get campaign voice settings
campaign = await db.get_campaign(campaign_id)
voice_config = get_voice_config(campaign)

# Generate SSML with voice settings
ssml = generate_ssml(
    personalized_message,
    voice=voice_config["voice"],  # e.g., "en-US-AvaMultilingualNeural"
    speed=voice_config["speed"],  # e.g., 1.3
    pitch=voice_config["pitch"]   # e.g., 0
)

# Send SSML to Edge TTS
# (your existing TTS code here)
```

### Full Integration Example

```python
async def start_conversation(lead_id: int, campaign_id: int):
    # Get lead and campaign data
    lead = await db.get_lead(lead_id)
    campaign = await db.get_campaign(campaign_id)
    
    # Get voice config for this campaign
    voice_config = get_voice_config(campaign)
    
    # Get opening message template from campaign
    opening_template = campaign.get("opening_message", 
        "Hi {{first_name}}, this is calling from {{company}}.")
    
    # Personalize with lead data
    personalized_message = replace_dynamic_vars(opening_template, lead)
    
    # Generate SSML with campaign voice settings
    ssml = generate_ssml(
        personalized_message,
        voice=voice_config["voice"],
        speed=voice_config["speed"],
        pitch=voice_config["pitch"]
    )
    
    # Configure interrupt sensitivity for this campaign
    vad_sensitivity = voice_config["interrupt_sensitivity"]
    
    # Start the conversation with personalized settings
    await bot.speak(ssml, vad_sensitivity=vad_sensitivity)
```

---

## Database Schema Updates

Voice settings are stored in the `campaigns` table:

```sql
ALTER TABLE campaigns ADD COLUMN tts_voice VARCHAR(100) DEFAULT 'en-US-AvaMultilingualNeural';
ALTER TABLE campaigns ADD COLUMN tts_speed FLOAT DEFAULT 1.3;
ALTER TABLE campaigns ADD COLUMN tts_pitch INTEGER DEFAULT 0;
ALTER TABLE campaigns ADD COLUMN interrupt_sensitivity FLOAT DEFAULT 0.5;
```

---

## Best Practices

### Voice Selection
- **Sales Calls:** Ava Multilingual, Aria, Jenny (friendly female voices)
- **Professional:** Sara, Guy, Christopher (authoritative)
- **Casual:** Brian, Ashley, Jason (relaxed, conversational)
- **Warm/Empathetic:** Michelle, Emma, Tony (emotional connection)

### Speed Settings
- **0.8-1.0x:** Slow, deliberate (complex information)
- **1.1-1.3x:** Natural pace (most sales calls) ⭐
- **1.4-1.6x:** Energetic, upbeat
- **1.7-2.0x:** Very fast (use sparingly)

### Pitch Adjustments
- **-20 to -10Hz:** Slightly deeper (more authority)
- **0Hz:** Natural (recommended) ⭐
- **+10 to +20Hz:** Slightly higher (more energetic)
- **Avoid extremes** (-100 or +100 sounds unnatural)

### Interrupt Sensitivity
- **0.2-0.3:** Very responsive (ideal for Q&A)
- **0.4-0.5:** Balanced (recommended) ⭐
- **0.6-0.8:** Patient (for longer explanations)

### Dynamic Variables
- **Always use {{first_name}}** - Most impactful personalization
- **Use {{company}}** for B2B calls
- **Use {{city}}, {{state}}** for local relevance
- **Test with real data** before going live

---

## Testing

### Test the API Endpoints

```bash
# Get voice settings for campaign 1
curl http://localhost:8001/campaigns/1/voice-settings

# Update voice settings
curl -X PUT http://localhost:8001/campaigns/1/voice-settings \
  -H "Content-Type: application/json" \
  -d '{"voice":"en-US-AriaNeural","speed":1.2,"pitch":-10,"interrupt_sensitivity":0.4}'
```

### Test Dynamic Variables

```bash
cd /home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/01_Core_System
python voice_utils.py
```

### Test in Dashboard

1. Open dashboard → Settings
2. Select a campaign
3. Change voice to "Aria"
4. Set speed to 1.2x
5. Set pitch to -10Hz
6. Save settings
7. Make a test call
8. Listen to the new voice

---

## Troubleshooting

### Voice settings not saving
- Check that campaign ID is valid
- Verify API endpoint is accessible
- Check browser console for errors

### Variables not replacing
- Ensure lead has the required fields
- Check spelling of variable names (case-sensitive)
- Verify `voice_utils.py` is imported

### Voice sounds wrong
- Try different voices from the list
- Adjust speed (1.2-1.4x works best for most)
- Keep pitch between -20 and +20Hz

### Bot interrupts too much/too little
- **Too much:** Increase interrupt_sensitivity to 0.6-0.8
- **Too little:** Decrease to 0.2-0.3

---

## Next Steps

1. **Add to your bot code:** Import `voice_utils.py` and use `replace_dynamic_vars()`
2. **Create campaign templates:** Save prompts with variables in database
3. **A/B test voices:** Try different voices and track performance
4. **Monitor metrics:** Track how voice settings affect conversion rates

---

## Summary

✅ **25 American Edge-TTS voices** installed  
✅ **Speed/Pitch/Sensitivity controls** added  
✅ **12 dynamic variables** for personalization  
✅ **Full API integration** with validation  
✅ **Beautiful dashboard UI** with sliders  
✅ **Helper functions** for easy integration  

**Your Exodus dialer now has enterprise-level voice customization!**

---

**Need Help?**
- Check the example code in `voice_utils.py`
- Test API endpoints with curl
- Review dashboard Settings → Voice Settings section
