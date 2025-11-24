#!/usr/bin/env python3
"""
Subdomain Scanner for warmconnect.com
Scans for active subdomains on warmconnect.com
"""

import requests
import concurrent.futures
from typing import List, Tuple
import sys

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_subdomain(subdomain: str) -> Tuple[str, bool, str, str]:
    """
    Check if a subdomain is active
    
    Args:
        subdomain: The subdomain to check (e.g., "www", "onelove.cc")
        
    Returns:
        Tuple of (subdomain, is_active, status_info, url)
    """
    # Try both http and https
    for protocol in ['https', 'http']:
        url = f"{protocol}://{subdomain}.warmconnect.com/wiz.php"
        
        try:
            response = requests.get(url, timeout=5, allow_redirects=True, verify=False)
            if response.status_code == 200:
                return (subdomain, True, f"{protocol.upper()} 200 - Active ({len(response.content)} bytes)", url)
            elif response.status_code in [301, 302, 303, 307, 308]:
                return (subdomain, True, f"{protocol.upper()} {response.status_code} - Redirect", url)
            elif response.status_code == 403:
                return (subdomain, True, f"{protocol.upper()} 403 - Forbidden (Server exists)", url)
            elif response.status_code == 401:
                return (subdomain, True, f"{protocol.upper()} 401 - Auth Required (Server exists)", url)
        except requests.exceptions.SSLError:
            continue  # Try next protocol
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.ConnectionError:
            continue
        except Exception:
            continue
    
    return (subdomain, False, "Not accessible", "")

def scan_subdomains(subdomain_list: List[str], max_workers: int = 20) -> List[Tuple[str, bool, str, str]]:
    """Scan a list of subdomains concurrently"""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_subdomain, name): name for name in subdomain_list}
        
        completed = 0
        total = len(subdomain_list)
        
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            result = future.result()
            results.append(result)
            
            # Print progress
            if completed % 10 == 0 or result[1]:
                print(f"Progress: {completed}/{total} - Last checked: {result[0]}", end='\r')
                if result[1]:
                    print(f"\n[ACTIVE] {result[0]}.warmconnect.com - {result[2]}")
    
    print()
    return results

def generate_subdomain_patterns(mode: str = "common") -> List[str]:
    """Generate subdomain patterns to check"""
    
    if mode == "common":
        return [
            'www', 'onelove.cc', 'twolove.cc', 'threelove.cc', 'fourlove.cc', 'fivelove.cc',
            'ava', 'bot', 'dialer', 'vicidial', 'vici', 'asterisk',
            'pbx', 'voip', 'sip', 'admin', 'web', 'portal', 'dashboard',
            'prod', 'production', 'staging', 'dev', 'test',
            'server1', 'server2', 'server3', 'node1', 'node2',
            'cc', 'client', 'customer', 'demo', 'support'
        ]
    
    elif mode == "love":
        # Pattern: onelove.cc, twolove.cc, etc.
        numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                   'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen',
                   'eighteen', 'nineteen', 'twenty']
        return [f"{num}love.cc" for num in numbers]
    
    elif mode == "numeric-cc":
        # Pattern: 1.cc, 2.cc, ... 100.cc
        return [f"{i}.cc" for i in range(1, 101)]
    
    elif mode == "numeric":
        # Pattern: server1, server2, etc.
        patterns = []
        for prefix in ['server', 'node', 'host', 'vici', 'dialer', 'pbx']:
            for i in range(1, 51):
                patterns.append(f"{prefix}{i}")
        return patterns
    
    else:
        return generate_subdomain_patterns("common")

def main():
    print("=" * 70)
    print("Warmconnect.com Subdomain Scanner")
    print("=" * 70)
    print()
    
    mode = "common"
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    
    print(f"Scan mode: {mode}")
    subdomain_list = generate_subdomain_patterns(mode)
    
    print(f"Total subdomains to check: {len(subdomain_list)}")
    print()
    
    results = scan_subdomains(subdomain_list)
    
    # Filter active subdomains
    active_subdomains = [(name, status, url) for name, is_active, status, url in results if is_active]
    
    print()
    print("=" * 70)
    print("SCAN COMPLETE")
    print("=" * 70)
    print()
    print(f"Total scanned: {len(results)}")
    print(f"Active subdomains found: {len(active_subdomains)}")
    print()
    
    if active_subdomains:
        print("Active Subdomains:")
        print("-" * 70)
        for name, status, url in sorted(active_subdomains):
            print(f"  {name}.warmconnect.com")
            print(f"    Status: {status}")
            print(f"    URL: {url}")
            print()
    else:
        print("No active subdomains found.")
    
    # Save results
    output_file = f"warmconnect_scan_{mode}_results.txt"
    with open(output_file, 'w') as f:
        f.write(f"Warmconnect.com Subdomain Scan Results\n")
        f.write(f"Mode: {mode}\n")
        f.write(f"Total Scanned: {len(results)}\n")
        f.write(f"Active Found: {len(active_subdomains)}\n\n")
        f.write("=" * 70 + "\n")
        f.write("ACTIVE SUBDOMAINS:\n")
        f.write("=" * 70 + "\n\n")
        
        for name, status, url in sorted(active_subdomains):
            f.write(f"{name}.warmconnect.com\n")
            f.write(f"  Status: {status}\n")
            f.write(f"  URL: {url}\n\n")
    
    print(f"Results saved to: {output_file}")
    print()
    print("Available modes:")
    print("  common     - Common subdomain names")
    print("  love       - *love.cc patterns (onelove.cc, twolove.cc, etc.)")
    print("  numeric-cc - Numeric .cc subdomains (1.cc, 2.cc, ... 100.cc)")
    print("  numeric    - Numbered servers (server1-50, node1-50, etc.)")

if __name__ == "__main__":
    main()
