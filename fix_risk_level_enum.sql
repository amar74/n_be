-- Fix contract risk_level enum conflict
-- This script creates the contract_risk_level enum and updates the contracts table to use it

-- Step 1: Create the new enum if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contract_risk_level') THEN
        CREATE TYPE contract_risk_level AS ENUM ('low', 'medium', 'high');
        RAISE NOTICE 'Created contract_risk_level enum';
    ELSE
        RAISE NOTICE 'contract_risk_level enum already exists';
    END IF;
END
$$;

-- Step 2: Check current enum type
SELECT column_name, udt_name 
FROM information_schema.columns 
WHERE table_name = 'contracts' AND column_name = 'risk_level';

-- Step 3: Update the column to use the new enum
-- Note: This will fail if there's existing data with incompatible values
-- If there's existing data, you may need to convert it first
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'contracts' 
        AND column_name = 'risk_level' 
        AND udt_name != 'contract_risk_level'
    ) THEN
        -- First, convert any existing data (if any)
        -- Since the old enum has low_risk/medium_risk/high_risk and new has low/medium/high
        -- We need to handle this conversion
        
        -- Drop the old constraint if it exists
        ALTER TABLE contracts DROP CONSTRAINT IF EXISTS contracts_risk_level_check;
        
        -- Change the column type
        ALTER TABLE contracts 
        ALTER COLUMN risk_level TYPE contract_risk_level 
        USING CASE 
            WHEN risk_level::text = 'low_risk' THEN 'low'::contract_risk_level
            WHEN risk_level::text = 'medium_risk' THEN 'medium'::contract_risk_level
            WHEN risk_level::text = 'high_risk' THEN 'high'::contract_risk_level
            ELSE 'medium'::contract_risk_level
        END;
        
        RAISE NOTICE 'Updated contracts.risk_level to use contract_risk_level enum';
    ELSE
        RAISE NOTICE 'contracts.risk_level already uses contract_risk_level enum';
    END IF;
END
$$;

-- Step 4: Verify the change
SELECT column_name, udt_name 
FROM information_schema.columns 
WHERE table_name = 'contracts' AND column_name = 'risk_level';

