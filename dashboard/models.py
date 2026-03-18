from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Requester(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.name} {self.last_name}"


class Pet(models.Model):
    SPECIES_CHOICES = [("dog", "Dog"), ("cat", "Cat")]

    name = models.CharField(max_length=100)
    species = models.CharField(max_length=10, choices=SPECIES_CHOICES)
    # 1:N relation: an owner has lots of pets.
    # If we delete the requester, the pet is not deleted, the requester field will remain null.
    requester = models.ForeignKey(
        Requester, on_delete=models.SET_NULL, related_name="pets", null=True, blank=True
    )

    def __str__(self):
        return self.name


class Booking(models.Model):
    # 1:N relation: a pet may have lots of bookings.
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Booking for {self.pet.name}. Starts: {self.start_date.date()}. Finishes: {self.end_date.date()}"


class Review(models.Model):
    # 1:1 relation: a Booking has just ONE review.
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="review"
    )
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    # the validators assure that the number won't be smaller than 1 or greater than 5.
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.stars} stars for booking {self.booking.id}"
