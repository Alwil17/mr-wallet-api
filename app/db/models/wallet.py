from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.models.base import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(
        String, nullable=False
    )  # e.g., "checking", "savings", "cash", "credit"
    balance = Column(Numeric(precision=10, scale=2), default=0.00)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions = relationship(
        "Transaction", back_populates="wallet", cascade="all, delete-orphan"
    )
    debts = relationship("Debt", back_populates="wallet", cascade="all, delete-orphan")
    source_transfers = relationship(
        "Transfer",
        foreign_keys="Transfer.source_wallet_id",
        back_populates="source_wallet",
    )
    target_transfers = relationship(
        "Transfer",
        foreign_keys="Transfer.target_wallet_id",
        back_populates="target_wallet",
    )

    def __repr__(self):
        return f"<Wallet(id={self.id}, name='{self.name}', type='{self.type}', balance={self.balance})>"
