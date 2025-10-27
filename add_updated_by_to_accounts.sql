-- Add updated_by column to accounts table
ALTER TABLE accounts 
ADD COLUMN updated_by UUID REFERENCES users(id);

-- Add index for better query performance
CREATE INDEX idx_accounts_updated_by ON accounts(updated_by);

-- Add comment
COMMENT ON COLUMN accounts.updated_by IS 'User who last updated this account';
