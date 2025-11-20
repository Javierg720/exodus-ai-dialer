#!/usr/bin/env python3
"""
Lead Filtering Tool - Filter leads by date, time, duration, attempts, status
"""

import sqlite3
import argparse
from datetime import datetime, timedelta
from tabulate import tabulate

DB_PATH = "dialer.db"

def filter_leads(
    campaign_id=None,
    status=None,
    min_attempts=None,
    max_attempts=None,
    start_date=None,
    end_date=None,
    min_duration=None,
    max_duration=None,
    limit=100
):
    """Filter leads based on various criteria"""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query
    query = """
    SELECT 
        l.id,
        l.phone_number,
        l.first_name,
        l.last_name,
        l.company,
        l.status,
        l.attempts,
        l.last_call_time,
        l.created_at,
        c.name as campaign_name,
        (SELECT COUNT(*) FROM call_log WHERE lead_id = l.id) as total_calls,
        (SELECT SUM(duration_seconds) FROM call_log WHERE lead_id = l.id) as total_duration,
        (SELECT MAX(start_time) FROM call_log WHERE lead_id = l.id) as last_actual_call
    FROM leads l
    LEFT JOIN campaigns c ON l.campaign_id = c.id
    WHERE 1=1
    """
    
    params = []
    
    # Add filters
    if campaign_id:
        query += " AND l.campaign_id = ?"
        params.append(campaign_id)
    
    if status:
        query += " AND l.status = ?"
        params.append(status.upper())
    
    if min_attempts is not None:
        query += " AND l.attempts >= ?"
        params.append(min_attempts)
    
    if max_attempts is not None:
        query += " AND l.attempts <= ?"
        params.append(max_attempts)
    
    if start_date:
        query += " AND l.last_call_time >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND l.last_call_time <= ?"
        params.append(end_date)
    
    # Add having clause for duration filter (since it's calculated)
    having_clauses = []
    if min_duration is not None:
        having_clauses.append(f"total_duration >= {min_duration}")
    
    if max_duration is not None:
        having_clauses.append(f"total_duration <= {max_duration}")
    
    if having_clauses:
        query += " GROUP BY l.id HAVING " + " AND ".join(having_clauses)
    
    query += f" ORDER BY l.updated_at DESC LIMIT {limit}"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return results


def format_duration(seconds):
    """Format seconds into readable duration"""
    if seconds is None:
        return "N/A"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def display_results(results):
    """Display filtered results in a nice table"""
    
    if not results:
        print("\n❌ No leads found matching the filters.\n")
        return
    
    # Prepare table data
    table_data = []
    for row in results:
        table_data.append([
            row['id'],
            row['phone_number'],
            row['first_name'] or '',
            row['last_name'] or '',
            row['company'] or '',
            row['status'],
            row['attempts'],
            row['total_calls'] or 0,
            format_duration(row['total_duration']),
            row['last_actual_call'] or row['last_call_time'] or 'Never',
            row['campaign_name']
        ])
    
    headers = [
        'ID', 'Phone', 'First', 'Last', 'Company', 
        'Status', 'Attempts', 'Calls', 'Duration', 'Last Call', 'Campaign'
    ]
    
    print("\n" + "="*150)
    print(f"📊 FILTERED LEADS - {len(results)} results")
    print("="*150)
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    print()


def export_to_csv(results, filename):
    """Export filtered results to CSV"""
    import csv
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Phone', 'First Name', 'Last Name', 'Company',
            'Status', 'Attempts', 'Total Calls', 'Total Duration (seconds)',
            'Last Call Time', 'Campaign', 'Created At'
        ])
        
        for row in results:
            writer.writerow([
                row['id'],
                row['phone_number'],
                row['first_name'] or '',
                row['last_name'] or '',
                row['company'] or '',
                row['status'],
                row['attempts'],
                row['total_calls'] or 0,
                row['total_duration'] or 0,
                row['last_actual_call'] or row['last_call_time'] or '',
                row['campaign_name'],
                row['created_at']
            ])
    
    print(f"✅ Exported {len(results)} leads to {filename}\n")


def get_stats(campaign_id=None):
    """Get summary statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        status,
        COUNT(*) as count,
        AVG(attempts) as avg_attempts,
        SUM((SELECT SUM(duration_seconds) FROM call_log WHERE lead_id = leads.id)) as total_duration
    FROM leads
    """
    
    if campaign_id:
        query += f" WHERE campaign_id = {campaign_id}"
    
    query += " GROUP BY status"
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    print("\n" + "="*80)
    print("📈 LEAD STATISTICS")
    print("="*80)
    
    table_data = []
    for row in results:
        status, count, avg_attempts, total_dur = row
        table_data.append([
            status,
            count,
            f"{avg_attempts:.1f}" if avg_attempts else "0.0",
            format_duration(int(total_dur)) if total_dur else "N/A"
        ])
    
    print(tabulate(table_data, headers=['Status', 'Count', 'Avg Attempts', 'Total Duration'], tablefmt='grid'))
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Filter and export leads based on various criteria',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show all NEW leads
  python filter_leads.py --status NEW

  # Show leads with 2+ attempts
  python filter_leads.py --min-attempts 2

  # Show COMPLETED leads from today
  python filter_leads.py --status COMPLETED --start-date today

  # Show leads called in last 7 days with 30+ seconds duration
  python filter_leads.py --start-date 7days --min-duration 30

  # Export all ANSWERED leads to CSV
  python filter_leads.py --status ANSWERED --export leads.csv

  # Show statistics for campaign 47
  python filter_leads.py --campaign 47 --stats
        """
    )
    
    parser.add_argument('--campaign', type=int, help='Filter by campaign ID')
    parser.add_argument('--status', choices=['NEW', 'CALLING', 'ANSWERED', 'NO_ANSWER', 'BUSY', 'FAILED', 'COMPLETED'],
                       help='Filter by lead status')
    parser.add_argument('--min-attempts', type=int, help='Minimum number of attempts')
    parser.add_argument('--max-attempts', type=int, help='Maximum number of attempts')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD, "today", "7days", etc.)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--min-duration', type=int, help='Minimum call duration in seconds')
    parser.add_argument('--max-duration', type=int, help='Maximum call duration in seconds')
    parser.add_argument('--limit', type=int, default=100, help='Maximum results to show (default: 100)')
    parser.add_argument('--export', help='Export results to CSV file')
    parser.add_argument('--stats', action='store_true', help='Show statistics instead of individual leads')
    
    args = parser.parse_args()
    
    # Parse date shortcuts
    start_date = None
    if args.start_date:
        if args.start_date == 'today':
            start_date = datetime.now().strftime('%Y-%m-%d 00:00:00')
        elif args.start_date.endswith('days'):
            days = int(args.start_date.replace('days', ''))
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d 00:00:00')
        else:
            start_date = args.start_date
    
    end_date = args.end_date
    
    if args.stats:
        get_stats(args.campaign)
    else:
        results = filter_leads(
            campaign_id=args.campaign,
            status=args.status,
            min_attempts=args.min_attempts,
            max_attempts=args.max_attempts,
            start_date=start_date,
            end_date=end_date,
            min_duration=args.min_duration,
            max_duration=args.max_duration,
            limit=args.limit
        )
        
        display_results(results)
        
        if args.export:
            export_to_csv(results, args.export)


if __name__ == '__main__':
    main()
