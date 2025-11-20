#!/bin/bash
mkdir -p ~/.local/share/linphone
cp linphonerc ~/.local/share/linphone/linphonerc 2>/dev/null || echo "Config already exists"
echo "✅ Linphone configuration complete!"
