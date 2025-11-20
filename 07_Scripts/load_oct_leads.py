#!/usr/bin/env python3
import csv
import pymysql
import sys
from datetime import datetime

# VICIdial database connection
db_config = {
    'host': '46.62.216.79',
    'user': 'root',
    'password': '3L5v3XzKXC724bM8au8R',
    'database': 'asterisk',
    'charset': 'utf8mb4'
}

# List configuration
list_id = 31025
list_name = "CAMP 3 - OCT LEADS"

# CSV files to import
csv_files = [
    '/home/user/Desktop/LEADS\/OCT/1 LMG 3k 10.17.25 (2) (1).csv',
    '/home/user/Desktop/LEADS\/OCT/2 LMG 2k 10.17.25.csv',
    '/home/user/Desktop/LEADS\/OCT/LMG 2.5k 9.18.25.csv',
    '/home/user/Desktop/LEADS\/OCT/LMG 3k 09.30.25.csv'
]

def load_csv_to_vicidial(csv_file):
    """Load a CSV file into VICIdial vicidial_list table"""
    
    print(f"\n{'='*70}")
    print(f"Processing: {csv_file.split('/')[-1]}")
    print(f"{'='*70}")
    
    try:
        # Connect to database
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # Read CSV file
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            leads_inserted = 0
            leads_skipped = 0
            
            for row in reader:
                # Extract fields from CSV
                phone_number = row.get('phone1', '').strip()
                first_name = row.get('firstname', '').strip()
                last_name = row.get('lastname', '').strip()
                company = row.get('company', '').strip()
                email = row.get('email', '').strip()
                address1 = row.get('address1', '').strip()
                city = row.get('city', '').strip()
                state = row.get('state', '').strip()
                postal_code = row.get('zip', '').strip()
                vendor_lead_code = row.get('Data source', '').strip()
                
                # Skip if no phone number
                if not phone_number or len(phone_number) < 10:
                    leads_skipped += 1
                    continue
                
                # Clean phone number (remove non-digits)
                phone_clean = ''.join(filter(str.isdigit, phone_number))
                
                # Skip if phone already exists in this list
                cursor.execute(
                    "SELECT lead_id FROM vicidial_list WHERE phone_number = %s AND list_id = %s",
                    (phone_clean, list_id)
                )
                if cursor.fetchone():
                    leads_skipped += 1
                    continue
                
                # Insert lead
                insert_query = """
                    INSERT INTO vicidial_list (
                        phone_code, phone_number, list_id, status,
                        first_name, last_name, company, email,
                        address1, city, state, postal_code,
                        vendor_lead_code, entry_date, modify_date,
                        user, gmt_offset_now, called_since_last_reset,
                        called_count, rank, owner
                    ) VALUES (
                        '1', %s, %s, 'NEW',
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, NOW(), NOW(),
                        'VDAD', '-5.00', 'N',
                        0, 0, ''
                    )
                """
                
                cursor.execute(insert_query, (
                    phone_clean, list_id,
                    first_name, last_name, company, email,
                    address1, city, state, postal_code,
                    vendor_lead_code
                ))
                
                leads_inserted += 1
                
                # Commit every 100 leads
                if leads_inserted % 100 == 0:
                    conn.commit()
                    print(f"  Inserted: {leads_inserted} leads...", end='\r')
        
        # Final commit
        conn.commit()
        
        print(f"\n✓ Inserted: {leads_inserted} leads")
        print(f"  Skipped: {leads_skipped} leads (duplicates or invalid)")
        
        cursor.close()
        conn.close()
        
        return leads_inserted, leads_skipped
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 0, 0

def main():
    print("\n" + "="*70)
    print("VICIdial Lead Loader - OCT LEADS to CAMP3")
    print("="*70)
    print(f"Target List: {list_id} ({list_name})")
    print(f"Files to import: {len(csv_files)}")
    
    total_inserted = 0
    total_skipped = 0
    
    # Import each CSV file
    for csv_file in csv_files:
        inserted, skipped = load_csv_to_vicidial(csv_file)
        total_inserted += inserted
        total_skipped += skipped
    
    # Final summary
    print("\n" + "="*70)
    print("IMPORT COMPLETE")
    print("="*70)
    print(f"Total Inserted: {total_inserted}")
    print(f"Total Skipped: {total_skipped}")
    print(f"Total Processed: {total_inserted + total_skipped}")
    
    # Verify in database
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM vicidial_list WHERE list_id = %s", (list_id,))
        total_in_list = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vicidial_list WHERE list_id = %s AND status = 'NEW'", (list_id,))
        new_leads = cursor.fetchone()[0]
        
        print(f"\nDatabase Verification:")
        print(f"  Total leads in list {list_id}: {total_in_list}")
        print(f"  New (dialable) leads: {new_leads}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Verification error: {e}")

if __name__ == "__main__":
    main()
