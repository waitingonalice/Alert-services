import datetime
from typing import Optional
from pydantic import BaseModel


class PreferencesRepositorySchema(BaseModel):
    id: str
    alert_start_time: Optional[datetime.time] = None
    alert_end_time: Optional[datetime.time] = None

    # @field_validator("alert_start_time")
    # def convert_alert_start_time(value):
    #     if isinstance(value, str):
    #         return datetime.datetime.strptime(value, "%H:%M:%S").time()
    #     return value

    # @field_validator("alert_end_time")
    # def convert_alert_end_time(value):
    #     if isinstance(value, str):
    #         return datetime.datetime.strptime(value, "%H:%M:%S").time()
    #     return value
