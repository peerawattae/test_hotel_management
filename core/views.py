from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Room, Booking
from django.utils import timezone


def check_room_availability(request, room_id):
    check_in_date = request.GET.get('check_in_date')
    check_out_date = request.GET.get('check_out_date')

    # Validate input
    if not check_in_date or not check_out_date:
        return JsonResponse({'error': 'Please provide both check_in_date and check_out_date'}, status=400)

    room = get_object_or_404(Room, id=room_id)

    # Check availability
    if room.is_available(check_in_date, check_out_date):
        return JsonResponse({'available': True})
    else:
        return JsonResponse({'available': False})

def room_calendar_view(request, room_id):
    """
    Renders a calendar view for a specific room, showing the booked dates.
    """
    room = get_object_or_404(Room, pk=room_id)
    bookings = Booking.objects.filter(room=room, status='confirmed')

    # Debugging: Print out the bookings and booked dates
    print(bookings)  # Check in the console
    booked_dates = [
        {
            "start": booking.check_in_date.strftime('%Y-%m-%d'),
            "end": (booking.check_out_date + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
            "title": f"Booked by {booking.customer.first_name} {booking.customer.last_name}"
        }
        for booking in bookings
    ]

    # Debugging: Print out the booked dates
    print(booked_dates)  # Check in the console

    context = {
        "room": room,
        "booked_dates": booked_dates
    }

    return render(request, "core/room_calendar.html", context)
