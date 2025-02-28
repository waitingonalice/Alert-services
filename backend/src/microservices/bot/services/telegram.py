import datetime
import re
from abc import ABC, abstractmethod
from telegram import (
    Bot,
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
from src.core.depends import Depends
from src.core.regex import TWENTY_FOUR_HOUR_TIME_REGEX
from src.repository.telegram import TelegramRepository
from src.repository.preferences import PreferencesRepository
from src.schemas.telegram import (
    TelegramWeatherCommandsEnum,
    TelegramWeatherConfigEnum,
    TelegramWeatherConfigStatesEnum,
)


class BaseConversationBuilder(ABC):
    def __init__(
        self,
        application: Application,
        telegram_repo: TelegramRepository = Depends(TelegramRepository),
        preferences_repo: PreferencesRepository = Depends(PreferencesRepository),
    ):
        self.telegram_repo = telegram_repo
        self.preferences_repo = preferences_repo
        self.application = application
        self.bot: Bot = self.application.bot

    @abstractmethod
    def track_users(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        pass

    @abstractmethod
    def start_conversation(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        pass

    @abstractmethod
    def unsubscribe(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        pass


class WeatherConversationBuilder(BaseConversationBuilder):
    """
    Important links for Telegram API documentation:

    Handlers - https://docs.python-telegram-bot.org/en/v21.10/telegram.ext.basehandler.html#telegram.ext.BaseHandler.handle_update.params.context

    Application Package - https://docs.python-telegram-bot.org/en/v21.10/telegram.ext.application.html
    """

    def __init__(self, application: Application):
        super().__init__(application=application)
        self.end_convo_keyboard = [
            TelegramWeatherConfigStatesEnum.END_CONVERSATION.value
        ]

    async def __set_commands(self):
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
        await self.bot.set_my_commands(commands)

    async def __end_convo(
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
                silence_start_time="07:00",
                silence_end_time="22:00",
                session=session,
            )

    async def start_conversation(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            return
        await self.__set_commands()

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
            return ConversationHandler.END

        user = await self.telegram_repo.get_telegram_user(
            str(update.message.from_user.id),
        )
        if not user or not user.updated_at:
            return ConversationHandler.END

        days_left = (datetime.date.today() - user.updated_at.date()).days - 30
        if user.is_deleted:
            await update.message.reply_html(
                f"""
                What are you doing? You have already unsubscribed from receiving Singapore Weather Bot updates.
                \nShould you change your mind because you are indecisive 🙄, you can always resubscribe by using the /subscribe command.
                \nYou have <strong>{abs(days_left)}</strong> days left to resubscribe before your data is permanently deleted.
                \nI hope you do not have a great day ahead 🙄
                """
            )
            return ConversationHandler.END
        await self.telegram_repo.soft_delete_telegram_user(
            str(update.message.from_user.id),
            str(update.message.chat_id),
        )
        await update.message.reply_html(
            """
          You have successfully unsubscribed from receiving Singapore Weather Bot updates.
          \nYou have <strong>30</strong> days left to resubscribe before your data is permanently deleted. You can always resubscribe by using the /subscribe command.
          \nI hope you do not have a great day ahead 🙄
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
            is_deleted=False,
        )
        await update.message.reply_text(
            """
        Welcome back, I knew you will be back 🙄. You have successfully resubscribed to Singapore Weather Bot updates.
        \nIn case you have forgotten the available commands you can view them by using the /start command.
        """
        )

    ########### Configure Notifications Conversation ###########
    async def configure_notifications(
        self, update: Update, _: ContextTypes.DEFAULT_TYPE
    ) -> TelegramWeatherConfigStatesEnum:
        if not update.message or not update.message.from_user:
            return TelegramWeatherConfigStatesEnum.FALLBACK
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
        return TelegramWeatherConfigStatesEnum.SELECTING_NOTIFICATION_OPTION

    async def selected_option(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> TelegramWeatherConfigStatesEnum | int:
        if (
            not update.message
            or not update.message.from_user
            or not update.message.text
        ):
            return TelegramWeatherConfigStatesEnum.FALLBACK
        if (
            TelegramWeatherConfigStatesEnum.END_CONVERSATION.value
            == update.message.text
        ):
            return await self.__end_convo(update, context)

        selected_option = update.message.text
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

        context.user_data["selected_option"] = selected_option

        await update.message.reply_html(
            selected_option_instruction_map[selected_option],
            reply_markup=ReplyKeyboardMarkup(keyboard),
        )

        return TelegramWeatherConfigStatesEnum.ALERT_TIME

    async def configure_alert_time(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> TelegramWeatherConfigStatesEnum | int:
        if (
            not update.message
            or not update.message.from_user
            or not update.message.text
        ):
            return TelegramWeatherConfigStatesEnum.FALLBACK

        if (
            TelegramWeatherConfigStatesEnum.END_CONVERSATION.value
            == update.message.text
        ):
            return await self.__end_convo(update, context)

        user_input = update.message.text
        validate_time_input = re.match(
            TWENTY_FOUR_HOUR_TIME_REGEX,
            user_input,
        )

        if not bool(validate_time_input):
            await update.message.reply_text(
                "What is this gibberish? Please enter a valid 24-hour time format.",
            )
            return TelegramWeatherConfigStatesEnum.ALERT_TIME

        user_preference = await self.preferences_repo.get_user_preference(
            str(update.message.from_user.id),
        )
        if not user_preference:
            return TelegramWeatherConfigStatesEnum.FALLBACK

        params = {**user_preference.model_dump()}
        selected_option = str(
            context.user_data and context.user_data["selected_option"]
        )

        if TelegramWeatherConfigEnum.ALERT_START_TIME.value == selected_option:
            params["silence_start_time"] = user_input
        elif TelegramWeatherConfigEnum.ALERT_END_TIME.value == selected_option:
            params["silence_end_time"] = user_input

        await self.preferences_repo.update_preferences(
            **params,
        )

        return await self.__end_convo(
            update,
            context,
            message=f"""{selected_option} - updated to {user_input}.
            \n<i>Conversation ended</i>""",
        )

    async def fallback_conversation(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        return await self.__end_convo(
            update,
            context,
            message="I am sorry, I did not understand that. Please try again.",
        )


class WeatherConversationDirector:
    def __init__(
        self,
        builder: WeatherConversationBuilder,
        application: Application,
    ):
        self.application = application
        self.builder = builder

    def __add_notif_config_conversation_handler(self):
        conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler(
                    TelegramWeatherCommandsEnum.CONFIGURE.value,
                    self.builder.configure_notifications,
                )
            ],
            states={
                TelegramWeatherConfigStatesEnum.SELECTING_NOTIFICATION_OPTION: [
                    MessageHandler(
                        filters.TEXT,
                        self.builder.selected_option,
                    ),
                ],
                TelegramWeatherConfigStatesEnum.ALERT_TIME: [
                    MessageHandler(
                        filters.TEXT,
                        self.builder.configure_alert_time,
                    ),
                ],
                TelegramWeatherConfigStatesEnum.FALLBACK: [
                    MessageHandler(
                        filters.TEXT,
                        self.builder.fallback_conversation,
                    )
                ],
            },
            fallbacks=[
                MessageHandler(
                    filters.TEXT,
                    self.builder.fallback_conversation,
                )
            ],
        )
        self.application.add_handler(conversation_handler)

    def construct_conversation(self):
        # run track_users in its own group to not interfere with the user handlers
        self.application.add_handler(
            TypeHandler(
                Update,
                self.builder.track_users,
            ),
            group=-1,
        )
        # Commands to be added
        self.application.add_handler(
            CommandHandler(
                TelegramWeatherCommandsEnum.START.value,
                self.builder.start_conversation,
            )
        )
        self.application.add_handler(
            CommandHandler(
                TelegramWeatherCommandsEnum.UNSUBSCRIBE.value,
                self.builder.unsubscribe,
            )
        )
        self.application.add_handler(
            CommandHandler(
                TelegramWeatherCommandsEnum.SUBSCRIBE.value,
                self.builder.subscribe,
            )
        )

        self.__add_notif_config_conversation_handler()
