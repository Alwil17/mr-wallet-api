from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional


class UserCreateDTO(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserUpdateDTO(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AccountDeletionRequest(BaseModel):
    confirmation_text: str  # User must type "DELETE" to confirm


class UserExportData(BaseModel):
    user_info: UserResponse
    wallets: list = []  # Will be populated with wallet data
    transactions: list = []  # Will be populated with transaction data
    debts: list = []  # Will be populated with debt data
    transfers: list = []  # Will be populated with transfer data
    export_timestamp: datetime
    data_retention_period: str
