import datetime
from typing import List
from telegram.ext import Application, ContextTypes
from .weather import WeatherService
from src.schemas.telegram import TelegramAddJobSchema
from src.core.depends import Depends
from src.repository.telegram import TelegramRepository
from ..utils.director import BaseDirector


class TelegramService:
    def __init__(
        self,
        telegram_repo: TelegramRepository = Depends(TelegramRepository),
    ):
        self.telegram_repo = telegram_repo

    async def clean_up_user(self, _: ContextTypes.DEFAULT_TYPE):
        await self.telegram_repo.hard_delete_telegram_users()


class TelegramServiceDirector(BaseDirector):
    def __init__(
        self,
        application: Application,
        service: TelegramService,
        weather_service: WeatherService,
    ):
        super().__init__(application)
        self.weather_service = weather_service
        self.service = service
        self.job_list: List[TelegramAddJobSchema] = []

    def __add_job(
        self,
        schema: TelegramAddJobSchema,
    ):
        self.job_list.append(schema)

    def __run_all_jobs(self):
        job_queue = self.application.job_queue
        if not job_queue:
            return
        for job in self.job_list:
            job_queue.run_repeating(
                callback=job.callback,
                interval=job.interval,
                first=job.first,
            )

    def construct(self):
        self.__add_job(
            TelegramAddJobSchema(
                callback=self.service.clean_up_user,
                interval=datetime.timedelta(hours=24),
            )
        )
        # check and send weather updates every hour to subscribed users
        self.__add_job(
            TelegramAddJobSchema(
                callback=self.weather_service.send_weather_update_to_users,
                interval=datetime.timedelta(minutes=60),
                first=datetime.timedelta(seconds=10),
            )
        )

        self.__run_all_jobs()
