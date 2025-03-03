import datetime
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
            alert_start_time=dao.alert_start_time,
            alert_end_time=dao.alert_end_time,
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
        alert_start_time: datetime.time | str,
        alert_end_time: datetime.time | str,
    ):
        preferences = PreferencesRepositorySchema(
            id=user_id,
            alert_start_time=alert_start_time,
            alert_end_time=alert_end_time,
        )

        statement = """
            INSERT INTO preferences (id, alert_start_time, alert_end_time)
            VALUES (:id, :alert_start_time, :alert_end_time)
        """

        await session.execute(
            text(statement),
            preferences.model_dump(),
        )

    @async_transaction
    async def update_preferences(
        self,
        id: str,
        alert_start_time: datetime.time | str,
        alert_end_time: datetime.time | str,
        session: AsyncSession,
    ):
        statement = """
            UPDATE preferences
            SET alert_start_time = :alert_start_time, alert_end_time = :alert_end_time
            WHERE id = :id
        """
        params = PreferencesRepositorySchema(
            id=id,
            alert_start_time=alert_start_time,
            alert_end_time=alert_end_time,
        )
        await session.execute(
            text(statement),
            params=params.model_dump(),
        )
