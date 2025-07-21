from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WalletBase(BaseModel):
    id: UUID


class WalletCreateResponse(WalletBase):
    email: str
    model_config = ConfigDict(from_attributes=True)


class WalletResponse(WalletBase):
    balance: Decimal
