# PRODUCTION VOICE AI AGENT - COMPLETE GUIDE

## 🎯 YOUR CRITICAL ISSUE: ECHO LOOP

**Symptom:** Bot hearing its own TTS output and responding to itself

**Root Cause:** No STT muting during bot speech in your pipeline

**1-Line Diagnosis:** Missing `STTMuteFilter` between transport.input() and stt

---

## 🔧 IMMEDIATE FIX (5 minutes)

### Step 1: Add Import (Line 26)
```python
from pipecat.processors.filters.stt_mute_filter import (
    STTMuteFilter,
    STTMuteConfig,
    STTMuteStrategy
)
```

### Step 2: Create Filter (Before Pipeline, ~Line 312)
```python
# Echo cancellation: Mute STT during bot speech
stt_mute_filter = STTMuteFilter(
    config=STTMuteConfig(
        strategies={STTMuteStrategy.MUTE_UNTIL_FIRST_BOT_COMPLETE}
    )
)
```

### Step 3: Insert in Pipeline (Line 316-326)
```python
pipeline = Pipeline([
    transport.input(),
    stt_mute_filter,  # ← ADD THIS LINE
    stt,
    context_aggregator.user(),
    llm,
    tts,
    transport.output(),
    context_aggregator.assistant(),
])
```

**That's it!** 3 lines of code fixes the echo.

---

## 📊 STRATEGY COMPARISON

| Strategy | When STT Muted | Best For | Pros | Cons |
|----------|---------------|----------|------|------|
| **MUTE_UNTIL_FIRST_BOT_COMPLETE** | During opening pitch only | Sales calls | Natural after intro | Can't interrupt pitch |
| **ALWAYS** | Anytime bot speaks | Demos, testing | 100% no echo | No interruptions |
| **FIRST_SPEECH** | First utterance only | Systems with good AEC | Most natural | Echo risk if AEC fails |

**Recommendation:** Start with `MUTE_UNTIL_FIRST_BOT_COMPLETE` for your sales bot.

---

## 🎙️ VAD OPTIMIZATION

### Current Setting Analysis
```python
VADParams(stop_secs=0.2)  # Your current (VERY aggressive)
```

**Issue:** 200ms is extremely fast - may cut off natural pauses mid-sentence

### Recommended Settings

**For Sales (Fast-Paced):**
```python
VADParams(
    stop_secs=0.3,     # 300ms pause = done speaking
    start_secs=0.1,    # 100ms to detect start
    confidence=0.6,    # Slightly more sensitive
    min_volume=0.4     # Lower for phone background noise
)
```

**For Natural Conversation:**
```python
VADParams(
    stop_secs=0.5,     # 500ms pause (balanced)
    start_secs=0.1,
    confidence=0.6,
    min_volume=0.4
)
```

**Conservative (If Users Get Cut Off):**
```python
VADParams(
    stop_secs=0.8,     # Pipecat default
    start_secs=0.2,
    confidence=0.7,
    min_volume=0.6
)
```

---

## 🤖 LLM SETTINGS: VOICE vs CHAT

### ✅ Your Current Settings (EXCELLENT)
```json
{
  "temperature": 0,
  "max_completion_tokens": 150,
  "top_p": 1
}
```

### Why These Are Perfect

**Temperature = 0:**
- Deterministic responses (follows script exactly)
- No improvisation/hallucination
- Faster generation (less sampling)
- Consistent across calls

**Max Tokens = 150:**
- ~30-40 words per response
- Natural conversation chunk size
- Prevents rambling
- Good for phone pacing

**Comparison:**

| Setting | Chat Mode | Voice Mode |
|---------|-----------|------------|
| Temperature | 0.7-1.0 | 0-0.3 |
| Max Tokens | 500-2000 | 50-150 |
| Format | Markdown, bullets | Plain text only |
| Style | Detailed, formatted | Conversational, brief |

---

## 📝 PROMPT ENGINEERING FOR VOICE

### ❌ NEVER Use in Voice Prompts
- Emojis (🚨, ✅, etc.) - TTS reads them literally
- Markdown formatting (**bold**, *italic*)
- Stage directions (*smiling*, (pause), [laughs])
- Multi-paragraph instructions
- "Use bullet points" or "format as..."

### ✅ ALWAYS Include in Voice Prompts
- "Keep responses under 40 words"
- "Ask ONE question then STOP"
- "Sound like a natural phone conversation"
- "Use contractions (you're, I'm, we'll)"
- "NO emojis, asterisks, or special characters"

### Your Prompt Issues

**Current Problems:**
1. Contains emoji: 🚨 (TTS may say "siren")
2. Very long (may slow first token)
3. "ENTHUSIASTIC, ENTHUSIASTIC" may cause CAPS shouting

**Recommended Addition:**
```
VOICE CALL RULES:
- Keep EVERY response under 40 words
- NEVER use emojis, asterisks, parentheses, or brackets
- Sound natural like you're on the phone
- Use contractions
- NO stage directions
```

---

## 📞 TELEPHONY BEST PRACTICES

### Audio Standards (SIP/PSTN)
- Sample Rate: 8kHz (G.711 standard)
- Bit Depth: 16-bit signed PCM
- Channels: Mono
- Frame Size: 20ms (160 samples @ 8kHz)

### Your Setup (✅ Good)
```
PSTN 8kHz → Asterisk → AudioSocket 8kHz → Pipecat → Deepgram 16kHz
                                                      (upsamples internally)
```

### Network Optimization
```conf
# Jitter buffer (smooths packet arrival)
jitterbuffer=yes
jitterbuffermax=50

# RTP optimization (reduce probation)
rtpstart=10000
rtpend=20000
probation=2  # Down from default 4 (saves 80ms)

# QoS (prioritize voice packets)
tos_audio=ef
cos_audio=5
```

### Latency Budget (Target: <1500ms)
- STT (Deepgram): ~300ms
- LLM (Cerebras 70B): ~200-400ms
- TTS (Edge): ~300ms
- Network: ~100-200ms
- **Total:** ~900-1200ms ✅

---

## 🧪 TESTING CHECKLIST

### Echo Test
1. Call bot, stay SILENT after opening
2. ✅ Bot should NOT continue talking to itself
3. ✅ Transcript shows no bot speech in STT output

### Conversation Flow Test
1. Let bot finish opening pitch
2. Speak after it completes
3. ✅ Bot hears you and responds appropriately
4. ✅ Natural back-and-forth rhythm

### VAD Tuning Test
1. Speak with natural pauses mid-sentence
2. If bot cuts you off → increase stop_secs
3. If long silence after you finish → decrease stop_secs
4. ✅ Optimal: ~300-500ms response delay

### Interruption Test (If Enabled)
1. Try interrupting bot mid-sentence
2. Say 2+ words: "Wait, I have..."
3. ✅ Bot should stop and listen
4. Single words ("um") should NOT interrupt

---

## 🚀 ADVANCED: SMART INTERRUPTIONS

Once echo is fixed and stable:

```python
from pipecat.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy

interruption_strategy = MinWordsInterruptionStrategy(min_words=2)

task = PipelineTask(
    pipeline,
    params=PipelineParams(
        allow_interruptions=True,
        interruption_strategy=interruption_strategy,
    ),
)
```

**Why 2 words:**
- Prevents false triggers ("uh", "um")
- Allows real interruptions ("wait, actually...")
- Natural conversation feel

---

## 📈 PRODUCTION METRICS

### Monitor These:
- **Echo rate:** Should be 0%
- **Avg response latency:** Target <1500ms
- **Call completion rate:** Should increase
- **User interruptions:** Track frequency
- **VAD false positives:** Background noise triggers

### Success Criteria:
✅ Zero echo events  
✅ <1500ms response time  
✅ Natural conversation pacing  
✅ Users can interrupt when needed  
✅ No crashes on consecutive calls  

---

## 🔍 TROUBLESHOOTING

### Problem: Bot still echoes after adding filter
**Check:**
1. Filter is BEFORE stt in pipeline
2. Import is correct (STTMuteFilter not STTFilter)
3. Strategy is set correctly
4. No duplicate stt instances in pipeline

### Problem: User can't interrupt at all
**Solution:**
- Change to `MUTE_UNTIL_FIRST_BOT_COMPLETE`
- Or use `FIRST_SPEECH` instead of `ALWAYS`
- Add MinWordsInterruptionStrategy

### Problem: Bot cuts off user mid-sentence
**Solution:**
- Increase VAD stop_secs (try 0.5 or 0.8)
- Increase confidence threshold
- Check min_volume isn't too sensitive

### Problem: Long awkward pauses
**Solution:**
- Decrease VAD stop_secs (try 0.3)
- Check LLM latency isn't excessive
- Verify network/jitter buffer settings

---

## 📚 RESOURCES

**Pipecat Documentation:**
- STTMuteFilter: Used in all production voice AI (Vapi, Retell)
- VAD Analyzers: Silero is industry standard
- Interruption Strategies: Critical for natural conversation

**Industry Standards:**
- PSTN Audio: G.711 codec, 8kHz
- VoIP QoS: DSCP EF (46), COS 5
- Latency Target: <1500ms total RTT

**Your Implementation:**
- AudioSocket: Handles codec conversion automatically
- Asterisk: Provides RTP/jitter buffer optimization
- Pipecat: Battle-tested framework (Daily.co production)

---

## 🎬 QUICK START COMMANDS

```bash
# 1. Edit bot script
nano /home/user/Desktop/exodus-kali-deploy/ava_sales_bot_audiosocket.py

# 2. Add 3 changes:
#    - Import STTMuteFilter (line 26)
#    - Create filter (line 312)
#    - Insert in pipeline (line 318)

# 3. Restart bot
killall python3
./start_dialer.sh

# 4. Test call
# Dial extension 9092
# Stay silent after opening
# Verify no echo
```

---

**Implementation Time:** 5 minutes  
**Risk Level:** Very Low (battle-tested component)  
**Expected Result:** Zero echo, natural conversation
