#!/bin/bash
# Script to move analysis reports to Desktop

REPORTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_DIR="$HOME/Desktop/EXODUS_SYSTEM_ANALYSIS_REPORTS"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  EXODUS SYSTEM ANALYSIS - MOVE TO DESKTOP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📂 Source: $REPORTS_DIR"
echo "📂 Destination: $DESKTOP_DIR"
echo ""

# Create Desktop directory
if [ ! -d "$DESKTOP_DIR" ]; then
    echo "📁 Creating Desktop folder..."
    mkdir -p "$DESKTOP_DIR"
else
    echo "📁 Desktop folder already exists"
fi

# Copy all reports
echo "📋 Copying reports..."
cp -r "$REPORTS_DIR"/* "$DESKTOP_DIR/"

# Verify
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Reports copied to:"
    echo "   $DESKTOP_DIR"
    echo ""
    echo "📊 Files copied:"
    ls -lh "$DESKTOP_DIR" | tail -n +2
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ ALL REPORTS READY ON YOUR DESKTOP!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📖 START HERE: Read 00_README_START_HERE.md first"
    echo ""
else
    echo ""
    echo "❌ ERROR: Failed to copy reports"
    echo "   Try running: sudo bash $0"
    exit 1
fi
