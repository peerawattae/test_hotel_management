from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Room, Booking, Payment, Customer, Review
from django.utils import timezone
from django.shortcuts import render, redirect
from .forms import BookingForm, RoomForm, PaymentForm, CustomerForm
from django.contrib import messages

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
    sort_order = request.GET.get('sort', 'asc')  # Get sorting order from query parameter; default to ascending
    if sort_order == 'desc':
        rooms = Room.objects.all().order_by('-price_per_night')  # Descending order
    else:
        rooms = Room.objects.all().order_by('price_per_night')  # Ascending order

    return render(request, 'core/room_list.html', {'rooms': rooms, 'sort_order': sort_order})


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
            booking = form.save(commit=False)
            # Check availability before saving
            if check_room_availability(booking.room, booking.check_in_date, booking.check_out_date):
                booking.save()
                messages.success(request, "Booking confirmed successfully!")
                return redirect('booking_list')
            else:
                messages.error(request, "Room is not available for the selected dates.")
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

# List Payments
def payment_list(request):
    payments = Payment.objects.all()  # Fetch all payments
    return render(request, 'payment_list.html', {'payments': payments})

# Create Payment
def payment_create(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # No need to manually set the booking if it's in the form
            form.save()
            messages.success(request, "Payment created successfully!")
            return redirect('payment_list')  # Redirect to the payment list view
    else:
        form = PaymentForm()
    
    bookings = Booking.objects.all()  # Pass available bookings to the template
    return render(request, 'core/payment_form.html', {'form': form, 'bookings': bookings})

# Edit Payment
def payment_edit(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()  # Save the edited payment
            messages.success(request, "Payment updated successfully!")
            return redirect('payment_list')  # Redirect to the payment list
    else:
        form = PaymentForm(instance=payment)
    
    # Fetch bookings related to the payment, assuming you want the current booking
    bookings = Booking.objects.all()  # Or filter by your logic (e.g., only related bookings)
    
    return render(request, 'core/payment_form.html', {'form': form, 'bookings': bookings, 'payment': payment})

# Delete Payment
def payment_delete(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, "Payment deleted successfully!")
        return redirect('payment_list')
    return render(request, 'core/payment_confirm_delete.html', {'payment': payment})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

def review_list(request):
    reviews = Review.objects.all()
    return render(request, 'review_list.html', {'reviews': reviews})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'core/customer_list.html', {'customers': customers})

# Create a New Customer
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'core/customer_form.html', {'form': form})

# Edit an Existing Customer
def customer_edit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'core/customer_form.html', {'form': form})

# Delete a Customer
def customer_delete(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customer_list')
    return render(request, 'core/customer_confirm_delete.html', {'customer': customer})
#end of code for user site

def check_room_availability(room, check_in_date, check_out_date):
    overlapping_bookings = Booking.objects.filter(
        room=room,
        check_in_date__lt=check_out_date,
        check_out_date__gt=check_in_date,
        status='confirmed'  # Only consider confirmed bookings
    )
    return not overlapping_bookings.exists()


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