from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


class WalletCreateDTO(BaseModel):
    """Schema for creating a new wallet"""
    name: str = Field(..., min_length=1, max_length=100, description="Wallet name")
    type: str = Field(..., min_length=1, max_length=50, description="Wallet type (e.g., checking, savings, cash, credit)")
    balance: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0, description="Initial balance")


class WalletUpdateDTO(BaseModel):
    """Schema for updating wallet information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Wallet name")
    type: Optional[str] = Field(None, min_length=1, max_length=50, description="Wallet type")


class WalletResponse(BaseModel):
    """Schema for wallet response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    type: str
    balance: Decimal
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class WalletListResponse(BaseModel):
    """Schema for wallet list response"""
    wallets: List[WalletResponse]
    total: int


class WalletBalanceUpdateDTO(BaseModel):
    """Schema for updating wallet balance"""
    amount: Decimal = Field(..., description="Amount to add or subtract from balance")
    operation: str = Field(..., pattern="^(add|subtract|set)$", description="Operation type: add, subtract, or set")
    note: Optional[str] = Field(None, max_length=255, description="Note for the balance update")


class WalletSummaryResponse(BaseModel):
    """Schema for wallet summary"""
    total_wallets: int
    total_balance: Decimal
    wallets_by_type: dict
    most_recent_wallet: Optional[WalletResponse] = None
