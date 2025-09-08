## Megapolis API – Development Guide

This is the go-to document for contributing to `megapolis-api`. It explains how the backend is structured, the conventions we follow, and a step-by-step workflow to add a new feature using FastAPI, async SQLAlchemy (2.0 style), Alembic, Pydantic v2, and Loguru.

- Tech stack: FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2, Loguru
- Entry: `app/main.py` with `FastAPI` app and CORS; routers included in `app/router.py`
- DB: Transactional Postgres via `app/db/session.py` (`get_request_transaction` for DI, `get_request_transaction` will return the current request-scoped transaction if a error occurs transaction will be rolled back)
- Models: SQLAlchemy models in `app/models/*` extending `app.db.base.Base`
- Schemas: Pydantic v2 models in `app/schemas/*` with `Config.from_attributes = True`
- Services: Business logic in `app/services/*`
- Routes: Feature routers in `app/routes/*`, included from `app/router.py`
- Logging: Loguru via `from app.utils.logger import logger`
- Auth: Supabase token verification and local JWT issuance in `app/routes/auth.py`

### Quick Start

Install dependencies, configure env, and run the server.

```bash
poetry install
python manage.py run --host 127.0.0.1 --port 8000 --reload
```

### Project Structure

Understand where code lives and what belongs where.

- `app/main.py`: FastAPI app and CORS
- `app/router.py`: Aggregates feature routers
- `app/routes/*`: Feature endpoints (keep thin)
- `app/services/*`: Business logic (async)
- `app/models/*`: SQLAlchemy models (DeclarativeBase)
- `app/schemas/*`: Pydantic v2 schemas (`from_attributes = True`)
- `app/db/session.py`: Async engine, `get_request_transaction` will return the current request-scoped transaction if a error occurs transaction will be rolled back
- `app/utils/logger.py`: Loguru configuration
- `alembic/*`: Migrations
- `manage.py`: Typer CLI for running and migrating

### Common Commands

Use the project CLI for local development and migrations.

```bash
poetry run python manage.py run --host 127.0.0.1 --port 8000 --reload
poetry run python manage.py migrate -m "add <feature>"
poetry run python manage.py upgrade
poetry run python manage.py downgrade -1
poetry run python manage.py initdb
```


### Conventions and Patterns

- Keep endpoints thin; delegate to the service layer.
- Use async end-to-end for I/O: routes, services, DB.
- Type-annotate public functions; endpoints should return Pydantic models (avoid raw dicts).
- Prefer guard clauses and early returns over deep nesting.
- Use Loguru (`from app.utils.logger import logger`); avoid `print`.
- Avoid returning ORM models directly; return Pydantic models or sanitized dicts.
- For interconnected flows where values pass across layers, prefer an event/coordinator class per feature to orchestrate.

### Database Sessions

Everywhere in FastAPI, use `get_request_transaction` as an async context manager.

```python
from app.db.session import get_request_transaction
from app.models.user import User
from sqlalchemy import select

async def job():
    db = get_request_transaction()
    await db.execute(select(User).where(User.id == 1))
```

### Environment Variables

Read environment variables using `os.environ`. Optionally, you can add an `app/environment.py` helper to centralize configuration (not currently included by default).

```python
from app.utils.logger import logger
from app import environment

JWT_SECRET = environment.JWT_SECRET_KEY
logger.debug(f"JWT secret configured? {'yes' if bool(JWT_SECRET) else 'no'}")
```

### Authentication Overview

We use JWT for authentication. See `app/dependencies/user_auth.py` for the implementation. you can get the current user from the request context using `get_current_user` dependency.

```python
from app.dependencies.user_auth import get_current_user

@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return user
```

## How to Add a New Feature

Follow this checklist to add a new domain/feature. Each step has a short explanation followed by a concrete snippet.

### 1) Plan the Data Model and Flow

Define entities, relationships, and queries. Decide on request/response shapes and validation rules.

### 2) Create or Modify the SQLAlchemy Model

Add a model in `app/models/<feature>.py`. Use 2.0 style queries and provide class/instance convenience methods.

```python
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.base import Base

class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    @classmethod
    async def create(cls, name: str) -> "Widget":
        transaction = get_request_transaction()
        inst = cls(name=name)
        transaction.add(inst)
        # Let middleware commit on success; flush to persist and populate PKs
        await transaction.flush()
        await transaction.refresh(inst)
        return inst

    @classmethod
    async def get_by_id(cls, widget_id: int) -> Optional["Widget"]:
        transaction = get_request_transaction()
        res = await transaction.execute(select(cls).where(cls.id == widget_id))
        return res.scalar_one_or_none()
```

Run a migration to create the table.

```bash
poetry run python manage.py migrate -m "add widgets table"
poetry run python manage.py upgrade
```

### 3) Add Pydantic Schemas

Define request/response schemas in `app/schemas/<feature>.py`. Set `from_attributes = True` for ORM compatibility.

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

### 4) Implement the Service Layer

Keep routes thin by pushing business logic into services. Services should be async, typed, and use model methods. Log major events; raise `MegapolisHTTPException` for client-facing errors.

```python
from app.utils.exceptions import MegapolisHTTPException
from app.models.widget import Widget
from app.schemas.widget import WidgetCreateRequest
from app.utils.logger import logger

async def create(payload: WidgetCreateRequest) -> Widget:
    # Uniqueness check example
    existing = await Widget.get_by_id(1)  # replace with actual check
    if existing and getattr(existing, "name", None) == payload.name:
        raise MegapolisHTTPException(status_code=400, message="Name already exists", metadata={"name": payload.name})
    logger.info("Creating widget")
    return await Widget.create(payload.name)
```

### 5) Add Routes

Create an `APIRouter` in `app/routes/<feature>.py`. Return Pydantic models. `operation_id` is the name of the operation. This is a unique identifier for the operation. It is used to generate the client code.
Using this `operation_id`, you can generate the client code using the `openapi-zod-client` package.

```python
from fastapi import APIRouter
from app.schemas.widget import WidgetCreateRequest, WidgetResponse
from app.services.widget import create_widget
from app.utils.logger import logger

router = APIRouter(prefix="/widgets", tags=["widgets"])

@router.post("/", response_model=WidgetResponse, status_code=201, operation_id="createWidget")
async def create_widget_route(payload: WidgetCreateRequest) -> WidgetResponse:
    logger.info("POST /widgets")
    widget = await create_widget(payload)
    return WidgetResponse.model_validate(widget)
```

### 6) Register the Router

Include your new router in `app/router.py`.

```python
from fastapi import APIRouter
from app.routes.widget import router as widget_router

api_router = APIRouter()
api_router.include_router(widget_router)
```

### 7) Validate, Log, and Handle Errors

Validate inputs in services where business context exists. Use `logger.info` for major events, `logger.debug` for details (avoid logging secrets), `logger.warning` for handled anomalies, and `logger.error` when raising or catching errors.

```python
from app.utils.logger import logger

logger.info("Creating widget ...")
logger.debug("Payload received for widget creation")
```

## Additional Notes

- Avoid synchronous/blocking code inside request handlers; offload CPU-bound work.
- Avoid manual commits in request handlers; the RequestTransactionMiddleware commits on success and rolls back on error. Use `await session.flush()` to emit SQL and populate primary keys, and `await session.refresh(instance)` if you need server-assigned defaults.
- One router per feature/domain; keep naming consistent and clear.
- Do not write tests unless explicitly requested.



## Code rules
- Dont use `print` in the code, use `logger.info` instead.
- Use async/await properly in the code.
- Code should be properly formatted.
- Code should have proper type annotations.
- One router per feature/domain (users, orders, products, etc.)
- Use consistent naming conventions for endpoints and parameters
- Use guard clauses to handle edge cases and invalid inputs early
- Return early from functions to reduce nesting and improve readability
- Validate inputs at the beginning of functions before processing
