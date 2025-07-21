import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
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
        wallet = await session.scalar(stmt)
        if not wallet:
            logger.debug(f"Кошелёк с ID {uuid_wallet} не найден")
        return wallet
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении кошелька с ID {uuid_wallet}: {e}")
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
        async with session.begin():
            stmt = select(Wallet).where(Wallet.email == email)
            wallet = await session.scalar(stmt)
            if not wallet:
                logger.debug(f"Кошелёк с email {email} не найден")
            return wallet
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении кошелька с email {email}: {e}")
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
        async with session.begin():
            wallet = Wallet(email=email)
            session.add(wallet)
            await session.commit()
            logger.debug(f"Кошелёк с email {email} успешно создан")
            return wallet
    except IntegrityError:
        await session.rollback()
        logger.debug(f"Кошелёк с email {email} уже существует")
        return None
    except SQLAlchemyError:
        await session.rollback()
        raise
