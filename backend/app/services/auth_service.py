from sqlalchemy.orm import Session
from app.models.category import Category
from app.models.settings import UserSettings
from app.models.user import User

DEFAULT_EXPENSE_CATEGORIES = [
    {"name": "Food", "type": "expense", "icon": "Utensils"},
    {"name": "Transport", "type": "expense", "icon": "Car"},
    {"name": "Shopping", "type": "expense", "icon": "ShoppingBag"},
    {"name": "Bills", "type": "expense", "icon": "Receipt"},
    {"name": "Entertainment", "type": "expense", "icon": "Film"},
    {"name": "Education", "type": "expense", "icon": "GraduationCap"},
    {"name": "Health", "type": "expense", "icon": "HeartPulse"},
    {"name": "Travel", "type": "expense", "icon": "Plane"},
    {"name": "Subscriptions", "type": "expense", "icon": "Repeat"},
    {"name": "Other", "type": "expense", "icon": "MoreHorizontal"},
]

DEFAULT_INCOME_CATEGORIES = [
    {"name": "Salary", "type": "income", "icon": "Briefcase"},
    {"name": "Freelance", "type": "income", "icon": "Laptop"},
    {"name": "Business", "type": "income", "icon": "Building"},
    {"name": "Scholarship", "type": "income", "icon": "BookOpen"},
    {"name": "Gift", "type": "income", "icon": "Gift"},
    {"name": "Other", "type": "income", "icon": "DollarSign"},
]

def initialize_user_defaults(db: Session, user: User):
    """
    Provisions default categories and initial settings for a newly registered user.
    """
    # Create default settings if not exists
    if not user.settings:
        settings = UserSettings(
            user_id=user.id,
            currency=user.currency or "INR",
            monthly_income_target=0.0
        )
        db.add(settings)
    
    # Create default categories for this user
    existing_categories = db.query(Category).filter(Category.user_id == user.id).all()
    if not existing_categories:
        all_defaults = DEFAULT_EXPENSE_CATEGORIES + DEFAULT_INCOME_CATEGORIES
        for item in all_defaults:
            cat = Category(
                user_id=user.id,
                name=item["name"],
                type=item["type"],
                icon=item["icon"]
            )
            db.add(cat)
    
    db.commit()
