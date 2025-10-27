-- Migration: Add profile fields to users table
-- Run this manually if alembic migration doesn't work

-- Add name column (if not exists)
ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(255);

-- Add phone column (if not exists)
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

-- Add bio field
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio VARCHAR(500);

-- Add address fields
ALTER TABLE users ADD COLUMN IF NOT EXISTS address VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS state VARCHAR(2);
ALTER TABLE users ADD COLUMN IF NOT EXISTS zip_code VARCHAR(10);

-- Add country field with default
ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'United States';

-- Add preferences
ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'America/New_York';
ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en';

-- Verify all columns were added
SELECT column_name, data_type, character_maximum_length, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('name', 'phone', 'bio', 'address', 'city', 'state', 'zip_code', 'country', 'timezone', 'language')
ORDER BY column_name;
