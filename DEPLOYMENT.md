# 🚀 Deploying Expensely on Render (Via GitHub)

This guide walks you through deploying **EXPENSELY** (FastAPI Backend + React Frontend) to [Render](https://render.com) using your GitHub repository: `https://github.com/kritika7268/expense-tracker`.

---

## 🌟 Method 1: 1-Click Blueprint Deploy (Recommended)

Since this repository contains a pre-configured [`render.yaml`](./render.yaml), Render can automatically configure both the backend and frontend services in a single step!

### Steps:
1. Go to [dashboard.render.com](https://dashboard.render.com) and log in with your GitHub account.
2. Click **New +** in the top-right corner and select **Blueprint**.
3. Connect your GitHub repository: **`kritika7268/expense-tracker`**.
4. Render will read `render.yaml` and display the two services:
   - **`expensely-backend`** (Web Service, Python 3)
   - **`expensely-frontend`** (Static Site, React / Vite)
5. Click **Apply**.
6. Render will automatically build and deploy both services!

---

## 🛠️ Method 2: Manual Deploy via Render Dashboard

If you prefer configuring the services individually, follow the steps below:

### Step 1: Deploy Backend (FastAPI Web Service)
1. On [Render Dashboard](https://dashboard.render.com), click **New +** -> **Web Service**.
2. Select your GitHub repository: `expense-tracker`.
3. Configure the following settings:
   - **Name**: `expensely-backend`
   - **Region**: Oregon (or nearest to you)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
4. Expand **Environment Variables** and add:
   | Key | Value | Notes |
   |-----|-------|-------|
   | `DATABASE_URL` | `sqlite:///./expense_tracker.db` | Uses robust SQLite DB (or your MySQL/PostgreSQL connection string) |
   | `SECRET_KEY` | *(Click 'Generate' or enter a secure string)* | JWT secret |
   | `CORS_ORIGINS` | `*` | Allows frontend requests |
   | `PYTHON_VERSION` | `3.11.9` | Python runtime version |
5. Click **Create Web Service**.
6. Once deployed, note down your backend URL (e.g. `https://expensely-backend-xxxx.onrender.com`).
   - You can test it by visiting: `https://expensely-backend-xxxx.onrender.com/api/health`
   - Interactive Swagger API docs: `https://expensely-backend-xxxx.onrender.com/docs`

---

### Step 2: Deploy Frontend (React Static Site)
1. On [Render Dashboard](https://dashboard.render.com), click **New +** -> **Static Site**.
2. Select your GitHub repository: `expense-tracker`.
3. Configure the following settings:
   - **Name**: `expensely-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Expand **Environment Variables** and add:
   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://expensely-backend-xxxx.onrender.com/api` *(Replace with your backend URL from Step 1)* |
5. Go to the **Redirects / Rewrites** tab:
   - Add a rule:
     - **Type**: `Rewrite`
     - **Source**: `/*`
     - **Destination**: `/index.html`
   *(This ensures client-side routing like `/dashboard`, `/transactions`, `/budgets` works seamlessly without 404s on page refresh).*
6. Click **Create Static Site**.

---

## 🔑 Default Demo Login

When the backend starts up, it automatically initializes the database and creates a seeded demo account:
- **Email:** `demo@expensely.com`
- **Password:** `Demo@12345`

You can also register a new account from the frontend `/register` page at any time!
