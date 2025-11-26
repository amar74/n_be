# Seeding Expense Categories

## Option 1: Using SQL Script (Recommended)

Run the SQL script directly in your database:

```bash
# If you have psql access
psql $DATABASE_URL -f create_expense_categories_table.sql

# Or manually execute the SQL in your database client
```

The SQL script will:
- Create the `expense_categories` table
- Insert 12 default categories (Computer, Travel, Legal, Entertainment, Recruiting, Phone, Consultants, Office Expenses, Insurance, Rent, Training, Utilities)

## Option 2: Using Python Script

After ensuring the table exists (via migration or SQL script):

```bash
poetry run python seed_expense_categories.py
```

## Option 3: Using API Endpoint

Once the API is running and you're authenticated:

```bash
curl -X POST http://localhost:8000/api/v1/expense-categories/initialize-defaults \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

## Verification

After seeding, verify categories exist:

```bash
curl http://localhost:8000/api/v1/expense-categories \
  -H "Authorization: Bearer YOUR_TOKEN"
```

You should see 12 categories returned.

## Finance Planning Integration

Once categories are seeded, they will automatically appear in:
- Finance Planning → Revenue / Expense tab (both revenue and expense sections)
- Finance Dashboard → Overhead Spend by Account Group

The categories are used for both revenue and expense planning, providing a unified category system.

