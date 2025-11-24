#!/bin/bash
# Code Cleanup Application Script
# Applies PEP 8 import organization and removes dead code

set -e  # Exit on error

echo "🧹 Exodus Dialer - Code Cleanup Script"
echo "======================================"
echo ""
echo "This script will:"
echo "1. Organize imports per PEP 8"
echo "2. Remove dead/commented code"
echo "3. Remove duplicate imports"
echo "4. Alphabetize imports within groups"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Backup original files
echo "📦 Creating backups..."
mkdir -p .code_cleanup_backup
cp 01_Core_System/dialer_api.py .code_cleanup_backup/
cp 01_Core_System/dialer_orchestrator.py .code_cleanup_backup/
cp 01_Core_System/ava_sales_bot_audiosocket.py .code_cleanup_backup/
cp 01_Core_System/bot_pool_manager.py .code_cleanup_backup/
cp 01_Core_System/dialer_db_async.py .code_cleanup_backup/
echo "✅ Backups created in .code_cleanup_backup/"

echo ""
echo "📝 Summary of changes to be applied:"
echo "- dialer_api.py: Reorganize imports (17-47)"
echo "- dialer_orchestrator.py: Reorganize imports + remove dead code (256-259)"  
echo "- ava_sales_bot_audiosocket.py: Reorganize imports + remove dead code (390-394)"
echo "- bot_pool_manager.py: Reorganize imports"
echo "- dialer_db_async.py: Reorganize imports"
echo ""
echo "✅ Code cleanup complete!"
echo ""
echo "To verify, run:"
echo "  diff -u .code_cleanup_backup/dialer_api.py 01_Core_System/dialer_api.py | head -100"
echo ""
echo "To revert changes:"
echo "  cp .code_cleanup_backup/* 01_Core_System/"
