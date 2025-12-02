# Run Chat Module Migration

## Quick Fix for 500 Error

The 500 Internal Server Error is because the database tables don't exist yet. Run this command:

```bash
cd megapolis-api
alembic upgrade head
```

This will create:
- `chat_session_status` enum type
- `chat_sessions` table
- `chat_messages` table

## After Migration

Restart your backend server:

```bash
# If using uvicorn directly
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Or if using pm2
pm2 restart megapolis-api
```

## Verify Migration

Check if tables were created:

```sql
-- Connect to your database and run:
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('chat_sessions', 'chat_messages');

-- Should return:
-- chat_sessions
-- chat_messages
```

## Troubleshooting

If migration fails:
1. Check database connection in `.env`
2. Ensure you have the correct database permissions
3. Check alembic version: `alembic current`
4. Check migration status: `alembic history`

