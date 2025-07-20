import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Wallet


async def get_wallet_by_id(
    session: AsyncSession,
    uuid_wallet: uuid.UUID,
) -> Wallet | None:
    """_summary_

    Args:
        session (AsyncSession): _description_
        uuid_wallet (uuid.UUID): _description_

    Returns:
        Wallet | None: _description_
    """
    stmt = select(Wallet).where(Wallet.id == uuid_wallet)
    return await session.scalar(stmt)


async def create_wallet(
    session: AsyncSession,
    # uuid_wallet: uuid.UUID,
    name: str,
) -> Wallet:
    """_summary_

    Args:
        session (AsyncSession): _description_
        uuid_wallet (uuid.UUID): _description_
        name (str): _description_
    """
    # existing_wallet = await get_wallet_by_id(session, uuid_wallet)
    # if existing_wallet is not None:
    #     return
    wallet = Wallet(name=name)
    session.add(wallet)
    await session.commit()

    return wallet
