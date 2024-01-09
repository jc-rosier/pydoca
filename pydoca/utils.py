import datetime


def utc_now() -> datetime.datetime:
    """Datetime now with utc timezone aware."""
    return datetime.datetime.now(tz=datetime.timezone.utc)
