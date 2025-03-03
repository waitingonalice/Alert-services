import os
import signal
import time
from telegram import Update
from telegram.ext import (
    Application,
)

from .services.telegram import (
    WeatherConversationBuilder,
    WeatherConversationDirector,
)
from src.core.config import settings

application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
count = 0
max_retry_count = 5

# Instantiate Telegram weather bot conversation
weather_conversation_builder = WeatherConversationBuilder(application=application)
weather_conversation_director = WeatherConversationDirector(
    builder=weather_conversation_builder,
    application=application,
)
weather_conversation_director.construct_conversation()

# Instantiate push notification for weather updates from bot


def main(count: int):
    try:
        # TODO: Redis init and integration for caching user data
        # Start the bot + jobs here
        print("Bot Service - Bot is running...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )

    except Exception as e:
        if count == max_retry_count:
            print("Bot Service - Failed to initialise application. Exiting...")
            os.kill(1, signal.SIGTERM)
        print(f"Bot Service - Error: {e}")
        print(f"Bot Service - Retry count: {count}. Retrying in 10 seconds...")
        time.sleep(10)
        if count < max_retry_count:
            main(count + 1)


if __name__ == "__main__":
    main(count)
