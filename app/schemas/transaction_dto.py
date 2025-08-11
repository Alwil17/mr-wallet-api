from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Union, Any
from app.db.models.transaction import TransactionType, TransactionCategory
from app.db.models.file import FileType


class TransactionCreateDTO(BaseModel):
    """Schema for creating a new transaction"""

    type: TransactionType = Field(
        ..., description="Transaction type (income or expense)"
    )
    amount: Decimal = Field(
        ..., gt=0, description="Transaction amount (must be positive)"
    )
    category: Optional[TransactionCategory] = Field(None, description="Transaction category (enum)")
    category_id: Optional[int] = Field(None, description="User-defined category ID (optional)")
    note: Optional[str] = Field(
        None, max_length=1000, description="Optional note or description"
    )
    date: Optional[datetime] = Field(
        None, description="Transaction date (defaults to now)"
    )
    wallet_id: int = Field(..., description="Wallet ID for the transaction")


class TransactionUpdateDTO(BaseModel):
    """Schema for updating transaction information"""

    type: Optional[TransactionType] = Field(None, description="Transaction type")
    amount: Optional[Decimal] = Field(None, gt=0, description="Transaction amount")
    category: Optional[TransactionCategory] = Field(
        None, description="Transaction category (enum)"
    )
    category_id: Optional[int] = Field(None, description="User-defined category ID (optional)")
    note: Optional[str] = Field(
        None, max_length=1000, description="Note or description"
    )
    date: Optional[datetime] = Field(None, description="Transaction date")


class FileResponse(BaseModel):
    """Schema for file response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    original_filename: str
    url: str
    file_type: FileType
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    uploaded_at: datetime


class TransactionResponse(BaseModel):
    """Schema for transaction response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    type: TransactionType
    amount: Decimal
    category: Optional[TransactionCategory] = None
    category_id: Optional[int] = None
    user_category: Optional[dict] = None  # Populated with CategoryResponse if present
    note: Optional[str] = None
    date: datetime
    wallet_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    files: List[FileResponse] = []
    
    @field_validator('user_category', mode='before')
    @classmethod
    def validate_user_category(cls, v):
        if v is None:
            return None
        # If it's already a dict, return as-is
        if isinstance(v, dict):
            return v
        # If it's a SQLAlchemy model, convert to dict
        if hasattr(v, '__dict__'):
            from app.schemas.category_dto import CategoryResponse
            return CategoryResponse.model_validate(v).model_dump()
        return v


class TransactionListResponse(BaseModel):
    """Schema for transaction list response"""

    transactions: List[TransactionResponse]
    total: int
    page: int
    size: int
    total_pages: int


class TransactionSummaryResponse(BaseModel):
    """Schema for transaction summary response"""

    total_transactions: int
    total_income: Decimal
    total_expenses: Decimal
    net_amount: Decimal
    transactions_by_category: dict
    transactions_by_type: dict


class TransactionFilterDTO(BaseModel):
    """Schema for transaction filtering"""

    wallet_id: Optional[int] = Field(None, description="Filter by wallet ID")
    type: Optional[TransactionType] = Field(
        None, description="Filter by transaction type"
    )
    category: Optional[TransactionCategory] = Field(
        None, description="Filter by category"
    )
    start_date: Optional[datetime] = Field(None, description="Filter from start date")
    end_date: Optional[datetime] = Field(None, description="Filter to end date")
    min_amount: Optional[Decimal] = Field(
        None, ge=0, description="Minimum amount filter"
    )
    max_amount: Optional[Decimal] = Field(
        None, ge=0, description="Maximum amount filter"
    )
    search: Optional[str] = Field(None, max_length=255, description="Search in notes")


class FileUploadDTO(BaseModel):
    """Schema for file upload"""

    file_type: FileType = Field(..., description="Type of the file")
    transaction_id: int = Field(..., description="Transaction ID to attach file to")


class BulkTransactionCreateDTO(BaseModel):
    """Schema for creating multiple transactions"""

    transactions: List[TransactionCreateDTO] = Field(..., min_length=1, max_length=100)


class TransactionStatsResponse(BaseModel):
    """Schema for transaction statistics"""

    period: str  # "daily", "weekly", "monthly", "yearly"
    income_total: Decimal
    expense_total: Decimal
    net_total: Decimal
    transaction_count: int
    avg_transaction_amount: Decimal
    top_categories: List[dict]  # [{category: str, amount: Decimal, count: int}]
