from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
from app.utils.logger import logger

class BruteForceProtectionMiddleware(BaseHTTPMiddleware):
    
    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=15)
    WINDOW_DURATION = timedelta(minutes=5)
    
    def __init__(self, app):
        super().__init__(app)
        self.failed_attempts = defaultdict(list)
        self.locked_ips = {}
        self.cleanup_interval = timedelta(minutes=10)
        self.last_cleanup = datetime.utcnow()
    
    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _is_locked(self, ip: str) -> bool:
        if ip not in self.locked_ips:
            return False
        
        lockout_until = self.locked_ips[ip]
        if datetime.utcnow() > lockout_until:
            del self.locked_ips[ip]
            self.failed_attempts[ip] = []
            return False
        
        return True
    
    def _record_failed_attempt(self, ip: str):
        now = datetime.utcnow()
        cutoff = now - self.WINDOW_DURATION
        
        self.failed_attempts[ip] = [
            timestamp for timestamp in self.failed_attempts[ip]
            if timestamp > cutoff
        ]
        
        self.failed_attempts[ip].append(now)
        
        if len(self.failed_attempts[ip]) >= self.MAX_ATTEMPTS:
            lockout_until = now + self.LOCKOUT_DURATION
            self.locked_ips[ip] = lockout_until
            logger.warning(f"IP {ip} locked out due to {len(self.failed_attempts[ip])} failed attempts. Locked until {lockout_until}")
    
    def _record_success(self, ip: str):
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]
        if ip in self.locked_ips:
            del self.locked_ips[ip]
    
    def _cleanup_old_entries(self):
        now = datetime.utcnow()
        if (now - self.last_cleanup) < self.cleanup_interval:
            return
        
        cutoff = now - self.WINDOW_DURATION
        for ip in list(self.failed_attempts.keys()):
            self.failed_attempts[ip] = [
                timestamp for timestamp in self.failed_attempts[ip]
                if timestamp > cutoff
            ]
            if not self.failed_attempts[ip]:
                del self.failed_attempts[ip]
        
        for ip in list(self.locked_ips.keys()):
            if now > self.locked_ips[ip]:
                del self.locked_ips[ip]
        
        self.last_cleanup = now
    
    async def dispatch(self, request: Request, call_next):
        # Skip brute force protection for OPTIONS (preflight) requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        if not request.url.path.startswith("/api/auth/login"):
            return await call_next(request)
        
        self._cleanup_old_entries()
        client_ip = self._get_client_ip(request)
        
        if self._is_locked(client_ip):
            lockout_until = self.locked_ips[client_ip]
            remaining = (lockout_until - datetime.utcnow()).total_seconds() / 60
            logger.warning(f"Blocked login attempt from locked IP: {client_ip}")
            
            # Add CORS headers to locked response
            origin = request.headers.get("origin")
            from app.environment import environment
            allowed_origins = environment.ALLOWED_ORIGINS.split(",") if environment.ALLOWED_ORIGINS else ["http://localhost:5173", "http://127.0.0.1:5173"]
            if environment.ENVIRONMENT == "dev":
                allowed_origins.extend([
                    "http://localhost:5174",
                    "http://localhost:5175",
                    "http://localhost:3000",
                    "http://127.0.0.1:5174",
                    "http://127.0.0.1:5175",
                    "http://127.0.0.1:3000",
                ])
            cors_origin = origin if origin in allowed_origins else allowed_origins[0] if allowed_origins else "*"
            
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Too many failed login attempts. Account locked for {remaining:.0f} more minutes.",
                    "message": "Account temporarily locked"
                },
                headers={
                    "Retry-After": str(int(remaining * 60))
                }
            )
            
            # Add CORS headers
            response.headers["Access-Control-Allow-Origin"] = cors_origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, X-Requested-With"
            
            return response
        
        response = await call_next(request)
        
        if response.status_code == 401:
            self._record_failed_attempt(client_ip)
            remaining_attempts = self.MAX_ATTEMPTS - len(self.failed_attempts[client_ip])
            if remaining_attempts > 0:
                response.headers["X-Remaining-Attempts"] = str(remaining_attempts)
        elif response.status_code == 200:
            self._record_success(client_ip)
        
        return response

