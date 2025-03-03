import asyncio
import datetime
import re
from typing import List
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    BotCommand,
)
from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler,
    TypeHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.sql import async_transaction
from src.core.regex import TWENTY_FOUR_HOUR_TIME_REGEX
from src.core.formatting import toddmmYYYYHHMM
from src.schemas.weather import (
    TwentyFourHourSchema,
    rain_forecast_list,
)
from src.schemas.telegram import (
    TelegramPreferenceRepositorySchema,
    TelegramWeatherCommandsEnum,
    TelegramWeatherConfigEnum,
    TelegramWeatherConversationStatesEnum,
)
from ..utils.builder import BaseConversationBuilder
from ..utils.director import BaseDirector


class WeatherService(BaseConversationBuilder):
    """
    Important links for Telegram API documentation:

    Handlers - https://docs.python-telegram-bot.org/en/v21.10/telegram.ext.basehandler.html#telegram.ext.BaseHandler.handle_update.params.context

    Application Package - https://docs.python-telegram-bot.org/en/v21.10/telegram.ext.application.html
    """

    def __init__(self):
        super().__init__()
        self.end_convo_keyboard = [
            TelegramWeatherConversationStatesEnum.END_CONVERSATION.value
        ]
        # init user_data with last_updated in memory to prevent multiple similar notifications
        self.last_updated: datetime.datetime | None = None

    async def __set_commands(self, context: ContextTypes.DEFAULT_TYPE):
        command_description_map = {
            TelegramWeatherCommandsEnum.START: "Get a welcome message and a list of usable commands",
            TelegramWeatherCommandsEnum.CONFIGURE: "Start a conversation to configure notification settings",
            TelegramWeatherCommandsEnum.SUBSCRIBE: "Resubscribe to weather alerts",
            TelegramWeatherCommandsEnum.UNSUBSCRIBE: "Unsubscribe from weather alerts",
        }
        commands = [
            BotCommand(
                command=command.value,
                description=command_description_map[command],
            )
            for command in TelegramWeatherCommandsEnum
        ]
        await context.bot.set_my_commands(commands)

    async def __end_conversation(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        message: str = "Don't leave me!!",
    ):
        if not update.message:
            return ConversationHandler.END
        if context.user_data and "selected_option" in context.user_data:
            del context.user_data["selected_option"]
            context.user_data.clear()
        await update.message.reply_html(
            message,
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    @async_transaction
    async def track_users(
        self, update: Update, _: ContextTypes.DEFAULT_TYPE, session: AsyncSession
    ):
        if not update.message or not update.message.from_user:
            return

        user_metadata = (
            str(update.message.from_user.id),
            str(update.message.chat_id),
            update.message.from_user.username,
            update.message.from_user.first_name,
            update.message.from_user.last_name,
        )
        if update.message.from_user.is_bot:
            return

        await self.telegram_repo.upsert_telegram_user(
            *user_metadata,
            session=session,
        )
        user_preference = await self.preferences_repo.get_user_preference(
            str(update.message.from_user.id),
        )
        if not user_preference:
            await self.preferences_repo.create_preferences(
                user_id=str(update.message.from_user.id),
                alert_start_time="07:00",
                alert_end_time="22:00",
                session=session,
            )

    async def start_conversation(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if not update.message:
            return
        await self.__set_commands(context)

        text = """
        Hi there👋! Its your friendly Singapore Weather Bot🌦.
I will notify you when the skies are being unfriendly.
        \nWeather updates will be sent at 7am everyday.
        \nTo configure notification settings, send the /configure command.
        \nTo stop receiving weather updates, send the /unsubscribe command.
        \nTo resubscribe to weather updates, send the /subscribe command.
        """
        await update.message.reply_html(text)

    async def unsubscribe(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.from_user:
            return

        user = await self.telegram_repo.get_telegram_user(
            str(update.message.from_user.id),
        )
        if not user or not user.updated_at:
            return

        days_left = (datetime.date.today() - user.updated_at.date()).days - 30
        if user.is_deleted:
            await update.message.reply_html(
                f"""
                What are you doing? You have already unsubscribed from receiving Singapore Weather Bot updates.
                \nShould you change your mind because you are indecisive, you can always resubscribe by using the /subscribe command.
                \nYou have <strong>{abs(days_left)}</strong> days left to resubscribe before your data is permanently deleted.
                \nI hope you do not have a great day ahead 🙄
                """
            )
            return
        await self.telegram_repo.update_is_deleted_user(
            user_id=str(update.message.from_user.id),
            chat_id=str(update.message.chat_id),
            is_deleted=True,
        )
        await update.message.reply_html(
            """
          You have successfully unsubscribed from receiving Singapore Weather Bot updates.
          \nYou have <strong>30</strong> days left to resubscribe before your data is permanently deleted. You can always resubscribe by using the /subscribe command.
          \nI hope you do not have a great day ahead.
          """
        )

    async def subscribe(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.from_user:
            return
        user = await self.telegram_repo.get_telegram_user(
            str(update.message.from_user.id),
        )
        if not user or not user.is_deleted:
            await update.message.reply_text(
                """
            I know you love me, but you are already subscribed to Singapore Weather Bot updates.
            \nIn case you have forgotten the available commands you can view them by using the /start command.
            """
            )
            return

        await self.telegram_repo.update_is_deleted_user(
            user_id=user.user_id,
            chat_id=user.chat_id,
            is_deleted=False,
        )
        await update.message.reply_text(
            """
        Welcome back, I knew you will be back. You have successfully resubscribed to Singapore Weather Bot updates.
        \nIn case you have forgotten the available commands you can view them by using the /start command.
        """
        )

    ########### Configure Notifications Conversation ###########

    async def configure_notifications(
        self, update: Update, _: ContextTypes.DEFAULT_TYPE
    ) -> TelegramWeatherConversationStatesEnum:
        """
        Entry point for configuring notification settings.

        User has three options to choose from:
        1. Start time of alerts
        2. End time of alerts
        3. End conversation

        Proceeds to `SELECTING_NOTIFICATION_OPTION` state
        """
        if not update.message or not update.message.from_user:
            return TelegramWeatherConversationStatesEnum.FALLBACK
        text = """
        Please select the notification settings that you would like to configure.
        """
        keyboard = [
            [TelegramWeatherConfigEnum.ALERT_START_TIME.value],
            [TelegramWeatherConfigEnum.ALERT_END_TIME.value],
            self.end_convo_keyboard,
        ]
        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(keyboard),
        )
        return TelegramWeatherConversationStatesEnum.SELECTING_NOTIFICATION_OPTION

    async def selected_option(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> TelegramWeatherConversationStatesEnum | int:
        """
        Processes the selected option from the user and replies accordinly.
        Proceeds to `ALERT_TIME` state or ends the conversation.
        """
        if (
            not update.message
            or not update.message.from_user
            or not update.message.text
        ):
            return TelegramWeatherConversationStatesEnum.FALLBACK
        if (
            TelegramWeatherConversationStatesEnum.END_CONVERSATION.value
            == update.message.text
        ):
            return await self.__end_conversation(update, context)

        selected_option = update.message.text
        if selected_option not in [
            option.value for option in TelegramWeatherConfigEnum
        ]:
            await update.message.reply_text(
                "What is this gibberish? Please select a valid option.",
            )
            return TelegramWeatherConversationStatesEnum.SELECTING_NOTIFICATION_OPTION

        selected_option_instruction_map = {
            TelegramWeatherConfigEnum.ALERT_START_TIME.value: """
            Please specify the start time you would like to start receiving alerts.
            \nExample: <code>07:00</code>
            \n<strong>Time should be in 24-hour format. Default time is set to 0700 hours.</strong>
            """,
            TelegramWeatherConfigEnum.ALERT_END_TIME.value: """
            Please specify the end time you would like to receive alerts.
            \nExample: <code>22:00</code>
            \n<strong>Time should be in 24-hour format. Default time is set to 22:00 hours.</strong>
            """,
        }
        keyboard = [self.end_convo_keyboard]

        if context.user_data is not None:
            context.user_data["selected_option"] = selected_option

        await update.message.reply_html(
            selected_option_instruction_map[selected_option],
            reply_markup=ReplyKeyboardMarkup(keyboard),
        )

        return TelegramWeatherConversationStatesEnum.ALERT_TIME

    async def configure_alert_time(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> TelegramWeatherConversationStatesEnum | int:
        if (
            not update.message
            or not update.message.from_user
            or not update.message.text
        ):
            return TelegramWeatherConversationStatesEnum.FALLBACK

        if (
            TelegramWeatherConversationStatesEnum.END_CONVERSATION.value
            == update.message.text
        ):
            return await self.__end_conversation(update, context)

        user_input = update.message.text
        validate_time_input = re.match(
            TWENTY_FOUR_HOUR_TIME_REGEX,
            user_input,
        )

        if not bool(validate_time_input):
            await update.message.reply_text(
                "What is this gibberish? Please enter a valid 24-hour time format.",
            )
            return TelegramWeatherConversationStatesEnum.ALERT_TIME

        user_preference = await self.preferences_repo.get_user_preference(
            str(update.message.from_user.id),
        )
        if not user_preference:
            return TelegramWeatherConversationStatesEnum.FALLBACK

        params = {**user_preference.model_dump()}
        selected_option = str(
            context.user_data and context.user_data["selected_option"]
        )

        if TelegramWeatherConfigEnum.ALERT_START_TIME.value == selected_option:
            params["alert_start_time"] = user_input
        elif TelegramWeatherConfigEnum.ALERT_END_TIME.value == selected_option:
            params["alert_end_time"] = user_input

        await self.preferences_repo.update_preferences(
            **params,
        )

        return await self.__end_conversation(
            update,
            context,
            message=f"""{selected_option} - updated to {user_input}.
            \n<i>Conversation ended</i>""",
        )

    async def fallback_conversation(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        return await self.__end_conversation(
            update,
            context,
            message="I am sorry, there was an error processing your request, ending conversation.",
        )

    ########### End of Configure Notifications Conversation ###########

    def __get_weather_update(self):
        now = datetime.datetime.now()
        return self.weather_connector.get_24_hour_forecast_sg(now)

    def __is_going_to_rain(self, forecast: TwentyFourHourSchema) -> bool:
        return forecast.data.records[0].general.forecast.text in rain_forecast_list

    def __update_last_updated(self, dt: datetime.datetime):
        self.last_updated = dt

    # async def send_weather_update(self):
    #     """
    #     Method to send push notification to singular subscribed user on request.
    #     """

    #     pass

    async def send_weather_update_to_users(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Method to send push notification to all users subscribed to weather updates.
        """
        current_forecast = self.__get_weather_update()
        if not current_forecast:
            return
        record = current_forecast.data.records[0]
        valid_period = record.general.validPeriod
        forecast = record.general.forecast.text

        message = f"""
        It seems like the weather is going to be unfriendly today ⛈️.
        \nCurrent forecast: <strong>{forecast.value}</strong>
        \nTemperatures: <strong>{record.general.temperature.low}°C - {record.general.temperature.high}°C</strong>
        \nForecast validity: <strong>{toddmmYYYYHHMM(valid_period.start)}</strong> - <strong>{toddmmYYYYHHMM(valid_period.end)}</strong>
Last updated: <i>{toddmmYYYYHHMM(record.updatedTimestamp)}</i>.
        """

        if (
            self.__is_going_to_rain(current_forecast)
            and self.last_updated != record.updatedTimestamp
        ):
            user_list: List[
                TelegramPreferenceRepositorySchema
            ] = await self.telegram_repo.list_subscribed_users_within_timeframe()
            self.__update_last_updated(record.updatedTimestamp)

            async def send_message(user: TelegramPreferenceRepositorySchema):
                # TODO: add functionality for user to receive locational weather updates with button selection
                await context.bot.send_message(
                    chat_id=user.telegram.chat_id,
                    text=message,
                    parse_mode="HTML",
                )

            # Similar to nodejs Promise.all
            await asyncio.gather(*[send_message(user) for user in user_list])


class WeatherConversationDirector(BaseDirector):
    def __init__(
        self,
        application: Application,
        service: WeatherService,
    ):
        super().__init__(application)
        self.service = service

    def __config_conversation_handler(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[
                CommandHandler(
                    TelegramWeatherCommandsEnum.CONFIGURE.value,
                    self.service.configure_notifications,
                )
            ],
            states={
                TelegramWeatherConversationStatesEnum.SELECTING_NOTIFICATION_OPTION: [
                    MessageHandler(
                        filters.TEXT,
                        self.service.selected_option,
                    ),
                ],
                TelegramWeatherConversationStatesEnum.ALERT_TIME: [
                    MessageHandler(
                        filters.TEXT,
                        self.service.configure_alert_time,
                    ),
                ],
                TelegramWeatherConversationStatesEnum.FALLBACK: [
                    MessageHandler(
                        filters.TEXT,
                        self.service.fallback_conversation,
                    )
                ],
            },
            fallbacks=[
                MessageHandler(
                    filters.TEXT,
                    self.service.fallback_conversation,
                )
            ],
        )

    def construct(self):
        # run track_users in its own group to not interfere with the user handlers
        self.application.add_handler(
            TypeHandler(
                Update,
                self.service.track_users,
                block=False,
            ),
            group=-1,
        )
        # Commands to be added
        self.application.add_handler(
            CommandHandler(
                TelegramWeatherCommandsEnum.START.value,
                self.service.start_conversation,
                block=False,
            )
        )
        self.application.add_handler(
            CommandHandler(
                TelegramWeatherCommandsEnum.UNSUBSCRIBE.value,
                self.service.unsubscribe,
                block=False,
            )
        )
        self.application.add_handler(
            CommandHandler(
                TelegramWeatherCommandsEnum.SUBSCRIBE.value,
                self.service.subscribe,
                block=False,
            )
        )
        self.application.add_handler(
            self.__config_conversation_handler(),
        )
