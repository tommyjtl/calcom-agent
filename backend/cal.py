# System imports
import time
import requests

# Logging imports
from loguru import logger

# Utils imports
from enum import Enum
from utils.datetime import convert_to_utc_format, get_day_range_utc


# Function return status and code enums
class FunctionReturnStatus(Enum):
    ERROR = "error"
    SUCCESS = "success"


# Function return codes
class FunctionReturnCode(Enum):
    CALCOM_API_REQUEST_FAILED = "calcom_api_request_failed"
    UNEXPECTED_RESPONSE_FORMAT = "unexpected_response_format"
    FOUND_MATCH = "found_match"
    NO_MATCH = "no_match"
    SLOTS_REQUEST_FAILED = "slots_request_failed"
    ALL_MATCHED = "all_matched"
    AVAILABILITY_NO_EXACT_MATCH = "availability_no_exact_match"
    #
    LIST_ALL_CAL_BOOKINGS_SUCCESS = "list_all_cal_bookings_success"
    LIST_ALL_CAL_BOOKINGS_EMPTY = "list_all_cal_bookings_empty"
    #
    BOOKING_FOUND_AND_CANCELLED = "booking_found_and_cancelled"
    BOOKING_NOT_FOUND = "booking_not_found"
    BOOKING_CANCELLATION_FAILED = "booking_cancellation_failed"
    #
    UNKNOWN = "unknown"


# Template for function return
def function_return(
    status: FunctionReturnStatus,
    result_code: FunctionReturnCode,
    result_message: str,
    result_data: dict,
) -> dict:  # function return template for this class
    return {
        "status": status.value,
        "result": {
            "code": result_code.value,
            "message": result_message,
            "data": result_data,
        },
    }


class CalComTool:
    """
    CalComTool class for interacting with the Cal.com API
    - @TODO: Add flag to disable logging in production
    """

    def __init__(self, api_key=None):
        logger.debug("Initializing CalComTool...")

        if not api_key:
            # An API key must be presented to continue
            raise ValueError("Please provide a Cal.com API Key.")

        self.api_endpoint_prefix = "https://api.cal.com/v2/"
        self.api_key = api_key
        self.default_api_version = "2024-06-14"
        self.headers = {
            "Authorization": f"{self.api_key}",
            "Content-Type": "application/json",
            "cal-api-version": self.default_api_version,
        }

        # Check if the API key is valid on instantiation
        if not self.is_api_validity():
            raise ValueError("The Cal.com API Key provided is not valid.")

        logger.debug("Cal.com API Key successfully loaded")

        # Use the same owner just for demo purpose
        # We are only going to book a meeting with the same person
        self.user_id = 1650861
        self.user_name = "tommyjtl"

    def is_api_validity(self):
        response = self.get_my_profile()
        # {
        #   'status': 'error',
        #   'error': '401 Client Error: Unauthorized for url: https://api.cal.com/v2/me'
        # }
        if response["status"] == "error" and "Unauthorized" in response["error"]:
            return False
        return True

    def get_request(self, action, params=None, sub_path="", api_version=None):
        full_endpoint_url = f"{self.api_endpoint_prefix}{action}{sub_path}"
        headers = self.headers.copy()  # Create a copy to avoid mutation

        if api_version != None:
            headers["cal-api-version"] = api_version

        try:
            if params == None:
                response = requests.get(full_endpoint_url, headers=headers)
            else:
                response = requests.get(
                    full_endpoint_url, headers=headers, params=params
                )

            # Add a small delay to avoid rate limiting
            time.sleep(0.1)

            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"status": "error", "error": str(e)}

    def post_request(self, action, payload, sub_path="", api_version=None):
        full_endpoint_url = f"{self.api_endpoint_prefix}{action}{sub_path}"
        headers = self.headers.copy()  # Create a copy to avoid mutation

        if api_version != None:
            headers["cal-api-version"] = api_version

        try:
            response = requests.post(
                full_endpoint_url,
                headers=headers,
                json=payload,
            )

            # Add a small delay to avoid rate limiting
            time.sleep(0.1)

            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"status": "error", "error": str(e)}

    """
    Cal.com API Wrappers
    """

    def get_all_event_types(self):
        # https://cal.com/docs/api-reference/v2/event-types/get-all-event-types

        action = "event-types"
        params = {"username": self.user_name}

        # Retry logic in case of endpoint error
        max_retries = 3  # Allow at most 3 tries
        for attempt in range(max_retries):

            try:
                result = self.get_request(action, params=params)
                if "error" not in result:
                    return result
                logger.warning(f"Attempt {attempt + 1} failed: {result.get('error')}")
                if attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed with exception: {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))
                else:
                    return {"status": "error", "error": str(e)}

        return result

    def create_an_event_type(self, length_in_minutes, title, slug):
        # https://cal.com/docs/api-reference/v2/event-types/create-an-event-type

        action = "event-types"
        payload = {
            "lengthInMinutes": length_in_minutes,
            "title": title,
            "slug": slug,
            # "description": "", # Not needed for this demo
            "bookingFields": [
                {
                    "type": "name",
                    "label": "Name",
                    "placeholder": "John Doe",
                    "disableOnPrefill": True,
                }
            ],
            "bookingWindow": {"type": "businessDays", "value": 5, "rolling": True},
            "bookerLayouts": {"defaultLayout": "month", "enabledLayouts": ["month"]},
            "confirmationPolicy": {"disabled": True},
            "recurrence": {"disabled": True},
            "color": {"lightThemeHex": "#292929", "darkThemeHex": "#fafafa"},
            "locations": [{"type": "integration", "integration": "google-meet"}],
        }

        return self.post_request(action, payload=payload)

    def get_an_event_type(self, event_type_id):
        # https://cal.com/docs/api-reference/v2/event-types/get-an-event-type

        action = "event-types"
        sub_path = f"/{event_type_id}"

        return self.get_request(action, sub_path=sub_path)

    def get_available_time_slots(self, event_type_id, start, end):
        # https://cal.com/docs/api-reference/v2/slots/get-available-time-slots-for-an-event-type

        action = "slots"
        params = {"eventTypeId": event_type_id, "start": start, "end": end}

        return self.get_request(action, params=params, api_version="2024-09-04")

    def create_a_booking(
        self,
        start_datetime,
        event_type_id,
        name="Tomas",
        email="jingtao8@illinois.edu",
        time_zone="America/Los_Angeles",
        notes="This is an example note for this booking.",
    ):
        # https://cal.com/docs/api-reference/v2/bookings/create-a-booking

        action = "bookings"
        payload = {
            "start": start_datetime,
            "eventTypeId": event_type_id,
            "attendee": {
                "name": name,
                "email": email,
                "timeZone": time_zone,
            },
            "bookingFieldsResponses": {"notes": notes},
            # "metadata": {}, # no additional key-value pairs needed at the moment
        }

        return self.post_request(action, payload, api_version="2024-08-13")

    def get_all_bookings(
        self,
        attendee_email,
        status="upcoming",
        #  event_type_ids=[] # we aren't using this for this demo
    ):
        # https://cal.com/docs/api-reference/v2/bookings/get-all-bookings

        action = "bookings"
        params = {
            "take": "20",
            "sortStart": "asc",
            "status": status,
            "attendeeEmail": attendee_email,
        }

        return self.get_request(action, params=params, api_version="2024-08-13")

    def cancel_a_booking(self, booking_uid: str):
        # https://cal.com/docs/api-reference/v2/bookings/cancel-a-booking

        action = f"bookings/{booking_uid}/cancel"
        payload = {
            "cancellationReason": "User requested cancellation",
            "cancelSubsequentBookings": False,
        }

        return self.post_request(action, payload, api_version="2024-08-13")

    def get_my_profile(self):
        return self.get_request("me")

    """
    Functional call wrappers
    """

    def find_event_id_by_name(self, event_name):
        """
        Find the closest matching event type using simple string similarity.
        Returns the best matching event or an error if no match is found.
        """
        logger.debug(f"Looking for event with name: {event_name}")
        response = self.get_all_event_types()

        # Check if the response has an error key (from our improved error handling)
        if "error" in response:
            logger.error(f"API request failed: {response['error']}")
            return function_return(
                status=FunctionReturnStatus.ERROR,
                result_code=FunctionReturnCode.CALCOM_API_REQUEST_FAILED,
                result_message="Request to Cal.com API failed",
                result_data=response["error"],
            )

        # Check the response structure - Cal.com might return different formats
        if response.get("status") == "error":
            return function_return(
                status=FunctionReturnStatus.ERROR,
                result_code=FunctionReturnCode.CALCOM_API_REQUEST_FAILED,
                result_message="Request to Cal.com API failed",
                result_data=response.get("error", response),
            )

        # Handle case where response doesn't have expected 'data' field
        if "data" not in response:
            logger.error(f"Unexpected response format: {response}")
            return function_return(
                status=FunctionReturnStatus.ERROR,
                result_code=FunctionReturnCode.UNEXPECTED_RESPONSE_FORMAT,
                result_message="Unexpected response format from Cal.com API",
                result_data=response,
            )

        event_name_lower = event_name.lower().strip()
        best_match = None
        best_score = 0

        for event in response["data"]:
            title = event["title"].lower()
            slug = event["slug"].lower()

            # Exact match gets highest priority
            if event_name_lower == title or event_name_lower == slug:
                return function_return(
                    status=FunctionReturnStatus.SUCCESS,
                    result_code=FunctionReturnCode.FOUND_MATCH,
                    result_message="Found the exact match",
                    result_data={
                        "title": event["title"],
                        "slug": event["slug"],
                        "id": event["id"],
                    },
                )

            # Check if event name is contained in title or slug
            if event_name_lower in title or event_name_lower in slug:
                score = len(event_name_lower) / max(len(title), len(slug))
                if score > best_score:
                    best_score = score
                    best_match = event

            # Check if title/slug is contained in event name
            if title in event_name_lower or slug in event_name_lower:
                score = len(title) / len(event_name_lower)
                if score > best_score:
                    best_score = score
                    best_match = event

        if best_match:
            return function_return(
                status=FunctionReturnStatus.SUCCESS,
                result_code=FunctionReturnCode.FOUND_MATCH,
                result_message="Found the best match",
                result_data={
                    "title": best_match["title"],
                    "slug": best_match["slug"],
                    "id": best_match["id"],
                },
            )

        event_type_ids = []
        if response["status"] == "success":
            for d in response["data"]:
                event_type_ids.append(
                    {"title": d["title"], "slug": d["slug"], "id": d["id"]}
                )

        return function_return(
            status=FunctionReturnStatus.ERROR,
            result_code=FunctionReturnCode.NO_MATCH,
            result_message=f"No matching event found for '{event_name}'",
            result_data=event_type_ids,
        )

    def create_a_cal_booking_fc(self):
        return {
            "type": "function",
            "function": {
                "name": "create_a_cal_booking",
                "description": "Create a booking/event for a user for a specific event name at a given time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_name": {
                            "type": "string",
                            "description": "The name of the event to book.",
                        },
                        "datetime_start": {
                            "type": "string",
                            "description": "The start datetime for the booking in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.000-00:00).",
                        },
                        "timezone": {
                            "type": "string",
                            "description": "The timezone for the booking, e.g., 'America/Los_Angeles'.",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reasons for the booking.",
                        },
                        "user_email": {
                            "type": "string",
                            "description": "The email of the user making the booking.",
                        },
                        "user_name": {
                            "type": "string",
                            "description": "The name of the user making the booking.",
                        },
                    },
                    "required": [
                        "event_name",
                        "datetime_start",
                        "timezone",
                        "reason",
                        "user_email",
                        "user_name",
                    ],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }

    def create_a_cal_booking(
        self,
        event_name,
        datetime_start,
        timezone="America/Los_Angeles",
        reason="This is an example reason for this booking",
        user_email="user@example.com",
        user_name="John Doe",
    ):
        """
        Create a booking for a user for a specific event at a given time.
        Finds the event id by fuzzy matching the event name, then creates the booking.
        """
        logger.debug(
            f"Starting booking creation for event: {event_name} at {datetime_start}"
        )

        # Find the event_type_id from the name extracted from user's input
        result = self.find_event_id_by_name(event_name)

        # Convert datetime_start to UTC format
        datetime_start = convert_to_utc_format(datetime_start, timezone)

        # if there's no match, we return the result directly
        if result["status"] == "error":
            logger.debug(f"Event ID (by Name) lookup failed: {result}")
            return result  # returning "no_match" with list of events available

        # if there's a match, proceed with find the availabilities for that event
        if result["status"] == "success":
            # extract the event_type_id
            event_type_id = result["result"]["data"]["id"]
            same_day_time_range = get_day_range_utc(datetime_start)

            logger.debug(
                f"Found event ID: {event_type_id}, checking availability for {same_day_time_range}"
            )

            # Add error handling for get_available_time_slots
            available_slots = self.get_available_time_slots(
                event_type_id, same_day_time_range["start"], same_day_time_range["end"]
            )

            # Check if the slots request failed
            if "error" in available_slots:
                logger.error(f"Failed to get available slots: {available_slots}")
                return function_return(
                    status=FunctionReturnStatus.ERROR,
                    result_code=FunctionReturnCode.SLOTS_REQUEST_FAILED,
                    result_message="Failed to retrieve available time slots",
                    result_data=available_slots["error"],
                )

            logger.debug(f"Available slots response: {available_slots}")

            # check if we have an exact match in the list by going through the available slots
            found_exact_match = False

            if available_slots["status"] == "success":
                for slot in available_slots["data"].get(
                    same_day_time_range["start"].split("T")[0], []
                ):
                    if slot["start"] == datetime_start:
                        # if we have an exact match, we create a booking
                        booking_response = self.create_a_booking(
                            start_datetime=datetime_start,
                            event_type_id=event_type_id,
                            name=user_name,
                            email=user_email,
                            notes=reason,
                        )
                        logger.debug(
                            f"Exact match found, booking response: {booking_response}"
                        )
                        return function_return(
                            status=FunctionReturnStatus.SUCCESS,
                            result_code=FunctionReturnCode.ALL_MATCHED,
                            result_message=f"Booking created for '{event_name}' at {datetime_start}.",
                            result_data=booking_response["data"],
                        )

            if not found_exact_match:
                # if there's no exact match, we return the available slots
                logger.debug(f"No exact match found, returning available slots:")
                logger.debug(available_slots["data"])
                return function_return(
                    status=FunctionReturnStatus.ERROR,
                    result_code=FunctionReturnCode.AVAILABILITY_NO_EXACT_MATCH,
                    result_message=f"No exact match found for '{event_name}' at {datetime_start}.",
                    result_data=available_slots["data"],
                )

        return function_return(
            status=FunctionReturnStatus.ERROR,
            result_code=FunctionReturnCode.UNKNOWN,
            result_message="Unknown error from `create_a_cal_booking`",
            result_data=result,
        )

    def list_all_cal_bookings_fc(self):
        return {
            "type": "function",
            "function": {
                "name": "list_all_cal_bookings",
                "description": "List all Cal.com bookings relevant bookings based on the user's email",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_email": {
                            "type": "string",
                            "description": "The email of the user making the booking.",
                        },
                    },
                    "required": [
                        "user_email",
                    ],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }

    def list_all_cal_bookings(
        self,
        user_email,
    ):
        result = self.get_all_bookings(attendee_email=user_email)

        # Check if the API request was successful
        if result.get("status") == "success":
            # Check if the data array is empty (no bookings found)
            if not result.get("data") or len(result.get("data", [])) == 0:
                logger.debug(f"No bookings found for {user_email}")
                return function_return(
                    status=FunctionReturnStatus.SUCCESS,
                    result_code=FunctionReturnCode.LIST_ALL_CAL_BOOKINGS_EMPTY,
                    result_message=f"No bookings found for {user_email}",
                    result_data=[],
                )

            # Process the bookings data
            bookings = []
            for booking in result["data"]:
                booking_info = {
                    "uid": booking.get("uid"),
                    "id": booking.get("id"),
                    "title": booking.get("title"),
                    "startTime": booking.get("start"),
                    "endTime": booking.get("end"),
                    "status": booking.get("status"),
                    "attendees": booking.get("attendees", []),
                }
                bookings.append(booking_info)

            return function_return(
                status=FunctionReturnStatus.SUCCESS,
                result_code=FunctionReturnCode.LIST_ALL_CAL_BOOKINGS_SUCCESS,
                result_message=f"Successfully retrived a list of bookings relevant to {user_email}",
                result_data=bookings,
            )

        return function_return(
            status=FunctionReturnStatus.ERROR,
            result_code=FunctionReturnCode.UNKNOWN,
            result_message="Unknown error from `list_all_cal_bookings`",
            result_data=result,
        )

    def cancel_user_booking_fc(self):
        return {
            "type": "function",
            "function": {
                "name": "cancel_user_booking",
                "description": "Cancel a Cal.com booking/event based on booking name and start datetime."
                + "The function will find the booking by matching the name and datetime, then cancel it.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_email": {
                            "type": "string",
                            "description": "The email of the user who made the booking.",
                        },
                        "booking_name": {
                            "type": "string",
                            "description": "The title/name of the booking/event to cancel.",
                        },
                        "datetime_start": {
                            "type": "string",
                            "description": "The start datetime for the booking in ISO 8601 format "
                            + "(YYYY-MM-DDTHH:MM:SS.000-00:00).",
                        },
                    },
                    "required": ["user_email", "booking_name", "datetime_start"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }

    def cancel_user_booking(
        self,
        user_email,
        booking_name,
        datetime_start,
    ):
        """
        Cancel a booking for a user based on booking name and start datetime.
        First finds the booking UID by matching name and datetime, then cancels it.
        """
        logger.debug(
            f"Starting booking cancellation for: {booking_name} at {datetime_start} for {user_email}"
        )

        # # Add 5 seconds delay to allow newly created bookings to be available in the API
        # logger.debug("Waiting 5 seconds for booking to be available in the API...")
        # time.sleep(5)

        # Find the booking UID from the name and datetime
        result = self.find_booking_uid_by_name_and_datetime(
            user_email, booking_name, datetime_start
        )

        # If there's no match, return the result directly
        if result["status"] == "error":
            logger.debug(f"Booking lookup failed: {result}")
            return result  # returning error with list of available bookings

        # If there's a match, proceed with cancellation
        if result["status"] == "success":
            # Extract the booking UID
            booking_uid = result["result"]["data"]["uid"]
            booking_info = result["result"]["data"]

            logger.debug(f"Found booking UID: {booking_uid}, attempting cancellation")

            try:
                # Cancel the booking using the API method
                cancellation_response = self.cancel_a_booking(booking_uid)

                # Check if cancellation was successful
                if cancellation_response.get("status") == "success":
                    logger.debug(f"Successfully cancelled booking: {booking_name}")
                    return function_return(
                        status=FunctionReturnStatus.SUCCESS,
                        result_code=FunctionReturnCode.BOOKING_FOUND_AND_CANCELLED,
                        result_message=f"Booking cancelled '{booking_name}' at {datetime_start}",
                        result_data={
                            "cancelled_booking": booking_info,
                            "cancellation_response": cancellation_response,
                        },
                    )
                else:
                    logger.error(f"Failed to cancel booking: {cancellation_response}")
                    return function_return(
                        status=FunctionReturnStatus.ERROR,
                        result_code=FunctionReturnCode.BOOKING_CANCELLATION_FAILED,
                        result_message=f"Failed to cancel: {cancellation_response.get('message', 'Unknown error')}",
                        result_data={
                            "found_booking": booking_info,
                            "cancellation_error": cancellation_response,
                        },
                    )

            except Exception as e:
                logger.error(f"Exception during booking cancellation: {e}")
                return function_return(
                    status=FunctionReturnStatus.ERROR,
                    result_code=FunctionReturnCode.BOOKING_CANCELLATION_FAILED,
                    result_message=f"Exception occurred while cancelling booking: {str(e)}",
                    result_data={
                        "found_booking": booking_info,
                        "exception": str(e),
                    },
                )

        return function_return(
            status=FunctionReturnStatus.ERROR,
            result_code=FunctionReturnCode.UNKNOWN,
            result_message="Unknown error from `cancel_a_booking`",
            result_data=result,
        )

    def find_booking_uid_by_name_and_datetime(
        self, user_email, booking_name, datetime_start
    ):
        """
        Find a booking UID by matching booking name and start datetime.
        Returns the matching booking UID or an error if no match is found.
        """
        logger.debug(
            f"Looking for booking with name: {booking_name} and datetime: {datetime_start}"
        )

        # Convert datetime_start to UTC format for comparison
        datetime_start_utc = convert_to_utc_format(datetime_start)

        # Get all bookings for the user
        response = self.get_all_bookings(attendee_email=user_email)

        # Check if the response has an error key
        if "error" in response:
            logger.error(f"API request failed: {response['error']}")
            return function_return(
                status=FunctionReturnStatus.ERROR,
                result_code=FunctionReturnCode.CALCOM_API_REQUEST_FAILED,
                result_message="Request to Cal.com API failed",
                result_data=response["error"],
            )

        # Check the response structure
        if response.get("status") == "error":
            return function_return(
                status=FunctionReturnStatus.ERROR,
                result_code=FunctionReturnCode.CALCOM_API_REQUEST_FAILED,
                result_message="Request to Cal.com API failed",
                result_data=response.get("error", response),
            )

        # Handle case where response doesn't have expected 'data' field
        if "data" not in response:
            logger.error(f"Unexpected response format: {response}")
            return function_return(
                status=FunctionReturnStatus.ERROR,
                result_code=FunctionReturnCode.UNEXPECTED_RESPONSE_FORMAT,
                result_message="Unexpected response format from Cal.com API",
                result_data=response,
            )

        booking_name_lower = booking_name.lower().strip()

        for booking in response["data"]:
            title = booking.get("title", "").lower()
            start_time = booking.get("start", "")

            # Convert booking start time to UTC for comparison
            try:
                booking_start_utc = convert_to_utc_format(start_time)
            except Exception as e:
                logger.warning(f"Could not parse booking start time {start_time}: {e}")
                continue

            # @TODO: User is not able to cancel booking right after creation - has to send mutiple requests
            if booking_name_lower == title and datetime_start_utc == booking_start_utc:
                return function_return(
                    status=FunctionReturnStatus.SUCCESS,
                    result_code=FunctionReturnCode.FOUND_MATCH,
                    result_message="Found exact match for booking",
                    result_data={
                        "uid": booking.get("uid"),
                        "id": booking.get("id"),
                        "title": booking.get("title"),
                        "startTime": booking.get("start"),
                        "endTime": booking.get("end"),
                    },
                )

        # No exact match found - prepare list of available bookings for error response
        available_bookings = []
        if response["status"] == "success":
            for booking in response["data"]:
                available_bookings.append(
                    {
                        "uid": booking.get("uid"),
                        "title": booking.get("title"),
                        "startTime": booking.get("start"),
                        "endTime": booking.get("end"),
                    }
                )

        return function_return(
            status=FunctionReturnStatus.ERROR,
            result_code=FunctionReturnCode.BOOKING_NOT_FOUND,
            result_message=f"No matching booking found for '{booking_name}' at {datetime_start}",
            result_data=available_bookings,
        )

    """
    Function Calling Tools
    """

    def get_function_call_specs(self):
        return [
            self.cancel_user_booking_fc(),
            self.list_all_cal_bookings_fc(),
            self.create_a_cal_booking_fc(),
        ]
