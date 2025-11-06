-- Fix interview column types to match SQLAlchemy model
-- interview_date should be TIMESTAMP, not DATE
-- interview_time should be VARCHAR(10), not TIME

-- Step 1: Change interview_date from DATE to TIMESTAMP
ALTER TABLE employees 
ALTER COLUMN interview_date TYPE TIMESTAMP WITHOUT TIME ZONE 
USING interview_date::TIMESTAMP WITHOUT TIME ZONE;

-- Step 2: Change interview_time from TIME to VARCHAR(10)
ALTER TABLE employees 
ALTER COLUMN interview_time TYPE VARCHAR(10) 
USING interview_time::VARCHAR(10);

-- Verify changes
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'employees' 
  AND column_name IN ('interview_date', 'interview_time');

SELECT 'Migration completed successfully!' as status;

