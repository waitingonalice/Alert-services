import os
from dotenv import load_dotenv

load_dotenv()


class AppSettings:
    ENV: str | None = os.getenv("BUILD_ENV")
    APP_NAME: str = os.getenv("APP_NAME", "Alert Services API")
    CRON_APP_NAME: str = os.getenv("CRON_APP_NAME", "Alert Services Cron")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    OPEN_GOV_ENDPOINT: str = os.getenv(
        "OPEN_GOV_ENDPOINT", "https://api-open.data.gov.sg"
    )


class PostgresSettings:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_HOST: str = (
        os.getenv("POSTGRES_HOST", "localhost")
        if os.getenv("BUILD_END")
        else "localhost"  # For database migration outside of docker
    )
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "alerts")
    POSTGRES_SYNC_PREFIX: str = os.getenv("POSTGRES_SYNC_PREFIX", "postgresql://")
    POSTGRES_ASYNC_PREFIX: str = os.getenv(
        "POSTGRES_ASYNC_PREFIX", "postgresql+asyncpg://"
    )
    POSTGRES_URI: str = (
        f"{POSTGRES_USER}:"
        f"{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:"
        f"{POSTGRES_PORT}/"
        f"{POSTGRES_DB}"
    )


class SQLAlchemySettings:
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() in ("true", "1")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "2"))
    DB_POOL_RECYCLE_SECONDS: int = int(os.getenv("DB_POOL_RECYCLE_SECONDS", "3600"))
    DB_POOL_TIMEOUT_SECONDS: int = int(os.getenv("DB_POOL_TIMEOUT_SECONDS", "30"))
    DB_POOL_PRE_PING: bool = os.getenv("DB_POOL_PRE_PING", "True").lower() in (
        "true",
        "1",
    )


class MinioSettings:
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "")
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "")


class TelegramBotSettings:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")


class Settings(
    AppSettings,
    PostgresSettings,
    SQLAlchemySettings,
    MinioSettings,
    TelegramBotSettings,
):
    pass


settings = Settings()
