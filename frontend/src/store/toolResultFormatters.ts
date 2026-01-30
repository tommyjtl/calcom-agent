// Tool result formatters for different response codes

// Type definitions
interface ToolResult {
    result?: {
        result?: {
            code: string;
            message: string;
            data: unknown;
        };
    };
    error?: string;
}

interface BookingData {
    title: string;
    start?: string;
    end?: string;
    id: string | number;
    uid: string;
    startTime?: string;
    endTime?: string;
    status?: string;
    attendees?: Array<{ name: string }>;
}

interface CancelledBookingResult {
    cancelled_booking: BookingData;
}

interface CancellationFailedResult {
    found_booking: BookingData;
    cancellation_error: { message: string };
}

interface EventData {
    title: string;
    id: string | number;
    slug: string;
}

interface TimeSlot {
    start: string;
}

interface AvailabilityData {
    [date: string]: TimeSlot[];
}

export const formatToolResultAsMarkdown = (toolResult: ToolResult): string => {
    const { result, error } = toolResult;

    if (error) {
        return `❌ **Error:** ${error}`;
    }

    if (!result || !result.result) {
        return `**Debug:** \`\`\`json\n${JSON.stringify(toolResult, null, 2)}\n\`\`\``;
    }

    const { code, message, data } = result.result;

    switch (code) {
        case 'all_matched':
            return formatAllMatched(data);
        case 'list_all_cal_bookings_success':
            return formatBookingsList(data);
        case 'list_all_cal_bookings_empty':
            return formatBookingsEmpty(message);
        case 'booking_found_and_cancelled':
            return formatBookingCancelled(data, message);
        case 'booking_not_found':
            return formatBookingNotFound(data, message);
        case 'booking_cancellation_failed':
            return formatBookingCancellationFailed(data, message);
        case 'calcom_api_request_failed':
            return formatApiError(message);
        case 'unexpected_response_format':
            return formatDefault(code, message, data);
        case 'slots_request_failed':
            return formatApiError(message);
        case 'no_match':
            return formatNoMatch(data, message);
        case 'availability_no_exact_match':
            return formatAvailabilityNoMatch(data, message);
        default:
            return formatDefault(code, message, data);
    }
};

// Individual formatter functions
const formatAllMatched = (data: unknown): string => {
    const booking = data as BookingData;
    return `✅ I've created the event for you!\n\n**Event Details:**\n- **Title:** ${booking.title}\n- **Start:** ${new Date(booking.start || '').toLocaleString()}\n- **End:** ${new Date(booking.end || '').toLocaleString()}\n- **Booking ID:** ${booking.id}\n\n[View Booking Details](https://app.cal.com/booking/${booking.uid})`;
};

const formatBookingsList = (data: unknown): string => {
    let bookingMarkdown = `📅 **Your Cal.com Bookings:**\n\n`;

    const bookings = data as BookingData[];
    if (bookings && Array.isArray(bookings) && bookings.length > 0) {
        bookings.forEach((booking: BookingData) => {
            const attendeesText = booking.attendees?.map((attendee) => attendee.name).join(', ') || 'No attendees';
            const statusEmoji = booking.status === 'accepted' ? '✅' : booking.status === 'pending' ? '⏳' : '❓';

            bookingMarkdown += `**${booking.title}** \n`;
            bookingMarkdown += `- ${statusEmoji} Status: ${booking.status}\n`;
            bookingMarkdown += `- 👥 Attendees: ${attendeesText}\n`;
            bookingMarkdown += `- 🆔 Booking ID: \`${booking.id}\`\n`;

            if (booking.startTime) {
                bookingMarkdown += `- 🕐 Start: **${new Date(booking.startTime).toLocaleString()}**\n`;
            }
            if (booking.endTime) {
                bookingMarkdown += `- 🕐 End: **${new Date(booking.endTime).toLocaleString()}**\n`;
            }

            bookingMarkdown += `- [View Booking Details](https://app.cal.com/booking/${booking.uid})\n\n`;
        });
    } else {
        bookingMarkdown += `No bookings found.`;
    }

    return bookingMarkdown;
};

const formatBookingsEmpty = (message: string): string => {
    return `📅 **No Bookings Found**\n\n${message || 'You currently have no Cal.com bookings.'}\n\n💡 *Tip: You can create a new booking by asking me to schedule an event for you!*`;
};

const formatBookingCancelled = (data: unknown, message: string): string => {
    const result = data as CancelledBookingResult;
    return `✅ **Booking Cancelled Successfully!**\n\n**Cancelled Event Details:**\n- **Title:** ${result.cancelled_booking.title}\n- **Start:** ${new Date(result.cancelled_booking.startTime || '').toLocaleString()}\n- **End:** ${new Date(result.cancelled_booking.endTime || '').toLocaleString()}\n- **Booking ID:** ${result.cancelled_booking.id}\n\n${message}`;
};

const formatBookingNotFound = (data: unknown, message: string): string => {
    let notFoundMarkdown = `❌ **${message}**\n\n`;

    const bookings = data as BookingData[];
    if (bookings && Array.isArray(bookings) && bookings.length > 0) {
        notFoundMarkdown += `**Your existing bookings:**\n`;
        bookings.forEach((booking: BookingData, index: number) => {
            notFoundMarkdown += `**${index + 1}. ${booking.title}**\n`;
            notFoundMarkdown += `- 🕐 Start: ${new Date(booking.startTime || '').toLocaleString()}\n`;
            if (booking.endTime) {
                notFoundMarkdown += `- 🕐 End: ${new Date(booking.endTime).toLocaleString()}\n`;
            }
            notFoundMarkdown += `- [View Booking](https://app.cal.com/booking/${booking.uid})\n\n`;
        });
    } else {
        notFoundMarkdown += `No existing bookings found.`;
    }

    return notFoundMarkdown;
};

const formatBookingCancellationFailed = (data: unknown, message: string): string => {
    const result = data as CancellationFailedResult;
    return `❌ **Cancellation Failed**\n\n${message}\n\n**Found Booking:**\n- **Title:** ${result.found_booking.title}\n- **Start:** ${new Date(result.found_booking.startTime || '').toLocaleString()}\n- **End:** ${new Date(result.found_booking.endTime || '').toLocaleString()}\n- **Booking ID:** ${result.found_booking.id}\n\n**Error:** ${result.cancellation_error.message}`;
};

const formatApiError = (message: string): string => {
    return `❌ **Error:** ${message}`;
};

const formatNoMatch = (data: unknown, message: string): string => {
    const events = data as EventData[];
    return `❌ ${message}\n\n**Available Events:**\n${events.map((event: EventData) => `- **${event.title}** (ID: ${event.id}, Slug: ${event.slug})`).join('\n')}`;
};

const formatAvailabilityNoMatch = (data: unknown, message: string): string => {
    let markdown = `⏰ ${message}\n\n**Alternative Time Slots:**\n`;

    const availabilityData = data as AvailabilityData;
    Object.entries(availabilityData).forEach(([date, slots]: [string, TimeSlot[]]) => {
        // Use the date string directly since it's already in YYYY-MM-DD format
        const formattedDate = new Date(date + 'T00:00:00.000Z').toLocaleDateString([], {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        markdown += `\n**${formattedDate}:**\n`;
        slots.forEach((slot: TimeSlot) => {
            // Only format the start time since slots only have start property
            const startTime = new Date(slot.start).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            });
            markdown += `- ${startTime}\n`;
        });
    });

    return markdown;
};

const formatDefault = (code: string, message: string, data: unknown): string => {
    return `**Tool Result:**\n- **Code:** ${code}\n- **Message:** ${message}\n\n**Data:**\n\`\`\`json\n${JSON.stringify(data, null, 2)}\n\`\`\``;
};
