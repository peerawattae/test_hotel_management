from django.db import models
from django.db.models import Q 
# Enum choices
from django.db import models
from django.db.models import Q
from django.utils import timezone


# Enum choices
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
    status = models.CharField(max_length=50, choices=[('available', 'Available'), ('booked', 'Booked')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_available(self, check_in_date, check_out_date):
        """
        Check if the room is available for the given date range.
        """
        conflicting_bookings = self.bookings.filter(
            Q(check_in_date__lte=check_out_date) & Q(check_out_date__gte=check_in_date)
        )
        return not conflicting_bookings.exists()

    def mark_as_unavailable(self):
        """
        Mark the room as unavailable when it is booked.
        """
        self.status = 'booked'
        self.save()

class Booking(models.Model):
    room = models.ForeignKey(Room, related_name='bookings', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Set check_in_date and check_out_date if not provided
        if not self.check_in_date:
            # Example: Set check-in date to today if not set
            self.check_in_date = timezone.now().date()
        if not self.check_out_date:
            # Example: Set check-out date to 1 day after check-in
            self.check_out_date = self.check_in_date + timezone.timedelta(days=1)

        # When the booking is confirmed, update the room's status
        if self.status == 'confirmed':
            self.room.mark_as_unavailable()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking for {self.room.room_type} by {self.user.username}"

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Payment #{self.id}"

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
