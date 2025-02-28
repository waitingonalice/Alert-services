from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.preferences import PreferencesRepositorySchema
from ..models.preferences import Preferences as PreferencesDAO
from ..core.sql import async_session, async_transaction
from ..core.depends import Depends


class PreferencesRepository:
    def __init__(self, session: AsyncSession = Depends(async_session)):
        self.session = session

    def __dao_to_dto(self, dao: PreferencesDAO):
        return PreferencesRepositorySchema(
            id=dao.id,
            silence_start_time=dao.silence_start_time,
            silence_end_time=dao.silence_end_time,
        )

    async def get_user_preference(
        self, user_id: str
    ) -> PreferencesRepositorySchema | None:
        preferences_data = await self.session.execute(
            select(PreferencesDAO).where(PreferencesDAO.id == user_id)
        )
        preferences = preferences_data.scalar_one_or_none()
        if not preferences:
            return None
        return self.__dao_to_dto(preferences)

    async def create_preferences(
        self,
        user_id: str,
        session: AsyncSession,
        silence_start_time: str,
        silence_end_time: str,
    ):
        preferences = PreferencesRepositorySchema(
            id=user_id,
            silence_start_time=silence_start_time,
            silence_end_time=silence_end_time,
        )

        statement = """
            INSERT INTO preferences (id, silence_start_time, silence_end_time)
            VALUES (:id, :silence_start_time, :silence_end_time)
        """

        await session.execute(
            text(statement),
            preferences.model_dump(),
        )

    @async_transaction
    async def update_preferences(
        self,
        id: str,
        silence_start_time: str,
        silence_end_time: str,
        session: AsyncSession,
    ):
        statement = """
            UPDATE preferences
            SET silence_start_time = :silence_start_time, silence_end_time = :silence_end_time
            WHERE id = :id
        """
        params = PreferencesRepositorySchema(
            id=id,
            silence_start_time=silence_start_time,
            silence_end_time=silence_end_time,
        )
        await session.execute(
            text(statement),
            params=params.model_dump(),
        )
