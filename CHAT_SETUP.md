# Chat Module Setup Instructions

## Issues Fixed

1. ✅ **Select Component Error**: Fixed controlled/uncontrolled state issue
2. ✅ **Metadata Reserved Word**: Renamed `metadata` to `session_metadata` and `message_metadata` in models
3. ⚠️ **Database Migration**: Needs to be run

## Required Steps

### 1. Run Database Migration

The chat tables need to be created in the database. Run:

```bash
cd megapolis-api
alembic upgrade head
```

This will create:
- `chat_sessions` table
- `chat_messages` table
- `chat_session_status` enum type

### 2. Verify Migration

Check if tables exist:

```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('chat_sessions', 'chat_messages');
```

### 3. Restart Backend

After running the migration, restart the backend server:

```bash
# If using uvicorn directly
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Or if using pm2
pm2 restart megapolis-api
```

## Common Issues

### CORS Error
- **Cause**: Backend not running or crashed due to missing tables
- **Fix**: Run migration and restart backend

### 500 Internal Server Error
- **Cause**: Database tables don't exist
- **Fix**: Run `alembic upgrade head`

### Select Component Warning
- **Cause**: Switching between controlled/uncontrolled state
- **Fix**: ✅ Already fixed - using separate `templateValue` state

## Testing

After setup, test the chat functionality:

1. Navigate to any module (e.g., `/module/finance`)
2. Click "Chat History" button
3. Click "Create New Chat"
4. Fill in the form and create a session
5. Start chatting - messages should save automatically

