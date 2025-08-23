from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.middlewares.db_session import DBSessionMiddleware
from app.router import api_router
from app.utils.logger import logger

app = FastAPI(title="Megapolis API", version="0.1.0")

# Initialize logging
logger.info("Starting Megapolis API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Add DB session middleware 👇
# app.add_middleware(DBSessionMiddleware)
# Include API router
app.include_router(api_router)

logger.info("API router included successfully")


@app.get("/")
async def read_root() -> dict[str, str]:
    logger.info("Root endpoint accessed")
    return {"message": "Hello, world!"}
