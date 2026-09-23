# EXPENSELY — Track. Understand. Save. 💳
### Full-Stack Personal Financial Analytics & Budgeting Platform

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-expensely--frontend.onrender.com-00C7B7?style=for-the-badge&logo=render&logoColor=white)](https://expensely-frontend.onrender.com)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/kritika7268/expense-tracker)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://expensely-backend-0s6w.onrender.com/docs)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![MySQL](https://img.shields.io/badge/Database-MySQL_%7C_SQLite-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com)

> 🌐 **Live Application:** **[https://expensely-frontend.onrender.com](https://expensely-frontend.onrender.com)**  
> 📡 **Live Backend API & Health Check:** **[https://expensely-backend-0s6w.onrender.com/health](https://expensely-backend-0s6w.onrender.com/health)**  
> 📖 **API Documentation (Swagger UI):** **[https://expensely-backend-0s6w.onrender.com/docs](https://expensely-backend-0s6w.onrender.com/docs)**  
> 🔑 **Pre-Seeded Demo Account:** `demo@expensely.com` &nbsp;|&nbsp; Password: `Demo@12345`

*Note: Hosted on Render's free tier. If the backend is inactive, please allow 30–45 seconds for container wake-up on the first request.*

---

## 📌 Problem Statement
Personal financial tracking is commonly hindered by two extremes: rigid, manual spreadsheets with zero automation, or complex commercial banking apps that compromise user privacy. Furthermore, many hobbyist finance apps suffer from floating-point accumulation errors, poor data isolation between users, and an absence of proactive budget guardrails before overspending occurs.

## 💡 Solution
**Expensely** is a production-grade personal finance platform engineered with software engineering rigor:
- **Exact Decimal Arithmetic:** Employs `Numeric(12, 2)` SQL columns and Python `Decimal` data structures, guaranteeing zero binary floating-point drift.
- **Multi-Tenant Security:** Restricts all database transactions, budget ceilings, and categories to the authenticated JWT tenant.
- **Budget Threshold Alerts:** Monitors monthly category spending and generates automated alert banners at 80% (`Near Limit`) and 100% (`Over Budget`).
- **Interactive Visual Intelligence:** Delivers monthly cash-flow trends, spending breakdowns, and payment-method distributions via Recharts.
- **Data Portability:** Provides structured CSV export capabilities for personal tax and accounting records.

---

## ✨ Features

### 1. Authentication & Multi-Tenant Security
- **JWT Bearer Authentication:** Secure registration and login using passlib bcrypt hashing and signed JSON Web Tokens.
- **Database-Level Isolation:** Every query explicitly enforces `user_id == current_user.id`, preventing cross-account data leakage.

### 2. Transaction Management & Ledger
- **Full CRUD Support:** Add, update, view, and delete income and expense records.
- **Granular Query Filtering:** Server-side filtering by category, payment method (Cash, UPI, Debit Card, Credit Card, Bank Transfer), date range, and text search.
- **Server-Side Pagination:** Efficient paginated ledger supporting custom limit and page parameters.

### 3. Proactive Budget Guardrails
- **Category Caps:** Set specific monthly spending caps for custom categories.
- **Real-Time Progress Tracking:** Visual consumption bars with dynamic status badges: `Under Budget`, `Near Limit` (≥80%), and `Over Budget` (≥100%).
- **Dashboard Alerts:** Automated notification banners warning users when categories approach or exceed thresholds.

### 4. Interactive Financial Analytics
- **Cash Flow Trends:** Monthly income vs. expense bar charts powered by Recharts.
- **Category Breakdown:** Donut charts illustrating proportional expenditure distributions.
- **Payment Method Distribution:** Visual breakdown of spending channels (UPI, cards, cash).

### 5. Data Portability & Customization
- **CSV Data Export:** Generate downloadable, formatted financial statements with one click.
- **Category Management:** Pre-seeded categories plus custom categories with relational delete protection.
- **Theme & Personalization:** Dark/light mode toggle persisted to local storage and multi-currency formatting (`₹`, `$`, `€`, `£`).

---

## 📸 Screenshots

| Interactive Financial Dashboard | Visual Analytics & Cash Flow Trends |
|:---:|:---:|
| *(Capture from `http://localhost:5173/dashboard`)* | *(Capture from `http://localhost:5173/analytics`)* |

| Transaction Ledger & Filter Bar | Budget Guardrails & Threshold Warnings |
|:---:|:---:|
| *(Capture from `http://localhost:5173/transactions`)* | *(Capture from `http://localhost:5173/budgets`)* |

> 📁 *Recommended screenshot folder:* Place captured PNG files in `screenshots/` (e.g., `screenshots/dashboard.png`, `screenshots/analytics.png`, `screenshots/transactions.png`, `screenshots/budgets.png`).

---

## 🚀 Live Demo

- **Live Frontend:** [https://expensely-frontend.onrender.com](https://expensely-frontend.onrender.com)
- **Swagger API Docs:** [https://expensely-backend-0s6w.onrender.com/docs](https://expensely-backend-0s6w.onrender.com/docs)
- **Demo Account:** `demo@expensely.com` / `Demo@12345`

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Client ["Frontend Layer (React 18 + Vite + Tailwind CSS)"]
        Landing[Landing Page]
        AuthUI[Login / Register / JWT Context]
        Dash[Dashboard & Summary Cards]
        TxTable[Transactions Ledger & Filters]
        Charts[Recharts Analytics Visualizer]
        BudgetUI[Budget Guardrails & Alert Banners]
        AxiosClient[Axios Interceptors / Bearer Injection]
    end

    subgraph Server ["Backend Layer (FastAPI on Render)"]
        API[FastAPI Gateway / CORS Middleware]
        AuthDep[JWT Verification Dependency get_current_user]
        TxRouter[Transactions Router]
        BudgetRouter[Budgets & Threshold Engine]
        AnalyticsRouter[Analytics Aggregator]
        ExportService[CSV Generation Service]
        DBSession[SQLAlchemy SessionLocal]
    end

    subgraph Storage ["Database Layer (MySQL / SQLite Fallback)"]
        MySQL[(MySQL 8.0 Primary)]
        SQLite[(SQLite Failover expense_tracker.db)]
    end

    AuthUI --> AxiosClient
    Dash --> AxiosClient
    TxTable --> AxiosClient
    Charts --> AxiosClient
    BudgetUI --> AxiosClient

    AxiosClient -- "HTTP + Authorization: Bearer <token>" --> API
    API --> AuthDep
    AuthDep --> TxRouter
    AuthDep --> BudgetRouter
    AuthDep --> AnalyticsRouter

    TxRouter --> DBSession
    BudgetRouter --> DBSession
    AnalyticsRouter --> DBSession
    TxRouter --> ExportService

    DBSession -- "Pool Ping" --> MySQL
    MySQL -. "Fallback on Connection Error" .-> SQLite
```

---

## 🔄 How It Works (Request Flow)
1. **Authentication Flow:** User submits credentials → `POST /api/auth/login` verifies bcrypt hash → Returns signed JWT bearer token → React stores token in `localStorage` and sets default Axios authorization header.
2. **Ledger Query Flow:** User navigates to Transactions → Axios executes `GET /api/transactions?page=1&limit=10&category_id=2` → Backend dependency extracts `user_id` from token → SQLAlchemy executes filtered query with joined category details → Response returns paginated JSON metadata + records.
3. **Budget Evaluation Flow:** User opens Budgets or Dashboard → `GET /api/budgets/progress` runs an aggregation query summing current month expenses per category → Compares total against monthly budget cap → Evaluates threshold (`>= 80%` or `>= 100%`) → Returns calculated progress object.

---

## 💻 Tech Stack

- **Frontend:** React 18.3, Vite 6.1, Tailwind CSS 3.4, Recharts 2.15, Axios 1.7, React Router DOM 6.28, Lucide React.
- **Backend:** FastAPI 0.115+, Uvicorn 0.28+, SQLAlchemy 2.0, Pydantic v2, PyMySQL 1.2+, SQLite3, Passlib (Bcrypt), Python-Jose (JWT), Python-Dateutil.
- **Testing:** Pytest 9.1+ with 13 automated tests covering auth, tenant isolation, CRUD, and calculation precision.
- **Deployment:** Render Static Site (Frontend) + Render Web Service (Backend).

---

## ⚙️ Key Technical Challenges Solved

### 1. Decimal-Safe Financial Precision
- **Challenge:** Standard binary floating-point numbers (`float`) accumulate precision drift in repeated summation (e.g., `0.1 + 0.2 = 0.30000000000000004`), which is unacceptable for financial software.
- **Implementation:** Enforced SQL `Numeric(12, 2)` throughout SQLAlchemy models and converted all arithmetic operations in `calculation_service.py` to Python's `Decimal` type with fixed two-decimal quantizing.
- **Engineering Value:** Demonstrates awareness of real-world financial software constraints and numerical computing safety.

### 2. Multi-Tenant Data Isolation and Authorization
- **Challenge:** In multi-user applications, inadvertent omissions in authorization logic can permit horizontal privilege escalation, allowing one user to access or manipulate another's financial records.
- **Implementation:** Implemented an authentication dependency `get_current_user` that validates the JWT bearer token. Every database query, transaction insertion, and budget lookup explicitly binds the authenticated `user_id`. Wrote dedicated unit tests in `tests/test_isolation.py` verifying that cross-tenant access attempts return 404/403.
- **Engineering Value:** Shows security-first architecture, defensive programming, and robust automated test verification.

### 3. Dynamic Dual-Engine Database Fallback
- **Challenge:** Production cloud instances often run SQLite for free-tier hosting, while local development may use MySQL. A hardcoded connection string causes crashes when MySQL is unreachable.
- **Implementation:** Designed a dynamic engine initializer in `app/database.py`. It runs a connection pre-ping to MySQL with a 3-second timeout. If the database is unreachable or credentials fail, it logs an informative warning and automatically initializes an SQLite instance (`expense_tracker.db`).
- **Engineering Value:** Eliminates environment brittleness and guarantees zero-downtime deployment across heterogeneous infrastructure.

---

## 📡 API / Backend Endpoints

| Method | Endpoint | Description | Auth Required |
|:---|:---|:---|:---|
| `POST` | `/api/auth/register` | Register new user account with hashed password | Public |
| `POST` | `/api/auth/login` | Authenticate credentials and receive JWT bearer token | Public |
| `GET` | `/api/auth/me` | Fetch authenticated user profile and preferences | Bearer JWT |
| `GET` | `/api/dashboard/summary` | Get financial totals, balance, and active budget alerts | Bearer JWT |
| `GET` | `/api/transactions` | Paginated transaction list with category/date filters | Bearer JWT |
| `POST` | `/api/transactions` | Create new income or expense transaction | Bearer JWT |
| `PUT` | `/api/transactions/{id}` | Update existing transaction record | Bearer JWT |
| `DELETE` | `/api/transactions/{id}` | Delete transaction record | Bearer JWT |
| `GET` | `/api/transactions/export/csv` | Download filtered transactions as formatted CSV | Bearer JWT |
| `GET` | `/api/budgets/progress` | Retrieve monthly budget spending vs. cap progress | Bearer JWT |
| `POST` | `/api/budgets` | Set monthly category spending budget ceiling | Bearer JWT |
| `GET` | `/api/analytics/monthly-trends`| Monthly income vs. expense aggregate trends | Bearer JWT |
| `GET` | `/api/analytics/category-breakdown`| Percentage breakdown of spending by category | Bearer JWT |

---

## 🗄️ Database / Data Model

```mermaid
erDiagram
    USERS ||--o{ CATEGORIES : owns
    USERS ||--o{ TRANSACTIONS : records
    USERS ||--o{ BUDGETS : defines
    USERS ||--o| USER_SETTINGS : configures
    CATEGORIES ||--o{ TRANSACTIONS : categorizes
    CATEGORIES ||--o{ BUDGETS : limits

    USERS {
        int id PK
        string name
        string email UK
        string password_hash
        string currency
        datetime created_at
    }

    CATEGORIES {
        int id PK
        int user_id FK
        string name
        string type
        string icon
    }

    TRANSACTIONS {
        int id PK
        int user_id FK
        int category_id FK
        string type
        numeric amount
        string title
        text description
        date transaction_date
        string payment_method
    }

    BUDGETS {
        int id PK
        int user_id FK
        int category_id FK
        numeric amount
        int month
        int year
    }

    USER_SETTINGS {
        int id PK
        int user_id FK
        string theme
        boolean email_notifications
    }
```

---

## 🧪 Automated Testing

Expensely includes a dedicated test suite with 13 automated tests covering critical business logic:
- `test_auth.py`: User registration, validation errors, and token generation.
- `test_transactions.py`: Transaction creation, validation constraints, and pagination.
- `test_budgets.py`: Budget threshold progress calculations (80% and 100% triggers).
- `test_calculations.py`: Decimal arithmetic verification.
- `test_isolation.py`: Cross-tenant security validation.
- `test_export.py`: CSV generation and column header formatting.

Run tests locally:
```bash
cd backend
python -m pytest tests/ -v
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- MySQL (Optional; automatically defaults to SQLite if MySQL is absent)

### 1. Clone Repository
```bash
git clone https://github.com/kritika7268/expense-tracker.git
cd expense-tracker
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
*Backend runs at `http://127.0.0.1:8000` (API Docs: `http://127.0.0.1:8000/docs`).*

### 3. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs at `http://localhost:5173`.*

---

## 🔐 Environment Variables

### Backend (`backend/.env.example`)
```env
# Database Configuration (Defaults to SQLite if MySQL is not available)
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/expense_tracker

# JWT Security
SECRET_KEY=change_this_secret_key_to_a_random_32_character_string
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Environment
ENVIRONMENT=development
```

### Frontend (`frontend/.env.example`)
```env
VITE_API_URL=http://127.0.0.1:8000/api
```

---

## 🗺️ Future Improvements
- **Recurring Transactions Cron:** Scheduled automated deductions for monthly subscriptions and recurring salary entries.
- **Receipt OCR Parsing:** Mobile image upload for automated receipt line-item scanning.
- **Multi-Currency Conversion:** Dynamic real-time exchange rates for international travelers.

---

## 📂 Project Structure

```
expense-tracker/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM models (User, Transaction, Budget, Category)
│   │   ├── routers/         # FastAPI route handlers (auth, transactions, budgets, analytics)
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Business logic (calculations, CSV exports)
│   │   ├── utils/           # Security, password hashing, JWT dependencies
│   │   ├── config.py        # Environment settings and CORS configuration
│   │   ├── database.py      # Dual-engine connection manager (MySQL + SQLite failover)
│   │   └── main.py          # Application entry point and exception handlers
│   ├── tests/               # 13 automated Pytest test cases
│   ├── requirements.txt     # Python backend dependencies
│   └── scripts/seed.py      # Demo account and transaction seed utility
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI cards, tables, modals, and charts
│   │   ├── context/         # Auth, Theme, and Toast React contexts
│   │   ├── pages/           # Dashboard, Transactions, Budgets, Analytics pages
│   │   ├── services/api.js  # Axios HTTP client with JWT interceptor
│   │   └── App.jsx          # Route definitions and protected route wrappers
│   ├── package.json         # Node.js dependencies (React, Recharts, Tailwind)
│   └── vite.config.js       # Vite build configuration
├── .gitignore               # Git hygiene filters
├── render.yaml              # Render.com deployment blueprint
└── README.md                # Project documentation
```

---

## 👤 Author & License
- **Author:** Kritika Shukla ([@kritika7268](https://github.com/kritika7268))
- **Email:** shuklakritika7268@gmail.com
- **License:** Open Source under the MIT License.
