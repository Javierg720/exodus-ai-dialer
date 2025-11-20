#!/usr/bin/env python3
"""
Call History Viewer - View, filter, and export call history with recordings and transcriptions
"""

import sqlite3
import argparse
from datetime import datetime, timedelta
from tabulate import tabulate
import json
import re

DB_PATH = "dialer.db"

def filter_calls(
    campaign_id=None,
    status=None,
    start_date=None,
    end_date=None,
    min_duration=None,
    max_duration=None,
    min_talk_time=None,
    max_talk_time=None,
    phone_number=None,
    has_recording=None,
    has_transcription=None,
    was_dropped=None,
    limit=100
):
    """Filter call history based on various criteria"""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query
    query = """
    SELECT 
        cl.id,
        cl.call_uuid,
        cl.start_time,
        cl.answer_time,
        cl.end_time,
        cl.duration_seconds,
        cl.talk_time_seconds,
        cl.call_status,
        cl.disposition_code,
        cl.was_dropped,
        cl.bot_port,
        cl.recording_url,
        cl.transcription_text,
        cl.notes,
        l.phone_number,
        l.first_name,
        l.last_name,
        l.company,
        c.name as campaign_name
    FROM call_log cl
    LEFT JOIN leads l ON cl.lead_id = l.id
    LEFT JOIN campaigns c ON cl.campaign_id = c.id
    WHERE 1=1
    """
    
    params = []
    
    # Add filters
    if campaign_id:
        query += " AND cl.campaign_id = ?"
        params.append(campaign_id)
    
    if status:
        query += " AND cl.call_status = ?"
        params.append(status.upper())
    
    if start_date:
        query += " AND cl.start_time >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND cl.start_time <= ?"
        params.append(end_date)
    
    if min_duration is not None:
        query += " AND cl.duration_seconds >= ?"
        params.append(min_duration)
    
    if max_duration is not None:
        query += " AND cl.duration_seconds <= ?"
        params.append(max_duration)
    
    if min_talk_time is not None:
        query += " AND cl.talk_time_seconds >= ?"
        params.append(min_talk_time)
    
    if max_talk_time is not None:
        query += " AND cl.talk_time_seconds <= ?"
        params.append(max_talk_time)
    
    if phone_number:
        query += " AND l.phone_number LIKE ?"
        params.append(f"%{phone_number}%")
    
    if has_recording is not None:
        if has_recording:
            query += " AND cl.recording_url IS NOT NULL AND cl.recording_url != ''"
        else:
            query += " AND (cl.recording_url IS NULL OR cl.recording_url = '')"
    
    if has_transcription is not None:
        if has_transcription:
            query += " AND cl.transcription_text IS NOT NULL AND cl.transcription_text != ''"
        else:
            query += " AND (cl.transcription_text IS NULL OR cl.transcription_text = '')"
    
    if was_dropped is not None:
        query += " AND cl.was_dropped = ?"
        params.append(1 if was_dropped else 0)
    
    query += f" ORDER BY cl.start_time DESC LIMIT {limit}"
    
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


def generate_summary(transcription):
    """Generate a simple summary from transcription"""
    if not transcription:
        return "No transcription available"
    
    # Simple keyword extraction for summary
    lines = transcription.split('\n')
    agent_lines = [l for l in lines if l.startswith('Agent:')]
    user_lines = [l for l in lines if l.startswith('User:')]
    
    summary = f"Call with {len(agent_lines)} agent messages and {len(user_lines)} user responses. "
    
    # Check for common outcomes
    text_lower = transcription.lower()
    if 'not interested' in text_lower:
        summary += "Outcome: Not interested."
    elif 'callback' in text_lower or 'call back' in text_lower:
        summary += "Outcome: Callback requested."
    elif 'interested' in text_lower:
        summary += "Outcome: Expressed interest."
    elif len(user_lines) == 0:
        summary += "Outcome: No user response."
    else:
        summary += "Outcome: Conversation occurred."
    
    return summary


def display_results(results, show_details=False):
    """Display filtered call results"""
    
    if not results:
        print("\n❌ No calls found matching the filters.\n")
        return
    
    # Prepare table data
    table_data = []
    for row in results:
        # Basic info
        has_rec = "✓" if row['recording_url'] else "✗"
        has_trans = "✓" if row['transcription_text'] else "✗"
        dropped = "⚠" if row['was_dropped'] else ""
        
        table_data.append([
            row['id'],
            row['start_time'][:16] if row['start_time'] else 'N/A',
            row['phone_number'],
            (row['first_name'] or '') + ' ' + (row['last_name'] or ''),
            row['company'] or '',
            row['call_status'],
            format_duration(row['duration_seconds']),
            format_duration(row['talk_time_seconds']),
            f"Bot {row['bot_port']}" if row['bot_port'] else 'N/A',
            has_rec,
            has_trans,
            dropped,
            row['campaign_name']
        ])
    
    headers = [
        'ID', 'Date/Time', 'Phone', 'Name', 'Company',
        'Status', 'Duration', 'Talk Time', 'Bot', 'Rec', 'Trans', '⚠', 'Campaign'
    ]
    
    print("\n" + "="*180)
    print(f"📞 CALL HISTORY - {len(results)} results")
    print("="*180)
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    print()
    print("Legend: Rec=Recording, Trans=Transcription, ⚠=Dropped Call")
    print()


def show_call_details(call_id):
    """Show detailed information for a specific call"""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            cl.*,
            l.phone_number,
            l.first_name,
            l.last_name,
            l.company,
            c.name as campaign_name
        FROM call_log cl
        LEFT JOIN leads l ON cl.lead_id = l.id
        LEFT JOIN campaigns c ON cl.campaign_id = c.id
        WHERE cl.id = ?
    """, (call_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print(f"\n❌ Call ID {call_id} not found.\n")
        return
    
    print("\n" + "="*100)
    print(f"📞 CALL DETAILS - ID: {call_id}")
    print("="*100)
    print()
    
    # Basic Info
    print("BASIC INFORMATION:")
    print("-" * 100)
    print(f"  Call UUID:        {row['call_uuid']}")
    print(f"  Campaign:         {row['campaign_name']}")
    print(f"  Phone Number:     {row['phone_number']}")
    print(f"  Contact:          {(row['first_name'] or '')} {(row['last_name'] or '')}")
    print(f"  Company:          {row['company'] or 'N/A'}")
    print(f"  Bot Port:         {row['bot_port'] or 'N/A'}")
    print()
    
    # Timing
    print("TIMING:")
    print("-" * 100)
    print(f"  Start Time:       {row['start_time']}")
    print(f"  Answer Time:      {row['answer_time'] or 'Not answered'}")
    print(f"  End Time:         {row['end_time'] or 'N/A'}")
    print(f"  Duration:         {format_duration(row['duration_seconds'])}")
    print(f"  Talk Time:        {format_duration(row['talk_time_seconds'])}")
    print()
    
    # Outcome
    print("OUTCOME:")
    print("-" * 100)
    print(f"  Status:           {row['call_status']}")
    print(f"  Disposition:      {row['disposition_code'] or 'N/A'}")
    print(f"  Dropped Call:     {'YES ⚠' if row['was_dropped'] else 'No'}")
    print(f"  Connection Delay: {row['connection_delay_ms']}ms" if row['connection_delay_ms'] else "  Connection Delay: N/A")
    print()
    
    # Recording
    if row['recording_url']:
        print("RECORDING:")
        print("-" * 100)
        print(f"  URL: {row['recording_url']}")
        print()
    
    # Transcription
    if row['transcription_text']:
        print("TRANSCRIPTION:")
        print("-" * 100)
        # Format and display transcription
        trans = row['transcription_text']
        for line in trans.split('\n'):
            if line.strip():
                print(f"  {line}")
        print()
        
        # Generate summary
        print("AI SUMMARY:")
        print("-" * 100)
        print(f"  {generate_summary(trans)}")
        print()
    
    # Notes
    if row['notes']:
        print("NOTES:")
        print("-" * 100)
        print(f"  {row['notes']}")
        print()
    
    print("="*100)
    print()


def export_to_csv(results, filename, include_transcriptions=False):
    """Export call history to CSV"""
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fields = [
            'ID', 'Call UUID', 'Start Time', 'Answer Time', 'End Time',
            'Duration (sec)', 'Talk Time (sec)', 'Status', 'Disposition',
            'Was Dropped', 'Bot Port', 'Phone Number', 'First Name', 
            'Last Name', 'Company', 'Campaign', 'Recording URL', 'Notes'
        ]
        
        if include_transcriptions:
            fields.append('Transcription')
            fields.append('Summary')
        
        writer = csv.writer(f)
        writer.writerow(fields)
        
        for row in results:
            data = [
                row['id'],
                row['call_uuid'],
                row['start_time'],
                row['answer_time'] or '',
                row['end_time'] or '',
                row['duration_seconds'] or 0,
                row['talk_time_seconds'] or 0,
                row['call_status'],
                row['disposition_code'] or '',
                'Yes' if row['was_dropped'] else 'No',
                row['bot_port'] or '',
                row['phone_number'],
                row['first_name'] or '',
                row['last_name'] or '',
                row['company'] or '',
                row['campaign_name'],
                row['recording_url'] or '',
                row['notes'] or ''
            ]
            
            if include_transcriptions:
                data.append(row['transcription_text'] or '')
                data.append(generate_summary(row['transcription_text']) if row['transcription_text'] else '')
            
            writer.writerow(data)
    
    print(f"✅ Exported {len(results)} calls to {filename}")
    if include_transcriptions:
        print("   (including transcriptions and summaries)")
    print()


def get_stats(campaign_id=None):
    """Get call statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    where_clause = f"WHERE campaign_id = {campaign_id}" if campaign_id else ""
    
    # Overall stats
    cursor.execute(f"""
        SELECT 
            call_status,
            COUNT(*) as count,
            AVG(duration_seconds) as avg_duration,
            AVG(talk_time_seconds) as avg_talk_time,
            SUM(was_dropped) as dropped_count
        FROM call_log
        {where_clause}
        GROUP BY call_status
    """)
    
    results = cursor.fetchall()
    
    # Total stats
    cursor.execute(f"""
        SELECT 
            COUNT(*) as total_calls,
            SUM(duration_seconds) as total_duration,
            AVG(duration_seconds) as avg_duration,
            COUNT(CASE WHEN transcription_text IS NOT NULL THEN 1 END) as with_transcription,
            COUNT(CASE WHEN recording_url IS NOT NULL THEN 1 END) as with_recording,
            SUM(was_dropped) as total_dropped
        FROM call_log
        {where_clause}
    """)
    
    totals = cursor.fetchone()
    conn.close()
    
    print("\n" + "="*100)
    print("📊 CALL STATISTICS")
    print("="*100)
    print()
    
    # Overall numbers
    print("OVERALL:")
    print("-" * 100)
    print(f"  Total Calls:          {totals[0]}")
    print(f"  Total Duration:       {format_duration(int(totals[1]) if totals[1] else 0)}")
    print(f"  Average Duration:     {format_duration(int(totals[2]) if totals[2] else 0)}")
    print(f"  With Transcription:   {totals[3]} ({totals[3]/totals[0]*100:.1f}%)" if totals[0] > 0 else "  With Transcription:   0")
    print(f"  With Recording:       {totals[4]} ({totals[4]/totals[0]*100:.1f}%)" if totals[0] > 0 else "  With Recording:       0")
    print(f"  Dropped Calls:        {totals[5]} ({totals[5]/totals[0]*100:.1f}%)" if totals[0] > 0 else "  Dropped Calls:        0")
    print()
    
    # By status
    print("BY STATUS:")
    print("-" * 100)
    table_data = []
    for row in results:
        status, count, avg_dur, avg_talk, dropped = row
        table_data.append([
            status,
            count,
            format_duration(int(avg_dur) if avg_dur else 0),
            format_duration(int(avg_talk) if avg_talk else 0),
            dropped or 0
        ])
    
    print(tabulate(table_data, 
                  headers=['Status', 'Count', 'Avg Duration', 'Avg Talk Time', 'Dropped'],
                  tablefmt='grid'))
    print()


def main():
    parser = argparse.ArgumentParser(
        description='View and filter call history with recordings and transcriptions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View call statistics
  python call_history.py --stats

  # Show recent calls
  python call_history.py --limit 20

  # Show calls from today
  python call_history.py --start-date today

  # Show answered calls with transcriptions
  python call_history.py --status ANSWERED --has-transcription

  # Show call details (with transcription and summary)
  python call_history.py --details 237

  # Show long calls (60+ seconds)
  python call_history.py --min-duration 60

  # Export answered calls with transcriptions
  python call_history.py --status ANSWERED --export calls.csv --include-transcriptions

  # Show dropped calls
  python call_history.py --was-dropped

  # Show calls for specific phone number
  python call_history.py --phone 305215
        """
    )
    
    parser.add_argument('--campaign', type=int, help='Filter by campaign ID')
    parser.add_argument('--status', choices=['ANSWERED', 'NO_ANSWER', 'BUSY', 'FAILED', 'ABANDONED'],
                       help='Filter by call status')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD, "today", "7days")')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--min-duration', type=int, help='Minimum call duration in seconds')
    parser.add_argument('--max-duration', type=int, help='Maximum call duration in seconds')
    parser.add_argument('--min-talk-time', type=int, help='Minimum talk time in seconds')
    parser.add_argument('--max-talk-time', type=int, help='Maximum talk time in seconds')
    parser.add_argument('--phone', help='Filter by phone number (partial match)')
    parser.add_argument('--has-recording', action='store_true', help='Only calls with recordings')
    parser.add_argument('--has-transcription', action='store_true', help='Only calls with transcriptions')
    parser.add_argument('--was-dropped', action='store_true', help='Only dropped calls')
    parser.add_argument('--limit', type=int, default=100, help='Maximum results (default: 100)')
    parser.add_argument('--export', help='Export to CSV file')
    parser.add_argument('--include-transcriptions', action='store_true', 
                       help='Include transcriptions in CSV export')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--details', type=int, metavar='CALL_ID',
                       help='Show detailed info for specific call (includes transcription & summary)')
    
    args = parser.parse_args()
    
    # Show call details
    if args.details:
        show_call_details(args.details)
        return
    
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
    
    # Show statistics
    if args.stats:
        get_stats(args.campaign)
        return
    
    # Filter and display calls
    results = filter_calls(
        campaign_id=args.campaign,
        status=args.status,
        start_date=start_date,
        end_date=end_date,
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        min_talk_time=args.min_talk_time,
        max_talk_time=args.max_talk_time,
        phone_number=args.phone,
        has_recording=args.has_recording if args.has_recording else None,
        has_transcription=args.has_transcription if args.has_transcription else None,
        was_dropped=args.was_dropped if args.was_dropped else None,
        limit=args.limit
    )
    
    display_results(results)
    
    if args.export:
        export_to_csv(results, args.export, args.include_transcriptions)


if __name__ == '__main__':
    main()
