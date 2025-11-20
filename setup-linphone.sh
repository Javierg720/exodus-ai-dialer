#!/bin/bash

echo "=========================================="
echo "Linphone SIP Client Setup for AVA Bot"
echo "=========================================="
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "This script needs sudo access to install packages."
    echo "Please run: sudo bash setup-linphone.sh"
    exit 1
fi

echo "[1/4] Updating package lists..."
apt update

echo ""
echo "[2/4] Installing Linphone..."
apt install -y linphone-desktop

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Linphone"
    exit 1
fi

echo ""
echo "[3/4] Creating Linphone configuration..."

# Get the actual user (not root when using sudo)
ACTUAL_USER=${SUDO_USER:-$USER}
USER_HOME=$(eval echo ~$ACTUAL_USER)
LINPHONE_CONFIG_DIR="$USER_HOME/.local/share/linphone"
LINPHONE_RC="$LINPHONE_CONFIG_DIR/linphonerc"

# Create config directory
mkdir -p "$LINPHONE_CONFIG_DIR"

# Create Linphone configuration with testphone account
cat > "$LINPHONE_RC" << 'EOF'
[sip]
default_proxy=0
register_only_when_network_is_up=1
guess_hostname=1

[proxy_0]
reg_proxy=sip:10.0.0.113:5060;transport=udp
reg_identity=sip:testphone@10.0.0.113
reg_sendregister=1
reg_expires=3600
realm=asterisk
quality_reporting_enabled=0
quality_reporting_interval=0
contact_parameters=
publish=0
avpf=0
avpf_rr_interval=0
dial_escape_plus=0
privacy=0
push_notification_allowed=0

[auth_info_0]
username=testphone
userid=testphone
passwd=123456789101112jG
realm=asterisk
domain=10.0.0.113

[sound]
echocancellation=1
playback_dev_id=default
capture_dev_id=default
ringer_dev_id=default

[video]
enabled=0

[net]
mtu=1300
download_bw=0
upload_bw=0

[rtp]
audio_rtp_port=7078
video_rtp_port=9078
audio_jitt_comp=60
video_jitt_comp=60
nortp_timeout=30

[audio_codec_0]
mime=PCMU
rate=8000
channels=1
enabled=1

[audio_codec_1]
mime=PCMA
rate=8000
channels=1
enabled=1
EOF

# Set proper ownership
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$LINPHONE_CONFIG_DIR"

echo "✅ Linphone configuration created at: $LINPHONE_RC"

echo ""
echo "[4/4] Setup complete!"
echo ""
echo "=========================================="
echo "HOW TO USE LINPHONE"
echo "=========================================="
echo ""
echo "1. Launch Linphone:"
echo "   linphone"
echo ""
echo "2. The account should auto-register with these credentials:"
echo "   • Server: 10.0.0.113"
echo "   • Username: testphone"
echo "   • Password: 123456789101112jG"
echo ""
echo "3. To call AVA bot, dial: 9092"
echo ""
echo "4. To monitor the call in real-time, open another terminal:"
echo "   docker logs -f avr-bot-9092"
echo ""
echo "✅ You should hear AVA speak AND see ASR logs when you talk!"
echo ""
echo "=========================================="
echo "TROUBLESHOOTING"
echo "=========================================="
echo ""
echo "• If not registered: Check Settings → Accounts"
echo "• If no audio: Check Settings → Audio/Video devices"
echo "• If still issues: Run 'linphone' from terminal to see debug output"
echo ""
