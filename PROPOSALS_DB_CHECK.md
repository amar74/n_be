# Proposals Database Verification Guide

This guide helps you verify that the proposals database tables are created and working correctly.

## Quick Check Commands

### Option 1: Using the Check Script (Recommended)
```bash
cd megapolis-api
poetry run python check_proposals_db.py
# OR if using virtual environment:
python3 check_proposals_db.py
```

### Option 2: Check Migration Status
```bash
cd megapolis-api
poetry run python manage.py upgrade
# OR
poetry run alembic current
```

### Option 3: Direct SQL Query
If you have direct database access, run:
```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('proposals', 'proposal_sections', 'proposal_documents', 'proposal_approvals');

-- Check proposals count
SELECT COUNT(*) FROM proposals;

-- View recent proposals
SELECT id, proposal_number, title, status, created_at 
FROM proposals 
ORDER BY created_at DESC 
LIMIT 10;
```

## Expected Database Schema

### Tables That Should Exist:
1. ✅ `proposals` - Main proposals table
2. ✅ `proposal_sections` - Proposal sections/content
3. ✅ `proposal_documents` - Attached documents
4. ✅ `proposal_approvals` - Approval workflow

### Critical Columns in `proposals` Table:
- `id` (UUID, primary key)
- `org_id` (UUID, foreign key to organizations)
- `proposal_number` (String, unique, required)
- `title` (String, required)
- `status` (Enum: draft, in_review, approved, submitted, won, lost, archived)
- `proposal_type` (Enum: proposal, brochure, interview, campaign)
- `version` (Integer, default: 1)
- `currency` (String(3), default: "USD")
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Required Enums:
- `proposal_status`
- `proposal_source`
- `proposal_type`
- `proposal_section_status`
- `proposal_document_category`
- `proposal_approval_status`

## Common Issues and Solutions

### Issue 1: Tables Don't Exist
**Symptom**: 500 error when creating proposals, "relation does not exist"

**Solution**:
```bash
cd megapolis-api
poetry run python manage.py upgrade
# OR
poetry run alembic upgrade head
```

### Issue 2: Migration Not Applied
**Check current migration**:
```bash
poetry run alembic current
```

**Check available migrations**:
```bash
poetry run alembic history
```

**Apply pending migrations**:
```bash
poetry run alembic upgrade head
```

### Issue 3: Unique Constraint Violation on proposal_number
**Symptom**: Error about duplicate proposal_number

**Cause**: Race condition in proposal number generation

**Solution**: The code now includes retry logic. If it persists, check:
1. Database transactions are properly isolated
2. Proposal number generation logic handles concurrent requests

### Issue 4: Missing Foreign Key References
**Symptom**: Foreign key constraint violation

**Check**:
- Ensure `organizations` table exists
- Ensure `users` table exists  
- Ensure `opportunities` table exists (if linking proposals to opportunities)
- Ensure `accounts` table exists (if linking proposals to accounts)

## Verification Checklist

After running migrations, verify:

- [ ] All 4 proposal-related tables exist
- [ ] `proposals` table has all required columns
- [ ] Unique constraint exists on `proposal_number`
- [ ] All enum types are created
- [ ] Can insert a test proposal (use API or direct SQL)
- [ ] Proposal number generation works correctly
- [ ] Foreign key constraints are in place

## Test Proposal Creation

To test if proposals are being stored correctly:

1. **Via API**:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/proposals/create \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "title": "Test Proposal",
       "proposal_type": "proposal",
       "currency": "USD"
     }'
   ```

2. **Check Database**:
   ```sql
   SELECT * FROM proposals WHERE title = 'Test Proposal';
   ```

3. **Verify via API**:
   ```bash
   curl http://127.0.0.1:8000/api/proposals/ \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## Next Steps After Verification

1. ✅ Tables exist → Test proposal creation via frontend
2. ❌ Tables missing → Run migrations
3. ✅ Tables exist but errors → Check logs for specific error messages
4. ✅ Data not persisting → Check transaction commit logic

