#!/bin/bash
# Exodus AI Dialer System - Complete Backup Script
# Created: 2025-11-17
# This script backs up ALL critical files needed to run the Exodus system

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/media/ubuntu/c734bfa2-4378-42f2-8635-4003a9ce637f/home/user/EXODUS_BACKUP_${TIMESTAMP}"
WORK_DIR="/media/ubuntu/c734bfa2-4378-42f2-8635-4003a9ce637f/home/user"

echo "================================================================"
echo "EXODUS AI DIALER - COMPLETE SYSTEM BACKUP"
echo "================================================================"
echo "Timestamp: ${TIMESTAMP}"
echo "Backup location: ${BACKUP_DIR}"
echo ""

# Create backup directory structure
mkdir -p "${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}/01_Core_System"
mkdir -p "${BACKUP_DIR}/02_AVR_Platform"
mkdir -p "${BACKUP_DIR}/03_Asterisk_Config"
mkdir -p "${BACKUP_DIR}/04_Documentation"
mkdir -p "${BACKUP_DIR}/05_Database"
mkdir -p "${BACKUP_DIR}/06_Memory_Files"
mkdir -p "${BACKUP_DIR}/07_Scripts"

echo "[1/8] Backing up Core System Files..."
cd "${WORK_DIR}/Desktop/Projects_Organized/01_Exodus_Dialer/exodus-kali-deploy"

# Core Python files
cp -v dialer_orchestrator.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v dialer_api.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v dialer_db.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v dialer_db_async.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v bot_pool_manager.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v avr_bot_pool_manager.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v ava_sales_bot_audiosocket.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v audiosocket_transport.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v edge_tts_service.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v tcpa_compliance.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v transcript_manager.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v simple_ami.py "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true

# Configuration files
cp -v docker-compose-avr-bots.yml "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v .env "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v bot_config.json "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v requirements.txt "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true

# Startup/management scripts
cp -v start_production.sh "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v stop_production.sh "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v check_status.sh "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v start_bot_pool_20.sh "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true
cp -v start_dialer.sh "${BACKUP_DIR}/01_Core_System/" 2>/dev/null || true

echo "[2/8] Backing up AVR Platform Files..."
if [ -d "${WORK_DIR}/Desktop/Projects_Organized/02_AVR_Voice_Platform" ]; then
    # AVR custom providers
    if [ -d "${WORK_DIR}/Desktop/Projects_Organized/02_AVR_Voice_Platform/avr-app/custom-providers" ]; then
        cp -rv "${WORK_DIR}/Desktop/Projects_Organized/02_AVR_Voice_Platform/avr-app/custom-providers" \
               "${BACKUP_DIR}/02_AVR_Platform/" 2>/dev/null || true
    fi

    # AVR working configs backup
    if [ -d "${WORK_DIR}/Desktop/Projects_Organized/02_AVR_Voice_Platform/WORKING_CONFIGS_BACKUP" ]; then
        cp -rv "${WORK_DIR}/Desktop/Projects_Organized/02_AVR_Voice_Platform/WORKING_CONFIGS_BACKUP" \
               "${BACKUP_DIR}/02_AVR_Platform/" 2>/dev/null || true
    fi
fi

echo "[3/8] Backing up Asterisk Configuration..."
if [ -d "${WORK_DIR}/Desktop/ava-asterisk-config" ]; then
    cp -rv "${WORK_DIR}/Desktop/ava-asterisk-config/conf" "${BACKUP_DIR}/03_Asterisk_Config/" 2>/dev/null || true
fi

echo "[4/8] Backing up Documentation..."
cd "${WORK_DIR}/Desktop/Projects_Organized/01_Exodus_Dialer/exodus-kali-deploy"

# All markdown documentation
find . -maxdepth 1 -name "*.md" -exec cp -v {} "${BACKUP_DIR}/04_Documentation/" \; 2>/dev/null || true

# Copy additional important docs from home directory
cp -v "${WORK_DIR}/AUDIOSOCKET_INVESTIGATION_SUMMARY.md" "${BACKUP_DIR}/04_Documentation/" 2>/dev/null || true
cp -v "${WORK_DIR}/OPENING_MESSAGE_RESEARCH.md" "${BACKUP_DIR}/04_Documentation/" 2>/dev/null || true
cp -v "${WORK_DIR}/VICIDIAL_"*.md "${BACKUP_DIR}/04_Documentation/" 2>/dev/null || true
cp -v "${WORK_DIR}/CAMP3_OCT_LEADS_COMPLETE.md" "${BACKUP_DIR}/04_Documentation/" 2>/dev/null || true

echo "[5/8] Backing up Database..."
cd "${WORK_DIR}/Desktop/Projects_Organized/01_Exodus_Dialer/exodus-kali-deploy"

# Main database
cp -v dialer.db "${BACKUP_DIR}/05_Database/dialer.db" 2>/dev/null || true

# Database WAL and SHM files (if exist)
cp -v dialer.db-wal "${BACKUP_DIR}/05_Database/" 2>/dev/null || true
cp -v dialer.db-shm "${BACKUP_DIR}/05_Database/" 2>/dev/null || true

# Any other databases in data/ directory
if [ -d "data" ]; then
    cp -v data/*.db "${BACKUP_DIR}/05_Database/" 2>/dev/null || true
fi

echo "[6/8] Backing up Memory Files..."
# Claude memory file
cp -v "${WORK_DIR}/Desktop/claude_memory.txt" "${BACKUP_DIR}/06_Memory_Files/" 2>/dev/null || true

# Claude config
cp -rv "${WORK_DIR}/.claude" "${BACKUP_DIR}/06_Memory_Files/.claude" 2>/dev/null || true

# Project memory files
cp -v "${WORK_DIR}/bug_bounty_project_memory.md" "${BACKUP_DIR}/06_Memory_Files/" 2>/dev/null || true

echo "[7/8] Backing up Utility Scripts..."
cd "${WORK_DIR}"

# Test scripts
cp -v test_exodus_*.sh "${BACKUP_DIR}/07_Scripts/" 2>/dev/null || true
cp -v monitor_call.sh "${BACKUP_DIR}/07_Scripts/" 2>/dev/null || true
cp -v production_check.sh "${BACKUP_DIR}/07_Scripts/" 2>/dev/null || true
cp -v ssh_commands.sh "${BACKUP_DIR}/07_Scripts/" 2>/dev/null || true

# VICIdial scripts
cp -v vicidial_*.py "${BACKUP_DIR}/07_Scripts/" 2>/dev/null || true
cp -v load_oct_leads.py "${BACKUP_DIR}/07_Scripts/" 2>/dev/null || true
cp -v upload_vicidial_leads.py "${BACKUP_DIR}/07_Scripts/" 2>/dev/null || true

# Ethereum scripts
cp -v fetch_balances.py "${BACKUP_DIR}/07_Scripts/" 2>/dev/null || true
cp -v check_eth_balances.py "${BACKUP_DIR}/07_Scripts/" 2>/dev/null || true

echo "[8/8] Creating backup manifest..."

cat > "${BACKUP_DIR}/BACKUP_MANIFEST.txt" << 'EOF'
================================================================================
EXODUS AI DIALER - COMPLETE SYSTEM BACKUP MANIFEST
================================================================================

Backup Date: $(date)
Backup Location: $(basename ${BACKUP_DIR})

================================================================================
DIRECTORY STRUCTURE
================================================================================

01_Core_System/           - Core Python files, configurations, startup scripts
02_AVR_Platform/          - AVR custom providers (Groq, Deepgram, Edge TTS)
03_Asterisk_Config/       - Asterisk dialplan and SIP trunk configuration
04_Documentation/         - All markdown documentation and guides
05_Database/              - SQLite databases (dialer.db + backups)
06_Memory_Files/          - Claude memory and configuration files
07_Scripts/               - Utility and management scripts

================================================================================
CRITICAL FILES INCLUDED
================================================================================

CORE SYSTEM:
- dialer_orchestrator.py      - Main orchestration engine
- dialer_api.py                - FastAPI backend
- dialer_db.py                 - Database operations
- dialer_db_async.py           - Async database layer
- avr_bot_pool_manager.py      - AVR bot pool management
- ava_sales_bot_audiosocket.py - Pipecat bot implementation
- audiosocket_transport.py     - AudioSocket transport layer
- docker-compose-avr-bots.yml  - AVR Docker orchestration
- bot_config.json              - Bot configuration
- .env                         - Environment variables

STARTUP SCRIPTS:
- start_production.sh          - Production startup
- stop_production.sh           - Production shutdown
- check_status.sh              - System status check

ASTERISK CONFIG:
- extensions.conf              - Dialplan with AudioSocket routing
- pjsip.conf                   - Twilio SIP trunk configuration

AVR PLATFORM:
- custom-providers/avr-llm-groq/      - Groq LLM provider (FREE)
- custom-providers/avr-tts-edgetts/   - Edge TTS provider (FREE)
- custom-providers/avr-asr-deepgram/  - Deepgram ASR provider

DATABASE:
- dialer.db                    - Main production database
- All WAL and SHM files

DOCUMENTATION:
- PROJECT_STATUS.md            - Current project status
- EXECUTIVE_SUMMARY.md         - System overview
- SYSTEM_FAILURE_ANALYSIS_AND_SOLUTIONS.md - Troubleshooting
- All other .md files

MEMORY:
- claude_memory.txt            - Complete project memory (Phases 1-16)
- .claude/                     - Claude configuration

================================================================================
SYSTEM SPECIFICATIONS (as of backup)
================================================================================

Technology Stack:
- 20 AVR Core bots (ports 9092-9111)
- Groq llama-3.3-70b-versatile (LLM - FREE)
- Deepgram nova-2-phonecall (ASR - $0.26/hr)
- Edge TTS en-US-AvaMultilingualNeural (TTS - FREE)
- Asterisk + AudioSocket
- Twilio SIP trunk
- SQLite database
- FastAPI backend

Cost Structure:
- $0.26/hour per bot
- $5.20/hour for 20 bots
- 94% cheaper than STS mode

Current Status:
- Phase 16: Recording working with AUDIOHOOK_INHERIT
- Modular pipeline operational (Groq + Deepgram + Edge)
- All 20 bots deployed and idle
- Production ready

================================================================================
RESTORATION INSTRUCTIONS
================================================================================

To restore the Exodus system from this backup:

1. COPY CORE FILES:
   cp 01_Core_System/* /path/to/exodus-kali-deploy/

2. RESTORE ASTERISK CONFIG:
   cp 03_Asterisk_Config/conf/* /path/to/ava-asterisk-config/conf/
   docker exec ava-asterisk asterisk -rx "dialplan reload"

3. RESTORE AVR PROVIDERS:
   cp -r 02_AVR_Platform/custom-providers /path/to/avr-app/
   cd /path/to/avr-app/custom-providers/avr-llm-groq
   docker build -t avr-llm-groq:latest .

4. RESTORE DATABASE:
   cp 05_Database/dialer.db /path/to/exodus-kali-deploy/

5. CONFIGURE ENVIRONMENT:
   Edit 01_Core_System/.env with your credentials:
   - GROQ_API_KEY
   - DEEPGRAM_API_KEY
   - TWILIO credentials

6. START SYSTEM:
   cd /path/to/exodus-kali-deploy
   docker-compose -f docker-compose-avr-bots.yml up -d
   ./start_production.sh

================================================================================
CREDENTIALS (stored in .env - UPDATE BEFORE DEPLOYMENT)
================================================================================

GROQ_API_KEY=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
DEEPGRAM_API_KEY=44f464f1116d54ee9412f7b9214cdde028240091
TWILIO_ACCOUNT_SID=(in .env)
TWILIO_AUTH_TOKEN=(in .env)
TWILIO_PHONE_NUMBER=+15615324683

VICIdial (separate system):
- Server: 46.62.216.79
- Admin: https://merchantfundexp.cloudautodialer.in
- User: javiersuper / oX05mP6450c4L10

================================================================================
IMPORTANT NOTES
================================================================================

1. This backup includes PRODUCTION database with live leads
2. .env file contains API keys - keep secure
3. Docker images must be rebuilt for AVR custom providers
4. Asterisk configuration assumes Twilio trunk "twilio"
5. Recording requires AUDIOHOOK_INHERIT in extensions.conf
6. Bot ports 9092-9111 must be available
7. System requires ~4GB RAM for 20 bots

================================================================================
BACKUP VERIFICATION
================================================================================

To verify backup integrity:
1. Check file count in each directory
2. Verify dialer.db opens with: sqlite3 dialer.db ".tables"
3. Confirm .env has all required keys
4. Test docker-compose-avr-bots.yml syntax

================================================================================
SUPPORT & DOCUMENTATION
================================================================================

For system documentation, see:
- 04_Documentation/PROJECT_STATUS.md
- 04_Documentation/EXECUTIVE_SUMMARY.md
- 06_Memory_Files/claude_memory.txt

For troubleshooting:
- 04_Documentation/SYSTEM_FAILURE_ANALYSIS_AND_SOLUTIONS.md
- 04_Documentation/QUICK_FIX_IMPLEMENTATION.md

================================================================================
EOF

# Update manifest with actual timestamp
sed -i "s/\$(date)/${TIMESTAMP}/g" "${BACKUP_DIR}/BACKUP_MANIFEST.txt"
sed -i "s/\$(basename \${BACKUP_DIR})/EXODUS_BACKUP_${TIMESTAMP}/g" "${BACKUP_DIR}/BACKUP_MANIFEST.txt"

echo ""
echo "[✓] Creating file list..."
find "${BACKUP_DIR}" -type f > "${BACKUP_DIR}/FILE_LIST.txt"

echo "[✓] Calculating sizes..."
du -sh "${BACKUP_DIR}" > "${BACKUP_DIR}/BACKUP_SIZE.txt"
du -sh "${BACKUP_DIR}"/* >> "${BACKUP_DIR}/BACKUP_SIZE.txt"

echo ""
echo "================================================================"
echo "BACKUP COMPLETE!"
echo "================================================================"
echo ""
echo "Backup Location: ${BACKUP_DIR}"
echo ""
echo "Summary:"
cat "${BACKUP_DIR}/BACKUP_SIZE.txt"
echo ""
echo "Files backed up:"
wc -l < "${BACKUP_DIR}/FILE_LIST.txt"
echo ""
echo "Next steps:"
echo "1. Review: cat ${BACKUP_DIR}/BACKUP_MANIFEST.txt"
echo "2. Compress: tar -czf EXODUS_BACKUP_${TIMESTAMP}.tar.gz -C $(dirname ${BACKUP_DIR}) $(basename ${BACKUP_DIR})"
echo "3. Transfer to safe location"
echo ""
echo "================================================================"
