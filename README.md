# Megapolis API

FastAPI + SQLAlchemy (async) + Alembic + Poetry + Docker Compose.

## Contents
- Stack overview
- Requirements
- Project layout
- Configuration (env vars)
- Local development (without Docker)
- Database & migrations (Alembic)
- Docker Compose (API + Postgres)
- Management CLI (`manage.py`)
- API quick test
- Architecture & Development Guidelines
- Troubleshooting

## Stack overview
- FastAPI (web framework)
- SQLAlchemy 2.x (async engine + async sessions)
- Alembic (database migrations, async-aware env)
- PostgreSQL (database)
- Uvicorn (ASGI server)
- Poetry (dependency & runtime management)

## Requirements
- Python 3.10+
- Poetry 2.x (`poetry --version`)
- Optional for containers: Docker + Docker Compose

## Project layout
```
megapolis-api/
├─ app/
│  ├─ main.py                  # FastAPI app entry point
│  ├─ router.py                # Central router combining all routes
│  ├─ db/
│  │  ├─ base.py               # Declarative Base
│  │  └─ session.py            # Async engine/session factory
│  ├─ models/
│  │  ├─ __init__.py
│  │  └─ user.py               # Database models (SQLAlchemy)
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  └─ user.py               # Pydantic models for API validation
│  ├─ services/
│  │  ├─ __init__.py
│  │  └─ user.py               # Business logic layer
│  ├─ routes/
│  │  ├─ __init__.py
│  │  └─ user.py               # API controllers/endpoints
│  └─ middlewares/
│     └─ __init__.py           # Custom middleware components
├─ alembic/
│  ├─ env.py                   # Alembic config (async engine, imports models)
│  ├─ script.py.mako           # Migration template
│  └─ versions/                # Generated migration files
├─ alembic.ini                 # Alembic settings (overridden by env var at runtime)
├─ docker-compose.yml          # API + Postgres services
├─ Dockerfile                  # API image (Poetry install + Uvicorn entry)
├─ manage.py                   # Typer-based mgmt CLI: run, migrate, upgrade, etc.
├─ pyproject.toml              # Poetry project & deps
└─ README.md                   # This file
```

## Configuration
Set the database URL via the `DATABASE_URL` environment variable. Defaults are provided for Docker.

- Format: `postgresql+asyncpg://<user>:<password>@<host>:<port>/<db>`
- Examples:
  - Local: `postgresql+asyncpg://postgres:postgres@localhost:5432/megapolis`
  - Docker network: `postgresql+asyncpg://postgres:postgres@db:5432/megapolis`

Note: `.env` loading is not wired by default; export env vars in your shell or set them in Compose.

## Local development (without Docker)
1) Install deps
```bash
poetry lock
poetry install --no-root
```

2) Ensure Postgres is running and reachable at your `DATABASE_URL` (create database if needed):
```bash
createdb megapolis   # if you have local Postgres and want this DB name
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/megapolis
```

3) Run the API (hot reload on by default):
```bash
poetry run python manage.py run
```
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Database & migrations (Alembic)
Alembic is configured for the async engine. The `alembic/env.py` imports `app.models` so autogenerate sees your models.

- Create a new migration (autogenerate):
```bash
poetry run python manage.py migrate -m "add_user_table"
```

- Apply migrations:
```bash
poetry run python manage.py upgrade
```

- Downgrade migrations:
```bash
poetry run python manage.py downgrade -1
```

Tips:
- If autogenerate creates an empty revision, ensure your models are imported (see `alembic/env.py`) and tables inherit from `app.db.base.Base`.
- For new apps, the first migration is typically `init` or `base`.

## Docker Compose (API + Postgres)
Bring up Postgres and API together:
```bash
docker compose up -d --build
```
- API: http://localhost:8000
- DB: host `db`, port `5432` inside the Compose network

Run migrations inside the API container:
```bash
docker compose exec api alembic revision --autogenerate -m "init"
docker compose exec api alembic upgrade head
# or via the CLI
docker compose exec api python manage.py migrate -m "init"
docker compose exec api python manage.py upgrade
```

Stop and clean up:
```bash
docker compose down -v
```

## Management CLI (`manage.py`)
All commands accept `DATABASE_URL` from the environment. Defaults are reasonable for local dev.

- Run server:
```bash
poetry run python manage.py run --host 127.0.0.1 --port 8000 --reload
```

- Generate migration (autogenerate):
```bash
poetry run python manage.py migrate -m "your_message"
```

- Upgrade / Downgrade:
```bash
poetry run python.manage.py upgrade        # to head
poetry run python.manage.py downgrade -1   # step back one
```

- Initialize DB to latest:
```bash
poetry run python manage.py initdb
```

## API quick test
- Simple Hello World endpoint (already included):
```bash
curl http://127.0.0.1:8000/
# {"message": "Hello, world!"}
```

## SQLAlchemy usage (async)
Use the provided async session factory in `app/db/session.py`.

Example pattern inside your endpoints or services:
```python
from app.db.session import get_session

@app.get("/users")
async def list_users():
    async with get_session() as session:
        result = await session.execute(select(User))
        return [u for u in result.scalars().all()]
```

## Architecture & Development Guidelines

### Directory Structure & Responsibilities

#### **`models/` - Database Models**
- Contains SQLAlchemy models representing database tables
- Each model should include basic CRUD operations as class/instance methods
- Example: `User.create()`, `User.get_by_id()`, `User.update()`, `User.delete()`

#### **`schemas/` - Pydantic Models**
- API request/response validation and serialization
- Separate schemas for create, update, and response operations
- Example: `UserCreateRequest`, `UserUpdateRequest`, `UserResponse`

#### **`services/` - Business Logic**
- Contains business logic and complex operations
- Keeps routes/controllers thin and focused
- Handles validation, error handling, and cross-cutting concerns
- Example: `UserService.create_user()` with email validation

#### **`routes/` - Controllers/Endpoints**
- HTTP request handlers (controllers)
- Should be kept minimal - delegate to services
- Each route file should export an APIRouter
- Example pattern:
```python
@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> UserResponse:
    user = await UserService.create_user(session, user_data)
    return UserResponse.model_validate(user)
```

#### **`router.py` - Central Router**
- Combines all route modules into a single API router
- Provides versioning (e.g., `/api/v1/`)
- Single place to manage all API routes

#### **`middlewares/` - Custom Middleware**
- Custom middleware components (CORS, authentication, logging, etc.)
- Reusable middleware functions
- Applied globally or to specific route groups

### Development Workflow

1. **Adding New Endpoints**:
   - Create/update model in `models/`
   - Define schemas in `schemas/`
   - Implement business logic in `services/`
   - Create route handlers in `routes/`
   - Register router in `router.py`

2. **API Endpoints Structure**:
   - All API endpoints are prefixed with `/api/v1/`
   - User endpoints: `/api/v1/users/`
   - Future endpoints: `/api/v1/posts/`, `/api/v1/auth/`, etc.

3. **Error Handling**:
   - Business logic validation in services layer
   - HTTP exceptions raised from services
   - Consistent error responses across the API

## Troubleshooting
- Docker not found: install Docker Desktop or engine + compose plugin.
- Alembic autogenerate empty: ensure models are imported (see `alembic/env.py`) and your models subclass `Base`.
- Cannot connect to DB: verify `DATABASE_URL`, network access, and that the DB exists.
- IDE reports unresolved imports (e.g. SQLAlchemy): select the Poetry virtualenv as your interpreter or run `poetry install`.

## License
MIT (or your preferred license).
