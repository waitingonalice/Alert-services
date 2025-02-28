from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey
from ..core.sql import SQLBase


class Preferences(SQLBase):
    __tablename__ = "preferences"
    id: Mapped[str] = mapped_column(
        ForeignKey("telegram.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    silence_start_time: Mapped[str] = mapped_column(
        nullable=False,
        server_default="07:00",
        insert_default="07:00",
    )
    silence_end_time: Mapped[str] = mapped_column(
        nullable=False,
        server_default="22:00",
        insert_default="22:00",
    )
