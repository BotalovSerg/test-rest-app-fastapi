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
    """
    Получает кошелёк по его уникальному идентификатору (UUID).

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        uuid_wallet (uuid.UUID): UUID кошелька для поиска.

    Returns:
        Wallet | None: Найденный кошелёк или None, если не найден.
    """
    try:
        stmt = select(Wallet).where(Wallet.id == uuid_wallet)
        return await session.scalar(stmt)
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении wallet: {e}")
        return None


async def get_wallet_by_email(
    session: AsyncSession,
    email: str,
) -> Wallet | None:
    """
    Получает кошелёк по email.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        email (str): Email для поиска кошелька.

    Returns:
        Wallet | None: Найденный кошелёк или None, если не найден.
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
) -> Wallet | None:
    """
    Создаёт новый кошелёк с указанным email, если такой email ещё не используется.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        email (str): Email, связанный с кошельком.

    Returns:
        Wallet | None: Созданный кошелёк или None, если создание не удалось.
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
