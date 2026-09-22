from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    type = Column(String(20), nullable=False)  # 'income' or 'expense'
    amount = Column(Numeric(12, 2), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    transaction_date = Column(Date, nullable=False, index=True)
    payment_method = Column(String(50), nullable=False)  # Cash, UPI, Debit Card, Credit Card, Bank Transfer, Other
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
