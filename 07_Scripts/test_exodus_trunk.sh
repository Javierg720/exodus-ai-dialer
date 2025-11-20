#!/bin/bash
# Test call using new exodus-final-trunk

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
  echo "Channel: PJSIP/+13057768712@exodus-final-trunk"
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
echo "Test call initiated to +13057768712 via exodus-final-trunk"
echo "Answer your phone to test!"
