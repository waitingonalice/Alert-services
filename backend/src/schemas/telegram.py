import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class TelegramWeatherCommandsEnum(Enum):
    START = "start"
    SUBSCRIBE = "subscribe"
    WEATHER = "weather"
    CONFIGURE = "configure"
    UNSUBSCRIBE = "unsubscribe"


class TelegramWeatherConfigEnum(Enum):
    ALERT_START_TIME = "Start time of alerts"
    ALERT_END_TIME = "End time of alerts"


class TelegramWeatherConfigStatesEnum(Enum):
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
