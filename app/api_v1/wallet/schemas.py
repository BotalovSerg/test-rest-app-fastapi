from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class WalletBase(BaseModel):
    id: UUID


class WalletCreateResponse(WalletBase):
    email: str

    class Config:
        from_attributes = True


class WalletResponse(WalletBase):
    balance: Decimal
