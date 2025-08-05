from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Transfer(Base):
    """Transfer model for wallet-to-wallet transactions"""

    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(
        Text, nullable=True
    )  # Optional description/note about the transfer

    # Foreign keys
    source_wallet_id = Column(
        Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )
    target_wallet_id = Column(
        Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_wallet = relationship(
        "Wallet", foreign_keys=[source_wallet_id], back_populates="source_transfers"
    )
    target_wallet = relationship(
        "Wallet", foreign_keys=[target_wallet_id], back_populates="target_transfers"
    )

    def __repr__(self):
        return f"<Transfer(id={self.id}, amount={self.amount}, source={self.source_wallet_id}, target={self.target_wallet_id})>"
