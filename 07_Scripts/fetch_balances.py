#!/usr/bin/env python3
"""
Fetch exact ETH balances for all wallets from hitttssss.csv
Usage: python3 fetch_balances.py
"""

import requests
import csv
import time
from urllib.parse import urlencode

# Read wallets from CSV
wallets = []
with open('/home/user/Documents/AnyDesk/hitttssss.csv', 'r') as f:
    for line in f:
        wallet = line.strip()
        if wallet.startswith('0x') and len(wallet) == 42:
            wallets.append(wallet)

print(f"Loaded {len(wallets)} wallets")
print("\n" + "="*100)
print("ETHEREUM WALLET ETH BALANCE FETCHER")
print("="*100 + "\n")

# Instructions
print("This script fetches exact ETH balances for all wallets.")
print("\nREQUIREMENT: Free Etherscan API key (get it at https://etherscan.io/apis)\n")

# Prompt for API key
api_key = input("Enter your Etherscan API key (or press Enter to use demo mode): ").strip()

if not api_key:
    print("\n⚠️  Demo mode: Showing 5 sample wallets only")
    print("For full dataset, get free key from: https://etherscan.io/apis\n")
    wallets = wallets[:5]  # Demo with first 5

# Fetch balances
print(f"Fetching balances for {len(wallets)} wallets...\n")

results = []
failed = []

for idx, wallet in enumerate(wallets, 1):
    try:
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "balance",
            "address": wallet,
            "tag": "latest",
            "apikey": api_key if api_key else "YourApiKeyToken"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == '1':
            balance_wei = int(data['result'])
            balance_eth = balance_wei / 1e18
            results.append({
                'wallet': wallet,
                'eth_balance': balance_eth,
                'wei_balance': balance_wei
            })
            status = "✓"
        else:
            failed.append(wallet)
            status = "✗"
        
        print(f"{status} [{idx}/{len(wallets)}] {wallet}")
        
        # Rate limiting
        if api_key:
            time.sleep(0.2)
        else:
            break  # Demo mode
            
    except Exception as e:
        failed.append(wallet)
        print(f"✗ [{idx}/{len(wallets)}] {wallet} - Error: {str(e)[:50]}")

# Save results
print(f"\n{'='*100}")
print(f"RESULTS: {len(results)} successful, {len(failed)} failed\n")

# Write to CSV
output_file = '/home/user/eth_balances.csv'
with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['wallet', 'eth_balance', 'wei_balance'])
    writer.writeheader()
    writer.writerows(sorted(results, key=lambda x: x['eth_balance'], reverse=True))

print(f"✓ Saved to: {output_file}")

# Summary statistics
if results:
    balances = [r['eth_balance'] for r in results]
    total = sum(balances)
    avg = total / len(balances)
    
    print(f"\nSTATISTICS:")
    print(f"  Total ETH: {total:.18f}")
    print(f"  Average per wallet: {avg:.18f}")
    print(f"  Max balance: {max(balances):.18f}")
    print(f"  Min balance: {min(balances):.18f}")
    print(f"  Non-zero wallets: {len([b for b in balances if b > 0])}")

