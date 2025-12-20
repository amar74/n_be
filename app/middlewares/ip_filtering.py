from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.utils.logger import logger
from app.environment import environment
import os

class IPFilteringMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app):
        super().__init__(app)
        self.blocked_ips = set()
        self.allowed_ips = set()
        self._load_ip_lists()
    
    def _load_ip_lists(self):
        blocked_ips_env = os.getenv("BLOCKED_IPS", "")
        allowed_ips_env = os.getenv("ALLOWED_IPS", "")
        
        if blocked_ips_env:
            self.blocked_ips = set(ip.strip() for ip in blocked_ips_env.split(",") if ip.strip())
        
        if allowed_ips_env and environment.ENVIRONMENT == "prod":
            self.allowed_ips = set(ip.strip() for ip in allowed_ips_env.split(",") if ip.strip())
    
    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked request from blacklisted IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Access denied",
                    "message": "IP address blocked"
                }
            )
        
        if self.allowed_ips and client_ip not in self.allowed_ips:
            logger.warning(f"Blocked request from non-whitelisted IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Access denied",
                    "message": "IP address not allowed"
                }
            )
        
        response = await call_next(request)
        return response

