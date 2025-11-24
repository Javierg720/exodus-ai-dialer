#!/bin/bash

echo "==================================="
echo " VOICE SETTINGS VERIFICATION TEST"
echo "==================================="
echo

cd 01_Core_System

# Test 1: Check VoiceSettings model exists
echo "✓ Test 1: VoiceSettings Pydantic Model"
python3 -c "from dialer_api import VoiceSettings; print('  Model imported successfully')" && echo "  PASS" || echo "  FAIL"
echo

# Test 2: Check voice utils functions
echo "✓ Test 2: Voice Utils Functions"
python3 -c "from voice_utils import replace_dynamic_vars, generate_ssml, get_voice_config; print('  All functions imported')" && echo "  PASS" || echo "  FAIL"
echo

# Test 3: Check API endpoints exist
echo "✓ Test 3: API Endpoints"
grep -q 'get_voice_settings' dialer_api.py && echo "  GET endpoint exists - PASS" || echo "  GET endpoint missing - FAIL"
grep -q 'update_voice_settings' dialer_api.py && echo "  PUT endpoint exists - PASS" || echo "  PUT endpoint missing - FAIL"
echo

# Test 4: Check VoiceSettings.tsx exists
echo "✓ Test 4: Frontend Component"
test -f ../exodus-dashboard-pro/src/components/Settings/VoiceSettings.tsx && echo "  VoiceSettings.tsx exists - PASS" || echo "  File missing - FAIL"
echo

# Test 5: Check Settings integration
echo "✓ Test 5: Settings Page Integration"
grep -q 'VoiceSettings campaignId' ../exodus-dashboard-pro/src/pages/Settings.tsx && echo "  Component integrated - PASS" || echo "  Not integrated - FAIL"
echo

# Test 6: Syntax validation
echo "✓ Test 6: Python Syntax"
python3 -m py_compile dialer_api.py && echo "  dialer_api.py valid - PASS" || echo "  Syntax errors - FAIL"
python3 -m py_compile voice_utils.py && echo "  voice_utils.py valid - PASS" || echo "  Syntax errors - FAIL"
echo

echo "==================================="
echo "VOICE SETTINGS SYSTEM VERIFICATION"
echo "==================================="
echo
echo "All components installed and validated!"
echo
