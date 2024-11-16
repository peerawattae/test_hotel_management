from django.contrib import admin
from .models import Customer, Room, Booking, Payment, Review, Promotion, Amenity
from .forms import RoomForm, BookingForm
from django.utils.html import format_html
from django.utils.timezone import now
from django.http import JsonResponse

# Room Booking Info View
def room_booking_info(request, room_id):
    try:
        room = Room.objects.prefetch_related('bookings').get(pk=room_id)
        bookings = room.bookings.values('check_in_date', 'check_out_date')
        return JsonResponse({'bookings': list(bookings)})
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)

class BookingAdmin(admin.ModelAdmin):
    form = BookingForm  # Use the custom form that calculates the price
    
    list_display = ['room', 'customer', 'check_in_date', 'check_out_date', 'total_price', 'status']
    search_fields = ['room__room_type', 'user__username']

    # Optional: You could add some inline validation to ensure check-in/check-out date
    def save_model(self, request, obj, form, change):
        # You can use save() method from form here to handle logic before saving.
        obj.save()

# Register the BookingAdmin for the Booking model
admin.site.register(Booking, BookingAdmin)

class RoomAdmin(admin.ModelAdmin):
    form = RoomForm

    def room_availability(self, obj):
        return format_html(
            '<button type="button" class="availability-check" data-room-id="{}">Check Availability</button>',
            obj.id
        )
    room_availability.short_description = 'Room Availability'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            kwargs["queryset"] = Room.objects.exclude(status='booked')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def status_duration(self, obj):
        if obj.updated_at:
            delta = now() - obj.updated_at
            return f"{delta.days} days, {delta.seconds // 3600} hours, {(delta.seconds // 60) % 60} minutes"
        return "N/A"
    status_duration.short_description = "Time in Current Status"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('room-booking-info/<int:room_id>/', room_booking_info, name='room_booking_info'),
        ]
        return custom_urls + urls
    
    def room_booking_info(self, obj):
        """
        Display a button that fetches the booking date range for the room.
        """
        return format_html(
            '<button type="button" class="btn btn-info" onclick="fetchBookingInfo({})">Show Bookings</button>',
            obj.id
        )
    room_booking_info.short_description = "Booking Info"
    list_display = ['id', 'room_type', 'status', 'price_per_night', 'room_booking_info']
    readonly_fields = ()  # Removed 'booked_at'
    list_filter = ('status',)
    search_fields = ('room_type', 'description')

    class Media:
        js = ('static/admin/js/room_availability_check.js',)

# Register the RoomAdmin for the Room model, only if not already registered
if not admin.site.is_registered(Room):
    admin.site.register(Room, RoomAdmin)

# Register other models
admin.site.register(Customer)
admin.site.register(Payment)
admin.site.register(Review)
admin.site.register(Promotion)
admin.site.register(Amenity)
