#!/bin/bash
# Configure DIDlogic SIP Trunk for Exodus Dialer Outbound Calls

echo "🔧 Configuring DIDlogic SIP trunk for Exodus..."

# Backup current configs
echo "📦 Backing up current Asterisk configs..."
cp /etc/asterisk/pjsip.conf /etc/asterisk/pjsip.conf.backup-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true
cp /etc/asterisk/extensions.conf /etc/asterisk/extensions.conf.backup-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true

# Copy updated configs
echo "📋 Copying updated configurations..."
cp 03_Asterisk_Config/conf/pjsip.conf /etc/asterisk/pjsip.conf
cp 03_Asterisk_Config/conf/extensions.conf /etc/asterisk/extensions.conf

# Set proper permissions
chown asterisk:asterisk /etc/asterisk/pjsip.conf
chown asterisk:asterisk /etc/asterisk/extensions.conf

# Reload Asterisk
echo "🔄 Reloading Asterisk configuration..."
asterisk -rx "pjsip reload"
asterisk -rx "dialplan reload"

# Verify registration
echo ""
echo "✅ Configuration complete!"
echo ""
echo "📊 Checking SIP registration status..."
sleep 3
asterisk -rx "pjsip show registrations"

echo ""
echo "📞 Testing SIP trunk..."
asterisk -rx "pjsip show endpoints" | grep didlogic

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIDlogic SIP Trunk Configuration Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 Trunk Details:"
echo "   • Provider: DIDlogic.com"
echo "   • Server: sip.nyc.didlogic.net"
echo "   • Account: 02244 (javier)"
echo "   • Max Channels: 5"
echo "   • Max Rate: \$0.35/min"
echo ""
echo "📞 Outbound calls will now route through DIDlogic trunk"
echo "   Format: PJSIP/{number}@didlogic"
echo ""
echo "🔍 To verify registration:"
echo "   asterisk -rx 'pjsip show registrations'"
echo ""
echo "🧪 To test a call:"
echo "   asterisk -rx 'channel originate PJSIP/15615324683@didlogic application Echo'"
echo ""
