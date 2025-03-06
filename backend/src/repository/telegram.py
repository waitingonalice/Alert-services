import datetime
from typing import List

# from sqlalchemy import text, select, and_
from sqlalchemy import text, select

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.sql import async_transaction, async_session
from src.schemas.preferences import PreferencesRepositorySchema
from src.schemas.telegram import (
    TelegramRepositorySchema,
    TelegramPreferenceRepositorySchema,
)
from src.models.telegram import Telegram as TelegramDAO
from src.models.preferences import Preferences as PreferencesDAO
from src.core.depends import Depends


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

    def __telegram_preference_dao_to_dto(
        self,
        user_dao: TelegramDAO,
        preference_dao: PreferencesDAO,
    ):
        return TelegramPreferenceRepositorySchema(
            telegram=self.__dao_to_dto(user_dao),
            preference=PreferencesRepositorySchema(
                id=preference_dao.id,
                alert_start_time=preference_dao.alert_start_time,
                alert_end_time=preference_dao.alert_end_time,
            ),
        )

    async def get_telegram_user(self, user_id: str) -> TelegramRepositorySchema | None:
        user_data = await self.session.execute(
            select(TelegramDAO).where(TelegramDAO.user_id == user_id)
        )
        user = user_data.scalar_one_or_none()
        if not user:
            return None
        return self.__dao_to_dto(user)

    @async_transaction
    async def list_subscribed_users_within_timeframe(
        self,
        session: AsyncSession,
    ) -> List[TelegramPreferenceRepositorySchema]:
        # transaction is required here to explicity execute join statement
        # now = datetime.datetime.now().time()
        data = await session.execute(
            select(
                TelegramDAO,
                PreferencesDAO,
            )
            .join_from(
                from_=TelegramDAO,
                target=PreferencesDAO,
                onclause=TelegramDAO.user_id == PreferencesDAO.id,
            )
            .where(
                # TODO: Uncomment this when user timezone is supported.
                TelegramDAO.is_deleted == False,  # noqa: E712
                # and_(
                #     TelegramDAO.is_deleted == False,  # noqa: E712
                #     now >= PreferencesDAO.alert_start_time,
                #     now <= PreferencesDAO.alert_end_time,
                # )
            )
        )
        return [
            self.__telegram_preference_dao_to_dto(
                telegram,
                preference,
            )
            for telegram, preference in data.tuples().all()
        ]

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
        user_id: str,
        chat_id: str,
        is_deleted: bool,
        session: AsyncSession,
    ):
        statement = """
            UPDATE telegram SET is_deleted = :is_deleted, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = :user_id AND chat_id = :chat_id
        """
        params = TelegramRepositorySchema(
            user_id=user_id,
            chat_id=chat_id,
            is_deleted=is_deleted,
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
