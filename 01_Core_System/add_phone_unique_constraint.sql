-- Add unique constraint to prevent duplicate phone numbers in same campaign
-- This prevents creating leads like +111111111111 multiple times

-- Step 1: Check for existing duplicates
SELECT campaign_id, phone_number, COUNT(*) as count
FROM leads
GROUP BY campaign_id, phone_number
HAVING COUNT(*) > 1;

-- Step 2: If duplicates exist, you need to clean them up first
-- DELETE FROM leads WHERE id IN (
--   SELECT id FROM (
--     SELECT id, ROW_NUMBER() OVER (PARTITION BY campaign_id, phone_number ORDER BY created_at DESC) as rn
--     FROM leads
--   ) WHERE rn > 1
-- );

-- Step 3: Add unique index
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_campaign_phone 
ON leads(campaign_id, phone_number);

-- Verify the index was created
SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='leads';
