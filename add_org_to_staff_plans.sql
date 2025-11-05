-- Add org_id to staff_plans table for multi-tenancy
-- This ensures each vendor/organization only sees their own staff planning data

ALTER TABLE staff_plans 
ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- Create index for faster filtering
CREATE INDEX IF NOT EXISTS idx_staff_plans_org_id ON staff_plans(org_id);

-- Update existing records to set org_id from the user who created them
-- This assigns existing staff plans to their creator's organization
UPDATE staff_plans sp
SET org_id = u.org_id
FROM users u
WHERE sp.created_by = u.id
  AND sp.org_id IS NULL
  AND u.org_id IS NOT NULL;

-- Optional: Delete orphaned plans that can't be assigned to any organization
-- DELETE FROM staff_plans WHERE org_id IS NULL;

-- Make org_id NOT NULL after backfilling (optional, for data integrity)
-- ALTER TABLE staff_plans ALTER COLUMN org_id SET NOT NULL;

SELECT 'Migration completed: org_id added to staff_plans' as status;

