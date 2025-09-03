from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
# from app.middlewares.db_session import DBSessionMiddleware
from app.router import api_router
from app.middlewares.request_transaction import RequestTransactionMiddleware
from app.utils.error import MegapolisHTTPException
from app.utils.logger import logger

app = FastAPI(title="Megapolis API", version="0.1.0")

# Initialize logging
logger.info("Starting Megapolis API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Frontend development server
        "http://localhost:5174",      # Frontend development server
        "http://127.0.0.1:5173",     # Frontend with 127.0.0.1
        "http://localhost:8000",      # API server (for testing)
        "http://127.0.0.1:8000",     # API server with 127.0.0.1
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.add_middleware(RequestTransactionMiddleware)


# Include API router
app.include_router(api_router)

@app.middleware("http")
async def handle_exception(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except MegapolisHTTPException as e:
        logger.exception(f"Error handling request: {e}", exc_info=True)
        return JSONResponse(status_code=e.status_code, content={"message": e.message, "metadata": e.metadata})
    except Exception as e:
        logger.exception(f"Error handling request: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"message": "Something went wrong"})

logger.info("API router included successfully")


@app.get("/")
async def read_root() -> dict[str, str]:
    logger.info("Root endpoint accessed")
    return {"message": "Hello, world!"}
