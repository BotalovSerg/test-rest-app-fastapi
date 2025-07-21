import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import logger
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


async def get_wallet_by_email(
    session: AsyncSession,
    email: str,
) -> None | Wallet:
    """_summary_

    Args:
        session (AsyncSession): _description_
        email (str): _description_

    Returns:
        None | Wallet: _description_
    """
    try:
        stmt = select(Wallet).where(Wallet.email == email)
        wallet = await session.scalar(stmt)
        if not wallet:
            logger.info(f"Wallet с email: {email} не найден")
            return None
        return wallet
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении wallet: {e}")
        return None


async def create_wallet_by_email(
    session: AsyncSession,
    email: str,
) -> Wallet:
    """_summary_

    Args:
        session (AsyncSession): _description_
        email (str): _description_

    Returns:
        Wallet: _description_
    """
    try:
        existing_wallet = await get_wallet_by_email(session, email)
        if existing_wallet is not None:
            logger.info(f"Wallet с email {email} существует")
            return None
        wallet = Wallet(email=email)
        session.add(wallet)
        await session.commit()
        logger.info(f"Wallet с email {email} создан")
        return wallet
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка при создании wallet: {e}")
        return None
