# How to Run Chat Migration

## Fix Applied
✅ Fixed `alembic/env.py` - moved `sys.path.insert` before imports

## Steps to Run Migration

### Option 1: Using Poetry (Recommended)
```bash
cd megapolis-api
poetry shell  # Activate poetry virtual environment
alembic upgrade head
```

### Option 2: Using Virtual Environment
```bash
cd megapolis-api
source .venv/bin/activate  # or: source venv/bin/activate
alembic upgrade head
```

### Option 3: Direct Python Path
```bash
cd megapolis-api
PYTHONPATH=/Users/macbookpro/Desktop/ny/megapolis-api alembic upgrade head
```

## Verify Migration Success

After running, check if tables exist:
```sql
-- Connect to your database
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('chat_sessions', 'chat_messages');
```

Should return:
- chat_sessions
- chat_messages

## If Still Getting Import Errors

Make sure you're in the correct directory and virtual environment:
```bash
cd /Users/macbookpro/Desktop/ny/megapolis-api
pwd  # Should show: /Users/macbookpro/Desktop/ny/megapolis-api
which python  # Should show path to your venv Python
python -c "import app; print('OK')"  # Test import
```

