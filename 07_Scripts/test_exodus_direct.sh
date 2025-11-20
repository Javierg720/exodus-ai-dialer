#!/bin/bash
# Test using direct SIP URI format

HOST="172.17.0.1"
PORT="5038"
USERNAME="ava"
SECRET="ava123"

{
  echo "Action: Login"
  echo "Username: $USERNAME"
  echo "Secret: $SECRET"
  echo ""
  sleep 1
  
  echo "Action: Originate"
  echo "Channel: PJSIP/exodus-dialer.pstn.twilio.com/sip:+13057768712@exodus-dialer.pstn.twilio.com"
  echo "Context: ava-context"
  echo "Exten: 9092"
  echo "Priority: 1"
  echo "CallerID: \"Ava Bot\" <+19544668818>"
  echo "Timeout: 30000"
  echo "Async: true"
  echo ""
  sleep 2
  
  echo "Action: Logoff"
  echo ""
} | nc $HOST $PORT

echo ""
echo "Test call using direct SIP URI format"
