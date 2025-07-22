import os

from dotenv import load_dotenv
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings

load_dotenv(".env.local", override=True)


class DatabaseConfig(BaseModel):
    user: str = os.getenv("POSTGRES_USER")
    password: str = os.getenv("POSTGRES_PASSWORD")
    port: str = os.getenv("POSTGRES_PORT")
    db_name: str = os.getenv("POSTGRES_DB")
    app_host: str = os.getenv("APP_HOST")
    url: PostgresDsn = f"postgresql+asyncpg://{user}:{password}@{app_host}:{port}/{db_name}"
    echo: bool = False


class Settings(BaseSettings):
    db: DatabaseConfig = DatabaseConfig()


settings = Settings()
