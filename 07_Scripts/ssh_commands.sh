#!/bin/bash
echo "=== SYSTEM INFO ==="
hostname
uptime

echo -e "\n=== ASTERISK STATUS ==="
asterisk -rx "core show version"
asterisk -rx "sip show peers" | head -20

echo -e "\n=== PHONE EXTENSIONS ==="
mysql -u cron -p1234 asterisk -e "SELECT extension, login, pass, status, active, server_ip FROM phones WHERE extension LIKE '753%' ORDER BY extension;"

echo -e "\n=== CAMPAIGNS ==="
mysql -u cron -p1234 asterisk -e "SELECT campaign_id, campaign_name, active, dial_method, auto_dial_level FROM vicidial_campaigns WHERE campaign_id='FUNDX';"

echo -e "\n=== CARRIERS ==="
mysql -u cron -p1234 asterisk -e "SELECT carrier_id, carrier_name, active, registration_string FROM vicidial_server_carriers LIMIT 5;"

echo -e "\n=== CAMPAIGN CARRIERS ==="
mysql -u cron -p1234 asterisk -e "SELECT * FROM vicidial_campaign_server_carriers WHERE campaign_id='FUNDX';"

echo -e "\n=== LEAD LISTS ==="
mysql -u cron -p1234 asterisk -e "SELECT list_id, list_name, campaign_id, active FROM vicidial_lists WHERE list_id IN ('1001','1002');"

echo -e "\n=== LEAD COUNTS ==="
mysql -u cron -p1234 asterisk -e "SELECT list_id, status, COUNT(*) as count FROM vicidial_list WHERE list_id IN ('1001','1002') GROUP BY list_id, status;"

echo -e "\n=== DIAGNOSTICS COMPLETE ==="
