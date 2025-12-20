from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.utils.logger import logger
from app.utils.security import validate_file_type, validate_file_size, sanitize_filename
from app.environment import environment

class FileUploadSecurityMiddleware(BaseHTTPMiddleware):
    
    ALLOWED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        'document': ['.pdf', '.doc', '.docx', '.txt', '.csv'],
        'spreadsheet': ['.xls', '.xlsx', '.csv'],
        'archive': ['.zip', '.rar']
    }
    
    MAX_FILE_SIZE_MB = 10
    
    async def dispatch(self, request: Request, call_next):
        # Skip file upload checks for OPTIONS (preflight) requests - let CORS middleware handle them
        if request.method == "OPTIONS":
            return await call_next(request)
        
        if request.method == "POST" and "multipart/form-data" in request.headers.get("content-type", ""):
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    size = int(content_length)
                    if not validate_file_size(size, self.MAX_FILE_SIZE_MB):
                        logger.warning(f"File upload rejected: size {size} bytes exceeds limit")
                        # Get origin for CORS headers
                        origin = request.headers.get("origin")
                        allowed_origins = environment.ALLOWED_ORIGINS.split(",") if environment.ALLOWED_ORIGINS else ["http://localhost:5173", "http://127.0.0.1:5173"]
                        cors_origin = origin if origin in allowed_origins else allowed_origins[0] if allowed_origins else "*"
                        
                        response = JSONResponse(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            content={
                                "detail": f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE_MB}MB",
                                "message": "File too large"
                            }
                        )
                        # Add CORS headers to error response
                        response.headers["Access-Control-Allow-Origin"] = cors_origin
                        response.headers["Access-Control-Allow-Credentials"] = "true"
                        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept"
                        return response
                except ValueError:
                    pass
        
        response = await call_next(request)
        return response

