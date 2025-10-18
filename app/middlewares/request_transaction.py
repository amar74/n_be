from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.session import AsyncSessionLocal, _bind_request_transaction, _reset_request_transaction
from app.utils.logger import logger

class RequestTransactionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        session = AsyncSessionLocal()
        token = None
        try:
            async with session.begin():
                token = _bind_request_transaction(session)
                response = await call_next(request)
                # Don't commit here - the context manager handles it
                return response
        except Exception as exc:
            try:
                await session.rollback()
            except Exception:
                pass
            logger.error(f"Request transaction rolled back due to error: {exc}")
            raise
        finally:
            if token is not None:
                _reset_request_transaction(token)
            await session.close()

