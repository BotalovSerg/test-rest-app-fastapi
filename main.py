from fastapi import FastAPI

from app.api_v1 import router as router_api_v1

app = FastAPI(title="App")

app.include_router(router=router_api_v1, prefix="/api/v1")
