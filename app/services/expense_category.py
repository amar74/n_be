from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.expense_category import ExpenseCategory
from app.schemas.finance import ExpenseCategoryCreate, ExpenseCategoryUpdate


DEFAULT_EXPENSE_CATEGORIES = [
    {"name": "Computer", "description": "Computer equipment and software", "is_default": True, "category_type": "expense"},
    {"name": "Travel", "description": "Business travel expenses", "is_default": True, "category_type": "expense"},
    {"name": "Legal", "description": "Legal services and fees", "is_default": True, "category_type": "expense"},
    {"name": "Entertainment", "description": "Client entertainment expenses", "is_default": True, "category_type": "expense"},
    {"name": "Recruiting", "description": "Recruiting and hiring expenses", "is_default": True, "category_type": "expense"},
    {"name": "Phone", "description": "Telecommunications expenses", "is_default": True, "category_type": "expense"},
    {"name": "Consultants", "description": "Consultant and contractor fees", "is_default": True, "category_type": "expense"},
    {"name": "Office Expenses", "description": "General office expenses", "is_default": True, "category_type": "expense"},
    {"name": "Insurance", "description": "Insurance premiums", "is_default": True, "category_type": "expense"},
    {"name": "Rent", "description": "Office rent and facilities", "is_default": True, "category_type": "expense"},
    {"name": "Training", "description": "Training and development expenses", "is_default": True, "category_type": "expense"},
    {"name": "Utilities", "description": "Utility bills and services", "is_default": True, "category_type": "expense"},
]

DEFAULT_REVENUE_CATEGORIES = [
    {"name": "Professional Services", "description": "Professional services revenue", "is_default": True, "category_type": "revenue"},
    {"name": "Consulting Services", "description": "Consulting services revenue", "is_default": True, "category_type": "revenue"},
    {"name": "Retainer Agreements", "description": "Retainer and recurring revenue", "is_default": True, "category_type": "revenue"},
    {"name": "Managed Services", "description": "Managed services revenue", "is_default": True, "category_type": "revenue"},
    {"name": "Project-Based Revenue", "description": "Project-based revenue", "is_default": True, "category_type": "revenue"},
    {"name": "Training & Workshops", "description": "Training and workshop revenue", "is_default": True, "category_type": "revenue"},
    {"name": "Software Licensing", "description": "Software licensing revenue", "is_default": True, "category_type": "revenue"},
]


class ExpenseCategoryService:
    @staticmethod
    async def get_all(
        db: AsyncSession,
        include_inactive: bool = False,
        include_subcategories: bool = True,
        category_type: Optional[str] = None,
    ) -> List[ExpenseCategory]:
        if include_subcategories:
            query = select(ExpenseCategory)
            
            if not include_inactive:
                query = query.where(ExpenseCategory.is_active == True)
            
            if category_type:
                query = query.where(ExpenseCategory.category_type == category_type)
            
            query = query.order_by(ExpenseCategory.display_order, ExpenseCategory.name)
            query = query.options(selectinload(ExpenseCategory.subcategories))
            
            result = await db.execute(query)
            all_categories = list(result.scalars().all())
            
            # Return all categories (both top-level and subcategories) so frontend can filter them
            return all_categories
        else:
            query = select(ExpenseCategory)
            
            if not include_inactive:
                query = query.where(ExpenseCategory.is_active == True)
            
            if category_type:
                query = query.where(ExpenseCategory.category_type == category_type)
            
            query = query.where(ExpenseCategory.parent_id == None)
            query = query.order_by(ExpenseCategory.display_order, ExpenseCategory.name)
            # Load subcategories relationship even if we're filtering them out, to avoid lazy load issues
            query = query.options(selectinload(ExpenseCategory.subcategories))
            
            result = await db.execute(query)
            categories = list(result.scalars().all())
            
            # Set subcategories to empty list for each category since include_subcategories=False
            for cat in categories:
                cat.subcategories = []
            
            return categories

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        category_id: int,
        include_subcategories: bool = True,
    ) -> Optional[ExpenseCategory]:
        query = select(ExpenseCategory).where(ExpenseCategory.id == category_id)
        
        if include_subcategories:
            query = query.options(selectinload(ExpenseCategory.subcategories))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_categories_for_overhead(db: AsyncSession) -> List[ExpenseCategory]:
        query = select(ExpenseCategory).where(
            ExpenseCategory.is_active == True,
            ExpenseCategory.category_type == 'expense'
        )
        query = query.options(selectinload(ExpenseCategory.subcategories))
        query = query.order_by(ExpenseCategory.display_order, ExpenseCategory.name)
        
        result = await db.execute(query)
        categories = list(result.scalars().all())
        
        flat_list = []
        for cat in categories:
            flat_list.append(cat)
            if cat.subcategories:
                flat_list.extend([sub for sub in cat.subcategories if sub.is_active and sub.category_type == 'expense'])
        
        return flat_list

    @staticmethod
    async def create(
        db: AsyncSession,
        category_data: ExpenseCategoryCreate,
    ) -> ExpenseCategory:
        if category_data.parent_id:
            parent = await ExpenseCategoryService.get_by_id(db, category_data.parent_id, include_subcategories=False)
            if not parent:
                raise ValueError(f"Parent category with ID {category_data.parent_id} not found")
        
        category = ExpenseCategory(
            name=category_data.name,
            description=category_data.description,
            parent_id=category_data.parent_id,
            is_active=category_data.is_active,
            display_order=category_data.display_order,
            is_default=False,
            category_type=category_data.category_type,
        )
        
        db.add(category)
        await db.flush()
        await db.refresh(category)
        # Note: subcategories will be empty for new categories, so we don't need to load them
        return category

    @staticmethod
    async def update(
        db: AsyncSession,
        category_id: int,
        category_data: ExpenseCategoryUpdate,
    ) -> Optional[ExpenseCategory]:
        category = await ExpenseCategoryService.get_by_id(db, category_id, include_subcategories=False)
        if not category:
            return None
        
        if category_data.parent_id is not None:
            if category_data.parent_id == category_id:
                raise ValueError("Category cannot be its own parent")
            parent = await ExpenseCategoryService.get_by_id(db, category_data.parent_id, include_subcategories=False)
            if not parent:
                raise ValueError(f"Parent category with ID {category_data.parent_id} not found")
        
        if category_data.name is not None:
            category.name = category_data.name
        if category_data.description is not None:
            category.description = category_data.description
        if category_data.parent_id is not None:
            category.parent_id = category_data.parent_id
        if category_data.is_active is not None:
            category.is_active = category_data.is_active
        if category_data.display_order is not None:
            category.display_order = category_data.display_order
        if category_data.category_type is not None:
            category.category_type = category_data.category_type
        
        await db.flush()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete(db: AsyncSession, category_id: int) -> bool:
        from sqlalchemy import select
        from app.models.finance_planning import FinanceRevenueLine, FinanceExpenseLine, FinanceAnnualBudget
        
        category = await ExpenseCategoryService.get_by_id(db, category_id, include_subcategories=False)
        if not category:
            return False
        
        if category.is_default:
            raise ValueError("Cannot delete default categories")
        
        # Check if category has subcategories
        subcategories = await ExpenseCategoryService.get_all(
            db, 
            include_inactive=True, 
            include_subcategories=False
        )
        has_subcategories = any(cat.parent_id == category_id for cat in (subcategories or []))
        if has_subcategories:
            raise ValueError("Cannot delete category with subcategories. Please delete or move subcategories first.")
        
        # Transfer values to "Other" category if category has budget values
        category_name = category.name
        category_type = category.category_type
        
        # Find or create "Other" category
        other_category_name = "Other Revenue" if category_type == "revenue" else "Other Expense"
        # First try to find an active "Other" category
        other_category_result = await db.execute(
            select(ExpenseCategory).where(
                ExpenseCategory.name == other_category_name,
                ExpenseCategory.category_type == category_type,
                ExpenseCategory.is_active == True
            ).order_by(ExpenseCategory.id).limit(1)
        )
        other_category = other_category_result.scalar_one_or_none()
        
        # If no active "Other" category, try to find any "Other" category
        if not other_category:
            other_category_result = await db.execute(
                select(ExpenseCategory).where(
                    ExpenseCategory.name == other_category_name,
                    ExpenseCategory.category_type == category_type
                ).order_by(ExpenseCategory.id).limit(1)
            )
            other_category = other_category_result.scalar_one_or_none()
        
        if not other_category:
            # Create "Other" category if it doesn't exist
            other_category = ExpenseCategory(
                name=other_category_name,
                description=f"Other {category_type} items",
                parent_id=None,
                is_active=True,
                display_order=9999,
                is_default=False,
                category_type=category_type,
            )
            db.add(other_category)
            await db.flush()
        elif not other_category.is_active:
            # Reactivate the "Other" category if it exists but is inactive
            other_category.is_active = True
            await db.flush()
        
        # Find all budgets with this category (if any exist)
        try:
            all_budgets_result = await db.execute(select(FinanceAnnualBudget))
            all_budgets = all_budgets_result.scalars().all() or []
        except Exception:
            # If no budgets table exists or error, just skip value transfer
            all_budgets = []
        
        for budget in all_budgets:
            if category_type == "revenue":
                # Find revenue lines with this category name
                revenue_lines_result = await db.execute(
                    select(FinanceRevenueLine).where(
                        FinanceRevenueLine.budget_id == budget.id,
                        FinanceRevenueLine.label == category_name
                    )
                )
                revenue_lines = revenue_lines_result.scalars().all()
                
                for line in revenue_lines:
                    # Find or create "Other Revenue" line for this budget
                    other_line_result = await db.execute(
                        select(FinanceRevenueLine).where(
                            FinanceRevenueLine.budget_id == budget.id,
                            FinanceRevenueLine.label == other_category_name
                        ).order_by(FinanceRevenueLine.id).limit(1)
                    )
                    other_line = other_line_result.scalar_one_or_none()
                    
                    if other_line:
                        # Transfer values to existing "Other Revenue" line
                        other_line.target += line.target
                        other_line.variance += line.variance
                    else:
                        # Create new "Other Revenue" line
                        other_line = FinanceRevenueLine(
                            budget_id=budget.id,
                            label=other_category_name,
                            target=line.target,
                            variance=line.variance,
                            display_order=9999,
                        )
                        db.add(other_line)
                    
                    # Delete the old line
                    await db.delete(line)
            else:
                # Find expense lines with this category name
                expense_lines_result = await db.execute(
                    select(FinanceExpenseLine).where(
                        FinanceExpenseLine.budget_id == budget.id,
                        FinanceExpenseLine.label == category_name
                    )
                )
                expense_lines = expense_lines_result.scalars().all()
                
                for line in expense_lines:
                    # Find or create "Other Expense" line for this budget
                    other_line_result = await db.execute(
                        select(FinanceExpenseLine).where(
                            FinanceExpenseLine.budget_id == budget.id,
                            FinanceExpenseLine.label == other_category_name
                        ).order_by(FinanceExpenseLine.id).limit(1)
                    )
                    other_line = other_line_result.scalar_one_or_none()
                    
                    if other_line:
                        # Transfer values to existing "Other Expense" line
                        other_line.target += line.target
                        other_line.variance += line.variance
                    else:
                        # Create new "Other Expense" line
                        other_line = FinanceExpenseLine(
                            budget_id=budget.id,
                            label=other_category_name,
                            target=line.target,
                            variance=line.variance,
                            display_order=9999,
                        )
                        db.add(other_line)
                    
                    # Delete the old line
                    await db.delete(line)
        
        # Now delete the category
        await db.delete(category)
        await db.flush()
        return True

    @staticmethod
    async def initialize_default_categories(db: AsyncSession, category_type: Optional[str] = None) -> List[ExpenseCategory]:
        created = []
        
        categories_to_create = []
        if category_type == "revenue":
            categories_to_create = DEFAULT_REVENUE_CATEGORIES
        elif category_type == "expense":
            categories_to_create = DEFAULT_EXPENSE_CATEGORIES
        else:
            categories_to_create = DEFAULT_EXPENSE_CATEGORIES + DEFAULT_REVENUE_CATEGORIES
        
        for default_cat in categories_to_create:
            existing_query = select(ExpenseCategory).where(
                ExpenseCategory.name == default_cat["name"],
                ExpenseCategory.is_default == True,
                ExpenseCategory.category_type == default_cat.get("category_type", "expense")
            )
            existing_result = await db.execute(existing_query)
            if existing_result.scalar_one_or_none():
                continue
            
            category = ExpenseCategory(
                name=default_cat["name"],
                description=default_cat.get("description", ""),
                is_default=True,
                is_active=True,
                display_order=len(created),
                category_type=default_cat.get("category_type", "expense"),
            )
            db.add(category)
            created.append(category)
        
        if created:
            await db.flush()
        
        return created