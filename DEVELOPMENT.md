## Megapolis API – Developer Guide

This guide explains how to work on the `megapolis-api` service using FastAPI, async SQLAlchemy, Alembic, Pydantic v2, and Loguru.

### Quick Start

1. Install dependencies (Poetry):
   - `poetry install`
2. Set environment variables (see Environment below).
3. Run the server:
   - `python manage.py run --host 127.0.0.1 --port 8000 --reload`

### Project Structure

- `app/main.py`: FastAPI app and CORS
- `app/router.py`: Aggregates feature routers
- `app/routes/*`: Feature endpoints (thin)
- `app/services/*`: Business logic (async)
- `app/models/*`: SQLAlchemy models (DeclarativeBase)
- `app/schemas/*`: Pydantic v2 schemas (`from_attributes = True`)
- `app/db/session.py`: Async engine, `get_session` and `get_db`
- `app/utils/logger.py`: Loguru configuration
- `alembic/*`: Migrations (async env)
- `manage.py`: Typer CLI for running and migrating

### Common Commands

Using `manage.py`:

```bash
python manage.py run --host 127.0.0.1 --port 8000 --reload
python manage.py migrate -m "add <feature>"
python manage.py upgrade
python manage.py downgrade -1
python manage.py initdb
```

Using Poetry + Alembic directly:

```bash
poetry run alembic revision --autogenerate -m "add <feature>"
poetry run alembic upgrade head
poetry run alembic downgrade -1
```

### Coding Conventions

- Use async/await for I/O across routes, services, and DB.
- Type-annotate public functions. Endpoints should return Pydantic models (avoid raw dicts).
- Keep routes thin; delegate to the service layer.
- Use `from app.utils.logger import logger`; avoid `print`.
- Prefer guard clauses and early returns; avoid deep nesting.

### Database Usage

- In routes (DI):

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session

async def handler(session: AsyncSession = Depends(get_session)):
    ...
```

- Outside routes (scripts/tasks):

```python
from app.db.session import get_db

async def job():
    async with get_db() as session:
        ...
```

### Adding a New Feature

1. Plan the data model and flow.
2. Create/modify SQLAlchemy models in `app/models/*`.
3. Generate and apply migrations (see commands above).
4. Add request/response schemas in `app/schemas/*`.
5. Implement business logic in `app/services/*` (async; keep boundaries typed).
6. Add FastAPI routes in `app/routes/*`, inject `get_session`, return schemas.
7. Register the router in `app/router.py`.
8. Add logging; validate inputs; raise appropriate HTTP errors.

### Example Patterns

Route:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.widget import WidgetCreateRequest, WidgetResponse
from app.services.widget import WidgetService
from app.utils.logger import logger

router = APIRouter(prefix="/widgets", tags=["widgets"])

@router.post("/", response_model=WidgetResponse, status_code=201)
async def create_widget(payload: WidgetCreateRequest, session: AsyncSession = Depends(get_session)) -> WidgetResponse:
    logger.info("Creating widget")
    widget = await WidgetService.create(session, payload)
    return WidgetResponse.model_validate(widget)
```

Model:

```python
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.db.base import Base

class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    @classmethod
    async def create(cls, session: AsyncSession, name: str) -> "Widget":
        inst = cls(name=name)
        session.add(inst)
        await session.commit()
        await session.refresh(inst)
        return inst

    @classmethod
    async def get_by_id(cls, session: AsyncSession, widget_id: int) -> Optional["Widget"]:
        res = await session.execute(select(cls).where(cls.id == widget_id))
        return res.scalar_one_or_none()
```

Schema:

```python
from pydantic import BaseModel

class WidgetCreateRequest(BaseModel):
    name: str

class WidgetResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
```

Service:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.widget import Widget
from app.schemas.widget import WidgetCreateRequest
from app.utils.logger import logger

class WidgetService:
    @staticmethod
    async def create(session: AsyncSession, payload: WidgetCreateRequest) -> Widget:
        # Implement a real uniqueness check here
        existing = await Widget.get_all(session, skip=0, limit=1)
        if any(w.name == payload.name for w in existing):
            raise HTTPException(status_code=400, detail="Name already exists")
        return await Widget.create(session, payload.name)
```

### Authentication

- Verify incoming Supabase token; fallback to decode-only if necessary to extract `email`.
- Ensure the user exists or create on the fly.
- Issue a local JWT (HS256) using `JWT_SECRET_KEY` with `sub`, `email`, and `exp` claims.

```python
import os, jwt
from datetime import datetime, timedelta

def issue_jwt(user_id: int, email: str) -> str:
    exp = datetime.utcnow() + timedelta(days=30)
    payload = {"sub": str(user_id), "email": email, "exp": exp}
    secret = os.environ.get("JWT_SECRET_KEY", "change-me")
    return jwt.encode(payload, secret, algorithm="HS256")
```

### Environment

- Prefer `from app import environment` and then `environment.<VARIABLE_NAME>`.
- Common variables:
  - `DATABASE_URL`
  - `JWT_SECRET_KEY`
  - `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
  - `ENVIRONMENT` (set to `production` to enable file logging)

Example:

```python
from app import environment
from app.utils.logger import logger

JWT_SECRET = environment.JWT_SECRET_KEY
logger.debug(f"JWT secret configured? {'yes' if bool(JWT_SECRET) else 'no'}")
```

### Logging

- Use Loguru: `from app.utils.logger import logger`
- Levels: `info` (major events), `debug` (details; do not log secrets), `warning` (recoverable issues), `error` (failures)

### Notes

- Avoid synchronous/blocking code inside request handlers.
- Avoid returning ORM instances from endpoints; return Pydantic models or sanitized dicts.
- Do not write tests unless explicitly requested.


