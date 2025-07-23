from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.models import OperationType


class WalletBase(BaseModel):
    id: UUID


class WalletCreateResponse(WalletBase):
    email: str
    model_config = ConfigDict(from_attributes=True)


class WalletResponse(WalletBase):
    balance: Decimal


class OperationCreate(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(gt=0, description="Сумма должна быть положительной")


class OperationResponse(BaseModel):
    id: UUID
    wallet_id: UUID
    operation_type: OperationType
    amount: Decimal
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EmailWallet(BaseModel):
    email: EmailStr
