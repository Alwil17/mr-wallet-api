import sqlalchemy as sa
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Text,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.models.base import Base
import enum


class TransactionType(str, enum.Enum):
    """Transaction type enumeration"""

    INCOME = "income"
    EXPENSE = "expense"


class TransactionCategory(str, enum.Enum):
    """Transaction category enumeration"""

    # Income categories
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT = "investment"
    GIFT = "gift"
    REFUND = "refund"
    OTHER_INCOME = "other_income"

    # Expense categories
    FOOD = "food"
    TRANSPORT = "transport"
    HOUSING = "housing"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    SHOPPING = "shopping"
    TRAVEL = "travel"
    INSURANCE = "insurance"
    TAXES = "taxes"
    DEBT_PAYMENT = "debt_payment"
    OTHER_EXPENSE = "other_expense"


class Transaction(Base):
    """Transaction model for tracking income and expenses"""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(TransactionType), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(Enum(TransactionCategory), nullable=True, index=True)
    category_id = Column(
        Integer, sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    note = Column(Text, nullable=True)
    date = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # Foreign keys
    wallet_id = Column(
        Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    files = relationship(
        "File", back_populates="transaction", cascade="all, delete-orphan"
    )
    user_category = relationship("Category", foreign_keys=[category_id])

    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.type}, amount={self.amount}, category={self.category})>"
