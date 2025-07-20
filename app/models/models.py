import enum
import uuid
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class OperationType(enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class Wallet(Base):
    __tablename__ = "wallets"

    name: Mapped[str] = mapped_column(String(30), nullable=False)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
        default=0.0,
        server_default="0.0",
    )
    operations: Mapped[list["Operation"]] = relationship(
        "Operation",
        back_populates="wallet",
    )


class Operation(Base):
    __tablename__ = "operations"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id"),
        nullable=False,
        index=True,
    )
    operation_type: Mapped[OperationType] = mapped_column(
        Enum(OperationType, name="operationtype"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
    )
    wallet: Mapped["Wallet"] = relationship(
        "Wallet",
        back_populates="operations",
    )
