from pydantic import BaseModel, Field, ConfigDict, model_validator
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


class TransferCreateDTO(BaseModel):
    """Schema for creating a new transfer"""
    amount: Decimal = Field(..., gt=0, description="Transfer amount (must be positive)")
    source_wallet_id: int = Field(..., description="ID of the source wallet (money comes from)")
    target_wallet_id: int = Field(..., description="ID of the target wallet (money goes to)")
    description: Optional[str] = Field(None, max_length=500, description="Optional description/note about the transfer")

    @model_validator(mode="after")
    def validate_wallets(self):
        if self.source_wallet_id == self.target_wallet_id:
            raise ValueError("Source and target wallets cannot be the same")
        return self


class TransferResponse(BaseModel):
    """Schema for transfer response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    amount: Decimal
    description: Optional[str] = None
    source_wallet_id: int
    target_wallet_id: int
    created_at: datetime
    
    # Additional fields for enriched response
    source_wallet_name: Optional[str] = None
    target_wallet_name: Optional[str] = None


class TransferListResponse(BaseModel):
    """Schema for transfer list response"""
    transfers: List[TransferResponse]
    total: int


class TransferSummaryResponse(BaseModel):
    """Schema for transfer summary response"""
    total_transfers: int
    total_amount_transferred: Decimal
    transfers_by_wallet: dict  # Statistics by wallet
    recent_transfers: List[TransferResponse]


class TransferFilterDTO(BaseModel):
    """Schema for filtering transfers"""
    source_wallet_id: Optional[int] = Field(None, description="Filter by source wallet ID")
    target_wallet_id: Optional[int] = Field(None, description="Filter by target wallet ID")
    wallet_id: Optional[int] = Field(None, description="Filter by transfers involving this wallet (source or target)")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum transfer amount")
    max_amount: Optional[Decimal] = Field(None, gt=0, description="Maximum transfer amount")
    date_from: Optional[datetime] = Field(None, description="Filter transfers from this date")
    date_to: Optional[datetime] = Field(None, description="Filter transfers to this date")


class WalletTransferSummaryDTO(BaseModel):
    """Schema for wallet-specific transfer summary"""
    wallet_id: int
    wallet_name: str
    total_sent: Decimal
    total_received: Decimal
    net_amount: Decimal  # received - sent
    transfer_count: int
