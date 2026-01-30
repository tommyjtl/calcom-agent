# CalComTool API Documentation

> Disclaimer: the following API docs is generated using Claude Sonnet.

This document describes the function call APIs available in the `CalComTool` class that use the standardized `function_return` structure.

## Response Structure

All function calls return a standardized response structure:

```json
{
  "status": "success" | "error",
  "result": {
    "code": "result_code",
    "message": "Human readable message",
    "data": {}
  }
}
```

## Status Codes

### FunctionReturnStatus
- `SUCCESS` - Operation completed successfully
- `ERROR` - Operation failed

### FunctionReturnCode
- `CALCOM_API_REQUEST_FAILED` - Request to Cal.com API failed
- `UNEXPECTED_RESPONSE_FORMAT` - Unexpected response format from Cal.com API
- `FOUND_MATCH` - Found a matching event or booking
- `NO_MATCH` - No matching event found
- `SLOTS_REQUEST_FAILED` - Failed to retrieve available time slots
- `ALL_MATCHED` - Exact match found and booking created
- `AVAILABILITY_NO_EXACT_MATCH` - No exact time slot match found
- `LIST_ALL_CAL_BOOKINGS_SUCCESS` - Successfully retrieved bookings list
- `BOOKING_FOUND_AND_CANCELLED` - Booking found and successfully cancelled
- `BOOKING_NOT_FOUND` - No matching booking found
- `BOOKING_CANCELLATION_FAILED` - Booking found but cancellation failed
- `UNKNOWN` - Unknown error occurred

---

## Function Call APIs

### 1. create_a_cal_booking

**Description:** Create a booking/event for a user for a specific event name at a given time.

**Parameters:**
- `event_name` (string, required): The name of the event to book
- `datetime_start` (string, required): Start datetime in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.000-00:00)
- `timezone` (string, required): Timezone for the booking (e.g., 'America/Los_Angeles')
- `reason` (string, required): Reasons for the booking
- `user_email` (string, required): Email of the user making the booking
- `user_name` (string, required): Name of the user making the booking

**Success Response Examples:**

```json
{
  "status": "success",
  "result": {
    "code": "all_matched",
    "message": "Exact match found for 'Meeting' at 2025-08-04T20:00:00.000Z. Booking created.",
    "data": {
      "id": 12345,
      "uid": "abc123def456",
      "title": "Meeting",
      "start": "2025-08-04T20:00:00.000Z",
      "end": "2025-08-04T20:30:00.000Z"
    }
  }
}
```

**Error Response Examples:**

```json
{
  "status": "error",
  "result": {
    "code": "no_match",
    "message": "No matching event found for 'NonexistentEvent'",
    "data": [
      {
        "title": "30 Min Meeting",
        "slug": "30min",
        "id": 2935832
      }
    ]
  }
}
```

```json
{
  "status": "error",
  "result": {
    "code": "availability_no_exact_match",
    "message": "No exact match found for 'Meeting' at 2025-08-04T20:00:00.000Z.",
    "data": {
      "2025-08-04": [
        {
          "start": "2025-08-04T19:00:00.000Z",
          "end": "2025-08-04T19:30:00.000Z"
        }
      ]
    }
  }
}
```

---

### 2. list_all_cal_bookings

**Description:** List all Cal.com bookings relevant bookings based on the user's email.

**Parameters:**
- `user_email` (string, required): Email of the user whose bookings to retrieve

**Success Response Example:**

```json
{
  "status": "success",
  "result": {
    "code": "list_all_cal_bookings_success",
    "message": "Successfully retrieved a list of bookings relevant to user@example.com",
    "data": [
      {
        "uid": "abc123def456",
        "id": 12345,
        "title": "30 Min Meeting",
        "startTime": "2025-08-04T20:00:00.000Z",
        "endTime": "2025-08-04T20:30:00.000Z",
        "status": "accepted",
        "attendees": [
          {
            "name": "John Doe",
            "email": "user@example.com"
          }
        ]
      }
    ]
  }
}
```

**Error Response Example:**

```json
{
  "status": "error",
  "result": {
    "code": "unknown",
    "message": "Unknown error from `list_all_cal_bookings`",
    "data": {
      "status": "error",
      "error": "API request failed"
    }
  }
}
```

---

### 3. cancel_user_booking

**Description:** Cancel a Cal.com booking/event based on booking name and start datetime. The function will find the booking by matching the name and datetime, then cancel it.

**Parameters:**
- `user_email` (string, required): Email of the user who made the booking
- `booking_name` (string, required): Title/name of the booking/event to cancel
- `datetime_start` (string, required): Start datetime in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.000-00:00)

**Success Response Example:**

```json
{
  "status": "success",
  "result": {
    "code": "booking_found_and_cancelled",
    "message": "Successfully cancelled booking '30 Min Meeting' at 2025-08-04T20:00:00.000Z",
    "data": {
      "cancelled_booking": {
        "uid": "abc123def456",
        "id": 12345,
        "title": "30 Min Meeting",
        "startTime": "2025-08-04T20:00:00.000Z",
        "endTime": "2025-08-04T20:30:00.000Z"
      },
      "cancellation_response": {
        "status": "success",
        "data": {
          "message": "Booking cancelled successfully"
        }
      }
    }
  }
}
```

**Error Response Examples:**

```json
{
  "status": "error",
  "result": {
    "code": "booking_not_found",
    "message": "No matching booking found for 'Nonexistent Meeting' at 2025-08-04T20:00:00.000Z",
    "data": [
      {
        "uid": "abc123def456",
        "title": "30 Min Meeting",
        "startTime": "2025-08-04T20:00:00.000Z",
        "endTime": "2025-08-04T20:30:00.000Z"
      }
    ]
  }
}
```

```json
{
  "status": "error",
  "result": {
    "code": "booking_cancellation_failed",
    "message": "Found booking but failed to cancel: Booking is already cancelled",
    "data": {
      "found_booking": {
        "uid": "abc123def456",
        "id": 12345,
        "title": "30 Min Meeting",
        "startTime": "2025-08-04T20:00:00.000Z",
        "endTime": "2025-08-04T20:30:00.000Z"
      },
      "cancellation_error": {
        "status": "error",
        "message": "Booking is already cancelled"
      }
    }
  }
}
```

---

## Common Error Responses

### API Request Failed

```json
{
  "status": "error",
  "result": {
    "code": "calcom_api_request_failed",
    "message": "Request to Cal.com API failed",
    "data": "401 Client Error: Unauthorized for url: https://api.cal.com/v2/..."
  }
}
```

### Unexpected Response Format

```json
{
  "status": "error",
  "result": {
    "code": "unexpected_response_format",
    "message": "Unexpected response format from Cal.com API",
    "data": {
      "unexpected_field": "unexpected_value"
    }
  }
}
```

### Slots Request Failed

```json
{
  "status": "error",
  "result": {
    "code": "slots_request_failed",
    "message": "Failed to retrieve available time slots",
    "data": "Network timeout error"
  }
}
```

---

## Usage Examples

### Creating a Booking

```python
result = calcom_tool.create_a_cal_booking(
    event_name="30 Min Meeting",
    datetime_start="2025-08-04T13:00:00.000-07:00",
    timezone="America/Los_Angeles",
    reason="Weekly sync meeting",
    user_email="user@example.com",
    user_name="John Doe"
)

if result["status"] == "success":
    print(f"Booking created: {result['result']['data']['uid']}")
else:
    print(f"Error: {result['result']['message']}")
```

### Listing Bookings

```python
result = calcom_tool.list_all_cal_bookings(
    user_email="user@example.com"
)

if result["status"] == "success":
    for booking in result["result"]["data"]:
        print(f"Booking: {booking['title']} at {booking['startTime']}")
```

### Cancelling a Booking

```python
result = calcom_tool.cancel_user_booking(
    user_email="user@example.com",
    booking_name="30 Min Meeting",
    datetime_start="2025-08-04T20:00:00.000Z"
)

if result["status"] == "success":
    print("Booking cancelled successfully")
else:
    print(f"Cancellation failed: {result['result']['message']}")
```

---

## Notes

1. All datetime parameters should be in ISO 8601 format
2. Timezone parameters should be valid timezone identifiers (e.g., 'America/Los_Angeles')
3. The system performs fuzzy matching for event names and booking names
4. All responses follow the standardized `function_return` structure
5. Error responses often include helpful data like available alternatives
