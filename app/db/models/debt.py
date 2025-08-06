from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    ForeignKey,
    Boolean,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.models.base import Base


class Debt(Base):
    """Debt model for tracking money owed or lent"""

    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    borrower = Column(
        String(100), nullable=False, index=True
    )  # Person who owes/is owed money
    type = Column(
        String(20), nullable=False, index=True
    )  # 'owed' (money you're owed) or 'given' (money you owe)
    is_paid = Column(Boolean, default=False, nullable=False, index=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)  # Additional details about the debt

    # Foreign keys
    wallet_id = Column(
        Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    wallet = relationship("Wallet", back_populates="debts")

    def __repr__(self):
        return f"<Debt(id={self.id}, borrower='{self.borrower}', type='{self.type}', amount={self.amount}, is_paid={self.is_paid})>"
