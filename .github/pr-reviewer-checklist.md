# PR Reviewer Checklist for megapolis-api

---

## 1. File Structure & Placement

- [ ] Models in `app/models/<feature>.py`, extend `Base`
    ```python
    # filepath: app/models/widget.py
    from app.db.base import Base
    class Widget(Base): ...
    ```
- [ ] Schemas in `app/schemas/<feature>.py`, use `from_attributes = True`
    ```python
    # filepath: app/schemas/widget.py
    class WidgetResponse(BaseModel):
        id: int
        name: str
        class Config:
            model_config = {"from_attributes": True}
    ```
- [ ] Services in `app/services/<feature>.py`, async functions
    ```python
    # filepath: app/services/widget.py
    async def create_widget(...): ...
    ```
- [ ] Routes in `app/routes/<feature>.py`, thin controllers
    ```python
    # filepath: app/routes/widget.py
    @router.post("/", ...)
    async def create_widget_route(...): ...
    ```
- [ ] Router registration in `app/router.py`
    ```python
    # filepath: app/router.py
    from app.routes.widget import router as widget_router
    api_router.include_router(widget_router)
    ```
- [ ] No missing required files for new features

---

## 2. Code Safety & Conventions

- [ ] Type annotations on all public functions/endpoints
    ```python
    async def create_widget(payload: WidgetCreateRequest) -> WidgetResponse:
        ...
    ```
- [ ] Async/await used end-to-end (routes, services, DB)
    ```python
    async def get_by_id(...): ...
    ```
- [ ] No blocking code in handlers
- [ ] No circular table references in models
- [ ] No raw ORM responses returned from endpoints
    ```python
    return WidgetResponse.model_validate(widget)
    ```
- [ ] No print statements; use Loguru logger
    ```python
    from app.utils.logger import logger
    logger.info("Creating widget")
    ```
- [ ] No hardcoded secrets/config; read from environment
    ```python
    from app import environment
    JWT_SECRET_KEY = environment.JWT_SECRET_KEY
    ```
- [ ] No relative imports; use absolute imports
- [ ] No function should return untyped dict or list
    ```python
    return {"id": widget.id, "name": widget.name}  # ❌
    return WidgetResponse.model_validate(widget)  # ✅
    ```
- [ ] No function should return untyped dict or list. Use Pydantic models or typed collections or dataclasses.
** NOTE: This is the most commonly missed item. So you need to look carefully at the return types of the functions which are getting added **
    ```python
    async def get_widgets_service_func(...) -> List[Dict[Any]]:  # ❌
        ...
    async def get_widgets_service_func(...) -> List[WidgetResponse]:  # ✅
        ...
    ```

---

## 3. API & Business Logic

- [ ] Thin endpoints: Routes only validate and call services
- [ ] Service functions are small, async, functional
- [ ] Guard clauses and early returns
    ```python
    if not payload.name:
        raise MegapolisHTTPException(status_code=400, message="Name required")
    ```
- [ ] Input validation performed upfront
- [ ] Errors raised as MegapolisHTTPException
    ```python
    from app.utils.exceptions import MegapolisHTTPException
    raise MegapolisHTTPException(status_code=400, message="Name exists")
    ```
- [ ] Logging at key events (never log secrets/tokens)
- [ ] Consistent naming for endpoints, params, models
- [ ] One router per domain
- [ ] Functional API code; avoid side effects in API layer
- [ ] OOP used for models, schemas, orchestration as needed

- [ ] Every endpoint must specify a unique `operation_id` (required for frontend type generation)
    ```python
    @router.post("/widgets", response_model=WidgetResponse, operation_id="createWidget")
    async def create_widget_route(...): ...
    ```

---

## 4. Authentication & Authorization

- [ ] JWT auth via get_current_user dependency
    ```python
    from app.dependencies.user_auth import get_current_user
    @router.get("/me")
    async def get_me(user = Depends(get_current_user)):
        return user
    ```

---

## 5. Database & Migrations

- [ ] DB access only via get_request_transaction()
    ```python
    from app.db.session import get_request_transaction
    db = get_request_transaction()
    ```
- [ ] Alembic migrations generated/applied for model changes
- [ ] No circular references in table relationships
- [ ] Transactional integrity: errors roll back transactions

---

## 6. Environment & Configuration

- [ ] Environment variables via from app import environment
    ```python
    from app import environment
    DATABASE_URL = environment.DATABASE_URL
    ```
- [ ] No hardcoded sensitive values

---

## 7. General Best Practices

- [ ] PEP 8 formatting and consistent style
- [ ] Small, reusable functions
- [ ] Limit function arguments; use Pydantic models if >3–4 args
- [ ] No unrelated reformatting in PRs
- [ ] No tests unless explicitly requested

---

## 8. Python Best Practices

- [ ] Type annotations everywhere
- [ ] Consistent, idiomatic formatting
- [ ] Decompose complex logic
- [ ] Read from environment
- [ ] Return early
- [ ] Separate API vs core
- [ ] Functional API code
- [ ] OOP for non-API code
- [ ] Limit function arguments
- [ ] Use async/await across I/O
- [ ] Avoid relative imports

---

**Use this checklist for every PR review. If any item fails, add a comment with the relevant snippet and suggest a fix.**
