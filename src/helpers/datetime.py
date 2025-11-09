import datetime


def get_current_datetime_YYYYMMDDHHMMSS() -> str:
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def get_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
