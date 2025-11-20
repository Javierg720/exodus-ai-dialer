#!/bin/bash
# Start 20 Pipecat bots (ports 9092-9111) with AudioSocket

cd /home/user/Desktop/Projects_Organized/01_Exodus_Dialer/exodus-kali-deploy

for port in {9092..9111}; do
    echo "Starting bot on port $port..."
    nohup python3 ava_sales_bot_audiosocket.py --port $port --host 0.0.0.0 > bot_${port}.log 2>&1 &
    sleep 0.5
done

echo "✅ Started 20 bots on ports 9092-9111"
ps aux | grep ava_sales_bot | grep -v grep | wc -l
