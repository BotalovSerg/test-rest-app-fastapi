import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.wallet.schemas import WalletCreateResponse, WalletResponse
from app.core import db_helper, logger
from app.crud.base import test_connection
from app.crud.wallet import create_wallet_by_email, get_wallet_by_id

router = APIRouter(tags=["Wallet"])


@router.get("/health_check")
async def health_check(
    session: Annotated[AsyncSession, Depends(db_helper.sesion_getter)],
):
    await test_connection(session)
    return {"messege": "OK"}


@router.post("/{wallet_id}/operation")
async def perform_operation(): ...


@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(db_helper.sesion_getter)],
) -> WalletResponse:
    """Получает информацию о кошельке по его UUID.

    Args:
        wallet_id: UUID кошелька.
        session: Асинхронная сессия SQLAlchemy.

    Returns:
        WalletResponse: Данные кошелька (id, balance, email).

    Raises:
        HTTPException:
            - 404: Если кошелёк не найден.
    """
    wallet = await get_wallet_by_id(session, wallet_id)
    if not wallet:
        logger.debug(f"Кошелёк с ID {wallet_id} не найден")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кошелёк не найден",
        )
    logger.info(f"Кошелёк с ID {wallet_id} успешно получен")
    return WalletResponse(id=wallet.id, balance=wallet.balance)


@router.post(
    "/create-wallet",
    status_code=status.HTTP_201_CREATED,
    response_model=WalletCreateResponse,
)
async def create_wallet(
    email: EmailStr,
    session: Annotated[AsyncSession, Depends(db_helper.sesion_getter)],
) -> WalletCreateResponse:
    """Создаёт новый кошелёк с указанным email.

    Args:
        email: Email для создания кошелька (должен быть валидным).
        session: Асинхронная сессия SQLAlchemy.

    Returns:
        WalletResponse: Данные созданного кошелька (id и email).

    Raises:
        HTTPException:
            - 400: Если email имеет некорректный формат.
            - 409: Если email уже используется.
            - 500: Если произошла ошибка сервера.
    """
    try:
        wallet = await create_wallet_by_email(session, email)
        if wallet is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Кошелёк с таким email уже существует",
            )
        logger.info(f"create_wallet: Кошелёк создан для email {email}")
        return WalletCreateResponse(id=wallet.id, email=wallet.email)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный формат email",
        )
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при создании кошелька для email {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )
