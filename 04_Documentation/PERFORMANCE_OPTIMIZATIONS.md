# PERFORMANCE OPTIMIZATIONS - IMPLEMENTING AUDIT RECOMMENDATIONS

**Date**: 2025-10-18  
**Goal**: Reduce 775ms response time by optimizing audio resampling + error handling

---

## OPTIMIZATIONS TO IMPLEMENT

### 1. Replace scipy resampling with librosa (PRIORITY 1)
**Current**: scipy.signal.resample_poly (~10ms per frame)  
**Target**: librosa.resample (~2ms per frame)  
**Expected Gain**: -8ms per frame × 2 directions = -16ms total  
**For 20 bots**: -320ms cumulative CPU time saved

### 2. Add comprehensive error handling (PRIORITY 1)
**Current**: Missing try-except in critical paths  
**Target**: Graceful degradation on all errors  
**Expected Gain**: Zero crashes, better stability

### 3. Implement backpressure handling (PRIORITY 2)
**Current**: No flow control for slow bots  
**Target**: Bounded queues with overflow detection  
**Expected Gain**: Better audio quality, no dropped frames

---

## IMPLEMENTATION PLAN

**Phase 1**: Install librosa + replace resampling (30 mins)
**Phase 2**: Add error handling to audiosocket_transport.py (30 mins)
**Phase 3**: Add error handling to ava_sales_bot_audiosocket.py (30 mins)
**Phase 4**: Test and verify improvements (30 mins)

**Total Time**: 2 hours

---

## FILES TO MODIFY

1. `audiosocket_transport.py` - Replace AudioResampler class
2. `ava_sales_bot_audiosocket.py` - Add error handling to main loop
3. `requirements.txt` - Add librosa dependency

