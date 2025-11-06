-- Add username column to users table for employee login
-- Employees will login with username (employee_number) instead of email
-- This eliminates email conflicts across organizations

-- Add username column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS username VARCHAR(50) UNIQUE;

-- Create index for fast username lookups during login
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- For existing employee users, populate username from their employee_number
UPDATE users u
SET username = e.employee_number
FROM employees e
WHERE e.user_id = u.id
  AND e.employee_number IS NOT NULL
  AND u.username IS NULL;

-- Verify the changes
SELECT 
  COUNT(*) as total_users,
  COUNT(username) as users_with_username
FROM users;

SELECT 'Migration completed: username column added to users table' as status;

