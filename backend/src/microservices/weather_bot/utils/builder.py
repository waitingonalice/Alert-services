from abc import ABC, abstractmethod
from telegram import (
    Bot,
    Update,
)
from telegram.ext import (
    Application,
    ContextTypes,
)
from src.core.depends import Depends
from src.repository.telegram import TelegramRepository
from src.repository.preferences import PreferencesRepository


class BaseConversationBuilder(ABC):
    """
    Base class for building a telegram bot conversation
    """

    def __init__(
        self,
        application: Application,
        telegram_repo: TelegramRepository = Depends(TelegramRepository),
        preferences_repo: PreferencesRepository = Depends(PreferencesRepository),
    ):
        self.telegram_repo = telegram_repo
        self.preferences_repo = preferences_repo
        self.application = application
        self.bot: Bot = self.application.bot

    @abstractmethod
    async def track_users(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        pass

    @abstractmethod
    async def start_conversation(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        pass
