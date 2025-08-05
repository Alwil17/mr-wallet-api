from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


class DebtCreateDTO(BaseModel):
    """Schema for creating a new debt"""
    amount: Decimal = Field(..., gt=0, description="Debt amount (must be positive)")
    borrower: str = Field(..., min_length=1, max_length=100, description="Person who owes/is owed money")
    type: str = Field(..., pattern="^(owed|given)$", description="Debt type: 'owed' (money you're owed) or 'given' (money you owe)")
    due_date: Optional[datetime] = Field(None, description="Due date for the debt (optional)")
    description: Optional[str] = Field(None, max_length=500, description="Additional details about the debt")
    wallet_id: int = Field(..., description="ID of the wallet this debt is associated with")


class DebtUpdateDTO(BaseModel):
    """Schema for updating debt information"""
    amount: Optional[Decimal] = Field(None, gt=0, description="Debt amount (must be positive)")
    borrower: Optional[str] = Field(None, min_length=1, max_length=100, description="Person who owes/is owed money")
    type: Optional[str] = Field(None, pattern="^(owed|given)$", description="Debt type: 'owed' or 'given'")
    due_date: Optional[datetime] = Field(None, description="Due date for the debt")
    description: Optional[str] = Field(None, max_length=500, description="Additional details about the debt")
    is_paid: Optional[bool] = Field(None, description="Whether the debt has been paid")


class DebtResponse(BaseModel):
    """Schema for debt response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    amount: Decimal
    borrower: str
    type: str
    is_paid: bool
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    wallet_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class DebtListResponse(BaseModel):
    """Schema for debt list response"""
    debts: List[DebtResponse]
    total: int


class DebtSummaryResponse(BaseModel):
    """Schema for debt summary response"""
    total_debts: int
    total_amount_owed: Decimal  # Money you're owed by others
    total_amount_given: Decimal  # Money you owe to others
    net_position: Decimal  # Positive if you're owed more, negative if you owe more
    paid_debts: int
    unpaid_debts: int
    overdue_debts: int
    debts_by_type: dict


class DebtFilterDTO(BaseModel):
    """Schema for filtering debts"""
    debt_type: Optional[str] = Field(None, pattern="^(owed|given)$", description="Filter by debt type")
    is_paid: Optional[bool] = Field(None, description="Filter by payment status")
    borrower: Optional[str] = Field(None, description="Filter by borrower name")
    overdue_only: Optional[bool] = Field(False, description="Show only overdue debts")
    wallet_id: Optional[int] = Field(None, description="Filter by wallet ID")


class DebtMarkPaidDTO(BaseModel):
    """Schema for marking a debt as paid"""
    is_paid: bool = Field(..., description="Payment status")
    payment_note: Optional[str] = Field(None, max_length=255, description="Note about the payment")
