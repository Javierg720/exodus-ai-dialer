-- Migration: Add Duplicate Lead Prevention
-- Description: Adds unique constraint to prevent duplicate leads in same campaign
-- Date: 2025-11-23

-- Step 1: Identify duplicates
-- Find all duplicate phone/campaign combinations
CREATE TEMP TABLE duplicate_leads AS
SELECT campaign_id, phone_number, MIN(id) as keep_id, COUNT(*) as dup_count
FROM leads  
GROUP BY campaign_id, phone_number
HAVING COUNT(*) > 1;

-- Step 2: Report duplicates before deletion
SELECT 
    'Found ' || COUNT(*) || ' sets of duplicates affecting ' || SUM(dup_count - 1) || ' extra leads' as summary
FROM duplicate_leads;

-- Step 3: Delete duplicate leads (keep the oldest one by ID)
DELETE FROM leads
WHERE id IN (
    SELECT l.id
    FROM leads l
    INNER JOIN duplicate_leads d 
        ON l.campaign_id = d.campaign_id 
        AND l.phone_number = d.phone_number
    WHERE l.id > d.keep_id
);

-- Step 4: Create unique index to prevent future duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_campaign_phone_unique 
ON leads(campaign_id, phone_number);

-- Step 5: Verify the index was created
SELECT name, sql 
FROM sqlite_master 
WHERE type='index' AND name='idx_campaign_phone_unique';

-- Step 6: Report final status
SELECT 
    'Unique constraint added. Current lead count: ' || COUNT(*) as status
FROM leads;
