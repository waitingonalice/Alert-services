import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, func
from ..core.sql import SQLBase


class Telegram(SQLBase):
    __tablename__ = "telegram"
    user_id: Mapped[str] = mapped_column(primary_key=True)
    chat_id: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    is_deleted: Mapped[bool] = mapped_column(
        nullable=False,
        insert_default=False,
        server_default="f",
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    # One-to-One relationship with Preferences, cascade delete
    preferences = relationship(
        "Preferences",
        backref="telegram",
        cascade="all,delete-orphan",
        # hard delete preferences when telegram user is deleted instead of sqlalchemy default set to null
        # LINK: https://docs.sqlalchemy.org/en/20/orm/cascades.html
        passive_deletes=True,
    )
