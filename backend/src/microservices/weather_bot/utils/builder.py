from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from src.connectors.weather import WeatherConnector
from src.core.depends import Depends
from src.repository.telegram import TelegramRepository
from src.repository.preferences import PreferencesRepository


class BaseConversationBuilder(ABC):
    """
    Base class for building a telegram bot conversation
    """

    def __init__(
        self,
        telegram_repo: TelegramRepository = Depends(TelegramRepository),
        preferences_repo: PreferencesRepository = Depends(PreferencesRepository),
        weather_connector: WeatherConnector = Depends(WeatherConnector),
    ):
        self.telegram_repo = telegram_repo
        self.preferences_repo = preferences_repo
        self.weather_connector = weather_connector

    @abstractmethod
    async def track_users(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        pass

    @abstractmethod
    async def start_conversation(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        pass
