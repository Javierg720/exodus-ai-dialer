#!/usr/bin/env python3
"""
Subdomain Scanner for Unidial instances on getcelerity.com
Scans for active unidialXXXX.getcelerity.com subdomains
"""

import requests
import concurrent.futures
from typing import List, Tuple
import sys

# Disable SSL warnings for self-signed certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_subdomain(subdomain_num: int) -> Tuple[int, bool, str]:
    """
    Check if a subdomain is active
    
    Args:
        subdomain_num: The subdomain number to check
        
    Returns:
        Tuple of (subdomain_num, is_active, status_info)
    """
    url = f"http://unidial{subdomain_num}.getcelerity.com/unidial/admin.php"
    
    try:
        response = requests.get(url, timeout=5, allow_redirects=True, verify=False)
        if response.status_code == 200:
            return (subdomain_num, True, f"Status 200 - Active")
        elif response.status_code in [301, 302, 303, 307, 308]:
            return (subdomain_num, True, f"Status {response.status_code} - Redirect to {response.headers.get('Location', 'unknown')}")
        elif response.status_code == 404:
            return (subdomain_num, False, f"Status 404 - Not Found")
        elif response.status_code == 403:
            return (subdomain_num, True, f"Status 403 - Forbidden (Server exists)")
        else:
            return (subdomain_num, True, f"Status {response.status_code} - Server responds")
    except requests.exceptions.Timeout:
        return (subdomain_num, False, "Timeout")
    except requests.exceptions.ConnectionError:
        return (subdomain_num, False, "Connection Error")
    except Exception as e:
        return (subdomain_num, False, f"Error: {str(e)}")

def scan_range(start: int, end: int, max_workers: int = 20) -> List[Tuple[int, bool, str]]:
    """
    Scan a range of subdomains concurrently
    
    Args:
        start: Starting subdomain number
        end: Ending subdomain number
        max_workers: Maximum concurrent workers
        
    Returns:
        List of results
    """
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_subdomain, num): num for num in range(start, end + 1)}
        
        completed = 0
        total = end - start + 1
        
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            result = future.result()
            results.append(result)
            
            # Print progress
            if completed % 10 == 0 or result[1]:  # Every 10 or when active found
                print(f"Progress: {completed}/{total} - Last checked: unidial{result[0]}", end='\r')
                if result[1]:
                    print(f"\n[ACTIVE] unidial{result[0]}.getcelerity.com - {result[2]}")
    
    print()  # New line after progress
    return results

def main():
    print("=" * 70)
    print("Unidial Subdomain Scanner for getcelerity.com")
    print("=" * 70)
    print()
    
    # Default range - adjust as needed
    start_range = 1800
    end_range = 1900
    
    if len(sys.argv) > 1:
        start_range = int(sys.argv[1])
    if len(sys.argv) > 2:
        end_range = int(sys.argv[2])
    
    print(f"Scanning range: unidial{start_range} to unidial{end_range}")
    print(f"Total subdomains to check: {end_range - start_range + 1}")
    print()
    
    results = scan_range(start_range, end_range)
    
    # Filter active subdomains
    active_subdomains = [(num, status) for num, is_active, status in results if is_active]
    
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
        for num, status in sorted(active_subdomains):
            print(f"  unidial{num}.getcelerity.com - {status}")
            print(f"    URL: http://unidial{num}.getcelerity.com/unidial/admin.php")
        print()
    else:
        print("No active subdomains found in this range.")
    
    # Save results to file
    output_file = f"subdomain_scan_results_{start_range}-{end_range}.txt"
    with open(output_file, 'w') as f:
        f.write(f"Unidial Subdomain Scan Results\n")
        f.write(f"Range: unidial{start_range} to unidial{end_range}\n")
        f.write(f"Scan Date: {requests.utils.default_headers()}\n")
        f.write(f"\nTotal Scanned: {len(results)}\n")
        f.write(f"Active Found: {len(active_subdomains)}\n\n")
        f.write("=" * 70 + "\n")
        f.write("ACTIVE SUBDOMAINS:\n")
        f.write("=" * 70 + "\n\n")
        
        for num, status in sorted(active_subdomains):
            f.write(f"unidial{num}.getcelerity.com\n")
            f.write(f"  Status: {status}\n")
            f.write(f"  Admin URL: http://unidial{num}.getcelerity.com/unidial/admin.php\n\n")
    
    print(f"Results saved to: {output_file}")

if __name__ == "__main__":
    main()
