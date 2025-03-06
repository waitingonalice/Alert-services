import os
import signal
from telegram import Update
from telegram.ext import (
    Application,
)

from src.core.config import settings
from .services.weather import (
    WeatherService,
    WeatherConversationDirector,
)
from .services.telegram import (
    TelegramService,
    TelegramServiceDirector,
)

application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
count = 0
max_retry_count = 5

weather_convo = WeatherService()
weather_convo_director = WeatherConversationDirector(
    application=application,
    service=weather_convo,
)
telegram_service = TelegramService()
telegram_service_director = TelegramServiceDirector(
    application=application,
    service=telegram_service,
    weather_service=weather_convo,
)


def main():
    try:
        # TODO: Redis init and integration for caching user data
        weather_convo_director.construct()
        telegram_service_director.construct()
        print("Weather Bot Service - Running")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
    except Exception as e:
        print(f"Weather Bot Service - Error: {e}")
        os.kill(1, signal.SIGTERM)


if __name__ == "__main__":
    main()
