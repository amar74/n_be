from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.utils.logger import logger
from app.utils.security import mask_id, sanitize_log_data
from datetime import datetime

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    
    SENSITIVE_ENDPOINTS = [
        "/api/auth/login",
        "/api/auth/signup",
        "/api/auth/password-reset",
        "/api/admin",
        "/api/super-admin",
    ]
    
    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        method = request.method
        path = request.url.path
        is_sensitive = any(path.startswith(endpoint) for endpoint in self.SENSITIVE_ENDPOINTS)
        
        start_time = datetime.utcnow()
        
        response = await call_next(request)
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        status_code = response.status_code
        
        if is_sensitive or status_code >= 400:
            user_id = None
            if hasattr(request.state, 'user_id'):
                user_id = mask_id(str(request.state.user_id))
            
            log_data = {
                "timestamp": start_time.isoformat(),
                "method": method,
                "path": path,
                "status_code": status_code,
                "client_ip": client_ip,
                "duration_ms": round(duration * 1000, 2),
                "user_id": user_id,
            }
            
            if status_code >= 400:
                logger.warning(f"Security event: {sanitize_log_data(log_data)}")
            elif is_sensitive:
                logger.info(f"Audit log: {sanitize_log_data(log_data)}")
        
        return response

