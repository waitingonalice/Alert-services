import datetime
from typing import Callable, Optional
from pydantic import BaseModel
from enum import Enum

from .preferences import PreferencesRepositorySchema


class TelegramWeatherCommandsEnum(Enum):
    START = "start"
    SUBSCRIBE = "subscribe"
    CONFIGURE = "configure"
    UNSUBSCRIBE = "unsubscribe"


class TelegramWeatherConfigEnum(Enum):
    ALERT_START_TIME = "Start time of alerts"
    ALERT_END_TIME = "End time of alerts"


class TelegramWeatherConversationStatesEnum(Enum):
    ALERT_TIME = "Alert time"
    SELECTING_NOTIFICATION_OPTION = "Selecting notification option"
    FALLBACK = "Fallback"
    END_CONVERSATION = "See ya!"


class TelegramRepositorySchema(BaseModel):
    user_id: str
    chat_id: str
    is_deleted: Optional[bool] = False
    updated_at: Optional[datetime.datetime] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TelegramPreferenceRepositorySchema(BaseModel):
    telegram: TelegramRepositorySchema
    preference: PreferencesRepositorySchema


class TelegramAddJobSchema(BaseModel):
    callback: Callable
    interval: float | datetime.timedelta
    first: Optional[float | datetime.timedelta] = None
