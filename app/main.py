# @author harsh.pawar
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.router import api_router
from app.middlewares.request_transaction import RequestTransactionMiddleware
from app.utils.error import MegapolisHTTPException
from app.utils.logger import logger
from pydantic import BaseModel

app = FastAPI(title="Megapolis API", version="0.1.0")

logger.info("Starting Megapolis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Frontend development server
        "http://localhost:5174",      # Frontend development server (alternative port)
        "http://localhost:5175",      # Frontend development server (port 5175)
        "http://localhost:5176",      # Frontend development server (port 5176)
        "http://localhost:5177",      # Frontend development server (port 5177)
        "http://127.0.0.1:5173",     # Frontend with 127.0.0.1
        "http://127.0.0.1:5174",     # Frontend with 127.0.0.1 (alternative port)
        "http://127.0.0.1:5175",     # Frontend with 127.0.0.1 (port 5175)
        "http://127.0.0.1:5176",     # Frontend with 127.0.0.1 (port 5176)
        "http://127.0.0.1:5177",     # Frontend with 127.0.0.1 (port 5177)
        "http://localhost:3000",      # Another common frontend port
        "http://127.0.0.1:3000",     # Another common frontend port with 127.0.0.1
        "http://localhost:8000",      # API server
        "http://127.0.0.1:8000",     # API server with 127.0.0.1
        "*",                          # Allow all origins for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, PATCH, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.add_middleware(RequestTransactionMiddleware)


app.include_router(api_router, prefix="/api")

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
    return {"message": "Hello, Amarnath Rana!, all endpoints are working fine!"}

