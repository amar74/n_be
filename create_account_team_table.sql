-- Create account_team table
CREATE TABLE IF NOT EXISTS account_team (
    id SERIAL PRIMARY KEY,
    account_id UUID NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    role_in_account VARCHAR(100),
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    removed_at TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_account_team_account_id ON account_team(account_id);
CREATE INDEX IF NOT EXISTS idx_account_team_employee_id ON account_team(employee_id);

-- Create unique constraint for active assignments
CREATE UNIQUE INDEX IF NOT EXISTS idx_account_team_unique 
ON account_team(account_id, employee_id) 
WHERE removed_at IS NULL;

-- Display success message
SELECT 'Account team table created successfully!' AS status;

