-- Check if account_documents table exists and has data
-- Run this to verify documents are being saved

-- Check table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'account_documents'
ORDER BY ordinal_position;

-- Check if there are any documents
SELECT COUNT(*) as total_documents FROM account_documents;

-- Show recent documents
SELECT 
    id,
    account_id,
    name,
    category,
    file_name,
    created_at,
    updated_at
FROM account_documents
ORDER BY created_at DESC
LIMIT 10;

-- Check documents per account
SELECT 
    a.client_name,
    a.account_id,
    COUNT(ad.id) as document_count
FROM accounts a
LEFT JOIN account_documents ad ON a.account_id = ad.account_id
GROUP BY a.account_id, a.client_name
HAVING COUNT(ad.id) > 0
ORDER BY document_count DESC;
