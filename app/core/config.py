import os

from dotenv import load_dotenv
from pydantic import BaseModel, PostgresDsn, Secret
from pydantic_settings import BaseSettings

load_dotenv(".env.local")


class DatabaseConfig(BaseModel):
    user: str = os.getenv("POSTGRES_USER")
    password: Secret = os.getenv("POSTGRES_PASSWORD")
    port: str = os.getenv("POSTGRES_PORT")
    db_name: str = os.getenv("POSTGRES_DB")
    app_host: str = os.getenv("APP_HOST")
    url: PostgresDsn = f"postgresql+asyncpg://{user}:{password}@{app_host}:{port}/{db_name}"


class Settings(BaseSettings):
    db: DatabaseConfig = DatabaseConfig()


settings = Settings()
