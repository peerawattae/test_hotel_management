from django import forms
from django.contrib import admin  # Corrected import statement
from .models import Room, Booking, Customer, Payment
from django.utils import timezone

class RoomForm(forms.ModelForm):    
    check_in_date = forms.DateField(
        required=False, 
        widget=forms.SelectDateWidget(years=range(2024, 2026)),
        initial=None  # Default value set to None
    )
    check_out_date = forms.DateField(
        required=False, 
        widget=forms.SelectDateWidget(years=range(2024, 2026)),
        initial=None  # Default value set to None
    )


    class Meta:
        model = Room
        fields = ['room_type', 'description', 'price_per_night', 'status']

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')

        # Ensure check-in and check-out dates are provided
        if check_in_date and check_out_date:
            # Check availability for the given dates
            room = self.instance
            if not room.is_available(check_in_date, check_out_date):
                raise forms.ValidationError("This room is not available for the selected dates.")
        return cleaned_data

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'customer', 'check_in_date', 'check_out_date', 'status']
    
    check_in_date = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'datepicker',
            'placeholder': 'Select check-in date'
        })
    )
    check_out_date = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'datepicker',
            'placeholder': 'Select check-out date'
        })
    )
    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        status = cleaned_data.get('status')

        # Skip availability check if the booking is being cancelled
        if status != 'cancelled' and check_in_date and check_out_date:
            # Only check availability if booking is not cancelled
            if room and not room.is_available(check_in_date, check_out_date):
                raise forms.ValidationError("This room is not available for the selected dates.")
        
            # Calculate the total price if room, check_in_date, and check_out_date are present
            if room and check_in_date and check_out_date:
                duration = (check_out_date - check_in_date).days
                if duration > 0:
                    self.instance.total_price = room.price_per_night * duration
                else:
                    raise forms.ValidationError("Check-out date must be after check-in date.")
        
        return cleaned_data

    def save(self, commit=True):
        """
        Override the save method to ensure total_price is set before saving.
        """
        if not self.instance.total_price:
            self.calculate_price()  # Ensure total price is calculated before saving.
        return super().save(commit)

    def calculate_price(self):
        """
        Automatically calculate the total price based on the room's price and the duration.
        """
        room = self.cleaned_data.get('room')
        check_in_date = self.cleaned_data.get('check_in_date')
        check_out_date = self.cleaned_data.get('check_out_date')

        if room and check_in_date and check_out_date:
            duration = (check_out_date - check_in_date).days
            if duration > 0:
                self.instance.total_price = room.price_per_night * duration
            else:
                raise ValueError("Check-out date must be after check-in date.")


class BookingAdmin(admin.ModelAdmin):
    list_display = ['room', 'customer', 'check_in_date', 'check_out_date', 'status', 'total_price']
    actions = ['cancel_booking', 'confirm_booking']

    def cancel_booking(self, request, queryset):
        for booking in queryset:
            if booking.status != 'cancelled':  # Ensure we don't cancel an already cancelled booking
                booking.cancel_booking()
                booking.room.status = 'available'  # Set room status to 'available'
                booking.room.save()
        self.message_user(request, "Selected bookings have been cancelled.")
    
    def confirm_booking(self, request, queryset):
        for booking in queryset:
            if booking.status == 'cancelled':  # Allow re-confirmation after cancellation
                booking.status = 'confirmed'
                booking.room.status = 'booked'  # Mark room as booked
                booking.room.save()  # Save room status
                booking.save()
                self.message_user(request, f"Booking {booking.id} has been confirmed.")
            elif booking.can_confirm():  # Confirm the booking only if it's not cancelled
                booking.status = 'confirmed'
                booking.room.status = 'booked'  # Mark room as booked
                booking.room.save()  # Save room status
                booking.save()
                self.message_user(request, f"Booking {booking.id} has been confirmed.")
            else:
                self.message_user(request, f"Booking {booking.id} cannot be confirmed due to room availability.")

    cancel_booking.short_description = "Cancel selected bookings"
    confirm_booking.short_description = "Confirm selected bookings"

class PaymentForm(forms.ModelForm):
    booking = forms.ModelChoiceField(queryset=Booking.objects.all(), required=True)

    class Meta:
        model = Payment
        fields = ['booking', 'amount', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Automatically set the amount based on the selected booking
        if self.instance and self.instance.booking:
            self.fields['amount'].initial = self.instance.booking.total_price

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        booking = cleaned_data.get('booking')

        if booking and amount != booking.total_price:
            raise forms.ValidationError("Amount must match the booking's total price.")
        return cleaned_data

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone_num']
