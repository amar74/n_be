-- ============================================
-- Megapolis Database Migrations
-- Run this to update the database with all recent changes
-- ============================================

-- Usage:
-- psql your_database_url -f run_all_migrations.sql

BEGIN;

-- 1. Add approval columns to accounts table
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS approval_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS approval_notes VARCHAR(1024);

-- 2. Add created_by column to accounts table
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);
CREATE INDEX IF NOT EXISTS idx_accounts_created_by ON accounts(created_by);

-- 3. Add updated_by column to accounts table
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id);
CREATE INDEX IF NOT EXISTS idx_accounts_updated_by ON accounts(updated_by);

-- 4. Add user profile fields (if not already added)
ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS address VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS state VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS zip_code VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(50);

COMMIT;

-- Verify the changes
SELECT 'Accounts table columns:' AS info;
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'accounts' 
  AND column_name IN ('approval_status', 'approval_notes', 'created_by', 'updated_by')
ORDER BY column_name;

SELECT 'Users table columns:' AS info;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users' 
  AND column_name IN ('name', 'phone', 'bio', 'address', 'city', 'state', 'zip_code', 'country', 'timezone', 'language')
ORDER BY column_name;

-- Show sample data
SELECT 'Sample accounts with new columns:' AS info;
SELECT 
    account_id,
    client_name,
    approval_status,
    created_by,
    updated_by,
    account_approver,
    approval_date
FROM accounts
LIMIT 5;
