import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ForecastTextEnum(Enum):
    F = "Fair"
    FD = "Fair (Day)"
    FN = "Fair (Night)"
    FW = "Fair and Warm"
    PC = "Partly Cloudy"
    PCD = "Partly Cloudy (Day)"
    PCN = "Partly Cloudy (Night)"
    C = "Cloudy"
    H = "Hazy"
    SH = "Slightly Hazy"
    W = "Windy"
    M = "Mist"
    FG = "Fog"
    LR = "Light Rain"
    MR = "Moderate Rain"
    HR = "Heavy Rain"
    PS = "Passing Showers"
    LS = "Light Showers"
    S = "Showers"
    HS = "Heavy Showers"
    TS = "Thundery Showers"
    HTS = "Heavy Thundery Showers"
    HTSGW = "Heavy Thundery Showers with Gusty Winds"


rain_forecast_list = [
    ForecastTextEnum.LR,
    ForecastTextEnum.MR,
    ForecastTextEnum.HR,
    ForecastTextEnum.PS,
    ForecastTextEnum.LS,
    ForecastTextEnum.S,
    ForecastTextEnum.HS,
    ForecastTextEnum.TS,
    ForecastTextEnum.HTS,
    ForecastTextEnum.HTSGW,
]


################## Start of Primitive Data ##################
class TemperatureSchema(BaseModel):
    low: int
    high: int
    unit: str


class HumiditySchema(BaseModel):
    low: int
    high: int
    unit: str


class ForecastSchema(BaseModel):
    text: ForecastTextEnum
    code: str


class ValidPeriodSchema(BaseModel):
    start: datetime.datetime
    end: datetime.datetime
    text: str


class SpeedSchema(BaseModel):
    low: int
    high: int


class WindSchema(BaseModel):
    speed: SpeedSchema
    direction: str


################## End of Primitive Data ##################


class GeneralSchema(BaseModel):
    temperature: TemperatureSchema
    relativeHumidity: HumiditySchema
    forecast: ForecastSchema
    validPeriod: ValidPeriodSchema
    wind: WindSchema


class TimePeriodSchema(BaseModel):
    start: datetime.datetime
    end: datetime.datetime
    text: str


class AreaSchema(BaseModel):
    code: str
    text: ForecastTextEnum


class RegionSchema(BaseModel):
    west: AreaSchema
    east: AreaSchema
    central: AreaSchema
    south: AreaSchema
    north: AreaSchema


class SegmentedPeriodSchema(BaseModel):
    timePeriod: TimePeriodSchema
    regions: RegionSchema


class RecordSchema(BaseModel):
    date: datetime.date
    updatedTimestamp: datetime.datetime
    general: GeneralSchema
    periods: List[SegmentedPeriodSchema]
    timestamp: datetime.datetime


class ListRecordSchema(BaseModel):
    records: List[RecordSchema]


class TwentyFourHourSchema(BaseModel):
    code: int
    data: ListRecordSchema
    errorMsg: Optional[str] = None
    paginationToken: Optional[str] = None

    model_config = ConfigDict(
        extra="allow",
    )


class TwentyFourHourParams(BaseModel):
    date: str


# Example JSON response
# json = {
#     "code": 0,
#     "data": {
#         "records": [
#             {
#                 "date": "2025-03-02",
#                 "updatedTimestamp": "2025-03-02T11:40:55+08:00",
#                 "general": {
#                     "temperature": {"low": 25, "high": 34, "unit": "Degrees Celsius"},
#                     "relativeHumidity": {"low": 55, "high": 95, "unit": "Percentage"},
#                     "forecast": {"code": "TL", "text": "Thundery Showers"},
#                     "validPeriod": {
#                         "start": "2025-03-02T12:00:00+08:00",
#                         "end": "2025-03-03T12:00:00+08:00",
#                         "text": "12 PM 2 Mar to 12 PM 3 Mar",
#                     },
#                     "wind": {"speed": {"low": 10, "high": 20}, "direction": "NE"},
#                 },
#                 "periods": [
#                     {
#                         "timePeriod": {
#                             "start": "2025-03-02T12:00:00+08:00",
#                             "end": "2025-03-02T18:00:00+08:00",
#                             "text": "Midday to 6 pm 02 Mar",
#                         },
#                         "regions": {
#                             "west": {"code": "TL", "text": "Thundery Showers"},
#                             "east": {"code": "PC", "text": "Partly Cloudy (Day)"},
#                             "central": {"code": "TL", "text": "Thundery Showers"},
#                             "south": {"code": "TL", "text": "Thundery Showers"},
#                             "north": {"code": "PC", "text": "Partly Cloudy (Day)"},
#                         },
#                     },
#                     {
#                         "timePeriod": {
#                             "start": "2025-03-02T18:00:00+08:00",
#                             "end": "2025-03-03T06:00:00+08:00",
#                             "text": "6 pm 02 Mar to 6 am 03 Mar",
#                         },
#                         "regions": {
#                             "west": {"code": "PN", "text": "Partly Cloudy (Night)"},
#                             "east": {"code": "PN", "text": "Partly Cloudy (Night)"},
#                             "central": {"code": "PN", "text": "Partly Cloudy (Night)"},
#                             "south": {"code": "PN", "text": "Partly Cloudy (Night)"},
#                             "north": {"code": "PN", "text": "Partly Cloudy (Night)"},
#                         },
#                     },
#                     {
#                         "timePeriod": {
#                             "start": "2025-03-03T06:00:00+08:00",
#                             "end": "2025-03-03T12:00:00+08:00",
#                             "text": "6 am to Midday 03 Mar",
#                         },
#                         "regions": {
#                             "west": {"code": "PC", "text": "Partly Cloudy (Day)"},
#                             "east": {"code": "PC", "text": "Partly Cloudy (Day)"},
#                             "central": {"code": "PC", "text": "Partly Cloudy (Day)"},
#                             "south": {"code": "PC", "text": "Partly Cloudy (Day)"},
#                             "north": {"code": "PC", "text": "Partly Cloudy (Day)"},
#                         },
#                     },
#                 ],
#                 "timestamp": "2025-03-02T11:37:00+08:00",
#             }
#         ]
#     },
#     "errorMsg": "",
# }
