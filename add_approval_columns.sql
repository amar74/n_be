-- Add approval_status and approval_notes columns to accounts table
-- Run this with: psql your_database_url -f add_approval_columns.sql

-- Add approval_status column with default 'pending'
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS approval_status VARCHAR(20) DEFAULT 'pending';

-- Add approval_notes column
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS approval_notes VARCHAR(1024);

-- Verify columns were added
SELECT 
    column_name, 
    data_type, 
    character_maximum_length, 
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'accounts' 
  AND column_name IN ('approval_status', 'approval_notes')
ORDER BY column_name;

-- Show sample of accounts with new columns
SELECT 
    account_id,
    client_name,
    approval_status,
    account_approver,
    approval_date,
    approval_notes
FROM accounts
LIMIT 3;
