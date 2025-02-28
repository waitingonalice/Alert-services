import datetime
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.sql import async_transaction, async_session
from ..schemas.telegram import TelegramRepositorySchema
from ..models.telegram import Telegram as TelegramDAO
from ..core.depends import Depends


class TelegramRepository:
    def __init__(self, session: AsyncSession = Depends(async_session)):
        self.session = session

    def __dao_to_dto(self, dao: TelegramDAO):
        return TelegramRepositorySchema(
            user_id=dao.user_id,
            chat_id=dao.chat_id,
            is_deleted=dao.is_deleted,
            updated_at=dao.updated_at,
            username=dao.username,
            first_name=dao.first_name,
            last_name=dao.last_name,
        )

    async def get_telegram_user(self, user_id: str) -> TelegramRepositorySchema | None:
        user_data = await self.session.execute(
            select(TelegramDAO).where(TelegramDAO.user_id == user_id)
        )
        user = user_data.scalar_one_or_none()
        if not user:
            return None
        return self.__dao_to_dto(user)

    async def upsert_telegram_user(
        self,
        user_id: str,
        chat_id: str,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        session: AsyncSession,
    ):
        statement = """
            INSERT INTO telegram (user_id, chat_id, username, first_name, last_name)
            VALUES (:user_id, :chat_id, :username, :first_name, :last_name)
            ON CONFLICT (user_id) DO UPDATE
            SET chat_id = :chat_id, username = :username, first_name = :first_name, last_name = :last_name
        """
        params = TelegramRepositorySchema(
            user_id=user_id,
            chat_id=chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        ).model_dump(exclude=["updated_at", "is_deleted"])

        await session.execute(
            text(statement),
            params,
        )

    @async_transaction
    async def update_is_deleted_user(
        self,
        is_deleted: bool,
        user_id: str,
        session: AsyncSession,
    ):
        statement = """
            UPDATE telegram SET is_deleted = :is_deleted
            WHERE user_id = :user_id
        """
        params = {
            "is_deleted": is_deleted,
            "user_id": user_id,
        }
        await session.execute(
            text(statement),
            params,
        )

    @async_transaction
    async def soft_delete_telegram_user(
        self,
        user_id: str,
        chat_id: str,
        session: AsyncSession,
    ):
        statement = """
            UPDATE telegram SET is_deleted = :is_deleted
            WHERE user_id = :user_id AND chat_id = :chat_id
            AND is_deleted = FALSE
        """

        params = TelegramRepositorySchema(
            user_id=user_id,
            chat_id=chat_id,
            is_deleted=True,
        ).model_dump(exclude=["updated_at"])

        await session.execute(
            text(statement),
            params,
        )

    @async_transaction
    async def hard_delete_telegram_users(self, session: AsyncSession):
        # To be used in a cron job for database cleanup
        statement = """
            DELETE FROM telegram
            WHERE is_deleted = :is_deleted
            AND updated_at < :updated_at
        """

        params = {
            "is_deleted": True,
            "updated_at": datetime.datetime.now() - datetime.timedelta(days=30),
        }

        await session.execute(
            text(statement),
            params,
        )
