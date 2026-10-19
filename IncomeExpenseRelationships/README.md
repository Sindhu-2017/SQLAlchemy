# IncomeManagement: SQLAlchemy Relationships and Joins

This companion project uses the same `income` columns and four sample income rows from the uploaded project, and adds an `expenses` table.

## Relationship design
- One `Income` has many `Expense` records (`Income.expenses`).
- Each `Expense` belongs to one `Income` (`Expense.income`).
- `expenses.income_id` is a foreign key to `income.income_id`.
- `back_populates` synchronizes the two ORM relationship attributes.
- `selectinload()` demonstrates relationship loading without an N+1 query.
- `/api/income/join` demonstrates INNER JOIN.
- `/api/income/left-join` demonstrates LEFT OUTER JOIN.

## Setup
1. Create/activate a virtual environment.
2. `pip install -r requirements.txt`
3. Create a PostgreSQL database and copy `.env.example` to `.env`; fill in credentials.
4. If the original database already contains the income table and data, keep using it. `Base.metadata.create_all()` creates the new `expenses` table without dropping existing tables or rows.
5. If setting up a fresh database, first create the `income` table using your original `sql/income_db.sql` (use only its `CREATE TABLE income` portion if you don't want its stored procedure), then run `seed_income.sql` once. Do not run the seed file if income rows already exist.
6. Run `uvicorn main:app --reload`
7. Open `http://127.0.0.1:8000/docs`.

## Endpoints
- `GET /api/income/` — incomes with nested expenses, using `selectinload`.
- `GET /api/income/{income_id}` — one income with its expenses.
- `POST /api/expenses/` — create an expense and update that income's expense total and cash in hand.
- `GET /api/income/join` — INNER JOIN (only income rows that have expenses).
- `GET /api/income/left-join` — LEFT OUTER JOIN (includes incomes with no expenses; expense columns are null).

## Example expense request
```json
{
  "income_id": 1,
  "expense_date": "2026-10-17",
  "category": "Travel",
  "amount": "750.00",
  "description": "Bus and train"
}
```

Note: `expense_amount` in the original income table was a single manually tracked amount. In this version it is maintained as the sum of individual rows in `expenses`. If your existing rows already have expense totals, creating the new `expenses` table does not automatically split those old totals into expense records. Add individual expense rows only for the amounts you want itemized, otherwise totals could be counted twice.
