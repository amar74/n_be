-- Migration: Add name column to users table
-- Run this manually if alembic migration doesn't work

ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(255);

-- Verify the column was added
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'name';
