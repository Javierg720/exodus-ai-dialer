# Dashboard Filters Documentation

## Overview
The Exodus Dialer Dashboard now includes comprehensive filtering capabilities on both the **Leads** and **Call History** pages.

---

## Leads Page Filters

Access: Click the "Filters" button on the Leads page

### Available Filters:

1. **Status Filter**
   - Filter leads by their current status
   - Options: NEW, CALLING, ANSWERED, NO_ANSWER, BUSY, FAILED, COMPLETED
   
2. **Campaign Filter**
   - Filter leads by which campaign they belong to
   - Shows all active campaigns in dropdown

3. **Min/Max Attempts**
   - Filter by number of call attempts made
   - Example: Show only leads with 2+ attempts

4. **Has Email** (checkbox)
   - Show only leads that have an email address

5. **Has Company** (checkbox)
   - Show only leads that have a company name

### Search Bar
- Search by: Phone number, First name, Last name, Company name

### Filter Badge
- Shows count of active filters
- Click "Clear All" to reset

---

## Call History Page Filters

Access: Click the "Filters" button on the Call History page

### Available Filters:

1. **Call Status**
   - Filter by call outcome
   - Options: Answered, Completed, Failed, No Answer, Busy

2. **Disposition**
   - Filter by call disposition code
   - Options: INTERESTED, NOT_INTERESTED, CALLBACK, VOICEMAIL, WRONG_NUMBER, DNC

3. **Campaign Filter**
   - Filter calls by campaign
   - Shows all active campaigns

4. **Date Range**
   - From Date: Start date for call history
   - To Date: End date for call history

5. **Duration Filters**
   - Min Duration: Minimum call length in seconds
   - Max Duration: Maximum call length in seconds
   - Example: Show calls between 30-300 seconds

6. **Has Recording** (checkbox)
   - Show only calls with audio recordings

7. **Has Transcript** (checkbox)
   - Show only calls with AI transcriptions

### Search Bar
- Search by: Phone number, Disposition code

### Filter Badge
- Shows count of active filters
- Click "Clear All" to reset

---

## Usage Tips

### Common Use Cases:

**Find leads that need follow-up:**
- Status: NO_ANSWER
- Min Attempts: 1
- Max Attempts: 2

**Find quality leads:**
- Status: ANSWERED
- Has Email: ✓
- Has Company: ✓

**Analyze successful calls:**
- Call Status: Answered
- Disposition: INTERESTED
- Min Duration: 60

**Find calls needing callback:**
- Disposition: CALLBACK
- Date Range: Last 7 days

**Review transcribed calls:**
- Has Transcript: ✓
- Min Duration: 30

**Check campaign performance:**
- Select specific Campaign
- View statistics with filters applied

---

## Technical Details

### Filter State Management
- Filters use React state with real-time updates
- All filters are ANDed together (must match all criteria)
- Search is combined with filters
- Filters persist during session (reset on page reload)

### Performance
- Client-side filtering (no API calls needed)
- Instant results as you type/change filters
- Handles large datasets efficiently

### Accessibility
- All inputs are keyboard accessible
- Clear visual feedback for active filters
- Collapsible panel to reduce clutter

---

## Dashboard Access

- **URL:** http://localhost:3001
- **Backend API:** http://localhost:8000
- **Pages with Filters:** Leads, Call History

Last Updated: November 19, 2025
