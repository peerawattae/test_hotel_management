from django import forms
from django.contrib.auth.models import User
from .models import Room
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
