import sys
import os
from datetime import date, timedelta
from decimal import Decimal

# Set standard output encoding to utf-8 if possible
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent directory to sys.path so app modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.settings import UserSettings
from app.utils.security import hash_password
from app.services.auth_service import initialize_user_defaults

def seed_database():
    print("[INIT] Initializing Expensely database tables...")
    init_db()
    db = SessionLocal()

    try:
        demo_email = "demo@expensely.com"
        demo_password = "Demo@12345"
        
        # Check if demo user already exists
        user = db.query(User).filter(User.email == demo_email).first()
        if user:
            print(f"[INFO] Demo user '{demo_email}' already exists. Re-syncing demo data...")
        else:
            print(f"[USER] Creating demo user '{demo_email}'...")
            user = User(
                name="Demo User",
                email=demo_email,
                password_hash=hash_password(demo_password),
                currency="INR"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Initialize defaults (Categories + Settings)
        initialize_user_defaults(db, user)

        # Retrieve user categories
        categories = db.query(Category).filter(Category.user_id == user.id).all()
        cat_map = {c.name: c for c in categories}

        today = date.today()
        current_month = today.month
        current_year = today.year

        # Seed sample budgets for current month if not already present
        sample_budgets = [
            ("Food", 10000.0),
            ("Transport", 4000.0),
            ("Shopping", 8000.0),
            ("Bills", 6000.0),
            ("Entertainment", 3500.0),
            ("Subscriptions", 1500.0),
        ]

        print("[BUDGETS] Setting up monthly budgets...")
        for cat_name, budget_amt in sample_budgets:
            if cat_name in cat_map:
                existing_budget = db.query(Budget).filter(
                    Budget.user_id == user.id,
                    Budget.category_id == cat_map[cat_name].id,
                    Budget.month == current_month,
                    Budget.year == current_year
                ).first()
                if not existing_budget:
                    b = Budget(
                        user_id=user.id,
                        category_id=cat_map[cat_name].id,
                        amount=budget_amt,
                        month=current_month,
                        year=current_year
                    )
                    db.add(b)
        db.commit()

        # Seed realistic transactions if user has fewer than 10 transactions
        existing_tx_count = db.query(Transaction).filter(Transaction.user_id == user.id).count()
        if existing_tx_count < 10:
            print("[TRANSACTIONS] Seeding realistic sample transactions across multiple months...")
            transactions_data = [
                # Current month transactions
                {"title": "Monthly Salary", "amount": 85000.0, "type": "income", "cat": "Salary", "pm": "Bank Transfer", "days_ago": 2, "desc": "Corporate payroll deposit"},
                {"title": "Freelance Web UI Project", "amount": 28000.0, "type": "income", "cat": "Freelance", "pm": "UPI", "days_ago": 7, "desc": "Landing page redesign milestone 1"},
                {"title": "Gourmet Grocery & Organics", "amount": 4250.0, "type": "expense", "cat": "Food", "pm": "UPI", "days_ago": 1, "desc": "Weekly pantry restocking"},
                {"title": "Cafe & Working Lunch", "amount": 850.0, "type": "expense", "cat": "Food", "pm": "UPI", "days_ago": 3, "desc": "Cold brew and brunch with colleagues"},
                {"title": "Fine Dining Weekend", "amount": 3400.0, "type": "expense", "cat": "Food", "pm": "Credit Card", "days_ago": 5, "desc": "Family dinner"},
                {"title": "Metro Smart Card Recharge", "amount": 1500.0, "type": "expense", "cat": "Transport", "pm": "UPI", "days_ago": 4, "desc": "Monthly commute pass"},
                {"title": "Fuel Refill", "amount": 2200.0, "type": "expense", "cat": "Transport", "pm": "Debit Card", "days_ago": 8, "desc": "Car fuel refill"},
                {"title": "Zara Winter Jacket & Jeans", "amount": 6499.0, "type": "expense", "cat": "Shopping", "pm": "Credit Card", "days_ago": 6, "desc": "New seasonal wardrobe"},
                {"title": "Apartment High-Speed Broadband", "amount": 1199.0, "type": "expense", "cat": "Bills", "pm": "UPI", "days_ago": 9, "desc": "300 Mbps fiber internet"},
                {"title": "Electricity & Power Utility", "amount": 2850.0, "type": "expense", "cat": "Bills", "pm": "Bank Transfer", "days_ago": 10, "desc": "Monthly power consumption"},
                {"title": "IMAX Cinema Tickets & Snacks", "amount": 1450.0, "type": "expense", "cat": "Entertainment", "pm": "UPI", "days_ago": 11, "desc": "Weekend movie premiere"},
                {"title": "Cloud Hosting & Subscriptions", "amount": 999.0, "type": "expense", "cat": "Subscriptions", "pm": "Credit Card", "days_ago": 12, "desc": "AWS dev server + Spotify"},
                {"title": "Tech Conference Pass", "amount": 4500.0, "type": "expense", "cat": "Education", "pm": "Debit Card", "days_ago": 14, "desc": "Full Stack Dev Summit 2026"},

                # Previous month transactions
                {"title": "Previous Month Salary", "amount": 85000.0, "type": "income", "cat": "Salary", "pm": "Bank Transfer", "days_ago": 33, "desc": "Corporate payroll deposit"},
                {"title": "UI Consulting Project", "amount": 22000.0, "type": "income", "cat": "Freelance", "pm": "UPI", "days_ago": 38, "desc": "Client dashboard design sprint"},
                {"title": "Supermarket Supplies", "amount": 5400.0, "type": "expense", "cat": "Food", "pm": "Credit Card", "days_ago": 35, "desc": "Pantry items and home essentials"},
                {"title": "Cab Commutes", "amount": 2100.0, "type": "expense", "cat": "Transport", "pm": "UPI", "days_ago": 39, "desc": "Airport cab rides"},
                {"title": "Annual Dental Checkup", "amount": 3200.0, "type": "expense", "cat": "Health", "pm": "Debit Card", "days_ago": 41, "desc": "Routine dental cleaning"},
                {"title": "Home Maintenance & Repair", "amount": 3800.0, "type": "expense", "cat": "Bills", "pm": "Cash", "days_ago": 44, "desc": "Plumbing and fixture repairs"},
                {"title": "Audiobooks & Learning Platform", "amount": 1800.0, "type": "expense", "cat": "Education", "pm": "Credit Card", "days_ago": 46, "desc": "Technical books and courses"},
            ]

            for item in transactions_data:
                cat = cat_map.get(item["cat"])
                if cat:
                    tx_date = today - timedelta(days=item["days_ago"])
                    tx = Transaction(
                        user_id=user.id,
                        category_id=cat.id,
                        type=item["type"],
                        amount=item["amount"],
                        title=item["title"],
                        description=item["desc"],
                        transaction_date=tx_date,
                        payment_method=item["pm"]
                    )
                    db.add(tx)
            db.commit()
            print("[SUCCESS] Successfully added sample transactions.")
        else:
            print("[INFO] Sample transactions already populated.")

        print("\n" + "="*50)
        print("SEEDING COMPLETED SUCCESSFULLY!")
        print("Demo Account Credentials:")
        print(f"  Email:    {demo_email}")
        print(f"  Password: {demo_password}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"[ERROR] Error during database seeding: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
