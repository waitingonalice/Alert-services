from enum import Enum


class EnvironmentEnum(Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class FetchMethodEnum(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
