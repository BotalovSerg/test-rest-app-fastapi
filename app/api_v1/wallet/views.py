import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper
from app.crud.base import test_connection
from app.crud.wallet import create_wallet, get_wallet_by_id

router = APIRouter(tags=["Wallet"])


@router.get("/health_check")
async def health_check(
    session: Annotated[AsyncSession, Depends(db_helper.sesion_getter)],
):
    await test_connection(session)
    return {"messege": "OK"}


@router.post("/{wallet_id}/operation")
async def perform_operation(): ...


@router.get("/{wallet_id}")
async def get_wallet(
    wallet_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(db_helper.sesion_getter)],
):
    wallet = await get_wallet_by_id(session, wallet_id)
    if wallet:
        return {"wallet": wallet}
    return {"message": "Not found"}


@router.post("/create-wallet")
async def create_wallet_at_db(
    name: str,
    session: Annotated[AsyncSession, Depends(db_helper.sesion_getter)],
):
    wallet = await create_wallet(session, name)

    return {"message": wallet}
