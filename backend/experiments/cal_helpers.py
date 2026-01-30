# We use V2 version
# https://cal.com/docs/api-reference/v2/introduction
# https://github.com/calcom/cal.com/blob/main/docs/api-reference/v2/openapi.json

import os
import json
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from cal import CalComTool
from utils.print import json_print

from dotenv import load_dotenv

# Load environment variables from .env in the parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


def get_all_eventtype_ids(calcom_client):
    response = calcom_client.get_all_event_types()
    # json_print(response)
    ids = []
    if response["status"] == "success":
        for d in response["data"]:
            ids.append({"title": d["title"], "slug": d["slug"], "id": d["id"]})
        return json.dumps(ids, indent=2)
    return None


def get_all_bookings_for_cancellation(
    calcom_client, attendee_email="estxhc@gmail.com", status="upcoming"
):
    """
    Get all bookings for a specific attendee email that can be cancelled

    Args:
        calcom_client: The CalComTool instance
        attendee_email: Email of the attendee whose bookings to retrieve
        status: Status of bookings to retrieve (default: "upcoming")

    Returns:
        List of booking dictionaries with relevant cancellation info
    """
    response = calcom_client.get_all_bookings(
        attendee_email=attendee_email, status=status
    )
    bookings = []

    if response.get("status") == "success" and response.get("data"):
        for booking in response["data"]:
            booking_info = {
                "uid": booking.get("uid"),
                "id": booking.get("id"),
                "title": booking.get("title"),
                "startTime": booking.get("startTime"),
                "endTime": booking.get("endTime"),
                "status": booking.get("status"),
                "attendees": booking.get("attendees", []),
            }
            bookings.append(booking_info)

    return bookings


def cancel_all_bookings(
    calcom_client, attendee_email="estxhc@gmail.com", status="upcoming", dry_run=True
):
    """
    Cancel all bookings for a specific attendee

    Args:
        calcom_client: The CalComTool instance
        attendee_email: Email of the attendee whose bookings to cancel
        status: Status of bookings to cancel (default: "upcoming")
        dry_run: If True, only shows what would be cancelled without actually cancelling

    Returns:
        Dictionary with results of cancellation attempts
    """
    print(
        f"{'[DRY RUN] ' if dry_run else ''}Finding all bookings for {attendee_email}..."
    )

    # Get all bookings
    bookings = get_all_bookings_for_cancellation(calcom_client, attendee_email, status)

    if not bookings:
        print(f"No {status} bookings found for {attendee_email}")
        return {"cancelled": [], "failed": [], "total": 0}

    print(
        f"Found {len(bookings)} booking(s) to {'would be ' if dry_run else ''}cancel:"
    )
    for i, booking in enumerate(bookings, 1):
        print(
            f"  {i}. {booking['title']} - {booking['startTime']} (UID: {booking['uid']})"
        )

    if dry_run:
        print("\nThis is a dry run. Set dry_run=False to actually cancel the bookings.")
        return {"cancelled": [], "failed": [], "total": len(bookings), "dry_run": True}

    # Actually cancel the bookings
    cancelled = []
    failed = []

    for booking in bookings:
        try:
            print(f"Cancelling booking: {booking['title']} (UID: {booking['uid']})")
            response = calcom_client.cancel_a_booking(booking["uid"])

            if response.get("status") == "success":
                cancelled.append(
                    {
                        "uid": booking["uid"],
                        "title": booking["title"],
                        "response": response,
                    }
                )
                print(f"  ✓ Successfully cancelled: {booking['title']}")
            else:
                failed.append(
                    {
                        "uid": booking["uid"],
                        "title": booking["title"],
                        "error": response.get("message", "Unknown error"),
                        "response": response,
                    }
                )
                print(
                    f"  ✗ Failed to cancel: {booking['title']} - {response.get('message', 'Unknown error')}"
                )

        except Exception as e:
            failed.append(
                {"uid": booking["uid"], "title": booking["title"], "error": str(e)}
            )
            print(f"  ✗ Exception while cancelling: {booking['title']} - {str(e)}")

    print(f"\nCancellation complete:")
    print(f"  Successfully cancelled: {len(cancelled)}")
    print(f"  Failed to cancel: {len(failed)}")

    return {"cancelled": cancelled, "failed": failed, "total": len(bookings)}


if __name__ == "__main__":
    client = CalComTool(
        # # Wrong API key for testing
        # load API key from .env
        api_key=os.getenv("CALCOM_API_KEY")
    )
    # response = client.get_my_profile()

    """
    List all event types
    """
    # print(get_all_eventtype_ids(client))

    """
    Create an event type
    """
    # response = client.create_an_event_type(30, "sup", "sup-yeahhhhasdasd")
    # print(json.dumps(response, indent=2))

    """
    Get the detail of an event type
    """
    # response = client.get_an_event_type(2935832)
    # print(json.dumps(response, indent=2))

    """
    Get available time slot
    """
    # response = client.get_available_time_slots(
    #     2935832,  # event type id
    #     "2025-08-01T02:00:00Z",  # start date time
    #     "2025-08-18T02:00:00Z",  # end sate time
    # )
    # print(json.dumps(response, indent=2))

    """
    Create a booking
    """
    # response = client.create_a_booking(
    #     "2025-08-04T13:00:00.000-07:00",
    #     event_type_id=2935832,  # event type id
    #     name="Thomas",
    #     email="estxhc@gmail.com",  # make this default
    #     time_zone="America/Los_Angeles",  #
    # )
    # json_print(response)

    """
    Cancel a booking
    """
    # response = client.cancel_a_booking(
    #     booking_uid="vPtvMsFt9umknd5H2Gwyzu"  # booking_uid, not id
    # )
    # json_print(response)

    """
    List all bookings
    """
    # response = client.get_all_bookings()
    # json_print(response)

    """
    Helper functions for bulk booking management
    """
    # Get all bookings for cancellation (with details)
    bookings = get_all_bookings_for_cancellation(
        client, attendee_email="estxhc@gmail.com"
    )
    print(f"Found {len(bookings)} bookings:")
    json_print(bookings)

    # Cancel all bookings (dry run first to see what would be cancelled)
    result = cancel_all_bookings(
        client,
        # attendee_email="estxhc@gmail.com",
        attendee_email="jingtao8@illinois.edu",
        dry_run=False,
        # dry_run=True,
    )
    json_print(result)
