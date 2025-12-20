from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.utils.logger import logger
import re

class InputValidationMiddleware(BaseHTTPMiddleware):
    
    MAX_STRING_LENGTH = 10000
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'\.\./',
        r'\.\.\\',
        r'<iframe',
        r'eval\(',
        r'exec\(',
    ]
    
    def _validate_string(self, value: str) -> bool:
        if not isinstance(value, str):
            return True
        
        if len(value) > self.MAX_STRING_LENGTH:
            return False
        
        value_lower = value.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return False
        
        return True
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation for OPTIONS (preflight) requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip validation for file uploads (multipart/form-data) to avoid interfering with FastAPI's form parsing
        content_type = request.headers.get("content-type", "").lower()
        is_file_upload = "multipart/form-data" in content_type
        
        # Skip file upload endpoints - they handle their own validation
        path = request.url.path.lower()
        is_upload_endpoint = any(
            path.endswith(endpoint_path) for endpoint_path in [
                "/documents/upload",
                "/upload",
                "/file",
                "/files",
            ]
        )
        
        # NEVER read body for file uploads - it breaks multipart parsing
        if is_file_upload or is_upload_endpoint:
            # Skip body reading for any file upload
            response = await call_next(request)
            return response
        
        # Only validate body for non-file-upload requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8', errors='ignore')
                    if not self._validate_string(body_str):
                        logger.warning(f"Potentially dangerous input detected from {request.client.host if request.client else 'unknown'}")
                        
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
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "detail": "Invalid input detected",
                                "message": "Request contains potentially dangerous content"
                            }
                        )
                        
                        # Add CORS headers
                        response.headers["Access-Control-Allow-Origin"] = cors_origin
                        response.headers["Access-Control-Allow-Credentials"] = "true"
                        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, X-Requested-With"
                        
                        return response
            except Exception as e:
                logger.error(f"Error validating input: {e}")
        
        response = await call_next(request)
        return response

