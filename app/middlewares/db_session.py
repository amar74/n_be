from starlette.middleware.base import BaseHTTPMiddleware
from app.db.session import AsyncSessionLocal, set_session, reset_session


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        session = AsyncSessionLocal()
        token = set_session(session)
        try:
            response = await call_next(request)
            return response
        finally:
            await session.close()
            reset_session(token)
