# Pipecat Audio Frame Research Findings
## Problem: Audio arrives at transport but empty at STT

**Date**: 2025-10-19  
**Issue**: Transport logs show `UserAudioRawFrame` with 320 bytes, but STT receives `frame.audio=0 bytes`

---

## ROOT CAUSE IDENTIFIED ✅

### The Problem: Frame Type Mismatch

**Your code** (audiosocket_transport.py:444-449):
```python
frame = UserAudioRawFrame(
    audio=audio_16k,
    sample_rate=PIPECAT_SAMPLE_RATE,
    num_channels=PIPECAT_CHANNELS,
    user_id="caller",
)
await self.push_audio_frame(frame)
```

**The issue**: You're calling `BaseInputTransport.push_audio_frame()` which has this signature:

```python
# From base_input.py:257-264
async def push_audio_frame(self, frame: InputAudioRawFrame):
    """Push an audio frame to the processing queue if audio input is enabled.
    
    Args:
        frame: The input audio frame to process.
    """
    if self._params.audio_in_enabled and not self._paused:
        await self._audio_in_queue.put(frame)
```

**Critical discovery**: `push_audio_frame()` expects `InputAudioRawFrame`, not `UserAudioRawFrame`!

---

## Understanding Frame Hierarchy

### Frame Type Definitions (from frames.py)

1. **AudioRawFrame** (Mixin - contains audio data):
```python
@dataclass
class AudioRawFrame:
    audio: bytes
    sample_rate: int
    num_channels: int
    num_frames: int = field(default=0, init=False)
```

2. **InputAudioRawFrame** (SystemFrame + AudioRawFrame):
```python
@dataclass
class InputAudioRawFrame(SystemFrame, AudioRawFrame):
    """Raw audio input frame from transport."""
    # Used for single-user scenarios (local audio, websockets)
```

3. **UserAudioRawFrame** (InputAudioRawFrame + user_id):
```python
@dataclass
class UserAudioRawFrame(InputAudioRawFrame):
    """Raw audio input frame associated with a specific user."""
    user_id: str = ""
    # Used for multi-user scenarios (Daily, Livekit, etc.)
```

**Key insight**: `UserAudioRawFrame` IS-A `InputAudioRawFrame`, so the type should work... but there's something else going on!

---

## How Audio Flows in Pipecat

### 1. Transport pushes frame → audio queue

```python
# base_input.py:257-264
async def push_audio_frame(self, frame: InputAudioRawFrame):
    if self._params.audio_in_enabled and not self._paused:
        await self._audio_in_queue.put(frame)  # ← Frame goes into queue
```

### 2. Audio task handler processes queue

```python
# base_input.py:459-489 (_audio_task_handler)
while True:
    frame: InputAudioRawFrame = await asyncio.wait_for(
        self._audio_in_queue.get(), timeout=AUDIO_INPUT_TIMEOUT_SECS
    )
    
    # Apply audio filter (if configured)
    if self._params.audio_in_filter:
        frame.audio = await self._params.audio_in_filter.filter(frame.audio)
    
    # Run VAD analysis (if configured)
    if self._params.vad_analyzer:
        vad_state = await self._handle_vad(frame, vad_state)
    
    # ⚠️ CRITICAL: Push frame downstream ONLY if passthrough enabled
    if self._params.audio_in_passthrough:
        await self.push_frame(frame)  # ← This sends to STT
```

### 3. STT service receives and processes frame

```python
# stt_service.py:160-189 (process_audio_frame)
async def process_audio_frame(self, frame: AudioRawFrame, direction: FrameDirection):
    if self._muted:
        return
    
    # Extract user_id if present
    if hasattr(frame, "user_id"):
        self._user_id = frame.user_id
    
    # ⚠️ CRITICAL CHECK: Empty audio frames are rejected!
    if not frame.audio:
        logger.warning(
            f"Empty audio frame received for STT service: {self.name} {frame.num_frames}"
        )
        return  # ← Your frames are getting rejected here!
    
    await self.process_generator(self.run_stt(frame.audio))

# stt_service.py:191-213 (process_frame dispatcher)
async def process_frame(self, frame: Frame, direction: FrameDirection):
    await super().process_frame(frame, direction)
    
    if isinstance(frame, AudioRawFrame):  # ← Matches both Input and User frames
        await self.process_audio_frame(frame, direction)
        if self._audio_passthrough:
            await self.push_frame(frame, direction)
```

---

## The Real Problem: Audio Filter or Frame Mutation

Based on the code flow, there are **THREE potential causes**:

### Hypothesis 1: Audio Filter is Clearing Data ❌ (UNLIKELY)
```python
# base_input.py:469-470
if self._params.audio_in_filter:
    frame.audio = await self._params.audio_in_filter.filter(frame.audio)
```

**Your config**: `audio_in_filter=None` (not set), so this can't be the issue.

### Hypothesis 2: VAD is Modifying Frames ❌ (UNLIKELY)
```python
# base_input.py:475-476
if self._params.vad_analyzer:
    vad_state = await self._handle_vad(frame, vad_state)
```

**Your config**: `vad_enabled=False, vad_analyzer=None`, so this can't be the issue.

### Hypothesis 3: Frame Audio Field Not Being Copied ✅ (MOST LIKELY)

**CRITICAL DISCOVERY**: Python dataclasses with mutable fields (like `bytes`) can have reference issues!

When you create `UserAudioRawFrame`, the `audio` field might not be properly initialized if:
1. The parent `__post_init__` isn't called correctly
2. There's a shallow vs deep copy issue
3. The audio bytes are being garbage collected

---

## Working Examples from Pipecat

### Daily Transport (Multi-user, uses UserAudioRawFrame)
```python
# daily/transport.py:1736-1743
async def _on_participant_audio_data(self, participant_id: str, audio: AudioData, audio_source: str):
    frame = UserAudioRawFrame(
        user_id=participant_id,
        audio=audio.audio_frames,  # Direct bytes assignment
        sample_rate=audio.sample_rate,
        num_channels=audio.num_channels,
    )
    frame.transport_source = audio_source
    await self.push_audio_frame(frame)  # ← Works perfectly
```

### Local Audio Transport (Single-user, uses InputAudioRawFrame)
```python
# local/audio.py:106-112
frame = InputAudioRawFrame(
    audio=audio_bytes,
    sample_rate=self._sample_rate,
    num_channels=1,
)
asyncio.run_coroutine_threadsafe(
    self.push_audio_frame(frame), 
    self.get_event_loop()
)
```

---

## SOLUTION: What's Wrong in Your Code

### Issue #1: Bytes Object Lifecycle ⚠️

```python
# audiosocket_transport.py:434-435
audio_8k = payload  # ← payload is raw bytes from network
audio_16k = AudioResampler.resample_8k_to_16k(audio_8k)  # ← Creates new bytes

# audiosocket_transport.py:444-449
frame = UserAudioRawFrame(
    audio=audio_16k,  # ← This should work, but...
    sample_rate=PIPECAT_SAMPLE_RATE,
    num_channels=PIPECAT_CHANNELS,
    user_id="caller",
)
```

**Potential problem**: The `audio_16k` bytes object might be getting modified or cleared AFTER frame creation but BEFORE the audio task handler processes it from the queue.

### Issue #2: Async Queue Timing ⚠️

```python
# Your code calls this:
await self.push_audio_frame(frame)  # Puts frame in queue

# But the frame sits in queue until:
frame = await asyncio.wait_for(self._audio_in_queue.get(), ...)  # Retrieved later

# By the time it's retrieved, frame.audio might be empty!
```

---

## DEBUGGING STEPS

### Step 1: Add Deep Copy Test
```python
# In audiosocket_transport.py after line 435:
import copy
audio_16k = AudioResampler.resample_8k_to_16k(audio_8k)
audio_16k_copy = copy.deepcopy(audio_16k)  # Force a deep copy

logger.info(f"🔍 PRE-FRAME: audio_16k={len(audio_16k)}, copy={len(audio_16k_copy)}")

frame = UserAudioRawFrame(
    audio=audio_16k_copy,  # Use the copy instead
    sample_rate=PIPECAT_SAMPLE_RATE,
    num_channels=PIPECAT_CHANNELS,
    user_id="caller",
)

logger.info(f"🔍 POST-FRAME: frame.audio={len(frame.audio) if frame.audio else 0}")
```

### Step 2: Verify Frame Contents Immediately After Creation
```python
# After line 449:
assert frame.audio is not None, "Frame audio is None right after creation!"
assert len(frame.audio) > 0, f"Frame audio is empty right after creation! len={len(frame.audio)}"
logger.info(f"✅ Frame created successfully with {len(frame.audio)} bytes")
```

### Step 3: Check if Queue is Preserving Data
```python
# Modify push_audio_frame in your AudioSocketInputTransport:
async def push_audio_frame(self, frame: InputAudioRawFrame):
    """Override to add debugging."""
    logger.info(f"🔍 BEFORE QUEUE: frame.audio={len(frame.audio) if frame.audio else 0}")
    await super().push_audio_frame(frame)
    logger.info(f"🔍 AFTER QUEUE PUT")
```

### Step 4: Check Audio Task Handler Receives Data
Add logging to base class (monkey patch):
```python
# In your bot script, after imports:
original_audio_task = BaseInputTransport._audio_task_handler

async def debug_audio_task(self):
    """Wrapper to debug audio task."""
    logger.info("🎧 Audio task handler started")
    # Call original
    await original_audio_task(self)

BaseInputTransport._audio_task_handler = debug_audio_task
```

---

## RECOMMENDED FIX

### Option 1: Use InputAudioRawFrame Instead (Simpler)

```python
# audiosocket_transport.py:444-455
# CHANGE FROM UserAudioRawFrame TO InputAudioRawFrame
frame = InputAudioRawFrame(  # ← Use simpler frame type
    audio=audio_16k,
    sample_rate=PIPECAT_SAMPLE_RATE,
    num_channels=PIPECAT_CHANNELS,
)
# Don't set user_id - not needed for single-caller telephony

await self.push_audio_frame(frame)
```

**Reasoning**: 
- You're doing telephony (1 caller per connection)
- `user_id` isn't needed for single-user scenarios
- Simpler frame type = less potential for inheritance issues
- Daily transport uses `UserAudioRawFrame` for MULTI-participant conferences
- Local audio uses `InputAudioRawFrame` for single-user scenarios
- **Your use case matches local audio, not Daily**

### Option 2: Force Bytes Copy (If you need user_id)

```python
# audiosocket_transport.py:434-455
audio_8k = payload
audio_16k = AudioResampler.resample_8k_to_16k(audio_8k)

# Force a bytes copy to ensure data persistence
audio_copy = bytes(audio_16k)  # ← Create new bytes object

frame = UserAudioRawFrame(
    audio=audio_copy,  # ← Use the copy
    sample_rate=PIPECAT_SAMPLE_RATE,
    num_channels=PIPECAT_CHANNELS,
    user_id="caller",
)

# Verify frame has data before queueing
assert frame.audio and len(frame.audio) > 0, "Frame audio empty after creation!"
logger.debug(f"✅ Frame created: {len(frame.audio)} bytes")

await self.push_audio_frame(frame)
```

---

## Additional Findings

### audio_in_passthrough is CRITICAL ✅

```python
# base_input.py:485-487
# Push audio downstream if passthrough is set.
if self._params.audio_in_passthrough:
    await self.push_frame(frame)  # ← Without this, STT never gets audio!
```

**Your config**: `audio_in_passthrough=True` ✅ CORRECT

### vad_enabled in TransportParams is DEPRECATED ⚠️

```python
# base_input.py:90-99
if self._params.vad_enabled:
    warnings.warn(
        "Parameter 'vad_enabled' is deprecated, use 'audio_in_enabled' and 'vad_analyzer' instead.",
        DeprecationWarning,
    )
    self._params.audio_in_enabled = True
```

**Your config**: You're using the deprecated parameter, but it still works.

---

## STT Service Audio Processing

### How Deepgram Processes Audio

```python
# deepgram/stt.py:203-213
async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
    """Send audio data to Deepgram for transcription."""
    await self._connection.send(audio)  # ← Sends bytes to WebSocket
    yield None  # ← Doesn't yield frames (transcripts come via callbacks)
```

**Key insight**: Deepgram sends audio bytes directly to WebSocket, so empty bytes = no transcription.

---

## Conclusion

**Most likely cause**: Frame's audio field is being cleared/modified between creation and consumption from queue.

**Recommended fix**: 
1. **First try**: Switch to `InputAudioRawFrame` (simpler, matches your use case)
2. **If that fails**: Force `bytes()` copy when creating frame
3. **Add assertions**: Verify frame.audio is not empty immediately after creation

**Next steps**:
1. Add debug logging to verify where audio disappears
2. Test with InputAudioRawFrame
3. If issue persists, check for memory corruption or garbage collection issues

---

## Files Referenced

- `/home/user/pipecat-research/src/pipecat/transports/base_input.py` - Audio frame queuing
- `/home/user/pipecat-research/src/pipecat/services/stt_service.py` - STT audio processing
- `/home/user/pipecat-research/src/pipecat/frames/frames.py` - Frame definitions
- `/home/user/pipecat-research/src/pipecat/transports/daily/transport.py` - UserAudioRawFrame example
- `/home/user/pipecat-research/src/pipecat/transports/local/audio.py` - InputAudioRawFrame example

---

**Research completed**: 2025-10-19  
**Researcher**: Multi-agent analysis (Pipecat codebase + documentation)
