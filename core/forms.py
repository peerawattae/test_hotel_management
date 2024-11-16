from django import forms
from django.contrib.auth.models import User
from .models import Room, Booking
from django.utils import timezone

class RoomForm(forms.ModelForm):
    check_in_date = forms.DateField(required=False, widget=forms.SelectDateWidget(years=range(2024, 2026)))
    check_out_date = forms.DateField(required=False, widget=forms.SelectDateWidget(years=range(2024, 2026)))

    class Meta:
        model = Room
        fields = ['room_type', 'description', 'price_per_night', 'status', 'check_in_date', 'check_out_date']

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Automatically set the total_price when the room is selected
        if 'room' in self.initial:
            self.calculate_price()

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
    
    def save(self, commit=True):
        """
        Override the save method to ensure total_price is set before saving.
        """
        if not self.instance.total_price:
            self.calculate_price()
        return super().save(commit)