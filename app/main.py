import traceback
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
# from app.middlewares.db_session import DBSessionMiddleware
from app.router import api_router
from app.middlewares.request_transaction import RequestTransactionMiddleware
from app.utils.error import MegapolisHTTPException
from app.utils.logger import logger
from pydantic import BaseModel

app = FastAPI(title="Megapolis API", version="0.1.0")

# Initialize logging
logger.info("Starting Megapolis API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Frontend development server
        "http://localhost:5174",      # Frontend development server (alternative port)
        "http://127.0.0.1:5173",     # Frontend with 127.0.0.1
        "http://127.0.0.1:5174",     # Frontend with 127.0.0.1 (alternative port)
        "http://localhost:3000",      # Another common frontend port
        "http://127.0.0.1:3000",     # Another common frontend port with 127.0.0.1
        "http://localhost:8000",      # API server (for testing)
        "http://127.0.0.1:8000",     # API server with 127.0.0.1
        "*",                          # Allow all origins for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.add_middleware(RequestTransactionMiddleware)


# Include API router
app.include_router(api_router)

# Customize OpenAPI to add global Bearer auth in Swagger UI
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
    # Apply Bearer auth globally so the Authorize button adds the header to all requests
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.middleware("http")
async def handle_exception(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except MegapolisHTTPException as e:
        logger.exception("Error handling request", e, exc_info=True)
        return JSONResponse(status_code=e.status_code, content={"message": e.message, "metadata": e.metadata})
    except Exception as e:
        logger.exception("Error handling request", e, exc_info=True)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": "Something went wrong"})

logger.info("API router included successfully")


class HelloWorld(BaseModel):
    message: str

@app.get("/")
async def read_root() -> HelloWorld:
    logger.info("Root endpoint accessed")
    return {"message": "Hello, world!"}
