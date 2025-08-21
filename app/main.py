from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router import api_router

app = FastAPI(title="Megapolis API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include API router
app.include_router(api_router)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Hello, world!"}
