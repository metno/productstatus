import datetime
import dateutil.tz


def coerce_to_utc(dt):
    """!
    @brief Sets the time zone of a DateTime object to UTC.
    """
    return dt.replace(tzinfo=dateutil.tz.tzutc())


def now_with_timezone():
    """!
    @brief Return a timezone-aware UTC datetime object representing the current timestamp.
    """
    return coerce_to_utc(datetime.datetime.utcnow())
