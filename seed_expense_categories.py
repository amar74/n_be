"""
Seed expense categories into the database.
Run this script to initialize default expense categories.
First ensure the expense_categories table exists by running the migration or SQL script.
"""
import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.db.session import get_session
from app.services.expense_category import ExpenseCategoryService


async def seed_expense_categories():
    """Seed default expense categories into the database."""
    print("🌱 Starting expense category seeding...")
    
    try:
        async with get_session() as db:
            # Try to check if categories exist, but handle table not existing
            try:
                existing_categories = await ExpenseCategoryService.get_all(
                    db, include_inactive=True, include_subcategories=False
                )
                
                if existing_categories:
                    print(f"✅ Found {len(existing_categories)} existing categories.")
                    print("Categories already exist. Skipping seed.")
                    for cat in existing_categories:
                        print(f"   - {cat.name} (ID: {cat.id}, Active: {cat.is_active}, Default: {cat.is_default})")
                    return
            except Exception as e:
                if "does not exist" in str(e) or "UndefinedTable" in str(e):
                    print("⚠️  expense_categories table does not exist.")
                    print("Please run the migration or SQL script first:")
                    print("   - Run: poetry run python manage.py upgrade")
                    print("   - Or execute: create_expense_categories_table.sql")
                    return
                raise
            
            # Initialize default categories
            print("📦 Creating default expense categories...")
            created_categories = await ExpenseCategoryService.initialize_default_categories(db)
            
            await db.commit()
            
            print(f"✅ Successfully created {len(created_categories)} expense categories:")
            for cat in created_categories:
                print(f"   - {cat.name} (ID: {cat.id})")
            
            print("\n🎉 Expense category seeding completed successfully!")
            
    except Exception as e:
        print(f"❌ Error seeding expense categories: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(seed_expense_categories())
