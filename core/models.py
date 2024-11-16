from django.db import models
from django.db.models import Q 
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

# Enum choices for status
STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('cancelled', 'Cancelled'),
]

class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_num = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Room(models.Model):
    room_type = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('available', 'Available'), ('booked', 'Booked'), ('pending', 'Pending')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_as_unavailable(self):
        """
        Mark the room as unavailable when it is booked.
        """
        self.status = 'booked'
        self.save()

    def is_available(self, check_in_date, check_out_date):
        """
        Check if the room is available for the given dates.
        """
        # Check if there are any bookings that overlap with the given dates and are not cancelled
        overlapping_bookings = Booking.objects.filter(
            room=self,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date
        ).exclude(status='cancelled')  # Exclude cancelled bookings

        # If there are overlapping bookings, the room is not available
        return not overlapping_bookings.exists()



    def __str__(self):
        return f"Room {self.id}: {self.room_type} - {self.status}"


from django.db import models

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    room = models.ForeignKey(Room, related_name='bookings', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, related_name='bookings', on_delete=models.CASCADE, default=1)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_confirm(self):
        """
        Check if the room can be confirmed (i.e., it's not already booked for the dates).
        """
        # Check if the room is already booked for the selected dates
        overlapping_bookings = Booking.objects.filter(
            room=self.room,
            status='confirmed',  # Only check confirmed bookings
            check_in_date__lt=self.check_out_date,
            check_out_date__gt=self.check_in_date,
        )
        return not overlapping_bookings.exists()
    def cancel_booking(self):
        """
        Cancel the booking if it's confirmed or pending.
        """
        if self.status != 'cancelled':  # Ensure it's not already cancelled
            self.status = 'cancelled'
            self.room.status = 'available'  # Mark the room as available again
            self.room.save()  # Save the room status
            self.save()  # Save the booking status
            return True
        return False

    def save(self, *args, **kwargs):
        # If the booking is being canceled, ensure the room is available again
        if self.status == 'cancelled' and self.room.status != 'available':
            self.room.status = 'available'  # Mark the room as available
            self.room.save()
            print(f"Room {self.room.id} status updated to available")
        if self.status == 'confirmed' and self.room.status != 'booked':
            self.room.status = 'booked'  # Mark the room as booked
            self.room.save()
            print(f"Room {self.room.id} status updated to booked")
        # Ensure the price is calculated when creating the booking
        if self.check_in_date and self.check_out_date and self.room:
            duration = (self.check_out_date - self.check_in_date).days
            if duration > 0:
                self.total_price = self.room.price_per_night * duration
            else:
                raise ValueError("Check-out date must be after check-in date.")
        
        # Check if the room is available for confirmation
        if self.status == 'confirmed' and not self.can_confirm():
            raise ValueError("The room is already booked for the selected dates and cannot be confirmed.")

        # Save the booking (after all validations)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking for {self.room.id}, {self.room.room_type} by {self.customer.last_name}"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]

    booking = models.ForeignKey(Booking, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for booking {self.booking.id} - {self.status}"

    def save(self, *args, **kwargs):
        if self.booking and not self.amount:
            # Automatically set the amount based on the associated booking's total_price
            self.amount = self.booking.total_price  
        super().save(*args, **kwargs)




# Signal to update Booking and Room status when Payment is confirmed
@receiver(post_save, sender=Payment)
def update_booking_and_room_status(sender, instance, created, **kwargs):
    if instance.status == 'confirmed':
        # Update the related booking status to 'confirmed'
        booking = instance.booking
        if booking.status != 'confirmed':
            booking.status = 'confirmed'
            booking.save()

        # Update the related room status to 'booked'
        room = booking.room
        if room.status != 'booked':
            room.status = 'booked'
            room.save()



class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.first_name}"

class Promotion(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Promotion for {self.room.room_type}"

class Amenity(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    amenity_name = models.CharField(max_length=255)

    def __str__(self):
        return self.amenity_name
