from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.utils.logger import logger

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    
    MAX_REQUEST_SIZE = 10 * 1024 * 1024
    
    async def dispatch(self, request: Request, call_next):
        # Skip size check for OPTIONS (preflight) requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.MAX_REQUEST_SIZE:
                    logger.warning(f"Request too large: {size} bytes from {request.client.host if request.client else 'unknown'}")
                    
                    # Add CORS headers to error response
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
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "detail": f"Request body too large. Maximum size: {self.MAX_REQUEST_SIZE / (1024*1024):.1f}MB",
                            "message": "Request size limit exceeded"
                        }
                    )
                    
                    # Add CORS headers
                    response.headers["Access-Control-Allow-Origin"] = cors_origin
                    response.headers["Access-Control-Allow-Credentials"] = "true"
                    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, X-Requested-With"
                    
                    return response
            except ValueError:
                pass
        
        response = await call_next(request)
        return response

