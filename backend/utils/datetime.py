from datetime import datetime, timezone
from dateutil import parser
import pytz
import tzlocal


def get_current_server_time_in_iso():
    return datetime.now().isoformat()


def get_current_server_time():
    now = datetime.now(tzlocal.get_localzone())
    return now.strftime("%Y-%m-%d %H:%M:%S %Z%z")


def get_day_range_utc(datetime_string):
    """
    Takes a datetime string and returns start and end of that day in UTC format
    """
    try:
        # Parse the input datetime string (handles timezone automatically)
        dt = parser.parse(datetime_string)

        # Convert to UTC if it has timezone info
        if dt.tzinfo is not None:
            dt_utc = dt.astimezone(timezone.utc)
        else:
            # If no timezone info, assume it's already UTC
            dt_utc = dt.replace(tzinfo=timezone.utc)

        # Get the date part and create start of day (00:00:00)
        date_part = dt_utc.date()
        start_of_day = datetime.combine(date_part, datetime.min.time(), timezone.utc)

        # Create end of day (23:59:59)
        end_of_day = datetime.combine(date_part, datetime.max.time(), timezone.utc)
        # Replace microseconds to get clean 23:59:59
        end_of_day = end_of_day.replace(microsecond=0)

        return {
            "start": start_of_day.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": end_of_day.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    except Exception as e:
        # @TODO: return error status and message
        raise ValueError(f"Error parsing datetime string '{datetime_string}': {str(e)}")


def convert_to_utc_format(datetime_string, user_timezone=None):
    """
    Convert any ISO datetime string to UTC format
    """
    try:
        # Parse the input datetime string (handles timezone automatically)
        dt = parser.parse(datetime_string)

        # Convert to UTC if it has timezone info
        if dt.tzinfo is not None:
            dt_utc = dt.astimezone(timezone.utc)
        else:
            # If no timezone info, use the provided user_timezone or assume UTC
            if user_timezone:
                # Apply the user's timezone to the naive datetime
                user_tz = pytz.timezone(user_timezone)
                dt_with_tz = user_tz.localize(dt)
                dt_utc = dt_with_tz.astimezone(timezone.utc)
            else:
                # If no timezone info and no user timezone provided, assume it's already UTC
                dt_utc = dt.replace(tzinfo=timezone.utc)

        # Return in clean UTC format ending with Z including milliseconds
        return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    except Exception as e:
        # @TODO: return error status and message
        raise ValueError(f"Error parsing datetime string '{datetime_string}': {str(e)}")
