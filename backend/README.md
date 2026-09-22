# Expensely Backend API

The backend for **EXPENSELY** ("Track. Understand. Save.") is built with FastAPI, SQLAlchemy ORM, and Pydantic. It provides secure JWT authentication, multi-tenant isolation, precise decimal-based financial calculations, monthly budgeting with threshold alert logic, and CSV exports.

## Features
- **JWT Authentication & Password Hashing**: Robust Bcrypt password hashing and signed JWT bearer tokens.
- **Relational Data Modeling**: SQLAlchemy models with foreign keys, cascading deletions, and uniqueness constraints.
- **Resilient Database Layer**: Configured for MySQL with PyMySQL; automatically and gracefully falls back to local SQLite if MySQL credentials are not yet supplied, ensuring immediate local execution.
- **Financial Calculation Service**: Decimal-safe computations for total balance, monthly income, expenses, savings rate, and category distributions.
- **Budgeting & Automated Alerts**: Tracks monthly budgets per category, computing status (`Under Budget`, `Near Limit` at >=80%, `Over Budget` at >=100%) and warnings.
- **Data Isolation**: Strict user-level access filters ensuring users can only read, update, or delete their own records.
- **Interactive Documentation**: Auto-generated Swagger UI (`/docs`) and ReDoc (`/redoc`).

## Setup & Running

### Windows (PowerShell / CMD)
```powershell
# Navigate to backend directory
cd expense-tracker/backend

# (Optional) Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed database with demo user & realistic multi-month data
python scripts/seed.py

# Start development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Running Tests
```powershell
python -m pytest tests -v
```

## Demo Credentials
- **Email**: `demo@expensely.com`
- **Password**: `Demo@12345`
