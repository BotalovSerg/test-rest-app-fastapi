from sqlalchemy import Column, Numeric

from .base import Base


class Wallet(Base):
    __tablename__ = "wallets"

    balance = Column(Numeric(10, 2), default=0.00)
