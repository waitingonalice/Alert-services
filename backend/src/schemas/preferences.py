from typing import Optional
from pydantic import BaseModel


class PreferencesRepositorySchema(BaseModel):
    id: str
    silence_start_time: Optional[str] = None
    silence_end_time: Optional[str] = None
