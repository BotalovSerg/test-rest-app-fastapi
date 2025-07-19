from fastapi import APIRouter

router = APIRouter(tags=["Wallet"])


@router.get("/health_check")
def health_check():
    return {"messege": "OK"}


@router.post("/{wallet_id}/operation")
async def perform_operation():
    ...