import datetime


def toddmmYYYYHHMM(date: datetime.datetime) -> str:
    return date.strftime("%d/%m/%Y %H:%M")
