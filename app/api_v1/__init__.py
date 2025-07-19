from fastapi import APIRouter

from .wallet.views import router as wallet_router

router = APIRouter()
router.include_router(router=wallet_router, prefix="/wallets")
