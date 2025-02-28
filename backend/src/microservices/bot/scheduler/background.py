from typing import Callable
from apscheduler.schedulers.background import BackgroundScheduler


class Scheduler:
    def __init__(
        self,
    ):
        self.scheduler = BackgroundScheduler()

    def add_job(
        self,
        func: Callable,
        trigger: str,
        **kwargs,
    ):
        hours, minutes, seconds = (
            kwargs.get("hours", 0),
            kwargs.get("minutes", 0),
            kwargs.get("seconds", 0),
        )
        self.scheduler.add_job(
            func,
            trigger,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            replace_existing=True,
        )

    def start(self):
        print("CRON Service - Starting scheduler...")
        self.scheduler.start()
        print("CRON Service - Scheduler started.")

    def kill(self):
        print("CRON Service - Shutting down scheduler...")
        self.scheduler.remove_all_jobs()
        self.scheduler.shutdown()
        print("CRON Service - Scheduler shutdown.")
