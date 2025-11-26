from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_request_transaction
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.schemas.finance import (
    ExpenseCategoryCreate,
    ExpenseCategoryUpdate,
    ExpenseCategoryResponse,
)
from app.services.expense_category import ExpenseCategoryService
from app.models.expense_category import ExpenseCategory

router = APIRouter(prefix="/v1/expense-categories", tags=["expense-categories"])


@router.get("", response_model=List[ExpenseCategoryResponse])
async def get_expense_categories(
    include_inactive: bool = Query(False, description="Include inactive categories"),
    include_subcategories: bool = Query(True, description="Include subcategories"),
    category_type: Optional[str] = Query(None, description="Filter by category type: 'revenue' or 'expense'"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
) -> List[ExpenseCategoryResponse]:
    categories = await ExpenseCategoryService.get_all(
        db, 
        include_inactive=include_inactive, 
        include_subcategories=include_subcategories,
        category_type=category_type
    )
    return [ExpenseCategoryResponse.model_validate(cat) for cat in categories]


@router.get("/{category_id}", response_model=ExpenseCategoryResponse)
async def get_expense_category(
    category_id: int,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
) -> ExpenseCategoryResponse:
    category = await ExpenseCategoryService.get_by_id(db, category_id, include_subcategories=True)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return ExpenseCategoryResponse.model_validate(category)


@router.post("", response_model=ExpenseCategoryResponse, status_code=201)
async def create_expense_category(
    category_data: ExpenseCategoryCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"finance": ["edit"]})),
) -> ExpenseCategoryResponse:
    try:
        category = await ExpenseCategoryService.create(db, category_data)
        # Convert to response - explicitly set subcategories to empty list to avoid async loading issues
        # The subcategories will be loaded when needed (e.g., in GET requests)
        response_data = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "parent_id": category.parent_id,
            "is_active": category.is_active,
            "display_order": category.display_order,
            "is_default": category.is_default,
            "category_type": category.category_type,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
            "subcategories": []  # Empty list for new categories (no subcategories yet)
        }
        return ExpenseCategoryResponse.model_validate(response_data)
    except ValueError as e:
        # Don't rollback manually - let the middleware handle it via exception
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions without wrapping
        raise
    except Exception as e:
        # Don't rollback manually - let the middleware handle it via exception
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{category_id}", response_model=ExpenseCategoryResponse)
async def update_expense_category(
    category_id: int,
    category_data: ExpenseCategoryUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"finance": ["edit"]})),
) -> ExpenseCategoryResponse:
    try:
        category = await ExpenseCategoryService.update(db, category_id, category_data)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        # Convert to response - explicitly set subcategories to empty list to avoid async loading issues
        # Subcategories will be loaded when needed (e.g., in GET requests with include_subcategories=True)
        response_data = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "parent_id": category.parent_id,
            "is_active": category.is_active,
            "display_order": category.display_order,
            "is_default": category.is_default,
            "category_type": category.category_type,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
            "subcategories": []  # Empty list to avoid async loading issues during Pydantic validation
        }
        return ExpenseCategoryResponse.model_validate(response_data)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", status_code=204)
async def delete_expense_category(
    category_id: int,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"finance": ["edit"]})),
):
    import traceback
    try:
        success = await ExpenseCategoryService.delete(db, category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
        # Service method already calls flush(), middleware handles commit
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the full error for debugging
        error_trace = traceback.format_exc()
        print(f"Error deleting category {category_id}: {str(e)}\n{error_trace}")
        # Catch any other exceptions and provide better error message
        raise HTTPException(status_code=500, detail=f"Failed to delete category: {str(e)}")


@router.post("/initialize-defaults", response_model=List[ExpenseCategoryResponse])
async def initialize_default_categories(
    category_type: Optional[str] = Query(None, description="Initialize categories for type: 'revenue' or 'expense'. If not provided, initializes both."),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"finance": ["edit"]})),
) -> List[ExpenseCategoryResponse]:
    categories = await ExpenseCategoryService.initialize_default_categories(db, category_type=category_type)
    # Service method already calls flush(), middleware handles commit
    return [ExpenseCategoryResponse.model_validate(cat) for cat in categories]

