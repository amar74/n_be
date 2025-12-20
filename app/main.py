# @author harsh.pawar
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from app.router import api_router
from app.middlewares.request_transaction import RequestTransactionMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware
from app.middlewares.request_size_limit import RequestSizeLimitMiddleware
from app.middlewares.brute_force_protection import BruteForceProtectionMiddleware
from app.middlewares.file_upload_security import FileUploadSecurityMiddleware
from app.middlewares.audit_logging import AuditLoggingMiddleware
from app.middlewares.input_validation import InputValidationMiddleware
from app.utils.error import MegapolisHTTPException
from app.utils.logger import logger
from app.utils.security import sanitize_log_data, mask_id
from app.environment import environment
from pydantic import BaseModel
import os

app = FastAPI(title="Megapolis API", version="0.1.0")

logger.info("Starting Megapolis API")

# CORS Configuration - Secure and Environment-Based
allowed_origins = environment.ALLOWED_ORIGINS.split(",") if environment.ALLOWED_ORIGINS else [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# In development, add common dev ports
if environment.ENVIRONMENT == "dev":
    allowed_origins.extend([
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],  # Restricted methods
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],  # Include headers needed for file uploads
    expose_headers=["Content-Length", "Content-Type"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

app.add_middleware(InputValidationMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(FileUploadSecurityMiddleware)
app.add_middleware(BruteForceProtectionMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=environment.RATE_LIMIT_PER_MINUTE)
app.add_middleware(AuditLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestTransactionMiddleware)

def add_cors_headers(response: JSONResponse, origin: str = None) -> JSONResponse:
    # Only add if CORSMiddleware hasn't already added them
    if "Access-Control-Allow-Origin" not in response.headers:
        if origin and origin in allowed_origins:
            cors_origin = origin
        else:
            cors_origin = allowed_origins[0] if allowed_origins else "*"
        response.headers["Access-Control-Allow-Origin"] = cors_origin
    
    # Add other headers only if missing
    if "Access-Control-Allow-Credentials" not in response.headers:
        response.headers["Access-Control-Allow-Credentials"] = "true"
    if "Access-Control-Allow-Methods" not in response.headers:
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    if "Access-Control-Allow-Headers" not in response.headers:
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, X-Requested-With"
    return response

# Register exception handlers BEFORE router to ensure they catch all errors
# Register more specific handlers first (MegapolisHTTPException before HTTPException)
@app.exception_handler(MegapolisHTTPException)
async def megapolis_http_exception_handler(request: Request, exc: MegapolisHTTPException):
    """Handle MegapolisHTTPException and add CORS headers"""
    origin = request.headers.get("origin")
    error_detail = exc.details if exc.details else (exc.message if exc.message else "An error occurred")
    
    logger.info(f"MegapolisHTTPException handler called: {exc.status_code} - {error_detail}")
    
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": error_detail}
    )
    return add_cors_headers(response, origin)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    origin = request.headers.get("origin")
    error_detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail) if exc.detail else "An error occurred"
    
    logger.info(f"HTTPException handler called: {exc.status_code} - {error_detail}")
    
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": error_detail}
    )
    cors_response = add_cors_headers(response, origin)
    logger.debug(f"CORS headers added: {dict(cors_response.headers)}")
    return cors_response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    origin = request.headers.get("origin")
    
    # Log detailed validation errors for debugging
    errors = exc.errors()
    logger.warning(f"RequestValidationError on {request.url.path}: {errors}")
    for error in errors:
        logger.warning(f"  - Location: {error.get('loc', [])}, Type: {error.get('type', 'unknown')}, Message: {error.get('msg', 'No message')}")
    
    # Build response content with validation errors (already JSON-serializable)
    response_content = {"detail": errors}
    
    # For multipart/form-data (file uploads), exc.body contains FormData which is not JSON serializable
    # Don't include body for multipart requests to avoid serialization issues
    content_type = request.headers.get("content-type", "")
    is_multipart = "multipart/form-data" in content_type
    
    # Only include body for non-multipart requests and if it's safely serializable
    if not is_multipart and exc.body:
        try:
            if isinstance(exc.body, (str, bytes)):
                body_str = exc.body.decode('utf-8', errors='ignore') if isinstance(exc.body, bytes) else exc.body
                if len(body_str) < 1000:
                    response_content["body"] = body_str
        except Exception:
            pass
    
    response = JSONResponse(
        status_code=422,
        content=response_content
    )
    return add_cors_headers(response, origin)

app.include_router(api_router, prefix="/api")

# Mount static files for uploads - SECURE: Only in development, require auth in production
if environment.ENVIRONMENT == "dev" and os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# In production, serve files through authenticated endpoints only

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="Megapolis API",
        routes=app.routes,
    )
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.middleware("http")
async def handle_exception(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException:
        # Allow FastAPI's HTTPException handlers to run
        raise
    except RequestValidationError:
        # Allow validation error handler to run
        raise
    # This middleware only handles unexpected exceptions (500 errors)
    except Exception as e:
        error_type = type(e).__name__
        # Safely convert error message to string, handling any non-serializable objects
        try:
            error_msg = str(e)
        except Exception:
            error_msg = "An error occurred"
        
        # Log full error internally
        logger.exception(f"Unhandled exception: {error_type}", exc_info=True)
        
        # In development, also print traceback to console
        if environment.ENVIRONMENT == "dev":
            traceback.print_exc()
        
        origin = request.headers.get("origin")
        
        # In dev mode, expose actual error for debugging (but ensure it's JSON-serializable)
        if environment.ENVIRONMENT == "dev":
            # Ensure error_detail is JSON-serializable (string only)
            error_detail = f"{error_type}: {error_msg}" if error_msg else f"{error_type}"
        else:
            error_detail = "An internal error occurred"
        
        # Ensure all response content is JSON-serializable
        response_content = {
            "detail": str(error_detail),  # Explicitly convert to string
            "message": "Something went wrong",
            "error_type": str(error_type)  # Explicitly convert to string
        }
        
        response = JSONResponse(
            status_code=500, 
            content=response_content
        )
        # Add CORS headers to error responses
        return add_cors_headers(response, origin)

logger.info("API router included successfully")

class HelloWorld(BaseModel):
    message: str

@app.get("/")
async def read_root() -> HelloWorld:
    # Don't log sensitive info - just basic access
    return {"message": "Megapolis API is running"}

