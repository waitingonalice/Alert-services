import os
from dotenv import load_dotenv
from core.directory import directory

# ENV loaded from docker build
load_dotenv(directory.ENV)


class AppSettings:
    APP_NAME = os.getenv("APP_NAME")


class PostgresSettings:
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")


class MongoSettings:
    pass


class Settings(
    AppSettings,
    PostgresSettings,
    MongoSettings,
):
    pass


settings = Settings()
