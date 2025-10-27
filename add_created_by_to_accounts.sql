-- Add created_by column to accounts table
ALTER TABLE accounts 
ADD COLUMN created_by UUID REFERENCES users(id);

-- Optional: Add index for better query performance
CREATE INDEX idx_accounts_created_by ON accounts(created_by);

-- Optional: Update existing accounts to set created_by to NULL (they already have NULL by default)
-- Or you can set them to a specific admin user if needed
-- UPDATE accounts SET created_by = 'admin-user-uuid' WHERE created_by IS NULL;
