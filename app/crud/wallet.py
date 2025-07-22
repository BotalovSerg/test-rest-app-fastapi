import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.wallet.schemas import OperationCreate, OperationResponse
from app.core import logger
from app.models import Operation, OperationType, Wallet


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
            return None
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


async def update_wallet_balance(
    session: AsyncSession,
    uuid_wallet: uuid.UUID,
    operation: OperationCreate,
):
    """Обновляет баланс кошелька и записывает операцию.

    Args:
        session: Асинхронная сессия SQLAlchemy.
        uuid_wallet: UUID кошелька.
        operation: Данные операции (тип и сумма).

    Returns:
        OperationResponse: Данные созданной операции.

    Raises:
        HTTPException:
            - 404: Если кошелёк не найден.
            - 422: Если недостаточно средств для снятия.
    """
    try:
        async with session.begin():
            wallet = await get_wallet_by_id(session, uuid_wallet)
            if not wallet:
                logger.debug(f"Кошелёк с ID {uuid_wallet} не найден")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Кошелёк не найден",
                )

            if operation.operation_type == OperationType.WITHDRAW:
                if wallet.balance < operation.amount:
                    logger.warning(
                        f"Недостаточно средств для снятия {operation.amount} с кошелька {uuid_wallet}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Недостаточно средств",
                    )
                wallet.balance -= operation.amount
            elif operation.operation_type == OperationType.DEPOSIT:
                wallet.balance += operation.amount

            new_operation = Operation(
                wallet_id=wallet.id,
                operation_type=operation.operation_type,
                amount=operation.amount,
            )

            session.add(new_operation)
            await session.commit()
            logger.info(
                f"Операция {operation.operation_type} на сумму {operation.amount} "
                f"выполнена для кошелька {uuid_wallet}"
            )
            return OperationResponse(
                id=new_operation.id,
                wallet_id=new_operation.wallet_id,
                operation_type=new_operation.operation_type,
                amount=new_operation.amount,
                created_at=new_operation.created_at,
            )
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка при обновлении баланса кошелька {uuid_wallet}: {e}")
        raise
