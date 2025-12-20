from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
from app.environment import environment
from app.utils.logger import logger

class RateLimitMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute if environment.RATE_LIMIT_ENABLED else 10000
        self.request_counts = defaultdict(list)
        self.cleanup_interval = timedelta(minutes=5)
        self.last_cleanup = datetime.utcnow()
    
    def _get_client_id(self, request: Request) -> str:
        if hasattr(request.state, 'user_id'):
            return f"user:{request.state.user_id}"
        
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _cleanup_old_entries(self):
        now = datetime.utcnow()
        if (now - self.last_cleanup) < self.cleanup_interval:
            return
        
        cutoff = now - timedelta(minutes=2)
        for client_id in list(self.request_counts.keys()):
            self.request_counts[client_id] = [
                timestamp for timestamp in self.request_counts[client_id]
                if timestamp > cutoff
            ]
            if not self.request_counts[client_id]:
                del self.request_counts[client_id]
        
        self.last_cleanup = now
    
    async def dispatch(self, request: Request, call_next):
        if not environment.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Skip rate limiting for OPTIONS (preflight) requests - CORS depends on these
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip rate limiting for health check and documentation endpoints
        if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        
        self._cleanup_old_entries()
        
        recent_requests = [
            timestamp for timestamp in self.request_counts[client_id]
            if timestamp > cutoff
        ]
        
        if len(recent_requests) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_id}: {len(recent_requests)} requests in last minute")
            
            # Get origin for CORS headers
            origin = request.headers.get("origin")
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
                    "detail": "Rate limit exceeded. Please try again later.",
                    "message": "Too many requests"
                }
            )
            
            # Add CORS headers to rate limit response
            response.headers["Access-Control-Allow-Origin"] = cors_origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, X-Requested-With"
            
            return response
        
        self.request_counts[client_id].append(now)
        
        response = await call_next(request)
        
        remaining = max(0, self.requests_per_minute - len(recent_requests) - 1)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(minutes=1)).timestamp()))
        
        return response

