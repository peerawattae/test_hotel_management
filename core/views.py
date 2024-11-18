from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Room, Booking
from django.utils import timezone
from django.shortcuts import render, redirect
from .forms import BookingForm, RoomForm, PaymentForm

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Room, Booking, Customer, Review
from .forms import BookingForm

#code for user view
def dashboard(request):
    return render(request, 'core/dashboard.html')

#code for user view

def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'core/room_list.html', {'rooms': rooms})

# Create a new room
def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_list')
    else:
        form = RoomForm()
    return render(request, 'core/room_form.html', {'form': form})

# Edit an existing room
def room_edit(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('room_list')
    else:
        form = RoomForm(instance=room)
    return render(request, 'core/room_form.html', {'form': form})

# Delete a room
def room_delete(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Room has been deleted successfully.')
        return redirect('room_list')
    return render(request, 'core/room_confirm_delete.html', {'room': room})

def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'room_list.html', {'rooms': rooms})

def room_detail(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    return render(request, 'room_detail.html', {'room': room})

def booking_list(request):
    bookings = Booking.objects.all()
    return render(request, 'booking_list.html', {'bookings': bookings})

def new_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm()
    
    return render(request, 'core/new_booking.html', {'form': form})



def booking_edit(request, booking_id):
    """
    Allows the user to edit their booking.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()  # Save the edited booking
            messages.success(request, "Booking updated successfully!")
            return redirect('booking_list')  # Redirect to the booking list
        else:
            messages.error(request, "There was an error updating the booking.")
    else:
        form = BookingForm(instance=booking)  # Load the booking form with existing data
    
    return render(request, 'core/booking_edit.html', {'form': form, 'booking': booking})

def booking_delete(request, booking_id):
    """
    Allows the user to delete their booking.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        booking.delete()  # Delete the booking
        messages.success(request, "Booking deleted successfully!")
        return redirect('booking_list')  # Redirect to the booking list
    
    return render(request, 'core/booking_confirm_delete.html', {'booking': booking})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

def review_list(request):
    reviews = Review.objects.all()
    return render(request, 'review_list.html', {'reviews': reviews})
#end of code for user site

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

def home_view(request):
    """
    Renders the homepage with links to main functionalities.
    """
    rooms = Room.objects.all()
    return render(request, "core/home.html")
def booking_view(request):
    """
    Allows users to book a room.
    """
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")  # Redirect to the homepage after booking
    else:
        form = BookingForm()
    return render(request, "core/booking.html", {"form": form})