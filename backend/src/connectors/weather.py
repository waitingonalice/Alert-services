import datetime
from src.core.routes import open_gov_v2_endpoint
from src.core.fetch import fetch
from src.schemas.weather import TwentyFourHourParams, TwentyFourHourSchema


class WeatherConnector:
    def get_24_hour_forecast_sg(
        self,
        datetime: datetime.datetime,
    ) -> TwentyFourHourSchema | None:
        # formatted datetime string to be parsed YYYY-MM-DDTHH:mm:ss
        format_datetime_param = datetime.strftime("%Y-%m-%dT%H:%M:%S")

        response = fetch(
            url=open_gov_v2_endpoint.twenty_four_hour_weather_forecast,
            params=TwentyFourHourParams(date=format_datetime_param),
        )
        if not response:
            return None

        return TwentyFourHourSchema(**response.json())
