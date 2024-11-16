from django.contrib import admin
from .models import Customer, Room, Booking, Payment, Review, Promotion, Amenity
from django.contrib import admin
from django.utils.html import format_html
from .models import Room
from .forms import RoomForm

class RoomAdmin(admin.ModelAdmin):
    form = RoomForm

    # Optionally, add custom logic to display availability directly in the admin
    def room_availability(self, obj):
        # Add a simple button that will allow users to check availability from the admin page
        return format_html(
            '<button type="button" class="availability-check" data-room-id="{}">Check Availability</button>', 
            obj.id
        )
    room_availability.short_description = 'Room Availability'

    list_display = ['room_type', 'status', 'room_availability']  # Add 'room_availability' to the list display
    list_filter = ('status',)
    search_fields = ('room_type', 'description')

    class Media:
        js = ('admin/js/room_availability_check.js',)

if not admin.site.is_registered(Room):
    admin.site.register(Room, RoomAdmin)
admin.site.register(Customer)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Review)
admin.site.register(Promotion)
admin.site.register(Amenity)
