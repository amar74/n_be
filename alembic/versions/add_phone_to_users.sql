-- Add phone field to users table
-- Run this with: psql your_database_url -f add_phone_to_users.sql

ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

-- Verify column was added
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'phone';
