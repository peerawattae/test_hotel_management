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

    def __str__(self):
        return f"Room {self.id}: {self.room_type} - {self.status}"

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

    def save(self, *args, **kwargs):
        if self.check_in_date and self.check_out_date and self.room:
            duration = (self.check_out_date - self.check_in_date).days
            if duration > 0:
                self.total_price = self.room.price_per_night * duration
            else:
                raise ValueError("Check-out date must be after check-in date.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking for {self.room.room_type} by {self.customer.last_name}"

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
            self.amount = self.booking.total_price  # Set amount from booking's total_price
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
