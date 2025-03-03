from src.core.config import settings


class OpenGovEndpointV2:
    BASE_URL = f"{settings.OPEN_GOV_ENDPOINT}/v2"

    # Routes here
    twenty_four_hour_weather_forecast = (
        f"{BASE_URL}/real-time/api/twenty-four-hr-forecast"
    )
    four_day_weather_forecast = f"{BASE_URL}/real-time/api/four-day-outlook"


class TelegramEndpoint:
    BASE_URL = f"{settings.TELEGRAM_ENDPOINT}/bot"

    # Routes here
    send_message = f"{BASE_URL}/sendMessage"


open_gov_v2_endpoint = OpenGovEndpointV2()
telegram_endpoint = TelegramEndpoint()
