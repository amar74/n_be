-- Add profile fields to users table
-- Run this with: psql your_database_url -f add_user_profile_fields.sql

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS bio VARCHAR(500),
ADD COLUMN IF NOT EXISTS address VARCHAR(255),
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS state VARCHAR(2),
ADD COLUMN IF NOT EXISTS zip_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'United States',
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'America/New_York',
ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en';

-- Verify columns were added
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    column_default
FROM information_schema.columns
WHERE table_name = 'users' 
  AND column_name IN ('bio', 'address', 'city', 'state', 'zip_code', 'country', 'timezone', 'language')
ORDER BY column_name;

-- Show sample of users with new columns
SELECT 
    email,
    name,
    phone,
    city,
    state,
    country
FROM users
LIMIT 3;
